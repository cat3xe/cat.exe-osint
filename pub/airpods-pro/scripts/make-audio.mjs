// Génère public/audio/score.wav (12 s, 44.1 kHz, stéréo) : bande-son procédurale
// synchronisée sur les coupes (frames 60, 150, 270 à 30 fps).
import {writeFileSync, mkdirSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';

const SR = 44100;
const DUR = 12;
const N = SR * DUR;
const L = new Float32Array(N);
const R = new Float32Array(N);

const hz = (n) => 440 * Math.pow(2, (n - 69) / 12);
const add = (t0, dur, fn) => {
  const s0 = Math.floor(t0 * SR);
  const len = Math.min(Math.floor(dur * SR), N - s0);
  for (let i = 0; i < len; i++) {
    const t = i / SR;
    const v = fn(t, i / len);
    if (s0 + i >= 0) {
      L[s0 + i] += v[0];
      R[s0 + i] += v[1];
    }
  }
};
let seed = 1;
const noise = () => ((seed = (seed * 16807) % 2147483647) / 2147483647) * 2 - 1;

// Pad : accord Am9 très doux, tout le long
const pad = [57, 60, 64, 67, 71];
add(0, DUR, (t) => {
  let v = 0;
  for (const n of pad) v += Math.sin(2 * Math.PI * hz(n) * t) * 0.012;
  const env = Math.min(1, t / 1.5) * Math.min(1, (DUR - t) / 1.5);
  return [v * env, v * env];
});

// Riser (bruit filtré) avant la coupe 1 (1.8 s → 2.0 s) : silence → tension
add(1.5, 0.5, (t, p) => {
  const v = noise() * p * p * 0.35;
  return [v, v];
});
// Whoosh à chaque coupe
for (const c of [2.0, 5.0, 9.0]) {
  add(c - 0.3, 0.6, (t, p) => {
    const v = noise() * Math.sin(Math.PI * p) * 0.25;
    return [v * 0.8, v * 1.2];
  });
}

// DROP (2.0 s) : kick + impact + accord F maj9
add(2.0, 1.2, (t) => {
  const f = 110 * Math.exp(-t * 18) + 45;
  const v = Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 6) * 0.9;
  return [v, v];
});
for (const n of [53, 57, 60, 64, 67]) {
  add(2.0, 3.0, (t) => {
    const v = Math.sin(2 * Math.PI * hz(n) * t) * Math.exp(-t * 1.2) * 0.07;
    return [v * 0.9, v * 1.1];
  });
}

// Groove 120 BPM (2.0 → 5.0 s) : kicks + hi-hats + plucks
for (let b = 0; b < 6; b++) {
  const t0 = 2.0 + b * 0.5;
  if (t0 + 0.3 > DUR) break;
  add(t0, 0.3, (t) => {
    const f = 90 * Math.exp(-t * 22) + 40;
    const v = Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 10) * 0.6;
    return [v, v];
  });
}
for (let h = 0; h < 12; h++) {
  const t0 = 2.25 + h * 0.25;
  add(t0, 0.05, (t, p) => {
    const v = noise() * (1 - p) * 0.08;
    return [v, v * 0.8];
  });
}
const plucks = [69, 72, 76, 79, 81, 79, 76, 72];
plucks.forEach((n, i) => {
  add(2.0 + i * 0.375, 0.5, (t) => {
    const v = (Math.sin(2 * Math.PI * hz(n) * t) + 0.3 * Math.sin(4 * Math.PI * hz(n) * t)) * Math.exp(-t * 7) * 0.09;
    return [v * 1.1, v * 0.9];
  });
});

// Taps UI (features) : 3 clics aux 3 lignes (frames 150, 186, 222)
for (const t0 of [5.0, 6.2, 7.4]) {
  add(t0, 0.08, (t) => {
    const v = Math.sin(2 * Math.PI * 1800 * t) * Math.exp(-t * 80) * 0.25;
    return [v, v];
  });
}

// Final (9.0 s) : cloche + accord qui résonne jusqu'à la fin
for (const n of [60, 64, 67, 71, 74]) {
  add(9.0, 3.0, (t) => {
    const v = (Math.sin(2 * Math.PI * hz(n) * t) + 0.2 * Math.sin(2 * Math.PI * hz(n) * 2.01 * t)) * Math.exp(-t * 1.4) * 0.08;
    return [v * 0.95, v * 1.05];
  });
}
add(9.0, 0.6, (t) => {
  const v = noise() * Math.exp(-t * 10) * 0.15;
  return [v, v];
});

// Normalisation : pic à -1 dBFS + saturation douce
let peak = 0;
for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
const gain = Math.pow(10, -1 / 20) / (peak || 1);
const shape = (x) => Math.tanh(x * gain * 1.2) / Math.tanh(1.2);

// Écriture WAV PCM 16 bits stéréo
const data = Buffer.alloc(N * 4);
for (let i = 0; i < N; i++) {
  data.writeInt16LE(Math.round(Math.max(-1, Math.min(1, shape(L[i]))) * 32767), i * 4);
  data.writeInt16LE(Math.round(Math.max(-1, Math.min(1, shape(R[i]))) * 32767), i * 4 + 2);
}
const header = Buffer.alloc(44);
header.write('RIFF', 0);
header.writeUInt32LE(36 + data.length, 4);
header.write('WAVE', 8);
header.write('fmt ', 12);
header.writeUInt32LE(16, 16);
header.writeUInt16LE(1, 20);
header.writeUInt16LE(2, 22);
header.writeUInt32LE(SR, 24);
header.writeUInt32LE(SR * 4, 28);
header.writeUInt16LE(4, 32);
header.writeUInt16LE(16, 34);
header.write('data', 36);
header.writeUInt32LE(data.length, 40);

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, '..', 'public', 'audio', 'score.wav');
mkdirSync(dirname(out), {recursive: true});
writeFileSync(out, Buffer.concat([header, data]));
console.log('audio →', out);

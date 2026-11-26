import * as THREE from 'three';
// Textures procédurales (originales, générées au lancement : aucun fichier externe à licencier).
function canvasTex(size, draw, repeat = 1) {
  const c = document.createElement('canvas'); c.width = c.height = size;
  const g = c.getContext('2d'); draw(g, size);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat, repeat);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
function noise(g, s, base, amp, n) {
  g.fillStyle = base; g.fillRect(0, 0, s, s);
  for (let i = 0; i < n; i++) {
    const v = Math.random() * amp; g.fillStyle = `rgba(${v > amp / 2 ? '255,255,255' : '0,0,0'},${Math.random() * 0.08})`;
    const r = Math.random() * 3 + 0.5; g.fillRect(Math.random() * s, Math.random() * s, r, r);
  }
}
export const makeConcrete = (rep = 1) => canvasTex(512, (g, s) => {
  noise(g, s, '#9a9a96', 1, 30000);
  g.strokeStyle = 'rgba(0,0,0,.25)'; g.lineWidth = 2;
  for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * s / 4, 0); g.lineTo(i * s / 4, s); g.stroke(); g.beginPath(); g.moveTo(0, i * s / 4); g.lineTo(s, i * s / 4); g.stroke(); }
  for (let i = 0; i < 12; i++) { g.fillStyle = `rgba(40,30,20,${Math.random() * 0.08})`; g.beginPath(); g.arc(Math.random() * s, Math.random() * s, Math.random() * 40 + 10, 0, 7); g.fill(); }
}, rep);
export const makeAsphalt = (rep = 1) => canvasTex(512, (g, s) => noise(g, s, '#3b3d40', 1, 60000), rep);
export const makeWood = (rep = 1) => canvasTex(256, (g, s) => {
  g.fillStyle = '#b07a45'; g.fillRect(0, 0, s, s);
  for (let i = 0; i < 8; i++) { g.fillStyle = `rgba(60,30,10,${0.1 + Math.random() * 0.15})`; g.fillRect(0, i * s / 8, s, 2); }
  for (let i = 0; i < 300; i++) { g.fillStyle = 'rgba(80,40,10,.08)'; g.fillRect(Math.random() * s, Math.random() * s, 40, 1); }
}, rep);
export const makeBrick = (rep = 1) => canvasTex(512, (g, s) => {
  g.fillStyle = '#ccc'; g.fillRect(0, 0, s, s);
  const bh = s / 16, bw = s / 8;
  for (let y = 0; y < 16; y++) for (let x = -1; x < 9; x++) {
    const o = (y % 2) * bw / 2; const v = 120 + Math.random() * 40;
    g.fillStyle = `rgb(${v + 30},${v * 0.5},${v * 0.4})`; g.fillRect(x * bw + o + 2, y * bh + 2, bw - 4, bh - 4);
  }
}, rep);
export const makeGraffiti = () => canvasTex(512, (g, s) => {
  g.fillStyle = '#d8d4cc'; g.fillRect(0, 0, s, s);
  const cols = ['#ff5a4f', '#ffcc33', '#3fd0ff', '#9b5cff', '#35d07f'];
  for (let i = 0; i < 6; i++) {
    g.strokeStyle = cols[i % 5]; g.lineWidth = 18 + Math.random() * 20; g.lineCap = 'round'; g.beginPath();
    g.moveTo(Math.random() * s, Math.random() * s);
    for (let k = 0; k < 4; k++) g.quadraticCurveTo(Math.random() * s, Math.random() * s, Math.random() * s, Math.random() * s);
    g.stroke();
  }
  g.font = 'bold 110px Impact,sans-serif'; g.fillStyle = '#111'; g.fillText('RIDE', 90, 300);
  g.fillStyle = '#ffcc33'; g.fillText('RIDE', 82, 292);
});
export const makeFacade = () => canvasTex(256, (g, s) => {
  g.fillStyle = '#8d8a84'; g.fillRect(0, 0, s, s);
  for (let y = 0; y < 8; y++) for (let x = 0; x < 4; x++) {
    const lit = Math.random() < 0.15; g.fillStyle = lit ? '#f3d58a' : `rgb(${40 + Math.random() * 30},${55 + Math.random() * 30},${75 + Math.random() * 30})`;
    g.fillRect(x * 64 + 12, y * 32 + 8, 40, 18); g.fillStyle = '#6d6a64'; g.fillRect(x * 64 + 8, y * 32 + 27, 48, 3);
  }
});

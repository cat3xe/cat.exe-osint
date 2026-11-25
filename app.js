// Mova Studio — génération d'image IA (Pollinations, gratuit) + mouvements de caméra rendus dans le navigateur.
const $ = (s) => document.querySelector(s);
const cv = $('#cv'), ctx = cv.getContext('2d');
let img = null, imgName = 'mova', move = 'zoomIn', style = '', recording = false, t0 = performance.now();

const STYLES = [
  ['', 'Aucun'], ['cinematic film still, anamorphic lens, dramatic lighting, film grain', 'Cinéma'],
  ['photorealistic, ultra detailed, 8k, natural light', 'Photo réaliste'], ['anime style, vibrant colors, detailed background', 'Anime'],
  ['3d render, pixar-like soft lighting, octane', '3D'], ['neon cyberpunk, night city, rain reflections', 'Cyberpunk'],
  ['vintage 35mm film, kodak portra, warm tones', 'Vintage'], ['moody dark fantasy, volumetric fog', 'Fantasy'],
];

const ease = (t) => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const easeIn = (t) => t * t * t * t;
const noise = (t, f, s) => Math.sin(t * f + s) * .6 + Math.sin(t * f * 2.3 + s * 3) * .3 + Math.sin(t * f * 5.1 + s * 7) * .1;

// Chaque mouvement renvoie {s: zoom, x, y: décalage (fraction du cadre), r: rotation rad, blur: flou de mouvement}
const MOVES = {
  zoomIn:   ['⊕', 'Zoom avant',   (t, k) => ({ s: 1 + .35 * k * ease(t) })],
  zoomOut:  ['⊖', 'Zoom arrière', (t, k) => ({ s: 1 + .35 * k * (1 - ease(t)) })],
  panL:     ['⇠', 'Travelling ←', (t, k) => ({ s: 1, x: .12 * k * (1 - 2 * ease(t)) })],
  panR:     ['⇢', 'Travelling →', (t, k) => ({ s: 1, x: -.12 * k * (1 - 2 * ease(t)) })],
  tiltUp:   ['⇡', 'Tilt haut',    (t, k) => ({ s: 1, y: -.12 * k * (1 - 2 * ease(t)) })],
  tiltDown: ['⇣', 'Tilt bas',     (t, k) => ({ s: 1, y: .12 * k * (1 - 2 * ease(t)) })],
  crash:    ['💥', 'Crash zoom',  (t, k) => { const e = easeIn(t); const sh = t > .85 ? (t - .85) * 6 : 0;
              return { s: 1 + 1.1 * k * e, x: sh * noise(t, 90, 1) * .03, y: sh * noise(t, 90, 2) * .03, blur: e * k * .6 }; }],
  orbit:    ['↻', 'Orbite',       (t, k) => { const a = (ease(t) - .5) * Math.PI; return { s: 1.12, x: Math.sin(a) * .07 * k, r: Math.sin(a) * .045 * k }; }],
  spiral:   ['🌀', 'Spirale',     (t, k) => ({ s: 1 + .45 * k * ease(t), r: ease(t) * .35 * k })],
  hand:     ['✋', 'Caméra épaule', (t, k) => ({ s: 1.06, x: noise(t, 9, 1) * .015 * k, y: noise(t, 7, 4) * .015 * k, r: noise(t, 5, 8) * .008 * k })],
  reveal:   ['🎬', 'Révélation',  (t, k) => ({ s: 1 + .4 * k * (1 - ease(t)), y: -.1 * k * (1 - ease(t)) })],
  whip:     ['⚡', 'Whip pan',     (t, k) => { const w = Math.exp(-Math.pow((t - .5) * 9, 2));
              return { s: 1.1, x: .14 * k * Math.tanh((t - .5) * 9) * -1, blur: w * k }; }],
};

// ---------- UI ----------
STYLES.forEach(([v, n], i) => { const b = document.createElement('button'); b.textContent = n; b.dataset.v = v; if (!i) b.classList.add('active');
  b.onclick = () => { style = v; $('#styles').querySelectorAll('button').forEach(x => x.classList.toggle('active', x === b)); }; $('#styles').append(b); });
Object.entries(MOVES).forEach(([id, [ic, name]]) => { const b = document.createElement('button'); b.className = 'move' + (id === move ? ' active' : '');
  b.innerHTML = `<span class="ic">${ic}</span>${name}`; b.onclick = () => { move = id; t0 = performance.now();
    document.querySelectorAll('.move').forEach(x => x.classList.toggle('active', x === b)); }; $('#moves').append(b); });

document.querySelectorAll('.tab').forEach(b => b.onclick = () => {
  document.querySelectorAll('.tab').forEach(x => x.classList.toggle('active', x === b));
  document.querySelectorAll('.view').forEach(v => v.classList.toggle('active', v.id === b.dataset.tab));
});
document.querySelectorAll('#srcSeg button').forEach(b => b.onclick = () => {
  document.querySelectorAll('#srcSeg button').forEach(x => x.classList.toggle('active', x === b));
  $('#aiBox').hidden = b.dataset.src !== 'ai'; $('#upBox').hidden = b.dataset.src !== 'upload';
});
$('#dur').oninput = (e) => $('#durVal').textContent = e.target.value;
$('#int').oninput = (e) => $('#intVal').textContent = (+e.target.value).toFixed(1);
$('#ratio').onchange = $('#quality').onchange = resize;

const status = (m) => $('#status').textContent = m;
const loading = (on, txt) => { $('#loader').hidden = !on; if (txt) $('#loadTxt').textContent = txt; };

function resize() {
  const [w, h] = $('#ratio').value.split(':').map(Number), q = +$('#quality').value;
  const short = q; cv.width = Math.round((w < h ? short : short * w / h) / 2) * 2; cv.height = Math.round((w < h ? short * h / w : short) / 2) * 2;
}
resize();

// ---------- Chargement d'image ----------
function setImage(im, name) { img = im; imgName = name || 'mova'; $('#empty').hidden = true; $('#recBtn').disabled = false; $('#dlImg').disabled = false; t0 = performance.now(); }

async function loadUrl(url) {
  // fetch → blob pour garder le canvas exportable (pas de "taint" CORS)
  const r = await fetch(url); if (!r.ok) throw new Error('HTTP ' + r.status);
  const blob = await r.blob(); if (!blob.type.startsWith('image')) throw new Error('Réponse non image');
  return await new Promise((ok, ko) => { const im = new Image(); im.onload = () => ok(im); im.onerror = ko; im.src = URL.createObjectURL(blob); });
}

$('#genBtn').onclick = async () => {
  const p = $('#prompt').value.trim(); if (!p) { $('#prompt').focus(); return status('Écris un prompt'); }
  const [w, h] = $('#ratio').value.split(':').map(Number), base = 1024;
  const W = Math.round(w >= h ? base : base * w / h), H = Math.round(h >= w ? base : base * h / w);
  const seed = $('#seed').value || Math.floor(Math.random() * 1e9);
  const full = style ? `${p}, ${style}` : p;
  const url = `https://image.pollinations.ai/prompt/${encodeURIComponent(full)}?width=${W}&height=${H}&seed=${seed}&model=${$('#model').value}&nologo=true`;
  $('#genBtn').disabled = true; loading(true, 'Génération de l\'image… (10-40 s)'); status('Génération…');
  try {
    const im = await loadUrl(url); setImage(im, 'mova-' + seed); saveGal({ url, prompt: p, seed }); status(`Image prête · seed ${seed}`);
  } catch (e) { status('Échec de génération (serveur gratuit saturé ?). Réessaie dans quelques secondes.'); console.error(e); }
  finally { $('#genBtn').disabled = false; loading(false); }
};

const drop = $('#drop');
$('#file').onchange = (e) => e.target.files[0] && readFile(e.target.files[0]);
['dragover', 'dragenter'].forEach(ev => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add('over'); }));
['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, () => drop.classList.remove('over')));
drop.addEventListener('drop', (e) => { e.preventDefault(); e.dataTransfer.files[0] && readFile(e.dataTransfer.files[0]); });
function readFile(f) { const im = new Image(); im.onload = () => { setImage(im, f.name.replace(/\.\w+$/, '')); status('Photo chargée'); }; im.src = URL.createObjectURL(f); }

// ---------- Rendu ----------
const grain = document.createElement('canvas'); grain.width = grain.height = 256;
{ const g = grain.getContext('2d'), d = g.createImageData(256, 256); for (let i = 0; i < d.data.length; i += 4) { const v = Math.random() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; } g.putImageData(d, 0, 0); }

function drawImg(p, alpha = 1) {
  const W = cv.width, H = cv.height, x = p.x || 0, y = p.y || 0, r = p.r || 0;
  // zoom minimum pour ne jamais voir les bords
  const need = 1 + 2 * Math.max(Math.abs(x), Math.abs(y)) + Math.abs(Math.sin(r)) * 1.3;
  const s = Math.max(p.s || 1, need);
  const cover = Math.max(W / img.width, H / img.height) * s;
  ctx.save(); ctx.globalAlpha = alpha; ctx.translate(W / 2 + x * W, H / 2 + y * H); ctx.rotate(r);
  ctx.drawImage(img, -img.width * cover / 2, -img.height * cover / 2, img.width * cover, img.height * cover); ctx.restore();
}

function render(t, frameNo) {
  const W = cv.width, H = cv.height, k = +$('#int').value, fn = MOVES[move][2];
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  if (!img) return;
  const p = fn(t, k), blur = Math.min(p.blur || 0, 1.5);
  if (blur > .05) { // flou de mouvement : on superpose des sous-images
    const n = 6, dt = .012 * blur; for (let i = 0; i < n; i++) drawImg(fn(Math.max(0, Math.min(1, t - dt * (i / n))), k), i ? .35 : 1);
  } else drawImg(p);
  if ($('#fxVignette').checked) { const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .35, W / 2, H / 2, Math.hypot(W, H) / 1.8);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.55)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
  if ($('#fxGrain').checked) { ctx.save(); ctx.globalAlpha = .07; ctx.globalCompositeOperation = 'overlay';
    ctx.fillStyle = ctx.createPattern(grain, 'repeat'); ctx.translate((frameNo * 37) % 256, (frameNo * 91) % 256); ctx.fillRect(-256, -256, W + 512, H + 512); ctx.restore(); }
  if ($('#fxBars').checked) { const bh = Math.max(0, (H - W / 2.39) / 2); if (W > H && bh) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, bh); ctx.fillRect(0, H - bh, W, bh); }
    else { const bh2 = H * .08; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, bh2); ctx.fillRect(0, H - bh2, W, bh2); } }
}

let frame = 0;
function loop(now) {
  if (!recording) { const d = +$('#dur').value * 1000; const t = ((now - t0) % (d + 600)) / d; render(Math.min(t, 1), frame++); $('#progress i').style.width = Math.min(t, 1) * 100 + '%'; }
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

// ---------- Export vidéo ----------
function pickMime() {
  const list = ['video/mp4;codecs=avc1', 'video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm', 'video/mp4'];
  return list.find(m => window.MediaRecorder && MediaRecorder.isTypeSupported(m)) || '';
}

$('#recBtn').onclick = async () => {
  if (!img || recording) return;
  if (!window.MediaRecorder || !cv.captureStream) return status('Ton navigateur ne permet pas l\'export vidéo. Essaie Chrome ou Firefox.');
  const mime = pickMime(), fps = 30, dur = +$('#dur').value, total = dur * fps;
  const stream = cv.captureStream(fps), rec = new MediaRecorder(stream, { mimeType: mime || undefined, videoBitsPerSecond: cv.height >= 1080 ? 12e6 : 7e6 });
  const chunks = []; rec.ondataavailable = (e) => e.data.size && chunks.push(e.data);
  recording = true; $('#recBtn').disabled = true; $('#dlVid').hidden = true; status('Export en cours…');
  const done = new Promise(r => rec.onstop = r);
  render(0, 0); rec.start(250);
  const start = performance.now();
  await new Promise(res => { const step = (now) => { const t = Math.min((now - start) / (dur * 1000), 1); render(t, Math.round(t * total));
    $('#progress i').style.width = t * 100 + '%'; status(`Export… ${Math.round(t * 100)} %`); t < 1 ? requestAnimationFrame(step) : setTimeout(res, 150); }; requestAnimationFrame(step); });
  rec.stop(); await done; stream.getTracks().forEach(t => t.stop());
  const type = mime.split(';')[0] || 'video/webm', blob = new Blob(chunks, { type }), ext = type.includes('mp4') ? 'mp4' : 'webm';
  const a = $('#dlVid'); a.href = URL.createObjectURL(blob); a.download = `${imgName}-${move}.${ext}`; a.hidden = false;
  recording = false; $('#recBtn').disabled = false; t0 = performance.now();
  status(`Vidéo prête (${ext.toUpperCase()}, ${(blob.size / 1e6).toFixed(1)} Mo)`);
};

$('#dlImg').onclick = () => { if (!img) return; const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
  c.getContext('2d').drawImage(img, 0, 0); c.toBlob(b => { const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = imgName + '.png'; a.click(); }); };

// ---------- Galerie (localStorage) ----------
const GK = 'mova-gallery';
const getGal = () => { try { return JSON.parse(localStorage.getItem(GK)) || []; } catch { return []; } };
function saveGal(item) { const g = [{ ...item, ts: Date.now() }, ...getGal()].slice(0, 60); try { localStorage.setItem(GK, JSON.stringify(g)); } catch {} drawGal(); }
function drawGal() {
  const g = getGal(); $('#galCount').textContent = g.length; $('#galEmpty').hidden = g.length > 0; $('#grid').innerHTML = '';
  g.forEach(it => { const c = document.createElement('div'); c.className = 'card'; c.innerHTML = `<img loading="lazy" alt=""><p></p>`;
    c.querySelector('img').src = it.url; c.querySelector('p').textContent = it.prompt;
    c.onclick = async () => { document.querySelector('[data-tab=create]').click(); loading(true, 'Chargement…');
      try { setImage(await loadUrl(it.url), 'mova-' + it.seed); $('#prompt').value = it.prompt; status('Image rechargée'); } catch { status('Impossible de recharger cette image'); } loading(false); };
    $('#grid').append(c); });
}
$('#clearGal').onclick = () => { if (confirm('Vider la galerie ?')) { try { localStorage.removeItem(GK); } catch {} drawGal(); } };
drawGal();

// Mova Studio — génération vidéo IA (Spaces Hugging Face via @gradio/client) + images IA (Pollinations)
import { Client, handle_file } from 'https://cdn.jsdelivr.net/npm/@gradio/client@2.7.2/dist/browser.js';

const $ = (s) => document.querySelector(s);
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
};
function toast(msg, ms = 4000) { const t = $('#toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast.h); toast.h = setTimeout(() => t.hidden = true, ms); }
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// ---------- Préréglages ----------
const MOVES = [
  ['none', '∅', 'Libre', ''],
  ['dollyIn', '⊕', 'Dolly avant', 'slow cinematic dolly in toward the subject'],
  ['dollyOut', '⊖', 'Dolly arrière', 'slow dolly out pulling away from the subject, revealing the scene'],
  ['orbit', '↻', 'Orbite', 'camera orbits smoothly around the subject, 360 degree arc shot'],
  ['crash', '💥', 'Crash zoom', 'sudden fast crash zoom into the subject'],
  ['fpv', '🛩️', 'Drone FPV', 'fast FPV drone shot flying through the scene, dynamic banking'],
  ['track', '⇢', 'Travelling', 'smooth lateral tracking shot following the subject'],
  ['crane', '⇡', 'Grue', 'crane shot rising up, revealing a wide view'],
  ['hand', '✋', 'Épaule', 'handheld camera, natural slight shake, documentary feel'],
  ['bullet', '⏱️', 'Bullet time', 'bullet time effect, frozen moment while the camera rotates around'],
  ['low', '⤒', 'Contre-plongée', 'low angle hero shot looking up at the subject'],
  ['push', '🎯', 'Push focus', 'rack focus from foreground to the subject, shallow depth of field'],
];
const STYLES = [
  ['', 'Style : aucun'], ['cinematic film look, anamorphic lens, dramatic lighting, film grain', 'Cinéma'],
  ['photorealistic, natural light, ultra detailed', 'Réaliste'], ['anime style, vibrant colors, detailed background', 'Anime'],
  ['3d animated film style, soft lighting', '3D'], ['premium commercial product shot, studio lighting, glossy reflections', 'Pub produit'],
  ['neon cyberpunk night, rain reflections', 'Cyberpunk'], ['vintage 16mm film, warm tones', 'Vintage'],
];
const IDEAS = [
  'Un samouraï sous une pluie de pétales de cerisier, ralenti',
  'Une voiture de sport qui dérape sur une route mouillée la nuit',
  'Un chat astronaute qui flotte dans une station spatiale',
  'Des vagues géantes qui frappent un phare pendant la tempête',
];
const NEG = 'worst quality, blurry, distorted, jittery, low resolution, watermark, text';

let move = 'none', vImg = null;
for (const [id, ic, name] of MOVES) {
  const b = document.createElement('button'); b.className = 'mv' + (id === move ? ' active' : ''); b.innerHTML = `<span>${ic}</span>${name}`;
  b.onclick = () => { move = id; document.querySelectorAll('.mv').forEach((x) => x.classList.toggle('active', x === b)); }; $('#vMoves').append(b);
}
for (const sel of ['#vStyle', '#iStyle']) for (const [v, n] of STYLES) { const o = document.createElement('option'); o.value = v; o.textContent = sel === '#iStyle' && !v ? 'Aucun' : n; $(sel).append(o); }
$('#vStyle').value = STYLES[1][0];
for (const t of IDEAS) { const b = document.createElement('button'); b.textContent = t; b.onclick = () => { $('#vPrompt').value = t; $('#vPrompt').focus(); }; $('#ideas').append(b); }

// ---------- Token ----------
const tok = () => { const t = store.get('mova-hf', ''); return /^hf_\w+/.test(t) ? t : null; };
function showTok() { $('#tokState').textContent = tok() ? 'Token HF actif : quota élargi' : 'Sans token : quelques vidéos par jour'; $('#hfTok').value = tok() ? '••••••••' : ''; }
$('#hfSave').onclick = () => { const v = $('#hfTok').value.trim(); if (!/^hf_\w{10,}/.test(v)) return toast('Le token doit commencer par hf_'); store.set('mova-hf', v); showTok(); toast('Token enregistré ✔'); };
$('#hfDel').onclick = () => { store.set('mova-hf', ''); showTok(); toast('Token effacé'); };
showTok();

// ---------- Image à animer ----------
function setVImg(blob) {
  vImg = blob; const u = URL.createObjectURL(blob); $('#vThumb').src = u; $('#vThumb').hidden = false; $('#imgSlotTxt').hidden = true; $('#vClearImg').hidden = false;
  const im = new Image(); im.onload = () => { vImg.w = im.naturalWidth; vImg.h = im.naturalHeight; }; im.src = u;
}
$('#vFile').onchange = (e) => e.target.files[0] && setVImg(e.target.files[0]);
$('#vClearImg').onclick = (e) => { e.preventDefault(); vImg = null; $('#vThumb').hidden = true; $('#imgSlotTxt').hidden = false; $('#vClearImg').hidden = true; $('#vFile').value = ''; };
$('#imgSlot').addEventListener('dragover', (e) => e.preventDefault());
$('#imgSlot').addEventListener('drop', (e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; f && f.type.startsWith('image') && setVImg(f); });

// ---------- Moteurs ----------
const r32 = (x) => Math.max(256, Math.round(x / 32) * 32);
function dims(ratio, q, img) {
  const long = q === 'hd' ? 1216 : 832;
  let a = img && img.w ? img.w / img.h : ({ '16:9': 16 / 9, '9:16': 9 / 16, '1:1': 1 })[ratio];
  return a >= 1 ? [r32(long), r32(long / a)] : [r32(long * a), r32(long)];
}
const ENGINES = {
  ltx23: { name: 'Mova Ciné', space: 'Lightricks/LTX-2-3', img: 'opt',
    call: (c, p) => c.predict('/generate_video', { input_image: p.img ? handle_file(p.img) : null, prompt: p.prompt, duration: p.dur, enhance_prompt: true, seed: 0, randomize_seed: true, height: p.h, width: p.w }) },
  ltxfast: { name: 'Mova Rapide', space: 'Lightricks/ltx-video-distilled', img: 'opt',
    call: (c, p) => p.img
      ? c.predict('/image_to_video', [p.prompt, NEG, handle_file(p.img), null, p.h, p.w, 'image-to-video', Math.min(p.dur, 8.5), 9, 42, true, 1, true])
      : c.predict('/text_to_video', [p.prompt, NEG, null, null, p.h, p.w, 'text-to-video', Math.min(p.dur, 8.5), 9, 42, true, 1, true]) },
  wan: { name: 'Mova Anim', space: 'zerogpu-aoti/wan2-2-fp8da-aoti-faster', img: 'req',
    call: (c, p) => c.predict('/generate_video', { input_image: handle_file(p.img), prompt: p.prompt, steps: 6, negative_prompt: NEG, duration_seconds: Math.min(p.dur, 5), guidance_scale: 1, guidance_scale_2: 1, seed: 42, randomize_seed: true }) },
};
const clients = {};
async function getClient(id) {
  const key = id + (tok() || '');
  if (!clients[key]) clients[key] = Client.connect(ENGINES[id].space, tok() ? { token: tok() } : {}).catch((e) => { delete clients[key]; throw e; });
  return clients[key];
}
const isQuota = (e) => /quota|exceeded|limit/i.test(e?.message || e?.title || '');

// ---------- Fil des générations ----------
function card(p) {
  $('#hero')?.remove();
  const el = document.createElement('div'); el.className = 'job';
  el.innerHTML = `<div class="media" style="aspect-ratio:${p.w}/${p.h}"><div class="wait"><div class="spin"></div><b class="st">Connexion…</b><small class="sub"></small><div class="pbar"><i></i></div></div></div>
    <div class="meta"><p>${esc(p.userPrompt)}</p><div class="tags"><span>${p.w}×${p.h}</span><span>${p.dur} s</span><span class="eng"></span>${p.moveName ? `<span>${esc(p.moveName)}</span>` : ''}</div><div class="acts"></div></div>`;
  $('#feed').prepend(el);
  return {
    el, status(t, sub = '', pct = null) { el.querySelector('.st').textContent = t; el.querySelector('.sub').textContent = sub; if (pct != null) el.querySelector('.pbar i').style.width = pct + '%'; },
    engine(n) { el.querySelector('.eng').textContent = n; },
    done(url) {
      el.querySelector('.media').innerHTML = `<video src="${esc(url)}" controls autoplay loop muted playsinline></video>`;
      const a = el.querySelector('.acts');
      a.innerHTML = '<button class="ghost dl">⬇ Télécharger</button><button class="ghost again">↻ Refaire</button>';
      a.querySelector('.dl').onclick = () => download(url, 'mova-' + Date.now() + '.mp4');
      a.querySelector('.again').onclick = () => { $('#vPrompt').value = p.userPrompt; generate(); };
    },
    fail(msg, quota) {
      el.querySelector('.media').innerHTML = `<div class="wait err"><b>${quota ? 'Quota gratuit atteint' : 'Échec'}</b><small>${esc(msg)}</small>${quota ? '<button class="ghost toSet">Ajouter un token gratuit</button>' : ''}</div>`;
      el.querySelector('.toSet')?.addEventListener('click', () => document.querySelector('[data-tab=settings]').click());
    },
  };
}

async function download(url, name) {
  try { const b = await (await fetch(url)).blob(); const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = name; a.click(); }
  catch { window.open(url, '_blank'); }
}

async function runEngine(id, p, ui) {
  const E = ENGINES[id]; ui.engine(E.name); ui.status('Connexion au GPU…', E.name, 3);
  const c = await getClient(id);
  const t0 = Date.now();
  const tick = setInterval(() => { const el = Math.round((Date.now() - t0) / 1000);
    ui.status(el < 4 ? 'Envoi au GPU…' : 'Génération en cours…', `${E.name} · ${el} s`, Math.min(94, 4 + 90 * (1 - Math.exp(-el / 45)))); }, 1000);
  try {
    const r = await E.call(c, p);
    const d = r?.data?.[0]; const url = d?.video?.url || d?.url || (typeof d === 'string' ? d : null);
    if (!url) throw new Error('Réponse vide du serveur');
    return url;
  } catch (e) {
    if (e instanceof Error) throw e;
    const err = new Error(e?.message || e?.title || 'Erreur du serveur'); err.title = e?.title; throw err;
  } finally { clearInterval(tick); }
}

async function generate() {
  const userPrompt = $('#vPrompt').value.trim();
  if (!userPrompt && !vImg) { $('#vPrompt').focus(); return toast('Écris une description ou ajoute une image'); }
  const mv = MOVES.find((m) => m[0] === move), style = $('#vStyle').value;
  const prompt = [userPrompt || 'bring this image to life with natural motion', mv[3], style].filter(Boolean).join(', ');
  let eng = $('#vEngine').value;
  if (eng === 'wan' && !vImg) return toast('Mova Anim a besoin d\'une image : ajoute-en une avec le bouton ＋');
  const order = eng !== 'auto' ? [eng] : vImg ? ['ltx23', 'wan', 'ltxfast'] : ['ltx23', 'ltxfast'];
  const [w, h] = dims($('#vRatio').value, $('#vQual').value, vImg);
  const p = { prompt, userPrompt: userPrompt || '(image animée)', img: vImg, dur: +$('#vDur').value, w, h, moveName: mv[0] === 'none' ? '' : mv[2] };
  const ui = card(p);
  let last;
  for (const id of order) {
    try {
      const url = await runEngine(id, p, ui); ui.done(url);
      const g = store.get('mova-vgal', []); g.unshift({ url, prompt: p.userPrompt, eng: ENGINES[id].name, ts: Date.now() }); store.set('mova-vgal', g.slice(0, 40)); drawVGal();
      return;
    } catch (e) {
      last = e; console.warn(id, e);
      if (isQuota(e)) break; // le quota est commun à tous les moteurs
      ui.status('Moteur indisponible, essai du suivant…', ENGINES[id].name, 5);
    }
  }
  ui.fail(isQuota(last) ? (tok() ? 'Ton quota du jour est épuisé, réessaie plus tard.' : 'Ajoute un token Hugging Face gratuit pour continuer (Réglages).') : (last?.message || 'Serveurs occupés, réessaie dans un moment.'), isQuota(last));
}
$('#vGo').onclick = generate;
$('#vPrompt').addEventListener('keydown', (e) => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) generate(); });

// ---------- Galerie vidéo ----------
function drawVGal() {
  const g = store.get('mova-vgal', []); $('#vGalEmpty').hidden = g.length > 0; $('#vGrid').innerHTML = '';
  for (const it of g) {
    const c = document.createElement('div'); c.className = 'card';
    c.innerHTML = `<video src="${esc(it.url)}" muted loop playsinline preload="metadata"></video><p>${esc(it.prompt)}</p>`;
    const v = c.querySelector('video'); c.onmouseenter = () => v.play().catch(() => {}); c.onmouseleave = () => v.pause();
    c.onclick = () => download(it.url, 'mova-' + it.ts + '.mp4');
    $('#vGrid').append(c);
  }
}
drawVGal();

// ---------- Image IA ----------
$('#iGo').onclick = async () => {
  const p = $('#iPrompt').value.trim(); if (!p) return toast('Écris une description');
  const [a, b] = $('#iRatio').value.split(':').map(Number); const W = Math.round(a >= b ? 1024 : 1024 * a / b), H = Math.round(b >= a ? 1024 : 1024 * b / a);
  const full = [p, $('#iStyle').value].filter(Boolean).join(', '); const n = +$('#iCount').value;
  for (let i = 0; i < n; i++) {
    const seed = Math.floor(Math.random() * 1e9);
    const url = `https://image.pollinations.ai/prompt/${encodeURIComponent(full)}?width=${W}&height=${H}&seed=${seed}&model=flux&nologo=true`;
    const c = document.createElement('div'); c.className = 'icard'; c.style.aspectRatio = `${W}/${H}`;
    c.innerHTML = '<div class="wait"><div class="spin"></div><small>Génération…</small></div>'; $('#iGrid').prepend(c);
    fetch(url).then((r) => { if (!r.ok) throw 0; return r.blob(); }).then((blob) => {
      const u = URL.createObjectURL(blob);
      c.innerHTML = `<img src="${u}" alt=""><div class="ov"><button data-a="vid">🎬 Animer en vidéo IA</button><button data-a="fx">🎥 Effet caméra</button><button data-a="dl">⬇</button></div>`;
      c.querySelector('[data-a=vid]').onclick = () => { setVImg(blob); $('#vPrompt').value = p; document.querySelector('[data-tab=video]').click(); toast('Image ajoutée : choisis un mouvement et génère'); };
      c.querySelector('[data-a=fx]').onclick = () => { const im = new Image(); im.onload = () => { window.setImage(im, 'mova-' + seed); document.querySelector('[data-tab=create]').click(); }; im.src = u; };
      c.querySelector('[data-a=dl]').onclick = () => { const a = document.createElement('a'); a.href = u; a.download = `mova-${seed}.jpg`; a.click(); };
      try { window.saveGal?.({ url, prompt: p, seed }); } catch {}
    }).catch(() => { c.innerHTML = '<div class="wait err"><small>Échec (serveur saturé), réessaie.</small></div>'; });
  }
};

import { settings, saveSettings, QUALITY, ACTION_LABELS, DEFAULT_BINDINGS, keyLabel } from '../save/settings.js';
// Menus réellement fonctionnels (aucun bouton décoratif : les sections à venir n'apparaissent pas encore).
export class Menu {
  constructor(game) { this.g = game; this.el = document.getElementById('menu'); this.stack = []; }
  // Navigation manette : D-pad / stick gauche = déplacer, A = valider, B = retour, Start = reprendre
  pad(cmd) {
    if (!cmd || !this.open) return;
    const items = [...this.el.querySelectorAll('button, select, input')];
    let i = items.indexOf(document.activeElement);
    const cur = items[i];
    if (cmd === 'up' || cmd === 'down') { i = i < 0 ? 0 : (i + (cmd === 'down' ? 1 : -1) + items.length) % items.length; items[i].focus(); items[i].scrollIntoView({ block: 'nearest' }); return; }
    if (cmd === 'back') { if (this.screen === 'pause') this.g.resume(); else if (this.screen !== 'main') this.back(); return; }
    if (cmd === 'start') { if (this.g.started) this.g.resume(); return; }
    if (!cur) { items[0]?.focus(); return; }
    if (cmd === 'left' || cmd === 'right') {
      const d = cmd === 'right' ? 1 : -1;
      if (cur.type === 'range') { cur.value = +cur.value + d * +cur.step; cur.dispatchEvent(new Event('input')); }
      else if (cur.tagName === 'SELECT') { cur.selectedIndex = (cur.selectedIndex + d + cur.options.length) % cur.options.length; cur.dispatchEvent(new Event('change')); }
      return;
    }
    if (cmd === 'ok') {
      if (cur.type === 'checkbox') { cur.checked = !cur.checked; cur.dispatchEvent(new Event('change')); }
      else if (cur.tagName === 'SELECT') { cur.selectedIndex = (cur.selectedIndex + 1) % cur.options.length; cur.dispatchEvent(new Event('change')); }
      else if (cur.tagName === 'BUTTON') cur.click();
      return;
    }
  }
  get open() { return !this.el.classList.contains('hidden'); }
  show(screen) { this.el.classList.remove('hidden'); this.screen = screen; this[screen](); document.exitPointerLock?.(); if (!this.el.contains(document.activeElement) || document.activeElement === document.body) this.el.querySelector('button, select, input')?.focus(); }
  hide() { this.el.classList.add('hidden'); this.screen = null; }
  back() { this.show(this.g.started ? 'pause' : 'main'); }
  panel(html) { this.el.innerHTML = `<div class="panel">${html}</div>`; return this.el.firstChild; }
  bind(id, fn) { this.el.querySelector('#' + id)?.addEventListener('click', fn); }
  main() {
    this.panel(`<h1>STREET RIDE 3D</h1><p class="sub">Prototype jouable · Phase 1-2 : skateboard</p>
      <button id="m-play">Jouer</button><button id="m-controls">Commandes</button><button id="m-settings">Paramètres</button>`);
    this.bind('m-play', () => this.g.start()); this.bind('m-controls', () => this.show('controls')); this.bind('m-settings', () => this.show('settingsScreen'));
    this.el.querySelector('#m-play').focus();
  }
  pause() {
    this.panel(`<h2>Pause</h2><button id="p-resume">Reprendre</button><button id="p-reset">Réinitialiser le personnage</button>
      <button id="p-controls">Commandes</button><button id="p-settings">Paramètres</button><button id="p-stats">Statistiques</button>`);
    this.bind('p-resume', () => this.g.resume()); this.bind('p-reset', () => { this.g.player.respawn(true); this.g.resume(); });
    this.bind('p-controls', () => this.show('controls')); this.bind('p-settings', () => this.show('settingsScreen')); this.bind('p-stats', () => this.show('stats'));
  }
  stats() {
    const s = this.g.score.stats;
    this.panel(`<h2>Statistiques</h2><table><tr><td>Meilleur score de session</td><td>${s.best}</td></tr><tr><td>Meilleure ligne</td><td>${s.bestLine}</td></tr>
      <tr><td>Points cumulés</td><td>${s.total}</td></tr><tr><td>Tricks réalisés</td><td>${s.tricks}</td></tr><tr><td>Chutes</td><td>${s.bails}</td></tr></table><button id="b">Retour</button>`);
    this.bind('b', () => this.back());
  }
  controls() {
    const k = a => `<b>${keyLabel(settings.bindings[a])}</b>`;
    this.panel(`<h2>Commandes — Skateboard (logique Flick-It)</h2><table>
      <tr><td>Pousser</td><td>${k('push')} · Manette A</td></tr><tr><td>Tourner / rotation en l'air</td><td>${k('left')} ${k('right')} · stick gauche</td></tr>
      <tr><td>Freiner</td><td>${k('brake')} · stick gauche bas</td></tr><tr><td>Stick droit (tricks)</td><td>Flèches · <b>clic droit maintenu + souris</b> · stick droit</td></tr>
      <tr><td>Ollie</td><td>Stick droit ↓ puis ↑ (rapide)</td></tr><tr><td>Nollie</td><td>↑ puis ↓</td></tr>
      <tr><td>Kickflip / Heelflip</td><td>↓ puis ↖ / ↓ puis ↗</td></tr><tr><td>Pop shove-it BS / FS</td><td>↓ puis ← puis ↑ / ↓ → ↑</td></tr>
      <tr><td>Shove-it (sans pop)</td><td>↓ puis ← (ou →) puis relâcher</td></tr><tr><td>Varial kickflip / heelflip</td><td>↓ ← ↖ / ↓ → ↗</td></tr>
      <tr><td>Nollie flips</td><td>↑ puis ↙ / ↑ puis ↘</td></tr><tr><td>Manual / Nose manual</td><td>Stick droit à mi-course bas / haut (souris), équilibre avec ${k('forward')} ${k('back')}</td></tr>
      <tr><td>Grinds / slides</td><td>Retomber sur un rail ou une ledge. Angle de la planche = type (50-50, boardslide, crooked). Stick droit ↑/↓ en arrivant = nosegrind / 5-0. Équilibre avec ${k('left')} ${k('right')}</td></tr>
      <tr><td>Monter / descendre du skate</td><td>${k('interact')} · Manette X</td></tr><tr><td>À pied : marcher / courir / sauter</td><td>${k('forward')}${k('left')}${k('back')}${k('right')} / ${k('run')} / ${k('push')}</td></tr>
      <tr><td>Réinitialiser</td><td>${k('reset')} · Manette Y</td></tr><tr><td>Caméra</td><td>Souris · ${k('camera')} change de vue · Manette RB</td></tr>
      <tr><td>Menu</td><td>Échap · Start</td></tr></table>
      <h2 style="margin-top:14px">Manette (Xbox / PlayStation)</h2><table>
      <tr><td>Stick gauche</td><td>Tourner, freiner (bas), rotation en l'air, équilibre</td></tr>
      <tr><td>Stick droit</td><td>Tricks Flick-It (en skate) · caméra (à pied)</td></tr>
      <tr><td>A / Croix · RT</td><td>Pousser / sauter</td></tr><tr><td>B / Rond</td><td>Freiner</td></tr>
      <tr><td>X / Carré</td><td>Monter / descendre du skate</td></tr><tr><td>Y / Triangle</td><td>Réinitialiser</td></tr>
      <tr><td>RB · LB</td><td>Changer de caméra · tourner la caméra</td></tr><tr><td>LT · L3</td><td>Courir (à pied)</td></tr>
      <tr><td>Start · Back</td><td>Menu · aide</td></tr><tr><td>Menus</td><td>D-pad / stick gauche, A valider, B retour, ←/→ régler</td></tr></table>
      <p class="sub" style="margin-top:10px">Réception : le flip doit être terminé, la planche alignée avec la direction, la rotation proche d'un multiple de 180°.</p><button id="b">Retour</button>`);
    this.bind('b', () => this.back());
  }
  settingsScreen() {
    const opt = (v, cur) => Object.keys(v).map(k => `<option value="${k}" ${k === cur ? 'selected' : ''}>${k}</option>`).join('');
    const binds = Object.keys(ACTION_LABELS).map(a => `<div class="row"><span>${ACTION_LABELS[a]}</span><button data-bind="${a}">${keyLabel(settings.bindings[a])}</button></div>`).join('');
    this.panel(`<h2>Paramètres</h2>
      <div class="row"><span>Qualité graphique</span><select id="s-q">${opt(QUALITY, settings.quality)}</select></div>
      <div class="row"><span>Échelle de résolution (${Math.round(settings.resolutionScale * 100)} %)</span><input id="s-res" type="range" min="0.5" max="1.5" step="0.05" value="${settings.resolutionScale}"></div>
      <div class="row"><span>Distance d'affichage (${settings.viewDist} m)</span><input id="s-vd" type="range" min="80" max="600" step="20" value="${settings.viewDist}"></div>
      <div class="row"><span>Ombres</span><input id="s-sh" type="checkbox" ${settings.shadows ? 'checked' : ''}></div>
      <div class="row"><span>Sensibilité souris</span><input id="s-ms" type="range" min="0.2" max="3" step="0.1" value="${settings.mouseSens}"></div>
      <div class="row"><span>Inverser l'axe Y caméra</span><input id="s-inv" type="checkbox" ${settings.invertY ? 'checked' : ''}></div>
      <h2 style="margin-top:18px">Touches (clic puis appuyer sur une touche)</h2>${binds}
      <button id="s-def">Touches par défaut (AZERTY)</button><button id="b">Retour</button>`);
    const apply = () => { saveSettings(); this.g.applyGraphics(); };
    this.el.querySelector('#s-q').onchange = e => { const q = QUALITY[e.target.value]; settings.quality = e.target.value; settings.shadows = q.shadows; settings.viewDist = q.viewDist; apply(); this.settingsScreen(); };
    this.el.querySelector('#s-res').oninput = e => { settings.resolutionScale = +e.target.value; apply(); e.target.parentNode.firstChild.textContent = `Échelle de résolution (${Math.round(settings.resolutionScale * 100)} %)`; };
    this.el.querySelector('#s-vd').oninput = e => { settings.viewDist = +e.target.value; apply(); e.target.parentNode.firstChild.textContent = `Distance d'affichage (${settings.viewDist} m)`; };
    this.el.querySelector('#s-sh').onchange = e => { settings.shadows = e.target.checked; apply(); };
    this.el.querySelector('#s-ms').oninput = e => { settings.mouseSens = +e.target.value; saveSettings(); };
    this.el.querySelector('#s-inv').onchange = e => { settings.invertY = e.target.checked; saveSettings(); };
    this.el.querySelectorAll('[data-bind]').forEach(b => b.onclick = () => {
      b.textContent = '…'; this.g.input.capture = code => { if (code !== 'Escape') { settings.bindings[b.dataset.bind] = code; saveSettings(); } this.settingsScreen(); };
    });
    this.bind('s-def', () => { settings.bindings = { ...DEFAULT_BINDINGS }; saveSettings(); this.settingsScreen(); });
    this.bind('b', () => this.back());
  }
}

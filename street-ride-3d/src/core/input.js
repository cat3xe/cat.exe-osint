import { settings } from '../save/settings.js';

// Agrège clavier, souris et manette en un état unique lu chaque frame.
// move  : stick gauche (x droite, y haut)   flick : stick droit (Flick-It)
// look  : delta caméra                      pressed()/just() : actions logiques
export class Input {
  constructor(canvas) {
    this.keys = new Set(); this.justKeys = new Set();
    this.move = { x: 0, y: 0 }; this.flick = { x: 0, y: 0 }; this.flickAnalog = { x: 0, y: 0 }; this.look = { x: 0, y: 0 };
    this.mouseStick = { x: 0, y: 0 }; this.rmb = false; this.pad = null; this.padPrev = []; this.padJust = new Set();
    this.source = 'clavier'; this.enabled = true; this.capture = null;
    this.flickQueue = []; // échantillons clavier horodatés : aucun appui court n'est perdu, même à bas FPS
    addEventListener('keydown', e => {
      if (this.capture) { e.preventDefault(); const c = this.capture; this.capture = null; c(e.code); return; }
      if (!this.keys.has(e.code)) this.justKeys.add(e.code);
      this.keys.add(e.code); this.source = 'clavier'; this.queueFlick(e.code, e.timeStamp);
      if (e.code.startsWith('Arrow') || e.code === 'Space' || e.code === 'Tab') e.preventDefault();
    });
    addEventListener('keyup', e => { this.keys.delete(e.code); this.queueFlick(e.code, e.timeStamp); });
    addEventListener('blur', () => this.keys.clear());
    canvas.addEventListener('contextmenu', e => e.preventDefault());
    canvas.addEventListener('mousedown', e => {
      if (document.pointerLockElement !== canvas && this.enabled) canvas.requestPointerLock?.();
      if (e.button === 2) this.rmb = true;
    });
    addEventListener('mouseup', e => { if (e.button === 2) { this.rmb = false; } });
    addEventListener('mousemove', e => {
      if (document.pointerLockElement !== canvas) return;
      const s = settings.mouseSens;
      if (this.rmb) { // souris = stick droit virtuel
        this.mouseStick.x += e.movementX * 0.02 * s; this.mouseStick.y -= e.movementY * 0.02 * s;
        const m = Math.hypot(this.mouseStick.x, this.mouseStick.y); if (m > 1) { this.mouseStick.x /= m; this.mouseStick.y /= m; }
      } else { this.look.x += e.movementX * 0.003 * s; this.look.y += e.movementY * 0.003 * s * (settings.invertY ? -1 : 1); }
      this.source = 'souris';
    });
  }
  queueFlick(code, ts = performance.now()) {
    const b = settings.bindings; if (![b.flickUp, b.flickDown, b.flickLeft, b.flickRight].includes(code)) return;
    let x = (this.keys.has(b.flickRight) ? 1 : 0) - (this.keys.has(b.flickLeft) ? 1 : 0), y = (this.keys.has(b.flickUp) ? 1 : 0) - (this.keys.has(b.flickDown) ? 1 : 0);
    if (x && y) { x *= 0.7071; y *= 0.7071; }
    this.flickQueue.push({ x, y, t: ts });
  }
  code(action) { return settings.bindings[action]; }
  pressed(action) {
    if (this.keys.has(this.code(action))) return true;
    return this.padBtn(action, false);
  }
  just(action) { return this.justKeys.has(this.code(action)) || this.padBtn(action, true); }
  justCode(code) { return this.justKeys.has(code); }
  padBtn(action, just) {
    // Disposition standard (Xbox / PlayStation via navigateur) : A/Croix=0 B/Rond=1 X/Carré=2 Y/Triangle=3 LB=4 RB=5 LT=6 RT=7 Back=8 Start=9 L3=10
    const map = { push: [0, 7], brake: [1], interact: [2], reset: [3], camera: [5], run: [10, 6], help: [8], menu: [9] };
    const ids = map[action]; if (!ids || !this.pad) return false;
    return ids.some(i => just ? this.padJust.has(i) : !!this.pad.buttons[i]?.pressed && !this.padBlock?.has(i));
  }
  update(dt) {
    // Manette
    const pads = navigator.getGamepads ? [...navigator.getGamepads()].filter(Boolean) : [];
    this.pad = pads[0] || null; this.padJust.clear();
    if (this.pad) {
      this.padBlock?.forEach(i => { if (!this.pad.buttons[i]?.pressed) this.padBlock.delete(i); });
      this.pad.buttons.forEach((b, i) => { if (b.pressed && !this.padPrev[i]) { this.padJust.add(i); this.source = 'manette'; } this.padPrev[i] = b.pressed; });
    }
    const dz = v => Math.abs(v) < 0.15 ? 0 : v;
    let mx = (this.pressed('right') ? 1 : 0) - (this.pressed('left') ? 1 : 0);
    let my = (this.keys.has(this.code('forward')) ? 1 : 0) - (this.keys.has(this.code('back')) ? 1 : 0);
    let fx = (this.keys.has(this.code('flickRight')) ? 1 : 0) - (this.keys.has(this.code('flickLeft')) ? 1 : 0);
    let fy = (this.keys.has(this.code('flickUp')) ? 1 : 0) - (this.keys.has(this.code('flickDown')) ? 1 : 0);
    if (fx && fy) { fx *= 0.7071; fy *= 0.7071; }
    // Stick souris : ressort de rappel vers le centre quand on relâche
    if (!this.rmb) { this.mouseStick.x *= Math.pow(0.0001, dt); this.mouseStick.y *= Math.pow(0.0001, dt); }
    else { this.mouseStick.x *= Math.pow(0.05, dt); this.mouseStick.y *= Math.pow(0.05, dt); }
    // Analogique (souris / manette) : échantillonné en continu. Le clavier passe uniquement par flickQueue.
    let ax = this.mouseStick.x, ay = this.mouseStick.y;
    if (Math.abs(ax) + Math.abs(ay) > Math.abs(fx) + Math.abs(fy)) { fx = ax; fy = ay; }
    if (this.pad) {
      const a = this.pad.axes;
      if (dz(a[0]) || dz(a[1])) { mx = dz(a[0]); my = -dz(a[1]); }
      if (dz(a[2]) || dz(a[3])) { fx = ax = dz(a[2]); fy = ay = -dz(a[3]); }
      // Stick droit = caméra quand on est à pied (en skate il sert aux tricks, la caméra suit seule)
      this.padLook = { x: dz(a[2]), y: dz(a[3]) };
      if (this.pad.buttons[4]?.pressed) this.look.x -= 1.5 * dt; // LB : tourner la caméra
    }
    this.move.x = mx; this.move.y = my; this.flick.x = fx; this.flick.y = fy; this.flickAnalog.x = ax; this.flickAnalog.y = ay;
  }
  // Vibration (si la manette et le navigateur la gèrent)
  rumble(strong = 0.5, ms = 120) {
    try { this.pad?.vibrationActuator?.playEffect?.('dual-rumble', { duration: ms, strongMagnitude: strong, weakMagnitude: strong * 0.6 }); } catch { /* non supporté */ }
  }
  // Lecture manette pendant les menus (la boucle de jeu est en pause)
  pollMenu() {
    const p = [...(navigator.getGamepads?.() || [])].find(Boolean); if (!p) return null;
    const ax = p.axes[0] || 0, ay = p.axes[1] || 0, now = performance.now();
    const btn = i => !!p.buttons[i]?.pressed; this.menuPrev ??= [];
    const edge = i => { const e = btn(i) && !this.menuPrev[i]; return e; };
    let out = null;
    if (edge(0)) out = 'ok'; else if (edge(1)) out = 'back'; else if (edge(9)) out = 'start';
    else if (edge(12)) out = 'up'; else if (edge(13)) out = 'down'; else if (edge(14)) out = 'left'; else if (edge(15)) out = 'right';
    else if (now - (this.menuStickT || 0) > 220) {
      const d = ay < -0.6 ? 'up' : ay > 0.6 ? 'down' : ax < -0.6 ? 'left' : ax > 0.6 ? 'right' : null;
      if (d) { out = d; this.menuStickT = now; }
    }
    p.buttons.forEach((b, i) => this.menuPrev[i] = b.pressed);
    return out;
  }
  endFrame() { this.justKeys.clear(); this.look.x = 0; this.look.y = 0; }
}

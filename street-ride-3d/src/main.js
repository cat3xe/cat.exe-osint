import * as THREE from 'three';
import { Input } from './core/input.js';
import { ScoreSystem } from './core/score.js';
import { PhysicsWorld } from './world/physics.js';
import { buildTestPark } from './world/testPark.js';
import { Player } from './player/player.js';
import { FollowCamera } from './camera/followCamera.js';
import { Menu } from './ui/menu.js';
import { settings, QUALITY, keyLabel } from './save/settings.js';

// Point d'entrée : crée le moteur de rendu, le monde, le joueur et la boucle à pas fixe.
class Game {
  constructor() {
    const canvas = document.getElementById('game');
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping; this.renderer.toneMappingExposure = 0.9;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(70, 1, 0.05, 500);
    this.world = buildTestPark(this.scene);
    this.physics = new PhysicsWorld(this.world.colliders, this.world.rails);
    this.score = new ScoreSystem();
    this.hud = this.bindHud();
    this.input = new Input(canvas);
    this.player = new Player(this.scene, this.physics, this.world.spawn, {
      trick: t => { this.score.trick(t); this.flashTrick(); },
      sustain: (n, p) => this.score.sustain(n, p), sustainEnd: () => this.score.sustainEnd(),
      land: ({ sketchy }) => { this.input.rumble(sketchy ? 0.6 : 0.35, 100); if (sketchy) this.notify('Réception limite', '#ffcc33'); },
      bail: reason => { this.score.bail(); this.notify('CHUTE — ' + reason); this.input.rumble(1, 350); },
      grindStart: () => this.input.rumble(0.3, 90),
    });
    this.cam = new FollowCamera(this.camera);
    this.menu = new Menu(this);
    this.started = false; this.paused = true; this.acc = 0; this.simTime = 0; this.last = performance.now();
    addEventListener('resize', () => this.resize()); this.applyGraphics();
    addEventListener('keydown', e => { if (e.code === 'Escape' && this.started && !this.input.capture) this.paused ? (this.menu.screen === 'pause' ? this.resume() : this.menu.show('pause')) : this.pause(); });
    document.addEventListener('pointerlockchange', () => { if (!document.pointerLockElement && this.started && !this.paused) { /* garde la partie active : clic pour recapturer */ } });
    this.menu.show('main');
    addEventListener('gamepadconnected', e => this.notify('Manette connectée : ' + e.gamepad.id.split('(')[0].trim().slice(0, 40), '#3fd0ff'));
    addEventListener('gamepaddisconnected', () => { this.notify('Manette déconnectée'); if (this.started && !this.paused) this.pause(); });
    window.__game = this; // accès pour les tests automatisés
    requestAnimationFrame(t => this.loop(t));
  }
  bindHud() { const q = id => document.getElementById(id); return { root: q('hud'), line: q('line-score'), combo: q('combo'), trick: q('trick'), total: q('total-score'), best: q('best'), vehicle: q('vehicle'), stance: q('stance'), speed: q('speed'), bal: q('balance'), needle: q('balance-needle'), notif: q('notif'), help: q('help') }; }
  start() { this.started = true; this.resume(); }
  resume() { const p = [...(navigator.getGamepads?.() || [])].find(Boolean); if (p) { this.input.padPrev = p.buttons.map(b => b.pressed); this.input.padBlock = new Set(p.buttons.map((b, i) => b.pressed ? i : -1).filter(i => i >= 0)); } this.paused = false; this.menu.hide(); this.hud.root.classList.remove('hidden'); this.last = performance.now(); this.renderer.domElement.requestPointerLock?.(); }
  pause() { this.paused = true; this.menu.show('pause'); }
  applyGraphics() {
    const q = QUALITY[settings.quality];
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, q.pixelRatio) * settings.resolutionScale);
    this.renderer.shadowMap.enabled = settings.shadows;
    const sl = this.world.sunLight; sl.castShadow = settings.shadows; sl.shadow.mapSize.set(q.shadowMap, q.shadowMap); sl.shadow.map?.dispose(); sl.shadow.map = null;
    this.camera.far = settings.viewDist + 50; this.scene.fog.far = settings.viewDist; this.scene.fog.near = settings.viewDist * 0.25; this.camera.updateProjectionMatrix();
    this.world.sky.scale.setScalar(settings.viewDist * 0.9);
    this.scene.traverse(o => { if (o.material) o.material.needsUpdate = true; });
    this.resize();
  }
  resize() { this.renderer.setSize(innerWidth, innerHeight, false); this.camera.aspect = innerWidth / innerHeight; this.camera.updateProjectionMatrix(); }
  notify(txt, color = '#ff5a4f') { const n = this.hud.notif; n.textContent = txt; n.style.color = color; clearTimeout(this.nt); this.nt = setTimeout(() => n.textContent = '', 1600); }
  flashTrick() { this.hud.trick.style.transform = 'scale(1.15)'; setTimeout(() => this.hud.trick.style.transform = '', 120); }
  step(dt, now) {
    const inp = this.input; inp.update(dt);
    if (inp.just('camera')) this.notify('Caméra : ' + this.cam.next(), '#3fd0ff');
    if (inp.just('help')) this.toggleHelp();
    if (inp.padBtn('menu', true)) { this.pause(); inp.menuPrev = inp.padPrev.slice(); }
    if (inp.pad && this.player.mode === 'walk' && inp.padLook) { inp.look.x += inp.padLook.x * 2.5 * dt; inp.look.y += inp.padLook.y * 1.5 * dt; }
    this.player.update(dt, inp, this.cam.yaw, now);
    const b = this.player.board, grounded = this.player.mode !== 'board' || b.state === 'ride';
    const banked = this.score.update(dt, grounded);
    if (banked) this.notify('+' + banked + ' pts', '#35d07f');
    this.cam.update(dt, this.player.focus, this.player.heading, inp, this.physics, this.player.mode === 'board');
    inp.endFrame();
  }
  toggleHelp() {
    const h = this.hud.help; h.classList.toggle('hidden');
    const k = a => keyLabel(settings.bindings[a]);
    h.innerHTML = `<b>Skateboard</b><br>${k('push')} pousser · ${k('left')}/${k('right')} tourner · ${k('brake')} freiner<br>Tricks : flèches ou clic droit + souris<br>↓↑ ollie · ↓↖ kickflip · ↓↗ heelflip · ↓←↑ pop shove-it<br>Mi-course ↓ : manual · Retomber sur un rail : grind<br>${k('interact')} descendre/monter · ${k('reset')} reset · ${k('camera')} caméra`;
  }
  updateHud() {
    const h = this.hud, s = this.score, b = this.player.board;
    h.line.textContent = s.active ? Math.round(s.line) : ''; h.combo.textContent = s.active && s.mult > 1 ? '× ' + s.mult : '';
    h.trick.textContent = s.names.slice(-5).join(' + ');
    h.total.textContent = s.session; h.best.textContent = s.stats.best;
    h.vehicle.textContent = this.player.mode === 'board' ? 'SKATEBOARD' : 'À PIED';
    h.stance.textContent = b.switch ? 'Switch' : 'Regular';
    h.speed.textContent = Math.round(this.player.speed * 3.6);
    const src = this.input.source; if (src !== this.lastSrc) { this.lastSrc = src; document.getElementById('help-hint').textContent = src === 'manette' ? 'Start : menu · Back : aide commandes' : 'Échap : menu · H : aide commandes'; }
    const showBal = this.player.mode === 'board' && (b.state === 'grind' || b.state === 'manual');
    h.bal.classList.toggle('hidden', !showBal); if (showBal) h.needle.style.left = (50 + b.balance * 50) + '%';
  }
  loop(t) {
    requestAnimationFrame(tt => this.loop(tt));
    const frame = Math.min(0.1, (t - this.last) / 1000); this.last = t;
    if (this.menu.open) this.menu.pad(this.input.pollMenu());
    if (!this.paused) {
      this.acc += frame; const DT = 1 / 120; // physique à pas fixe 120 Hz
      while (this.acc >= DT) { this.simTime += DT; this.step(DT, performance.now()); this.acc -= DT; }
      this.updateHud();
    }
    // l'ombre suit le joueur
    const sl = this.world.sunLight, f = this.player.focus; sl.target.position.copy(f); sl.position.copy(f).addScaledVector(this.world.sunDir, 80);
    this.world.sky.position.copy(this.camera.position);
    this.renderer.render(this.scene, this.camera);
  }
}
new Game();

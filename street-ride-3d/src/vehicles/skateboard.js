import * as THREE from 'three';
import { GestureRecognizer, SKATE_TRICKS } from '../core/gesture.js';
import { buildSkateboardModel } from './skateboardModel.js';

// Contrôleur skateboard : physique arcade-simulation + système Flick-It.
// Totalement indépendant de la future trottinette (aucun partage de tricks ni de commandes).
const G = 13.5, UP = new THREE.Vector3(0, 1, 0);
const v1 = new THREE.Vector3(), v2 = new THREE.Vector3(), q1 = new THREE.Quaternion();
const wrap = a => Math.atan2(Math.sin(a), Math.cos(a));

export class Skateboard {
  constructor(scene, physics, events) {
    this.physics = physics; this.ev = events; // events : { trick, land, bail, grindStart }
    this.model = buildSkateboardModel(); this.pivot = new THREE.Group(); this.pivot.add(this.model);
    this.root = new THREE.Group(); this.root.add(this.pivot); scene.add(this.root);
    this.gesture = new GestureRecognizer();
    this.reset(new THREE.Vector3(0, 0, 0), Math.PI);
  }
  reset(pos, yaw) {
    this.pos = pos.clone(); this.vel = new THREE.Vector3(); this.yaw = yaw; this.speed = 0;
    this.normal = UP.clone(); this.state = 'ride'; this.switch = false;
    this.flip = 0; this.flipTarget = 0; this.shove = 0; this.shoveTarget = 0; this.spin = 0; this.airTime = 0;
    this.trick = null; this.pushT = 0; this.balance = 0; this.grind = null; this.manual = null; this.bailT = 0;
    const gr = this.physics.ground(pos, 0.3, 0.3);
    if (!this.safe || (gr && Math.abs(gr.y - pos.y) < 0.05)) this.safe = { pos: pos.clone(), yaw }; this.gesture.reset(); this.lean = 0;
  }
  forward(out = new THREE.Vector3()) { return out.set(Math.sin(this.yaw), 0, Math.cos(this.yaw)); }

  update(dt, input, now) {
    if (this.state === 'bail') { this.bailT += dt; this.updateBail(dt); return; }
    // Échantillons clavier horodatés d'abord, puis la valeur analogique (souris / manette)
    for (const e of input.flickQueue) { const t = this.gesture.update(e.x, e.y, e.t); if (t) this.onGesture(t); }
    input.flickQueue.length = 0;
    const t = this.gesture.update(input.flickAnalog.x, input.flickAnalog.y, now);
    if (t) this.onGesture(t);
    if (this.state === 'ride' || this.state === 'manual') this.updateGround(dt, input);
    else if (this.state === 'air') this.updateAir(dt, input);
    else if (this.state === 'grind') this.updateGrind(dt, input);
    this.applyTransform(dt);
  }

  onGesture(id) {
    const def = SKATE_TRICKS[id];
    if (!def) return;
    const canPop = this.state === 'ride' || this.state === 'manual' || this.state === 'grind';
    if (!canPop) return;
    const base = this.state === 'grind' ? this.grindVelocity() : this.groundVelocity();
    if (this.state === 'manual') this.endManual();
    if (this.state === 'grind') this.endGrind(false);
    this.vel.copy(base).addScaledVector(UP, def.pop);
    this.state = 'air'; this.airTime = 0; this.spin = 0;
    this.flip = 0; this.flipTarget = def.flip * Math.PI * 2; this.shove = 0; this.shoveTarget = def.shove * Math.PI;
    const name = (this.switch && !id.startsWith('nollie') ? 'Switch ' : '') + def.name;
    this.trick = { name, pts: def.pts };
  }
  groundVelocity() {
    const f = this.forward(v1); const n = this.normal;
    return f.addScaledVector(n, -f.dot(n)).normalize().multiplyScalar(this.speed);
  }

  updateGround(dt, input) {
    const f = this.forward(new THREE.Vector3());
    // Poussée / frein
    this.pushT = Math.max(0, this.pushT - dt);
    if (this.state === 'ride') {
      if (input.pressed('push') && this.pushT === 0 && this.speed < 9.5) { this.speed += 2.6; this.pushT = 0.55; this.pushAnim = 0.55; }
      if (input.move.y < -0.5) this.speed = Math.max(0, this.speed - 7 * dt);
    }
    this.pushAnim = Math.max(0, (this.pushAnim || 0) - dt);
    // Virage (plus serré à basse vitesse)
    const turn = input.move.x * (2.6 / (1 + this.speed * 0.09));
    this.yaw -= turn * dt; this.lean = THREE.MathUtils.lerp(this.lean, input.move.x * Math.min(1, this.speed / 5), 1 - Math.exp(-8 * dt));
    // Gravité le long de la pente
    const n = this.normal; const fp = f.clone().addScaledVector(n, -f.dot(n)).normalize();
    const gt = new THREE.Vector3(0, -G, 0).addScaledVector(n, G * n.y);
    this.speed += gt.dot(fp) * dt;
    this.speed *= 1 - (this.state === 'manual' ? 0.25 : 0.12) * dt;
    if (Math.abs(this.speed) < 0.05 && !input.pressed('push')) this.speed = 0;
    // Recul -> fakie/switch
    if (this.speed < -0.3) { this.yaw += Math.PI; this.speed = -this.speed; this.switch = !this.switch; }
    // Manual : stick droit à mi-course (sans dépasser le seuil de flick)
    this.updateManual(dt, input);
    // Murs
    const wallN = this.collideWall(fp); if (wallN) return;
    // Déplacement
    this.pos.addScaledVector(fp, this.speed * dt);
    const g = this.physics.ground(this.pos, 0.5, 3);
    if (g && g.y >= this.pos.y - 0.35 && g.normal.y > 0.35) {
      // Transition trop brusque à vitesse = choc
      this.pos.y = g.y; this.normal.lerp(g.normal, 1 - Math.exp(-25 * dt)).normalize();
      if (this.state === 'ride' && this.speed < 6 && n.y > 0.97) { this.safe.pos.copy(this.pos); this.safe.yaw = this.yaw; }
    } else {
      // Le sol se dérobe : on décolle avec la vitesse actuelle (lancement sur les rampes)
      if (this.state === 'manual') this.endManual();
      this.vel.copy(fp).multiplyScalar(this.speed); this.state = 'air'; this.airTime = 0; this.spin = 0;
      this.flip = this.flipTarget = this.shove = this.shoveTarget = 0; this.trick = null;
    }
  }
  collideWall(dir) {
    if (this.speed < 0.1) return null;
    const o = v2.copy(this.pos).addScaledVector(UP, 0.25);
    const h = this.physics.wall(o, dir, 0.45 + this.speed * 0.02);
    if (!h) return null;
    if (this.speed > 7 && Math.abs(h.normal.dot(dir)) > 0.7) { this.bail('Mur !'); return h.normal; }
    // Rebond / glissement le long du mur
    const f = this.forward(v1); const hn = new THREE.Vector3(h.normal.x, 0, h.normal.z).normalize();
    const slide = f.clone().addScaledVector(hn, -f.dot(hn));
    if (slide.lengthSq() > 0.01) this.yaw = Math.atan2(slide.x, slide.z);
    this.speed *= 0.5; return h.normal;
  }

  updateManual(dt, input) {
    const fy = input.flick.y, mag = Math.hypot(input.flick.x, fy);
    const want = mag > 0.18 && mag < 0.55 && Math.abs(fy) > Math.abs(input.flick.x) ? (fy < 0 ? 'manual' : 'nose') : null;
    if (this.state === 'ride' && want && this.speed > 1.2) {
      this.state = 'manual'; this.manual = { type: want, t: 0 }; this.balance = (Math.random() - 0.5) * 0.2;
      this.ev.trick?.({ name: want === 'manual' ? 'Manual' : 'Nose Manual', pts: 0, sustained: true });
    }
    if (this.state !== 'manual') return;
    const m = this.manual; m.t += dt;
    // Équilibre : dérive naturelle croissante, correction avec avant/arrière (stick gauche Y)
    this.balance += (this.balance * 1.6 + (Math.random() - 0.5) * 0.6) * dt - input.move.y * 1.4 * dt;
    if (!want && mag < 0.12) { this.endManual(); return; }
    if (Math.abs(this.balance) > 1) { this.bail('Manual raté'); return; }
    this.ev.sustain?.(m.type === 'manual' ? 'Manual' : 'Nose Manual', dt * 120);
  }
  endManual() { if (this.state === 'manual') this.state = 'ride'; this.manual = null; this.ev.sustainEnd?.(); }

  updateAir(dt, input) {
    this.airTime += dt;
    this.vel.y -= G * dt;
    // Rotation en l'air (stick gauche)
    const spinRate = 7.5; this.spin += -input.move.x * spinRate * dt; this.yaw += -input.move.x * spinRate * dt;
    // Flips : le plateau termine sa rotation en ~0.42 s
    const fs = Math.PI * 2 / 0.42;
    this.flip = this.flipTarget > 0 ? Math.min(this.flipTarget, this.flip + fs * dt) : Math.max(this.flipTarget, this.flip - fs * dt);
    this.shove = this.shoveTarget > 0 ? Math.min(this.shoveTarget, this.shove + fs * dt) : Math.max(this.shoveTarget, this.shove - fs * dt);
    const prev = this.pos.clone();
    this.pos.addScaledVector(this.vel, dt);
    // Murs en l'air
    const hv = v1.set(this.vel.x, 0, this.vel.z); const hs = hv.length();
    if (hs > 0.1) { const h = this.physics.wall(v2.copy(prev).addScaledVector(UP, 0.3), hv.normalize(), hs * dt + 0.3);
      if (h) { this.pos.x = prev.x; this.pos.z = prev.z; const hn = new THREE.Vector3(h.normal.x, 0, h.normal.z).normalize(); const d = this.vel.dot(hn); if (d < 0) this.vel.addScaledVector(hn, -d * 1.3); } }
    // Accroche d'un rail (en descente, planche près de la hauteur du rail)
    if (this.vel.y < 0.5 && this.airTime > 0.12) {
      const r = this.physics.nearestRail(this.pos, 0.45);
      if (r && r.dy > -0.25 && r.dy < 0.35 && !(r.rail === this.lastRail && this.airTime < 0.5)) { this.startGrind(r, input); return; }
    }
    const g = this.physics.ground(this.pos, Math.max(0.3, -this.vel.y * dt + 0.3), 50);
    if (g && this.vel.y <= 0 && this.pos.y <= g.y + 0.02) { this.pos.y = g.y; this.land(g); }
    if (this.pos.y < -20) this.bail('Hors limites');
  }

  land(g) {
    // Vérifie : flips terminés, rotation proche d'un multiple de 180°, planche alignée avec la vitesse
    const flipDone = Math.abs(this.flip - this.flipTarget) < 0.05 && Math.abs(this.shove - this.shoveTarget) < 0.05;
    const halfTurns = Math.round(this.spin / Math.PI); const resid = Math.abs(this.spin - halfTurns * Math.PI);
    const hv = new THREE.Vector3(this.vel.x, 0, this.vel.z); const hs = hv.length();
    const boardYaw = this.yaw;
    let align = 0; if (hs > 1.5) { const vy = Math.atan2(hv.x, hv.z); align = Math.abs(wrap(boardYaw - vy)); }
    const fakie = align > Math.PI / 2; if (fakie) align = Math.PI - align;
    const hard = this.vel.y < -14;
    if (!flipDone) return this.bail('Flip pas terminé');
    if (resid > 0.65) return this.bail('Mauvaise réception');
    if (align > 0.8 && hs > 1.5) return this.bail('Planche de travers');
    if (hard) return this.bail('Réception trop violente');
    // Réception propre
    this.yaw = hs > 1.5 ? Math.atan2(hv.x, hv.z)   : boardYaw;
    if (fakie) { this.switch = !this.switch; }
    this.speed = hs * (resid > 0.35 || align > 0.4 ? 0.7 : 0.97); this.normal.copy(g.normal);
    if (this.trick || Math.abs(halfTurns) > 0) {
      const deg = Math.abs(halfTurns) * 180; const dirName = halfTurns > 0 ? 'FS ' : 'BS ';
      const name = (deg ? dirName + deg + ' ' : '') + (this.trick?.name ?? 'Air');
      const pts = (this.trick?.pts ?? 50) + deg * 1.5 + Math.round(this.airTime * 60);
      this.ev.trick?.({ name, pts: Math.round(pts) });
    }
    this.ev.land?.({ sketchy: resid > 0.35 || align > 0.4 });
    this.state = 'ride'; this.trick = null; this.flip = this.flipTarget = this.shove = this.shoveTarget = 0; this.spin = 0;
  }

  startGrind(r, input) {
    const dir = r.rail.b.clone().sub(r.rail.a).normalize();
    const hv = new THREE.Vector3(this.vel.x, 0, this.vel.z);
    let along = hv.dot(dir); const sign = along >= 0 ? 1 : -1;
    if (Math.abs(along) < 0.8) along = sign * 0.8;
    // Type de grind selon l'angle planche/rail et le stick droit
    const railYaw = Math.atan2(dir.x * sign, dir.z * sign); const ang = Math.abs(wrap(this.yaw - railYaw));
    const a = Math.min(ang, Math.PI - ang);
    let type = a < 0.45 ? '50-50' : a > 1.0 ? (r.rail.kind === 'rail' ? 'Boardslide' : 'Noseslide') : 'Crooked Grind';
    if (a < 0.45 && input.flick.y > 0.3) type = 'Nosegrind';
    if (a < 0.45 && input.flick.y < -0.3) type = '5-0 Grind';
    const trickBefore = this.trick?.name;
    if (this.trick && Math.abs(this.flip - this.flipTarget) > 0.05) return this.bail('Flip pas terminé');
    if (trickBefore) this.ev.trick?.({ name: trickBefore, pts: this.trick.pts });
    this.grind = { rail: r.rail, t: r.t, dir, sign, speed: Math.abs(along), type, slide: a > 1.0, time: 0, yawOffset: wrap(this.yaw - railYaw) };
    this.state = 'grind'; this.balance = (Math.random() - 0.5) * 0.3; this.trick = null;
    this.flip = this.flipTarget = this.shove = this.shoveTarget = 0; this.spin = 0;
    this.ev.trick?.({ name: type, pts: 0, sustained: true }); this.ev.grindStart?.();
  }
  grindVelocity() { const g = this.grind; return g.dir.clone().multiplyScalar(g.sign * g.speed); }
  updateGrind(dt, input) {
    const g = this.grind; g.time += dt;
    g.speed -= (g.slide ? 1.6 : 0.9) * dt; // friction
    const r = g.rail; const L = r.a.distanceTo(r.b);
    g.speed += -G * g.dir.y * g.sign * dt; // pente du rail
    g.t += (g.sign * g.speed * dt) / L;
    this.balance += (this.balance * 0.9 + (Math.random() - 0.5) * 0.5) * dt + input.move.x * 1.5 * dt;
    if (Math.abs(this.balance) > 1) return this.bail('Déséquilibre');
    this.pos.copy(r.a).lerp(r.b, THREE.MathUtils.clamp(g.t, 0, 1));
    this.yaw = Math.atan2(g.dir.x * g.sign, g.dir.z * g.sign) + g.yawOffset;
    this.ev.sustain?.(g.type, dt * (g.slide ? 220 : 180));
    if (g.t > 1 || g.t < 0 || g.speed < 0.4) this.endGrind(true);
  }
  endGrind(popOff) {
    const vel = this.grindVelocity(); const g = this.grind;
    this.vel.copy(vel).addScaledVector(UP, popOff ? 1.2 : 0);
    this.yaw = Math.atan2(vel.x, vel.z) + (g && g.slide ? 0 : g?.yawOffset ?? 0);
    if (g && g.slide) this.spin = 0; // l'atterrissage aligne la planche
    this.pos.addScaledVector(UP, 0.05);
    this.lastRail = g?.rail; this.state = 'air'; this.airTime = 0; this.grind = null; this.ev.sustainEnd?.();
  }

  bail(reason) {
    if (this.state === 'bail') return;
    const v = this.state === 'grind' ? this.grindVelocity() : this.state === 'air' ? this.vel.clone() : this.groundVelocity();
    this.state = 'bail'; this.bailT = 0; this.grind = null; this.manual = null; this.ev.sustainEnd?.();
    this.bailVel = v.clone().add(new THREE.Vector3(0, 2, 0));
    this.bailSpin = new THREE.Vector3(Math.random() * 8 - 4, Math.random() * 6 - 3, Math.random() * 8 - 4);
    this.ev.bail?.(reason);
  }
  updateBail(dt) {
    this.bailVel.y -= G * dt; this.pos.addScaledVector(this.bailVel, dt);
    const g = this.physics.ground(this.pos, 0.5, 50);
    if (g && this.pos.y < g.y) { this.pos.y = g.y; this.bailVel.y *= -0.3; this.bailVel.x *= 0.7; this.bailVel.z *= 0.7; this.bailSpin.multiplyScalar(0.6); }
    this.pivot.rotation.x += this.bailSpin.x * dt; this.pivot.rotation.y += this.bailSpin.y * dt; this.pivot.rotation.z += this.bailSpin.z * dt;
    this.root.position.copy(this.pos);
  }
  respawn() { this.reset(this.safe.pos, this.safe.yaw); this.pivot.rotation.set(0, 0, 0); this.ev.respawn?.(); }

  applyTransform(dt) {
    this.root.position.copy(this.pos);
    const n = this.state === 'air' || this.state === 'grind' ? UP : this.normal;
    q1.setFromUnitVectors(UP, n); this.root.quaternion.copy(q1).multiply(new THREE.Quaternion().setFromAxisAngle(UP, this.yaw));
    // Pivot : flip (axe long Z), shove (axe Y), manual (tangage X)
    const pitch = this.state === 'manual' ? (this.manual.type === 'manual' ? -0.28 : 0.28) : this.state === 'grind' && this.grind.type === 'Nosegrind' ? 0.25 : this.state === 'grind' && this.grind.type === '5-0 Grind' ? -0.25 : 0;
    this.pivot.rotation.set(pitch, this.shove, this.flip, 'YXZ');
    this.pivot.position.y = this.state === 'air' && this.flipTarget !== 0 ? 0.25 * Math.sin(Math.min(1, Math.abs(this.flip / this.flipTarget)) * Math.PI) : 0;
    this.model.rotation.z = -this.lean * 0.12;
    this.model.children.forEach(c => { if (c.userData.wheel) c.rotation.x += this.speed * dt / 0.027; });
  }
}

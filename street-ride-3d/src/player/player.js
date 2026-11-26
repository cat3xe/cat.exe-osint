import * as THREE from 'three';
import { Character, Poses } from './character.js';
import { Skateboard } from '../vehicles/skateboard.js';

// Joueur : bascule entre "à pied" et "sur un véhicule". Le véhicule actif possède sa propre logique.
const UP = new THREE.Vector3(0, 1, 0);
export class Player {
  constructor(scene, physics, spawn, events) {
    this.scene = scene; this.physics = physics; this.ev = events;
    this.char = new Character(); scene.add(this.char.root);
    this.board = new Skateboard(scene, physics, events);
    this.spawn = spawn.clone(); this.mode = 'board'; this.vehicle = 'skateboard';
    this.walk = { pos: spawn.clone(), vel: new THREE.Vector3(), yaw: Math.PI, onGround: true };
    this.t = 0; this.respawn(true);
  }
  respawn(full) {
    if (full) this.board.reset(this.spawn, Math.PI); else this.board.respawn();
    this.mode = 'board'; this.board.root.visible = true; this.char.root.rotation.set(0, 0, 0);
  }
  toggleBoard() {
    const b = this.board;
    if (this.mode === 'board') {
      if (b.state !== 'ride' || b.speed > 3) return;
      this.mode = 'walk'; this.walk.pos.copy(b.pos).add(new THREE.Vector3(Math.cos(b.yaw) * 0.4, 0, -Math.sin(b.yaw) * 0.4));
      this.walk.yaw = b.yaw; this.walk.vel.set(0, 0, 0);
    } else {
      this.mode = 'board'; b.reset(this.walk.pos, this.walk.yaw);
    }
  }
  update(dt, input, camYaw, now) {
    this.t += dt;
    if (input.just('interact')) this.toggleBoard();
    if (input.just('reset')) this.respawn(false);
    if (this.mode === 'board') this.updateBoard(dt, input, now); else this.updateWalk(dt, input, camYaw);
  }
  updateBoard(dt, input, now) {
    const b = this.board; b.update(dt, input, now);
    const c = this.char;
    if (b.state === 'bail') {
      // Le personnage est éjecté et roule au sol (ragdoll simplifié)
      if (!this.bailBody) this.bailBody = { pos: b.pos.clone(), vel: b.bailVel.clone().multiplyScalar(1.1), rot: 0 };
      const bb = this.bailBody; bb.vel.y -= 13.5 * dt; bb.pos.addScaledVector(bb.vel, dt); bb.rot += dt * 6;
      const g = this.physics.ground(bb.pos, 0.5, 50);
      if (g && bb.pos.y < g.y) { bb.pos.y = g.y; bb.vel.multiplyScalar(0.6); bb.vel.y = Math.abs(bb.vel.y) * 0.2; }
      c.root.position.copy(bb.pos); c.root.rotation.x = Math.min(Math.PI / 2, bb.rot * 0.4);
      c.apply(Poses.bail(), dt, 8);
      if (b.bailT > 2.2) { this.bailBody = null; c.root.rotation.x = 0; this.respawn(false); }
      return;
    }
    this.bailBody = null;
    c.root.position.copy(b.root.position).addScaledVector(UP, 0.1 + b.pivot.position.y * 0.6);
    c.root.quaternion.copy(b.root.quaternion).multiply(new THREE.Quaternion().setFromAxisAngle(UP, b.switch ? -Math.PI / 2 : Math.PI / 2));
    let pose;
    if (b.state === 'air') pose = b.airTime < 0.5 || b.flipTarget ? Poses.air(1) : Poses.air(0.5);
    else if (b.state === 'grind') pose = Poses.grind(b.balance);
    else if (b.state === 'manual') pose = Poses.manual(b.manual?.type === 'nose');
    else if (b.pushAnim > 0) pose = Poses.push(b.pushAnim);
    else if (Math.hypot(input.flick.x, input.flick.y) > 0.5) pose = Poses.crouch();
    else pose = Poses.ride(b.lean);
    c.apply(pose, dt, b.state === 'air' ? 16 : 10);
  }
  updateWalk(dt, input, camYaw) {
    const w = this.walk, c = this.char, b = this.board;
    const run = input.pressed('run'), sp = run ? 6 : 2.4;
    const mv = new THREE.Vector3(input.move.x, 0, -input.move.y);
    if (mv.lengthSq() > 1) mv.normalize();
    mv.applyAxisAngle(UP, camYaw);
    const target = mv.multiplyScalar(sp); const k = 1 - Math.exp(-10 * dt);
    w.vel.x += (target.x - w.vel.x) * k; w.vel.z += (target.z - w.vel.z) * k;
    if (target.lengthSq() > 0.01) w.yaw = Math.atan2(target.x, target.z);
    if (w.onGround && input.just('push')) { w.vel.y = 5; w.onGround = false; }
    w.vel.y -= 13.5 * dt;
    // Murs
    const hv = new THREE.Vector3(w.vel.x, 0, w.vel.z);
    if (hv.lengthSq() > 0.001) { const h = this.physics.wall(w.pos.clone().addScaledVector(UP, 0.5), hv.clone().normalize(), hv.length() * dt + 0.3); if (h) { const hn = new THREE.Vector3(h.normal.x, 0, h.normal.z).normalize(); const d = w.vel.dot(hn); if (d < 0) w.vel.addScaledVector(hn, -d); } }
    w.pos.addScaledVector(w.vel, dt);
    const g = this.physics.ground(w.pos, 0.6, 50);
    if (g && w.pos.y <= g.y + 0.05 && w.vel.y <= 0) { w.pos.y = g.y; w.vel.y = 0; w.onGround = true; } else w.onGround = false;
    if (w.pos.y < -20) { w.pos.copy(this.spawn); w.vel.set(0, 0, 0); }
    c.root.position.copy(w.pos); c.root.quaternion.setFromAxisAngle(UP, w.yaw);
    const hs = Math.hypot(w.vel.x, w.vel.z);
    c.apply(!w.onGround ? Poses.jump() : hs > 0.4 ? Poses.walk(this.t, run) : Poses.idle(this.t), dt, 10);
    // Skate porté sous le bras
    const hand = c.j.elbowR; hand.updateWorldMatrix(true, false);
    const hp = new THREE.Vector3(0, -0.25, 0).applyMatrix4(hand.matrixWorld);
    b.root.position.copy(hp); b.root.quaternion.copy(c.root.quaternion).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, Math.PI / 2)));
    b.pivot.rotation.set(0, 0, 0);
  }
  get focus() { return this.mode === 'board' ? (this.bailBody ? this.bailBody.pos : this.board.pos) : this.walk.pos; }
  get heading() { return this.mode === 'board' ? this.board.yaw : this.walk.yaw; }
  get speed() { return this.mode === 'board' ? (this.board.state === 'air' ? Math.hypot(this.board.vel.x, this.board.vel.z) : this.board.speed) : Math.hypot(this.walk.vel.x, this.walk.vel.z); }
}

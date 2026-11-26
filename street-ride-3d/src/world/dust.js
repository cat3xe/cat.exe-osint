import * as THREE from 'three';
// Nuages de poussière légers (pool de sprites) déclenchés à la réception et au grind.
export class DustFX {
  constructor(scene) {
    const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
    const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32); grd.addColorStop(0, 'rgba(230,220,200,0.9)'); grd.addColorStop(1, 'rgba(230,220,200,0)');
    g.fillStyle = grd; g.fillRect(0, 0, 64, 64);
    const tex = new THREE.CanvasTexture(c); this.mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, opacity: 0.6 });
    this.pool = []; this.live = [];
    for (let i = 0; i < 60; i++) { const s = new THREE.Sprite(this.mat.clone()); s.visible = false; scene.add(s); this.pool.push(s); }
  }
  emit(pos, n = 6, strength = 1) {
    for (let i = 0; i < n; i++) {
      const s = this.pool.pop(); if (!s) break;
      s.visible = true; s.position.copy(pos).add(new THREE.Vector3((Math.random() - 0.5) * 0.6, 0.05, (Math.random() - 0.5) * 0.6));
      s.userData = { life: 0, max: 0.6 + Math.random() * 0.5, vel: new THREE.Vector3((Math.random() - 0.5) * 1.5, 0.4 + Math.random() * 0.8, (Math.random() - 0.5) * 1.5).multiplyScalar(strength) };
      this.live.push(s);
    }
  }
  update(dt) {
    for (let i = this.live.length - 1; i >= 0; i--) {
      const s = this.live[i], u = s.userData; u.life += dt;
      s.position.addScaledVector(u.vel, dt); u.vel.multiplyScalar(1 - 2 * dt);
      const k = u.life / u.max; s.scale.setScalar(0.3 + k * 1.2); s.material.opacity = 0.6 * (1 - k);
      if (k >= 1) { s.visible = false; this.live.splice(i, 1); this.pool.push(s); }
    }
  }
}

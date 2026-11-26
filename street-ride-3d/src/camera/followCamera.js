import * as THREE from 'three';
// Caméras : "suiveuse" (style vidéo de skate, derrière le rider), "basse" (fisheye au ras du sol), "libre orbitale".
export class FollowCamera {
  constructor(camera) { this.cam = camera; this.modes = ['suiveuse', 'basse', 'orbitale']; this.mode = 0; this.yawOff = 0; this.pitch = 0.25; this.yaw = 0; this.pos = new THREE.Vector3(0, 3, 10); this.look = new THREE.Vector3(); this.dist = 4.2; }
  next() { this.mode = (this.mode + 1) % this.modes.length; return this.modes[this.mode]; }
  update(dt, target, heading, input, physics, follow = true) {
    if (!follow) { this.yaw -= input.look.x; heading = this.yaw - Math.PI - this.yawOff; }
    else this.yawOff -= input.look.x; this.pitch = THREE.MathUtils.clamp(this.pitch + input.look.y, -0.2, 1.2);
    const m = this.modes[this.mode];
    // retour progressif derrière le joueur
    if (m !== 'orbitale' && input.look.x === 0) this.yawOff *= Math.exp(-1.2 * dt);
    const desiredYaw = (m === 'orbitale' ? 0 : heading + Math.PI) + this.yawOff;
    this.yaw += Math.atan2(Math.sin(desiredYaw - this.yaw), Math.cos(desiredYaw - this.yaw)) * (1 - Math.exp(-5 * dt));
    const dist = m === 'basse' ? 2.6 : this.dist, h = m === 'basse' ? 0.35 : 1.0;
    const pitch = m === 'basse' ? 0.05 : this.pitch;
    const off = new THREE.Vector3(Math.sin(this.yaw) * Math.cos(pitch), Math.sin(pitch), Math.cos(this.yaw) * Math.cos(pitch)).multiplyScalar(dist);
    const look = target.clone().add(new THREE.Vector3(0, h, 0));
    const want = look.clone().add(off);
    // Évite que la caméra passe dans le sol
    const g = physics.ground(want, 2, 10); if (g && want.y < g.y + 0.25) want.y = g.y + 0.25;
    this.pos.lerp(want, 1 - Math.exp(-9 * dt)); this.look.lerp(look, 1 - Math.exp(-14 * dt));
    this.cam.position.copy(this.pos); this.cam.lookAt(this.look);
    this.cam.fov = THREE.MathUtils.lerp(this.cam.fov, m === 'basse' ? 95 : 70, 1 - Math.exp(-4 * dt)); this.cam.updateProjectionMatrix();
  }
}

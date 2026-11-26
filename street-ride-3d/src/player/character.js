import * as THREE from 'three';
// Personnage 3D procédural à squelette hiérarchique (joints = Groups). Les vêtements sont des meshes
// attachés aux os : ils suivent donc toutes les animations (base de l'éditeur de personnage Phase 5).
// Plus tard : remplacement par un modèle glTF skinné (SkinnedMesh) avec les mêmes noms d'os.
const lerpA = (a, b, k) => a + (b - a) * k;

export class Character {
  constructor(look = {}) {
    this.look = { skin: 0xc8946a, shirt: 0x2f6fde, pants: 0x3a3a42, shoes: 0xeeeeee, hair: 0x2a1a10, cap: 0xff5a4f, ...look };
    this.root = new THREE.Group(); this.j = {}; this.pose = {}; this.build();
    this.root.traverse(o => { if (o.isMesh) o.castShadow = true; });
  }
  mat(c, r = 0.8) { return new THREE.MeshStandardMaterial({ color: c, roughness: r }); }
  limb(parent, name, len, rad, mat, y = 0) {
    const j = new THREE.Group(); j.position.y = y; parent.add(j); this.j[name] = j;
    const m = new THREE.Mesh(new THREE.CapsuleGeometry(rad, len - rad * 2, 4, 10), mat); m.position.y = -len / 2; j.add(m);
    return j;
  }
  build() {
    const L = this.look, skin = this.mat(L.skin, 0.6), shirt = this.mat(L.shirt), pants = this.mat(L.pants), shoes = this.mat(L.shoes, 0.5);
    const hips = new THREE.Group(); hips.position.y = 0.95; this.root.add(hips); this.j.hips = hips;
    const pelvis = new THREE.Mesh(new THREE.CapsuleGeometry(0.13, 0.12, 4, 10), pants); pelvis.rotation.z = Math.PI / 2; hips.add(pelvis);
    const spine = new THREE.Group(); spine.position.y = 0.05; hips.add(spine); this.j.spine = spine;
    const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.3, 4, 12), shirt); torso.position.y = 0.25; torso.scale.z = 0.7; spine.add(torso);
    const neck = new THREE.Group(); neck.position.y = 0.52; spine.add(neck); this.j.neck = neck;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.11, 16, 12), skin); head.position.y = 0.12; head.scale.set(0.9, 1.05, 1); neck.add(head);
    const hair = new THREE.Mesh(new THREE.SphereGeometry(0.115, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), this.mat(L.hair, 1)); hair.position.y = 0.14; neck.add(hair);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.118, 0.118, 0.06, 16), this.mat(L.cap)); cap.position.y = 0.2; neck.add(cap);
    const visor = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.012, 0.1), this.mat(L.cap)); visor.position.set(0, 0.18, 0.13); neck.add(visor);
    for (const s of [-1, 1]) {
      const side = s < 0 ? 'L' : 'R';
      const sh = this.limb(spine, 'shoulder' + side, 0.3, 0.05, shirt, 0.44); sh.position.x = 0.21 * s;
      const el = this.limb(sh, 'elbow' + side, 0.28, 0.042, skin, -0.29);
      const hand = new THREE.Mesh(new THREE.SphereGeometry(0.045, 8, 8), skin); hand.position.y = -0.3; el.add(hand);
      const hip = this.limb(hips, 'hip' + side, 0.46, 0.075, pants, -0.02); hip.position.x = 0.1 * s;
      const knee = this.limb(hip, 'knee' + side, 0.44, 0.06, pants, -0.45);
      const ankle = new THREE.Group(); ankle.position.y = -0.44; knee.add(ankle); this.j['ankle' + side] = ankle;
      const shoe = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.07, 0.26), shoes); shoe.position.set(0, -0.02, 0.05); ankle.add(shoe);
    }
  }
  // Pose cible : { joint: [rx, ry, rz], hipsY } ; mélange exponentiel vers la cible
  apply(target, dt, speed = 12) {
    const k = 1 - Math.exp(-speed * dt);
    for (const name in this.j) {
      const r = target[name] || [0, 0, 0], j = this.j[name];
      j.rotation.x = lerpA(j.rotation.x, r[0], k); j.rotation.y = lerpA(j.rotation.y, r[1], k); j.rotation.z = lerpA(j.rotation.z, r[2], k);
    }
    this.j.hips.position.y = lerpA(this.j.hips.position.y, 0.95 + (target.hipsY || 0), k);
  }
}

// Bibliothèque de poses (corps tourné de 90° par rapport à la planche : pieds sur l'axe du skate)
export const Poses = {
  ride: (lean = 0) => ({ hipsY: -0.08, spine: [0.15, 0, lean * 0.3], neck: [-0.1, -1.2, 0], hipL: [-0.25, 0, -0.32], hipR: [-0.25, 0, 0.32], kneeL: [0.45, 0, 0], kneeR: [0.45, 0, 0],
    shoulderL: [0.1, 0, -0.35], shoulderR: [0.1, 0, 0.35], elbowL: [-0.3, 0, 0], elbowR: [-0.3, 0, 0], ankleL: [-0.2, 0.3, 0], ankleR: [-0.2, -0.3, 0] }),
  crouch: () => ({ hipsY: -0.3, spine: [0.45, 0, 0], neck: [-0.3, -1.2, 0], hipL: [-0.9, 0, -0.35], hipR: [-0.9, 0, 0.35], kneeL: [1.5, 0, 0], kneeR: [1.5, 0, 0],
    shoulderL: [0.4, 0, -0.6], shoulderR: [0.4, 0, 0.6], elbowL: [-0.5, 0, 0], elbowR: [-0.5, 0, 0], ankleL: [-0.6, 0.3, 0], ankleR: [-0.6, -0.3, 0] }),
  air: (tuck = 1) => ({ hipsY: -0.22 * tuck, spine: [0.3, 0, 0], neck: [-0.2, -1.2, 0], hipL: [-0.9 * tuck, 0, -0.3], hipR: [-0.9 * tuck, 0, 0.3], kneeL: [1.5 * tuck, 0, 0], kneeR: [1.5 * tuck, 0, 0],
    shoulderL: [0, 0, -1.1], shoulderR: [0, 0, 1.1], elbowL: [-0.4, 0, 0], elbowR: [-0.4, 0, 0], ankleL: [-0.5, 0.3, 0], ankleR: [-0.5, -0.3, 0] }),
  manual: (nose) => ({ hipsY: -0.1, spine: [0.1, 0, nose ? 0.25 : -0.25], neck: [0, -1.2, 0], hipL: [-0.3, 0, -0.32], hipR: [-0.3, 0, 0.32], kneeL: [0.5, 0, 0], kneeR: [0.5, 0, 0],
    shoulderL: [0, 0, -1.3], shoulderR: [0, 0, 1.3], elbowL: [0, 0, 0], elbowR: [0, 0, 0], ankleL: [-0.2, 0.3, 0], ankleR: [-0.2, -0.3, 0] }),
  grind: (bal = 0) => ({ hipsY: -0.15, spine: [0.25, 0, bal * 0.5], neck: [-0.15, -1.2, 0], hipL: [-0.5, 0, -0.32], hipR: [-0.5, 0, 0.32], kneeL: [0.8, 0, 0], kneeR: [0.8, 0, 0],
    shoulderL: [0, 0, -1.2 - bal * 0.4], shoulderR: [0, 0, 1.2 - bal * 0.4], elbowL: [-0.2, 0, 0], elbowR: [-0.2, 0, 0], ankleL: [-0.3, 0.3, 0], ankleR: [-0.3, -0.3, 0] }),
  push: (t) => ({ ...Poses.ride(), hipsY: -0.12, spine: [0.3, 0, 0], hipL: [-0.2, 0, -0.05], kneeL: [0.6, 0, 0], ankleL: [-0.3, 0, 0], neck: [-0.1, -0.2, 0],
    hipR: [0.6 * Math.sin(t * 11) + 0.1, 0, 0.1], kneeR: [0.5 + 0.4 * Math.max(0, Math.cos(t * 11)), 0, 0], ankleR: [0, 0, 0] }),
  walk: (t, run) => { const a = run ? 0.9 : 0.55, f = run ? 11 : 7, s = Math.sin(t * f);
    return { hipsY: run ? -0.05 : 0, spine: [run ? 0.25 : 0.05, 0, 0], hipL: [s * a, 0, 0], hipR: [-s * a, 0, 0], kneeL: [Math.max(0, -Math.cos(t * f)) * a * 1.4, 0, 0], kneeR: [Math.max(0, Math.cos(t * f)) * a * 1.4, 0, 0],
      shoulderL: [-s * a * 0.8, 0, -0.1], shoulderR: [s * a * 0.8, 0, 0.1], elbowL: [-0.4 - (run ? 0.8 : 0), 0, 0], elbowR: [-0.4 - (run ? 0.8 : 0), 0, 0] }; },
  idle: (t) => ({ spine: [0.02 * Math.sin(t * 2), 0, 0], shoulderL: [0, 0, -0.08], shoulderR: [0, 0, 0.08], elbowL: [-0.15, 0, 0], elbowR: [-0.15, 0, 0] }),
  jump: () => ({ hipsY: -0.05, hipL: [-0.8, 0, 0], kneeL: [1.2, 0, 0], hipR: [-0.3, 0, 0], kneeR: [0.6, 0, 0], shoulderL: [-2.4, 0, -0.3], shoulderR: [-2.4, 0, 0.3] }),
  bail: () => ({ hipsY: -0.4, spine: [0.9, 0.3, 0.4], hipL: [-1.4, 0, -0.5], hipR: [-0.6, 0, 0.6], kneeL: [1.8, 0, 0], kneeR: [0.8, 0, 0], shoulderL: [-2, 0, -0.8], shoulderR: [-1, 0, 1.2], elbowL: [-1, 0, 0], elbowR: [-0.5, 0, 0] }),
};

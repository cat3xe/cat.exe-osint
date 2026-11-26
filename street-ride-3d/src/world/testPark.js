import * as THREE from 'three';
import { makeGraffiti } from './textures.js';
import { pbr, worldUV } from './materials.js';
import { setupLighting } from './lighting.js';

// Skatepark de test (Phase 1). Expose :
//  colliders : meshes statiques utilisés pour le sol et les murs
//  rails     : segments grindables { a, b, kind: 'rail' | 'ledge' }
//  spawn     : point de départ
export function buildTestPark(scene, renderer) {
  const colliders = [], rails = [];
  const M = {
    concrete: pbr('ledge', { size: 2.5 }),
    ground: pbr('ground', { size: 4 }),
    asphalt: pbr('road', { size: 5 }),
    wood: pbr('wood', { size: 2.4, color: 0xd8c2a0 }),
    metal: new THREE.MeshStandardMaterial({ color: 0xc9ccd2, metalness: 1, roughness: 0.22 }),
    paintedMetal: new THREE.MeshStandardMaterial({ color: 0xd8382e, metalness: 0.5, roughness: 0.35 }),
    brick: pbr('brick', { size: 3 }),
    graffiti: new THREE.MeshStandardMaterial({ map: makeGraffiti(), roughness: 0.8 }),
    grass: new THREE.MeshStandardMaterial({ color: 0x4a6e35, roughness: 1 }),
    facade: pbr('facade', { size: 4 }),
    painted: pbr('ledge', { size: 4, color: 0xd8d2c8 }),
  };
  const add = (mesh, collide = true) => { mesh.castShadow = mesh.receiveShadow = true; scene.add(mesh); if (collide) colliders.push(mesh); return mesh; };
  const box = (w, h, d, x, y, z, mat, ry = 0) => { const m = add(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)); m.position.set(x, y + h / 2, z); m.rotation.y = ry; return m; };

  // Ciel HDR, soleil, brouillard
  const L = setupLighting(scene, renderer);

  // Sol : esplanade béton + route + herbe
  const ground = add(new THREE.Mesh(new THREE.PlaneGeometry(240, 240), M.ground)); ground.rotation.x = -Math.PI / 2;
  const road = add(new THREE.Mesh(new THREE.PlaneGeometry(16, 240), M.asphalt), false); road.rotation.x = -Math.PI / 2; road.position.set(-70, 0.01, 0);
  const grass = add(new THREE.Mesh(new THREE.PlaneGeometry(400, 400), M.grass), false); grass.rotation.x = -Math.PI / 2; grass.position.y = -0.02;

  // Rampe extrudée à partir d'un profil 2D (x = longueur, y = hauteur), largeur w
  function ramp(profile, w, x, z, ry, mat) {
    const sh = new THREE.Shape(profile.map(([a, b]) => new THREE.Vector2(a, b)));
    const g = new THREE.ExtrudeGeometry(sh, { depth: w, bevelEnabled: false }); g.translate(0, 0, -w / 2);
    const m = add(new THREE.Mesh(g, mat)); m.position.set(x, 0, z); m.rotation.y = ry; return m;
  }
  const kicker = (len, h, w, x, z, ry) => ramp([[0, 0], [len, h], [len + 0.4, h], [len + 0.4, 0]], w, x, z, ry, M.wood);
  function quarter(r, w, x, z, ry, deck = 1.5) {
    const pts = [[0, 0]]; const n = 12;
    for (let i = 1; i <= n; i++) { const a = (i / n) * THREE.MathUtils.degToRad(62); pts.push([Math.sin(a) * r, r - Math.cos(a) * r]); }
    const top = pts[pts.length - 1]; pts.push([top[0] + deck, top[1]], [top[0] + deck, 0]);
    const m = ramp(pts, w, x, z, ry, M.concrete);
    // coping = rail grindable en haut
    m.updateMatrixWorld(true);
    const p1 = new THREE.Vector3(top[0], top[1], -w / 2).applyMatrix4(m.matrixWorld);
    const p2 = new THREE.Vector3(top[0], top[1], w / 2).applyMatrix4(m.matrixWorld);
    rails.push({ a: p1, b: p2, kind: 'coping' });
    const cop = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, w, 8), M.metal); cop.position.copy(p1).add(p2).multiplyScalar(0.5);
    cop.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), p2.clone().sub(p1).normalize()); add(cop, false);
    return m;
  }
  function rail(a, b, color = M.metal) {
    const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), len = A.distanceTo(B);
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, len, 10), color);
    bar.position.copy(A).add(B).multiplyScalar(0.5); bar.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize()); add(bar, false);
    for (const p of [A.clone().lerp(B, 0.08), A.clone().lerp(B, 0.92)]) { const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, p.y, 8), M.metal); leg.position.set(p.x, p.y / 2, p.z); add(leg, false); }
    rails.push({ a: A, b: B, kind: 'rail' });
  }
  function ledge(w, h, d, x, z, ry = 0, mat = M.concrete) {
    const m = box(w, h, d, x, 0, z, mat, ry);
    // deux arêtes grindables (longues)
    const c = Math.cos(ry), s = Math.sin(ry);
    for (const side of [-1, 1]) {
      const ox = side * d / 2 * s, oz = side * d / 2 * c;
      rails.push({ a: new THREE.Vector3(x - w / 2 * c + ox, h, z + w / 2 * s + oz), b: new THREE.Vector3(x + w / 2 * c + ox, h, z - w / 2 * s + oz), kind: 'ledge' });
    }
    return m;
  }

  // --- Modules ---
  kicker(1.6, 0.55, 2, 0, -12, Math.PI / 2);   // petit kicker face au spawn
  kicker(2.4, 1.0, 3, 12, -18, Math.PI / 2);
  // Funbox : deux plans inclinés + plateau + ledges
  ramp([[0, 0], [2.5, 0.8], [6.5, 0.8], [9, 0], ], 4, -14, -20, Math.PI / 2, M.concrete);
  rails.push({ a: new THREE.Vector3(-16, 0.8, -22.5), b: new THREE.Vector3(-16, 0.8, -26.5), kind: 'ledge' });
  rails.push({ a: new THREE.Vector3(-12, 0.8, -22.5), b: new THREE.Vector3(-12, 0.8, -26.5), kind: 'ledge' });
  // Rails
  rail([4, 0.45, -4], [4, 0.45, -16]);
  rail([-5, 0.35, -2], [-5, 0.35, -12], M.paintedMetal);
  // Ledges et manual pad
  ledge(8, 0.45, 0.8, 9, -6, Math.PI / 2);
  ledge(6, 0.5, 0.8, -9, -6, Math.PI / 2, M.graffiti);
  box(4, 0.25, 2.4, 0, 0, -26, M.concrete); // manual pad
  // Escalier + rampe d'escalier (handrail)
  const stairX = 22, stairZ = -32;
  box(10, 1.6, 6, stairX, 0, stairZ - 6, M.concrete); // plateforme haute
  for (let i = 0; i < 4; i++) box(10, 1.6 - (i + 1) * 0.32, 0.6, stairX, 0, stairZ - 2.7 + i * 0.6 + 0.3, M.concrete);
  ramp([[0, 0], [5, 1.6], [5.5, 1.6], [5.5, 0]], 3, stairX + 6.5, stairZ - 3 + 3.8, Math.PI / 2, M.concrete); // accès en pente
  rail([stairX - 3, 2.3, stairZ - 3.2], [stairX - 3, 0.75, stairZ + 0.3]);
  // Quarter pipes au fond
  quarter(3, 10, -6, -44, Math.PI / 2);
  quarter(2.2, 8, 30, -10, Math.PI);
  // Murs de bordure (briques + graff)
  box(60, 3, 0.6, 0, 0, -52, M.brick); box(0.6, 3, 50, -32, 0, -27, M.brick); box(0.6, 3, 50, 38, 0, -27, M.graffiti);
  // Bancs
  for (const [x, z] of [[-20, 4], [-24, 4], [16, 6]]) { box(2, 0.45, 0.5, x, 0, z, M.wood); rails.push({ a: new THREE.Vector3(x - 1, 0.45, z), b: new THREE.Vector3(x + 1, 0.45, z), kind: 'ledge' }); }
  // Lampadaires + arbres décoratifs (léger)
  const trunkM = new THREE.MeshStandardMaterial({ color: 0x5a3d26 }), leafM = new THREE.MeshStandardMaterial({ color: 0x3e7a35, roughness: 1 });
  for (let i = 0; i < 14; i++) {
    const x = -55 + (i % 7) * 18, z = i < 7 ? 20 : 30;
    const t = add(new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.3, 3, 8), trunkM)); t.position.set(x, 1.5, z);
    const l = add(new THREE.Mesh(new THREE.IcosahedronGeometry(1.8, 1), leafM), false); l.position.set(x, 4, z);
  }
  // Immeubles en fond (silhouettes)
  for (let i = 0; i < 10; i++) { const h = 15 + Math.round(Math.random() * 6) * 5; box(14, h, 14, -90 + i * 20, 0, -80 - Math.random() * 10, i % 2 ? M.painted : M.brick); }
  // Décor de rue : trottoir en bordure, lampadaires, bancs, poubelles
  const curbM = M.concrete;
  for (const z of [-55, 40]) box(240, 0.15, 1.2, 0, 0, z, curbM);
  for (let i = 0; i < 8; i++) {
    const x = -60 + i * 17;
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.09, 5, 10), M.metal); pole.position.set(x, 2.5, 40 - 1); add(pole, false);
    const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.25, 12, 8), new THREE.MeshStandardMaterial({ color: 0xfff3d0, emissive: 0xffe2a0, emissiveIntensity: 0.8 })); lamp.position.set(x, 5.1, 39); add(lamp, false);
  }
  for (const x of [-30, 10]) { box(2, 0.45, 0.5, x, 0, 37, M.wood); }
  for (const x of [-45, 25]) { box(0.6, 0.9, 0.6, x, 0, 37.5, M.metal); }
  // UV en mètres pour toutes les surfaces texturées PBR
  scene.traverse(o => { if (o.isMesh) worldUV(o); });
  return { colliders, rails, spawn: new THREE.Vector3(0, 0, 6), sunLight: L.sun, sunDir: L.sunDir, ready: L.ready };
}

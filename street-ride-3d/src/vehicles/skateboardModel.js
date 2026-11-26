import * as THREE from 'three';
// Modèle 3D du skateboard (géométrie originale). Nez = +Z local. Hauteur du dessous des roues = 0.
export function buildSkateboardModel(colors = {}) {
  const root = new THREE.Group();
  const deckMat = new THREE.MeshStandardMaterial({ color: colors.deck ?? 0x2b2b30, roughness: 0.6 });
  const gripMat = new THREE.MeshStandardMaterial({ color: colors.grip ?? 0x111111, roughness: 1 });
  const truckMat = new THREE.MeshStandardMaterial({ color: colors.trucks ?? 0xb8bcc4, metalness: 0.85, roughness: 0.3 });
  const wheelMat = new THREE.MeshStandardMaterial({ color: colors.wheels ?? 0xf2efe6, roughness: 0.5 });
  // Plateau : forme arrondie extrudée, légèrement relevée aux extrémités (kicks)
  const shape = new THREE.Shape(); const L = 0.4, W = 0.105;
  shape.moveTo(-W, -L + W); shape.absarc(0, -L + W, W, Math.PI, 0, false); shape.lineTo(W, L - W); shape.absarc(0, L - W, W, 0, Math.PI, false); shape.closePath();
  const g = new THREE.ExtrudeGeometry(shape, { depth: 0.012, bevelEnabled: true, bevelSize: 0.004, bevelThickness: 0.003, bevelSegments: 2, curveSegments: 12 });
  g.rotateX(-Math.PI / 2);
  const pos = g.attributes.position;
  for (let i = 0; i < pos.count; i++) { const z = pos.getZ(i); const k = Math.max(0, Math.abs(z) - 0.27); pos.setY(i, pos.getY(i) + k * k * 4.5); }
  g.computeVertexNormals();
  const deck = new THREE.Mesh(g, [gripMat, deckMat]); deck.position.y = 0.085; root.add(deck);
  for (const z of [-0.22, 0.22]) {
    const base = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.03, 0.07), truckMat); base.position.set(0, 0.07, z);
    const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.2, 8), truckMat); axle.rotation.z = Math.PI / 2; axle.position.set(0, 0.03, z);
    root.add(base, axle);
    for (const x of [-0.085, 0.085]) {
      const w = new THREE.Mesh(new THREE.CylinderGeometry(0.027, 0.027, 0.03, 16), wheelMat); w.rotation.z = Math.PI / 2; w.position.set(x, 0.027, z); w.userData.wheel = true; root.add(w);
    }
  }
  root.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; });
  root.userData.materials = { deckMat, gripMat, truckMat, wheelMat };
  return root;
}

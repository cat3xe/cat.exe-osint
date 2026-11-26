import * as THREE from 'three';
// Matériaux PBR réalistes (couleur + normal map + rugosité) à partir des textures CC0 de public/assets.
const loader = new THREE.TextureLoader();
const cache = {};
function tex(file, srgb) {
  const t = loader.load('assets/textures/' + file);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
// size = taille réelle (m) couverte par une répétition de la texture
export function pbr(name, { size = 2, color = 0xffffff, metalness = 0, roughness = 1, normalScale = 1 } = {}) {
  const key = name + size + color;
  if (cache[key]) return cache[key];
  const m = new THREE.MeshStandardMaterial({
    map: tex(name + '_diff.jpg', true), normalMap: tex(name + '_nor.jpg'), roughnessMap: tex(name + '_rough.jpg'),
    color, metalness, roughness, normalScale: new THREE.Vector2(normalScale, normalScale),
  });
  m.userData.texSize = size;
  return (cache[key] = m);
}
// Projection "box mapping" : recalcule les UV en mètres selon l'axe dominant de la normale.
// Évite les textures étirées sur les grands blocs et garde une échelle cohérente partout.
export function worldUV(mesh) {
  const size = mesh.material?.userData?.texSize; if (!size) return;
  const g = mesh.geometry; const p = g.attributes.position, n = g.attributes.normal; if (!n) return;
  const uv = new Float32Array(p.count * 2); const s = new THREE.Vector3(); mesh.getWorldScale(s);
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i) * s.x, y = p.getY(i) * s.y, z = p.getZ(i) * s.z;
    const ax = Math.abs(n.getX(i)), ay = Math.abs(n.getY(i)), az = Math.abs(n.getZ(i));
    let u, v; if (ay >= ax && ay >= az) { u = x; v = z; } else if (ax >= az) { u = z; v = y; } else { u = x; v = y; }
    uv[i * 2] = u / size; uv[i * 2 + 1] = v / size;
  }
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
}

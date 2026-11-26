import * as THREE from 'three';
// Requêtes de collision sur la géométrie statique (raycasts). Suffisant pour le prototype ;
// à remplacer par une BVH (three-mesh-bvh) ou Rapier quand la ville sera grande.
const ray = new THREE.Raycaster(); const DOWN = new THREE.Vector3(0, -1, 0); const tmp = new THREE.Vector3();
const nm = new THREE.Matrix3();
export class PhysicsWorld {
  constructor(colliders, rails) { this.colliders = colliders; this.rails = rails; }
  // Sol sous un point : lance un rayon depuis "above" mètres au-dessus.
  ground(pos, above = 1.0, maxDist = 6) {
    ray.set(tmp.copy(pos).setY(pos.y + above), DOWN); ray.far = above + maxDist;
    const h = ray.intersectObjects(this.colliders, false)[0];
    if (!h) return null;
    const n = h.face.normal.clone().applyMatrix3(nm.getNormalMatrix(h.object.matrixWorld)).normalize();
    if (n.y < 0) n.negate();
    return { y: h.point.y, normal: n };
  }
  // Obstacle horizontal (mur) dans une direction.
  wall(origin, dir, dist) {
    ray.set(origin, dir); ray.far = dist;
    const h = ray.intersectObjects(this.colliders, false)[0];
    if (!h) return null;
    const n = h.face.normal.clone().applyMatrix3(nm.getNormalMatrix(h.object.matrixWorld)).normalize();
    return n.y < 0.55 ? { point: h.point, normal: n, dist: h.distance } : null;
  }
  // Rail le plus proche d'un point : renvoie { rail, t, point, dist(horizontal), dy }
  nearestRail(pos, maxDist = 0.6) {
    let best = null;
    for (const r of this.rails) {
      const ab = tmp.copy(r.b).sub(r.a); const L2 = ab.lengthSq();
      const raw = new THREE.Vector3().copy(pos).sub(r.a).dot(ab) / L2;
      if (raw < 0.01 || raw > 0.99) continue; // pas d'accroche sur les extrémités
      const t = raw;
      const p = r.a.clone().addScaledVector(ab, t);
      const d = Math.hypot(p.x - pos.x, p.z - pos.z);
      if (d < maxDist && (!best || d < best.dist)) best = { rail: r, t, point: p, dist: d, dy: pos.y - p.y };
    }
    return best;
  }
}

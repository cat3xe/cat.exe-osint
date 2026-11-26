import * as THREE from 'three';
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';
// Éclairage basé sur l'image (IBL) : un ciel HDR réel éclaire la scène et donne les reflets.
// Le soleil directionnel (ombres) est placé dans la direction du soleil de l'HDRI.
export function setupLighting(scene, renderer) {
  const sunDir = new THREE.Vector3().setFromSphericalCoords(1, THREE.MathUtils.degToRad(52), THREE.MathUtils.degToRad(215));
  const sun = new THREE.DirectionalLight(0xfff0dc, 3.2); sun.position.copy(sunDir).multiplyScalar(80); sun.castShadow = true;
  Object.assign(sun.shadow.camera, { left: -45, right: 45, top: 45, bottom: -45, near: 1, far: 220 });
  sun.shadow.bias = -0.0003; sun.shadow.normalBias = 0.04; sun.shadow.radius = 3;
  scene.add(sun, sun.target);
  const hemi = new THREE.HemisphereLight(0xcfe0ff, 0x6b5d4f, 0.35); scene.add(hemi); // remplissage avant chargement de l'HDRI
  scene.background = new THREE.Color(0xa9bed6);
  scene.fog = new THREE.Fog(0xb9c8d8, 80, 300);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const ready = new RGBELoader().loadAsync('assets/hdri/sky.hdr').then(hdr => {
    hdr.mapping = THREE.EquirectangularReflectionMapping;
    scene.environment = pmrem.fromEquirectangular(hdr).texture; scene.environmentIntensity = 0.7;
    scene.background = hdr; scene.backgroundIntensity = 0.9; scene.backgroundBlurriness = 0.0;
    hemi.intensity = 0.1; pmrem.dispose();
  }).catch(e => console.warn('HDRI indisponible, éclairage de secours', e));
  return { sun, sunDir, ready };
}

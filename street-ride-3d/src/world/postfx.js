import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/examples/jsm/postprocessing/GTAOPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { SMAAPass } from 'three/examples/jsm/postprocessing/SMAAPass.js';
// Chaîne d'effets "caméra" : occlusion ambiante (GTAO), bloom léger, étalonnage + vignette + grain, anticrénelage.
const GradeShader = {
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, speed: { value: 0 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time; uniform float speed; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + time) * 43758.5453); }
    void main(){
      vec2 c = vUv - .5;
      // flou radial léger avec la vitesse (sensation de vitesse)
      vec3 col = vec3(0.); float n = 6.;
      for (float i = 0.; i < 6.; i++) col += texture2D(tDiffuse, .5 + c * (1. - speed * .012 * i)).rgb;
      col /= n;
      // étalonnage : contraste doux, ombres froides / hautes lumières chaudes
      col = mix(col, col * col * (3. - 2. * col), .25);
      float l = dot(col, vec3(.299,.587,.114));
      col += mix(vec3(-.01,0.,.02), vec3(.03,.015,-.02), l);
      col *= 1. - dot(c, c) * .55;           // vignette
      col += (h(vUv * 1000.) - .5) * .025;   // grain pellicule
      gl_FragColor = vec4(col, 1.);
    }`,
};
export class PostFX {
  constructor(renderer, scene, camera) {
    this.r = renderer; this.scene = scene; this.camera = camera;
    const size = renderer.getDrawingBufferSize(new THREE.Vector2());
    const rt = new THREE.WebGLRenderTarget(size.x, size.y, { type: THREE.HalfFloatType, samples: 4 });
    this.composer = new EffectComposer(renderer, rt);
    this.composer.addPass(new RenderPass(scene, camera));
    this.ao = new GTAOPass(scene, camera, size.x, size.y); this.ao.updateGtaoMaterial({ radius: 0.6, distanceExponent: 1.5, thickness: 1.2, scale: 1.2 });
    this.ao.blendIntensity = 0.9; this.composer.addPass(this.ao);
    this.bloom = new UnrealBloomPass(size, 0.25, 0.5, 0.92); this.composer.addPass(this.bloom);
    this.composer.addPass(new OutputPass());
    this.grade = new ShaderPass(GradeShader); this.composer.addPass(this.grade);
    this.smaa = new SMAAPass(size.x, size.y); this.composer.addPass(this.smaa);
    this.enabled = true;
  }
  configure(q) { this.enabled = q.postfx; this.ao.enabled = q.ao; this.bloom.enabled = q.bloom; this.smaa.enabled = q.smaa; }
  setSize(w, h) { this.composer.setPixelRatio(this.r.getPixelRatio()); this.composer.setSize(w, h); }
  render(dt, speed) {
    if (!this.enabled) { this.r.render(this.scene, this.camera); return; }
    this.grade.uniforms.time.value += dt; this.grade.uniforms.speed.value = Math.max(0, (speed - 6) / 6);
    this.composer.render(dt);
  }
}

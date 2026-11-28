import React, {useMemo} from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import {RoundedBox} from '@react-three/drei';
import * as THREE from 'three';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {C, W, H, T} from './theme';

// Écouteur : pièce de révolution (lathe) avec tige qui s'évase vers la bulle.
function earbudGeometry(): THREE.LatheGeometry {
  const pts: THREE.Vector2[] = [];
  pts.push(new THREE.Vector2(0.0, -1.0));
  pts.push(new THREE.Vector2(0.05, -0.99));
  pts.push(new THREE.Vector2(0.085, -0.9));
  pts.push(new THREE.Vector2(0.1, -0.6));
  pts.push(new THREE.Vector2(0.12, -0.3));
  // Bulle : s'évase depuis la tige (r 0.12) jusqu'au bombé (r 0.36)
  for (let i = 1; i <= 48; i++) {
    const a = (i / 48) * Math.PI;
    const r = 0.12 + 0.24 * Math.pow(Math.sin(a), 0.5);
    const y = -0.3 + 0.85 * (1 - Math.cos(a)) * 0.5;
    pts.push(new THREE.Vector2(r, y));
  }
  pts.push(new THREE.Vector2(0.0, 0.56));
  return new THREE.LatheGeometry(pts, 96);
}

const Scene: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {gl, scene} = useThree();

  // Environnement studio (réflexions propres sur le plastique / métal)
  useMemo(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  }, [gl, scene]);

  const earbud = useMemo(() => earbudGeometry(), []);
  const bodyMat = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color: C.product,
        roughness: 0.22,
        metalness: 0,
        clearcoat: 1,
        clearcoatRoughness: 0.08,
      }),
    [],
  );
  const darkMat = useMemo(
    () => new THREE.MeshPhysicalMaterial({color: '#0A0A0C', roughness: 0.6}),
    [],
  );
  const ledMat = useMemo(
    () => new THREE.MeshStandardMaterial({color: C.accent, emissive: C.accent, emissiveIntensity: 2.5}),
    [],
  );

  // Apparition (ressort) à partir de T.hook + 50
  const appear = spring({frame: frame - 50, fps, config: {damping: 18, stiffness: 120}});
  const rise = interpolate(appear, [0, 1], [-3, 0]);

  // Rotation continue + ralentissement sur le hero
  const spin = interpolate(frame, [T.hero, T.features + 60], [0, Math.PI * 1.4], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // Écouteur : se décale à gauche quand l'étui arrive
  const earX = interpolate(frame, [T.features, T.features + 40], [0, -0.42], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // Étui : apparaît à droite
  const caseIn = spring({frame: frame - (T.features + 10), fps, config: {damping: 16, stiffness: 110}});
  const caseScale = Math.max(0, caseIn);

  // Position verticale du produit : centre (hero) → haut (features) → centre bas (end)
  const groupY = interpolate(frame, [T.hero, T.features, T.end], [0.45, 0.72, 0.5], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const groupScale = interpolate(frame, [T.features, T.end], [0.6, 0.55], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <>
      <color attach="background" args={[C.bg]} />
      <ambientLight intensity={0.25} />
      <directionalLight position={[3, 4, 5]} intensity={1.4} />
      {/* Rim couleur accent + rim blanche opposée : découpe le produit du fond */}
      <pointLight position={[-3, 1, -2]} color={C.accent} intensity={6} />
      <pointLight position={[3, -2, -3]} color="#ffffff" intensity={3} />

      <group position={[0, groupY + rise, 0]} scale={groupScale}>
        {/* Écouteur */}
        <group position={[earX, 0, 0]} rotation={[0.15, spin, 0.1]}>
          <mesh geometry={earbud} material={bodyMat} />
          {/* Grille du haut-parleur */}
          <mesh position={[0, 0.2, 0.3]} material={darkMat}>
            <sphereGeometry args={[0.07, 24, 24]} />
          </mesh>
          {/* LED sur la tige */}
          <mesh position={[0.02, -0.82, 0.1]} material={ledMat}>
            <sphereGeometry args={[0.03, 16, 16]} />
          </mesh>
        </group>

        {/* Étui de charge */}
        <group position={[0.85, -0.05, 0]} scale={caseScale} rotation={[0, -spin * 0.5, 0]}>
          <RoundedBox args={[0.95, 0.95, 0.55]} radius={0.14} smoothness={6} material={bodyMat} />
          <mesh position={[0, -0.2, 0.28]} material={ledMat}>
            <sphereGeometry args={[0.03, 16, 16]} />
          </mesh>
        </group>
      </group>
    </>
  );
};

export const Product3D: React.FC = () => (
  <ThreeCanvas width={W} height={H} camera={{position: [0, 0, 5], fov: 35}}>
    <Scene />
  </ThreeCanvas>
);

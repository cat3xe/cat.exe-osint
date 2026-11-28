import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

// ---------- Réglages globaux ----------
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const IPHONE_AD_DURATION = 450; // 15 s

// Palette néon bleu + blanc
const BG = '#03060f';
const BLUE = '#2aa8ff';
const BLUE_SOFT = '#7cd0ff';
const WHITE = '#ffffff';

// Logo officiel : place ici le fichier fourni par le client (ex. public/logo.png)
// Laisse null tant que le logo n'est pas fourni.
const LOGO_SRC: string | null = null;

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Lueur néon réutilisable
const neon = (intensity = 1) => ({
  filter: `drop-shadow(0 0 ${10 * intensity}px ${BLUE}) drop-shadow(0 0 ${32 * intensity}px ${BLUE})`,
});

// ---------- Fond : grille en perspective + halo qui respire ----------
const Background: React.FC<{frame: number}> = ({frame}) => {
  const drift = (frame * 1.2) % 120;
  const pulse = 0.5 + 0.5 * Math.sin(frame / 18);
  return (
    <AbsoluteFill style={{background: BG, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 45%, rgba(42,168,255,${0.18 + 0.08 * pulse}), transparent 60%)`,
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${BLUE}22 2px, transparent 2px), linear-gradient(90deg, ${BLUE}22 2px, transparent 2px)`,
          backgroundSize: '120px 120px',
          backgroundPosition: `0px ${drift}px`,
          transform: 'perspective(800px) rotateX(62deg) scale(2.4)',
          transformOrigin: 'center 70%',
          opacity: 0.45,
          maskImage: 'linear-gradient(to top, black, transparent 70%)',
        }}
      />
    </AbsoluteFill>
  );
};

// ---------- Scène 1 : clap (0 s → 2 s) ----------
const Clapperboard: React.FC<{frame: number}> = ({frame}) => {
  const {fps} = useVideoConfig();
  // Le bras s'ouvre puis claque en frame 36
  const open = interpolate(frame, [0, 22], [-35, -35], clamp);
  const clap = spring({frame: frame - 36, fps, config: {damping: 9, stiffness: 260}});
  const angle = interpolate(clap, [0, 1], [-35, 0]);
  const visible = interpolate(frame, [0, 8, 62, 74], [0, 1, 1, 0], clamp);
  const flash = interpolate(frame, [34, 38, 52], [0, 1, 0], clamp);

  return (
    <>
      <AbsoluteFill
        style={{background: WHITE, opacity: flash * 0.85, mixBlendMode: 'screen'}}
      />
      <div
        style={{
          position: 'absolute',
          left: WIDTH / 2 - 330,
          top: HEIGHT / 2 - 250,
          width: 660,
          opacity: visible,
          transform: `scale(${interpolate(frame, [0, 10], [0.9, 1], clamp)})`,
          ...neon(0.8),
        }}
      >
        <div
          style={{
            height: 120,
            transformOrigin: 'left center',
            transform: `rotate(${frame < 36 ? open : angle}deg)`,
            background: `repeating-linear-gradient(-45deg, ${WHITE} 0 40px, ${BLUE} 40px 80px)`,
            border: `4px solid ${BLUE_SOFT}`,
            borderRadius: 8,
          }}
        />
        <div
          style={{
            marginTop: 8,
            height: 340,
            borderRadius: 8,
            border: `4px solid ${BLUE}`,
            background: 'rgba(3,6,15,0.6)',
            color: BLUE_SOFT,
            fontFamily: 'monospace',
            fontSize: 40,
            padding: 28,
            lineHeight: 1.5,
          }}
        >
          <div>PROD: IPHONE</div>
          <div>SCENE: 01</div>
          <div>TAKE: 01</div>
        </div>
      </div>
    </>
  );
};

// ---------- Scène 2 + 3 : iPhone néon qui se transforme en tablette ----------
const Device: React.FC<{frame: number}> = ({frame}) => {
  const {fps} = useVideoConfig();
  const appear = spring({frame: frame - 60, fps, config: {damping: 16, stiffness: 120}});
  // Transformation iPhone -> tablette entre 120 et 210 (3 s)
  const morph = interpolate(frame, [120, 210], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.65, 0, 0.35, 1),
  });
  // Retour léger sur iPhone entre 300 et 340 pour la vente
  const back = interpolate(frame, [300, 340], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.65, 0, 0.35, 1),
  });
  const m = morph - back;

  const width = interpolate(m, [0, 1], [440, 820]);
  const height = interpolate(m, [0, 1], [900, 1080]);
  const radius = interpolate(m, [0, 1], [72, 36]);
  const scale = appear;

  return (
    <div
      style={{
        position: 'absolute',
        left: WIDTH / 2 - width / 2,
        top: HEIGHT / 2 - height / 2 - 80,
        width,
        height,
        borderRadius: radius,
        transform: `scale(${interpolate(scale, [0, 1], [0.6, 1])}) translateY(${interpolate(scale, [0, 1], [120, 0])}px)`,
        opacity: appear,
        border: `6px solid ${BLUE}`,
        background: 'linear-gradient(160deg, #0b1a33, #03060f 70%)',
        overflow: 'hidden',
        ...neon(1.2),
      }}
    >
      <Screen frame={frame} m={m} />
    </div>
  );
};

// Contenu de l'écran : cartes UI + balayage de lumière
const Screen: React.FC<{frame: number; m: number}> = ({frame, m}) => {
  const sweep = interpolate(frame, [90, 140], [-120, 140], clamp);
  const cards = [0, 1, 2];
  return (
    <div style={{position: 'absolute', inset: 0, padding: 36}}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `linear-gradient(115deg, transparent ${sweep - 10}%, ${BLUE}55 ${sweep}%, transparent ${sweep + 10}%)`,
        }}
      />
      <div style={{color: WHITE, fontSize: 56, fontWeight: 700, letterSpacing: 2}}>
        iPhone
      </div>
      {cards.map((i) => {
        const p = spring({frame: frame - 130 - i * 8, fps: 30, config: {damping: 18}});
        return (
          <div
            key={i}
            style={{
              marginTop: 36,
              height: 180 + m * 40,
              borderRadius: 28,
              background: `linear-gradient(120deg, ${BLUE}33, ${WHITE}11)`,
              border: `2px solid ${BLUE}88`,
              transform: `translateX(${interpolate(p, [0, 1], [400, 0])}px)`,
              opacity: p,
            }}
          />
        );
      })}
    </div>
  );
};

// ---------- Scène 4 : titre + offre + CTA ----------
const Copy: React.FC<{frame: number}> = ({frame}) => {
  const {fps} = useVideoConfig();
  const title = spring({frame: frame - 230, fps, config: {damping: 14}});
  const sub = interpolate(frame, [250, 280], [0, 1], clamp);
  const cta = spring({frame: frame - 350, fps, config: {damping: 12}});
  const logoIn = interpolate(frame, [390, 420], [0, 1], clamp);

  return (
    <>
      <div
        style={{
          position: 'absolute',
          top: 200,
          width: '100%',
          textAlign: 'center',
          color: WHITE,
          fontSize: 92,
          fontWeight: 800,
          opacity: title,
          transform: `translateY(${interpolate(title, [0, 1], [60, 0])}px)`,
          ...neon(0.6),
        }}
      >
        Nouveau
        <div style={{color: BLUE_SOFT, fontSize: 92}}>iPhone</div>
      </div>

      <div
        style={{
          position: 'absolute',
          top: 620,
          width: '100%',
          textAlign: 'center',
          color: WHITE,
          fontSize: 44,
          opacity: sub,
          letterSpacing: 4,
        }}
      >
        LANCEMENT · EN VENTE MAINTENANT
      </div>

      <div
        style={{
          position: 'absolute',
          bottom: 260,
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          transform: `scale(${interpolate(cta, [0, 1], [0.7, 1])})`,
          opacity: cta,
        }}
      >
        <div
          style={{
            padding: '36px 80px',
            borderRadius: 999,
            border: `4px solid ${BLUE}`,
            background: `${BLUE}22`,
            color: WHITE,
            fontSize: 54,
            fontWeight: 700,
            ...neon(0.9),
          }}
        >
          Découvrir l'iPhone →
        </div>
      </div>

      <div
        style={{
          position: 'absolute',
          bottom: 110,
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          opacity: logoIn,
        }}
      >
        {LOGO_SRC ? (
          <Img src={LOGO_SRC} style={{height: 110}} />
        ) : (
          <div style={{color: BLUE_SOFT, fontSize: 30, letterSpacing: 6}}>
            [ LOGO OFFICIEL ]
          </div>
        )}
      </div>
    </>
  );
};

// ---------- Composition principale ----------
export const IphoneAd: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <Clapperboard frame={frame} />
      <Device frame={frame} />
      <Copy frame={frame} />
    </AbsoluteFill>
  );
};

import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Product3D} from './Product3D';
import {C, CUTS, DURATION, FONT, SAFE, T} from './theme';

// Texte "kinetic" : lettre par lettre, ressort + flou → net.
const Kinetic: React.FC<{text: string; start?: number; size: number; color?: string; weight?: number; spacing?: number}> = ({
  text,
  start = 0,
  size,
  color = C.text,
  weight = 700,
  spacing = -2,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div style={{display: 'flex', justifyContent: 'center', flexWrap: 'wrap'}}>
      {Array.from(text).map((ch, i) => {
        const p = spring({frame: frame - start - i * 1.2, fps, config: {damping: 16, stiffness: 140}});
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              whiteSpace: 'pre',
              color,
              fontSize: size,
              fontWeight: weight,
              letterSpacing: spacing,
              fontFamily: FONT,
              opacity: p,
              transform: `translateY(${(1 - p) * 60}px)`,
              filter: `blur(${interpolate(p, [0, 1], [18, 0])}px)`,
            }}
          >
            {ch}
          </span>
        );
      })}
    </div>
  );
};

// Scène Hook : "Le silence." puis "Enfin."
const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [48, 58], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: out, justifyContent: 'center', alignItems: 'center', padding: `0 ${SAFE.left}px`}}>
      <Kinetic text="Le silence." size={124} />
      <div style={{height: 20}} />
      <Kinetic text="Enfin." size={124} color={C.accent} start={30} />
    </AbsoluteFill>
  );
};

// Scène Hero : titre du produit sous l'écouteur 3D
const Hero: React.FC = () => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [80, 90], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: out, justifyContent: 'flex-end', paddingBottom: SAFE.bottom + 180}}>
      <Kinetic text="AirPods Pro" size={120} start={6} />
      <div style={{height: 24}} />
      <Kinetic text="Le son, autour de vous." size={44} color={C.muted} weight={500} start={22} spacing={0} />
    </AbsoluteFill>
  );
};

// Scène Features : trois lignes avec index HUD et anneau animé
const FEATURES = ['Réduction de bruit active', 'Transparence adaptative', 'Audio spatial personnalisé'];
const Features: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const out = interpolate(frame, [112, 120], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: out, justifyContent: 'flex-end', padding: `0 ${SAFE.left}px ${SAFE.bottom + 60}px`}}>
      {FEATURES.map((label, i) => {
        const start = i * 36;
        const p = spring({frame: frame - start, fps, config: {damping: 18, stiffness: 120}});
        const ring = interpolate(frame - start, [0, 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return (
          <div
            key={label}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 28,
              borderTop: `1px solid rgba(255,255,255,0.15)`,
              padding: '26px 0',
              opacity: p,
              transform: `translateX(${(1 - p) * -80}px)`,
              fontFamily: FONT,
            }}
          >
            <svg width={72} height={72} viewBox="0 0 72 72">
              <circle cx={36} cy={36} r={30} fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth={3} />
              <circle
                cx={36}
                cy={36}
                r={30}
                fill="none"
                stroke={C.accent}
                strokeWidth={3}
                strokeLinecap="round"
                strokeDasharray={188}
                strokeDashoffset={188 * (1 - ring)}
                transform="rotate(-90 36 36)"
              />
            </svg>
            <div style={{color: C.muted, fontSize: 26, width: 50}}>0{i + 1}</div>
            <div style={{color: C.text, fontSize: 52, fontWeight: 600}}>{label}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Scène End : marque, slogan et CTA dans les 2 dernières secondes
const End: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cta = spring({frame: frame - 45, fps, config: {damping: 12, stiffness: 160}});
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: SAFE.bottom + 40}}>
      <div style={{fontFamily: FONT, color: C.muted, fontSize: 36, letterSpacing: 8, marginBottom: 24, textTransform: 'uppercase'}}>
        AirPods Pro
      </div>
      <Kinetic text="Entendre sans bruit." size={88} start={0} />
      <div style={{height: 60}} />
      <div
        style={{
          transform: `scale(${Math.max(0, cta)})`,
          background: C.accent,
          color: C.bg,
          fontFamily: FONT,
          fontSize: 44,
          fontWeight: 700,
          borderRadius: 999,
          padding: '28px 72px',
        }}
      >
        Découvrir
      </div>
    </AbsoluteFill>
  );
};

// Flash blanc + streak sur chaque coupe
const CutFlash: React.FC = () => {
  const frame = useCurrentFrame();
  const o = Math.max(
    ...CUTS.map((c) => interpolate(frame, [c - 1, c + 2, c + 10], [0, 0.85, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})),
  );
  return <AbsoluteFill style={{background: '#fff', opacity: o, mixBlendMode: 'screen', pointerEvents: 'none'}} />;
};

// Lueur d'ambiance qui respire
const Glow: React.FC = () => {
  const frame = useCurrentFrame();
  const pulse = 0.25 + 0.05 * Math.sin(frame / 18);
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 50% 35%, rgba(125,211,252,${pulse}) 0%, transparent 55%)`,
        mixBlendMode: 'screen',
        pointerEvents: 'none',
      }}
    />
  );
};

export const AirPodsAd: React.FC = () => (
  <AbsoluteFill style={{background: C.bg}}>
    <AbsoluteFill>
      <Product3D />
    </AbsoluteFill>
    <Glow />
    <Sequence from={T.hook} durationInFrames={T.hero - T.hook}>
      <Hook />
    </Sequence>
    <Sequence from={T.hero} durationInFrames={T.features - T.hero}>
      <Hero />
    </Sequence>
    <Sequence from={T.features} durationInFrames={T.end - T.features}>
      <Features />
    </Sequence>
    <Sequence from={T.end} durationInFrames={DURATION - T.end}>
      <End />
    </Sequence>
    <CutFlash />
    <Audio src={staticFile('audio/score.wav')} />
  </AbsoluteFill>
);

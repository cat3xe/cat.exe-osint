import React from 'react';
import {AbsoluteFill, Easing, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

// ---------- Réglages ----------
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION = 900; // 30 s

const BG = '#06030d';
const V = '#a238ff';
const V2 = '#d28bff';
const VD = '#4a0f8f';
const WHITE = '#ffffff';
const GREY = '#9d95b3';
const CARD = '#140c24';
const FONT = 'Inter, "Arial Black", sans-serif';
const FONT2 = 'Inter, Helvetica, Arial, sans-serif';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const EASE = Easing.bezier(0.7, 0, 0.2, 1);
const OUT = Easing.bezier(0.16, 1, 0.3, 1);

const rnd = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

const sp = (frame: number, fps: number, start: number, damping = 14) =>
  spring({frame: frame - start, fps, config: {damping, stiffness: 160}});

const HEART_PATH =
  'M12 21s-7.5-4.6-9.5-9.2C1 8.6 2.9 5 6.4 5c2 0 3.6 1.1 4.6 2.7C12 6.1 13.6 5 15.6 5 19.1 5 21 8.6 21.5 11.8 19.5 16.4 12 21 12 21z';

// ---------- Cœur violet (motif de marque, pas le logo officiel) ----------
const Heart: React.FC<{size: number; glow?: number}> = ({size, glow = 1}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{overflow: 'visible', filter: `drop-shadow(0 0 ${10 * glow}px ${V}) drop-shadow(0 0 ${34 * glow}px ${V})`}}>
    <defs>
      <linearGradient id="heartGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor={V2} />
        <stop offset="1" stopColor={VD} />
      </linearGradient>
    </defs>
    <path d={HEART_PATH} fill="url(#heartGrad)" />
  </svg>
);

// ---------- Fond global : halo, grain, poussières, fuite de lumière ----------
const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const x = 50 + Math.sin(frame / 40) * 18;
  const y = 40 + Math.cos(frame / 55) * 10;
  return (
    <AbsoluteFill style={{background: BG, overflow: 'hidden'}}>
      <AbsoluteFill style={{background: `radial-gradient(circle at ${x}% ${y}%, rgba(162,56,255,0.32), transparent 55%)`}} />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 80% 90%, rgba(74,15,143,0.35), transparent 50%)'}} />
      <svg width="100%" height="100%" style={{position: 'absolute', inset: 0, opacity: 0.07, mixBlendMode: 'overlay'}}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" seed={frame % 20} />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
      {Array.from({length: 60}, (_, i) => {
        const speed = 0.8 + rnd(i + 7) * 1.6;
        const yy = HEIGHT - ((frame * speed + rnd(i + 3) * HEIGHT) % HEIGHT);
        const xx = rnd(i) * WIDTH + Math.sin((frame + i * 9) / 30) * 14;
        const s = 3 + rnd(i + 11) * 5;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: xx,
              top: yy,
              width: s,
              height: s,
              borderRadius: s,
              background: i % 3 === 0 ? V2 : V,
              opacity: 0.2 + rnd(i + 5) * 0.55,
              boxShadow: `0 0 ${s * 3}px ${V}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// ---------- Texte : mots qui arrivent un par un ----------
const Words: React.FC<{text: string; size: number; top: number; delay?: number; color?: string; gap?: number}> = ({
  text,
  size,
  top,
  delay = 0,
  color = WHITE,
  gap = 4,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div style={{position: 'absolute', top, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: size, lineHeight: 1, color, textTransform: 'uppercase', letterSpacing: -2}}>
      {text.split(' ').map((w, i) => {
        const p = sp(frame, fps, delay + i * gap, 13);
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              marginRight: size * 0.18,
              opacity: p,
              transform: `translateY(${(1 - p) * size * 0.6}px) scale(${0.8 + 0.2 * p})`,
              filter: `blur(${(1 - p) * 8}px)`,
              textShadow: `0 0 40px ${V}99`,
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

// ---------- Pochette abstraite (dégradé + formes), sans visuel réel ----------
const Cover: React.FC<{hue: number; size: number; seed: number}> = ({hue, size, seed}) => (
  <div style={{position: 'relative', width: size, height: size, borderRadius: size * 0.05, overflow: 'hidden', background: `linear-gradient(160deg, hsl(${hue} 90% 60%), hsl(${hue + 40} 80% 18%))`}}>
    <div style={{position: 'absolute', width: size * 0.6, height: size * 0.6, borderRadius: '50%', left: size * (0.2 + rnd(seed) * 0.3), top: size * (0.15 + rnd(seed + 1) * 0.2), background: `radial-gradient(circle, hsl(${hue + 80} 100% 80%), transparent 70%)`, opacity: 0.85}} />
    <svg viewBox="0 0 100 100" width={size} height={size} style={{position: 'absolute', inset: 0}}>
      <path d={`M0 ${60 + rnd(seed) * 20} Q 35 ${35 + rnd(seed + 2) * 20} 60 ${58 + rnd(seed + 3) * 15} T 100 ${50 + rnd(seed + 4) * 20} L100 100 L0 100Z`} fill="rgba(0,0,0,0.45)" />
      <path d={`M0 ${75 + rnd(seed) * 10} Q 50 ${60 + rnd(seed + 5) * 15} 100 ${70 + rnd(seed + 6) * 10} L100 100 L0 100Z`} fill="rgba(0,0,0,0.6)" />
    </svg>
    <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(120deg, rgba(255,255,255,0.18), transparent 40%)'}} />
  </div>
);

// ---------- Scène 1 · Accroche (0–3 s) ----------
const SceneHook: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const heartIn = sp(frame, fps, 0, 10);
  const pulse = 1 + 0.06 * Math.sin(frame / 4.2);
  const zoom = interpolate(frame, [0, 90], [1.08, 1], {...clamp, easing: OUT});
  return (
    <AbsoluteFill style={{transform: `scale(${zoom})`}}>
      <div style={{position: 'absolute', top: 560, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${heartIn * pulse})`}}>
        <Heart size={220} />
      </div>
      <Words text="Ta musique," size={150} top={1000} delay={8} />
    </AbsoluteFill>
  );
};

// ---------- Scène 2 · SANS LIMITE (3–7 s) ----------
const SceneSlogan: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const slam = sp(frame, fps, 0, 9);
  const shake = frame < 20 ? Math.sin(frame * 2.3) * (20 - frame) * 0.9 : 0;
  const flash = interpolate(frame, [0, 3, 8], [0.9, 0.6, 0], clamp);
  const strike = interpolate(frame, [30, 48], [0, 1], {...clamp, easing: EASE});
  const limiteColor = frame > 36 ? V2 : WHITE;
  return (
    <AbsoluteFill style={{transform: `translateX(${shake}px)`}}>
      <div style={{position: 'absolute', top: 760, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 200, lineHeight: 0.95, color: WHITE, textTransform: 'uppercase', letterSpacing: -6, transform: `scale(${interpolate(slam, [0, 1], [2.4, 1])})`, opacity: Math.min(1, slam * 2), textShadow: `0 0 60px ${V}aa`}}>
        Sans
      </div>
      <div style={{position: 'absolute', top: 1010, width: '100%', display: 'flex', justifyContent: 'center'}}>
        <div style={{position: 'relative', fontFamily: FONT, fontWeight: 900, fontSize: 200, lineHeight: 0.95, color: limiteColor, textTransform: 'uppercase', letterSpacing: -6, textShadow: `0 0 60px ${V}aa`, transform: `scale(${interpolate(sp(frame, fps, 10, 9), [0, 1], [2.4, 1])})`, opacity: Math.min(1, sp(frame, fps, 10, 9) * 2)}}>
          Limite
          <div style={{position: 'absolute', left: -20, right: -20, top: '52%', height: 16, background: V, transformOrigin: 'left center', transform: `scaleX(${strike})`, boxShadow: `0 0 30px ${V}`}} />
        </div>
      </div>
      <AbsoluteFill style={{background: WHITE, opacity: flash, mixBlendMode: 'screen'}} />
    </AbsoluteFill>
  );
};

// ---------- Scène 3 · Site web plein écran (7–12 s) ----------
const SceneWeb: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const query = 'Ton prochain son';
  const typed = query.slice(0, Math.max(0, Math.min(query.length, Math.floor((frame - 12) / 2.5))));
  const scroll = interpolate(frame, [70, 150], [0, -420], {...clamp, easing: EASE});
  const hues = [280, 310, 255, 330, 300, 275];
  return (
    <AbsoluteFill style={{background: '#0d0717', fontFamily: FONT2, color: WHITE}}>
      {/* Barre du navigateur */}
      <div style={{position: 'absolute', top: 0, left: 0, right: 0, height: 170, background: '#1a1126', borderBottom: `2px solid ${V}33`, display: 'flex', alignItems: 'flex-end', padding: '0 40px 22px', gap: 18, boxSizing: 'border-box'}}>
        <div style={{display: 'flex', gap: 10, marginRight: 10, paddingBottom: 14}}>
          {['#ff5f57', '#febc2e', '#28c840'].map((c) => (
            <div key={c} style={{width: 18, height: 18, borderRadius: 9, background: c}} />
          ))}
        </div>
        <div style={{flex: 1, height: 72, borderRadius: 36, background: '#0d0717', display: 'flex', alignItems: 'center', padding: '0 28px', fontSize: 28, color: GREY}}>
          votre-marque.com/recherche
        </div>
      </div>
      {/* Page */}
      <div style={{position: 'absolute', top: 210, left: 0, right: 0, bottom: 0, padding: '0 40px', overflow: 'hidden'}}>
        <div style={{transform: `translateY(${scroll}px)`}}>
          <div style={{opacity: sp(frame, fps, 0, 16), transform: `translateY(${(1 - sp(frame, fps, 0, 16)) * 40}px)`, fontFamily: FONT, fontWeight: 900, fontSize: 64, textTransform: 'uppercase', letterSpacing: -2, marginBottom: 30}}>
            Recherche
          </div>
          <div style={{height: 110, borderRadius: 55, background: CARD, border: `3px solid ${V}`, boxShadow: `0 0 40px ${V}66`, display: 'flex', alignItems: 'center', padding: '0 40px', fontSize: 42, boxSizing: 'border-box', opacity: sp(frame, fps, 6, 16)}}>
            {typed}
            <span style={{display: 'inline-block', width: 4, height: 46, background: V2, marginLeft: 6, opacity: Math.floor(frame / 8) % 2 ? 0 : 1}} />
          </div>
          <div style={{marginTop: 40, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 28}}>
            {hues.map((h, i) => {
              const p = sp(frame, fps, 40 + i * 6, 14);
              return (
                <div key={i} style={{opacity: p, transform: `translateY(${(1 - p) * 90}px) scale(${0.9 + 0.1 * p})`, background: CARD, borderRadius: 22, padding: 18, boxSizing: 'border-box'}}>
                  <Cover hue={h} size={300} seed={i * 5 + 1} />
                  <div style={{marginTop: 14, fontFamily: FONT, fontWeight: 900, fontSize: 26, textTransform: 'uppercase'}}>Titre {i + 1}</div>
                  <div style={{marginTop: 4, fontSize: 22, color: GREY}}>Artiste</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- Pochette 3D (recto/verso) ----------
const Card3D: React.FC<{hue: number; seed: number; x: number; z: number; ry: number; flip: number; float: number; size: number}> = ({hue, seed, x, z, ry, flip, float, size}) => (
  <div
    style={{
      position: 'absolute',
      left: WIDTH / 2 - size / 2 + x,
      top: HEIGHT / 2 - size / 2 + float,
      width: size,
      height: size,
      transformStyle: 'preserve-3d',
      transform: `translateZ(${z}px) rotateY(${ry + flip}deg)`,
    }}
  >
    <div style={{position: 'absolute', inset: 0, backfaceVisibility: 'hidden', borderRadius: size * 0.05, boxShadow: `0 40px 80px rgba(0,0,0,0.7), 0 0 60px ${V}88`}}>
      <Cover hue={hue} size={size} seed={seed} />
    </div>
    <div
      style={{
        position: 'absolute',
        inset: 0,
        backfaceVisibility: 'hidden',
        transform: 'rotateY(180deg)',
        borderRadius: size * 0.05,
        background: CARD,
        border: `3px solid ${V}`,
        padding: 30,
        boxSizing: 'border-box',
        fontFamily: FONT2,
        color: WHITE,
      }}
    >
      <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 40, textTransform: 'uppercase', marginBottom: 20}}>Playlist</div>
      {[1, 2, 3, 4, 5].map((t) => (
        <div key={t} style={{display: 'flex', justifyContent: 'space-between', fontSize: 26, padding: '12px 0', borderBottom: `1px solid ${V}44`}}>
          <span>Titre {t}</span>
          <span style={{color: GREY}}>3:4{t}</span>
        </div>
      ))}
    </div>
  </div>
);

// ---------- Scène 4 · Pochettes 3D (12–18 s) ----------
const Scene3D: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const orbit = interpolate(frame, [0, 180], [-22, 22], {...clamp, easing: EASE});
  const tilt = interpolate(frame, [0, 180], [-10, -4], clamp);
  const flip = interpolate(frame, [80, 120], [0, 180], {...clamp, easing: EASE});
  const push = interpolate(frame, [100, 140], [0, 260], {...clamp, easing: OUT});
  const title = sp(frame, fps, 0, 14);
  return (
    <AbsoluteFill style={{perspective: 1400, perspectiveOrigin: '50% 45%', overflow: 'hidden'}}>
      <div style={{position: 'absolute', inset: 0, transformStyle: 'preserve-3d', transform: `rotateX(${tilt}deg) rotateY(${orbit}deg)`}}>
        <Card3D hue={300} seed={2} x={-330} z={-160} ry={38} flip={0} float={Math.sin(frame / 14) * 26} size={380} />
        <Card3D hue={255} seed={9} x={330} z={-160} ry={-38} flip={0} float={Math.cos(frame / 16) * 26} size={380} />
        <Card3D hue={330} seed={5} x={0} z={push} ry={0} flip={flip} float={Math.sin(frame / 12) * 18} size={460} />
      </div>
      <div style={{position: 'absolute', top: 260, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 84, textTransform: 'uppercase', color: WHITE, opacity: title, transform: `translateY(${(1 - title) * -40}px)`, textShadow: `0 0 40px ${V}`}}>
        Tes pochettes
      </div>
      <div style={{position: 'absolute', bottom: 260, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 60, textTransform: 'uppercase', color: V2, opacity: sp(frame, fps, 120, 14), letterSpacing: 2}}>
        En playlist
      </div>
    </AbsoluteFill>
  );
};

// ---------- Scène 5 · Lecture (18–23 s) ----------
const ScenePlay: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = interpolate(frame, [20, 140], [0, 0.66], {...clamp, easing: EASE});
  const spin = frame * 2.4;
  const radial = interpolate(frame, [128, 150], [0, 1600], {...clamp, easing: EASE});
  const sec = Math.floor(interpolate(frame, [20, 140], [0, 128], clamp));
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', top: 360, width: '100%', display: 'flex', justifyContent: 'center'}}>
        <div style={{transform: `rotate(${spin}deg) scale(${interpolate(sp(frame, fps, 0, 12), [0, 1], [0.6, 1])})`, borderRadius: '50%', boxShadow: `0 0 120px ${V}`}}>
          <div style={{borderRadius: '50%', overflow: 'hidden', width: 560, height: 560}}>
            <Cover hue={290} size={560} seed={21} />
          </div>
        </div>
      </div>
      <div style={{position: 'absolute', top: 1040, left: 120, right: 120}}>
        <div style={{height: 14, borderRadius: 7, background: '#2a1b40'}}>
          <div style={{height: '100%', width: `${progress * 100}%`, borderRadius: 7, background: `linear-gradient(90deg, ${VD}, ${V2})`, boxShadow: `0 0 20px ${V}`}} />
        </div>
        <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 16, fontFamily: FONT2, fontSize: 26, color: GREY}}>
          <span>{`${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`}</span>
          <span>3:48</span>
        </div>
      </div>
      <div style={{position: 'absolute', top: 1170, width: '100%', height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10}}>
        {Array.from({length: 36}, (_, i) => {
          const h = 30 + 150 * Math.abs(Math.sin(frame / 5 + i * 0.5)) * (0.5 + rnd(i) * 0.5);
          return <div key={i} style={{width: 14, height: h, borderRadius: 7, background: i / 36 < progress ? V2 : '#3a2655', boxShadow: `0 0 12px ${V}88`}} />;
        })}
      </div>
      <Words text="Lecture" size={120} top={1460} delay={20} color={WHITE} gap={3} />
      <Words text="illimitée" size={120} top={1600} delay={34} color={V2} gap={3} />
      <div style={{position: 'absolute', inset: 0, background: `radial-gradient(circle at 50% 35%, ${V} 0%, ${VD} 60%, ${BG} 100%)`, clipPath: `circle(${radial}px at 50% 35%)`}} />
    </AbsoluteFill>
  );
};

// ---------- Scène 6 · Atouts (23–27 s) ----------
const SceneFeatures: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const items = ['Sans pub', 'Hi-Fi', 'Hors ligne'];
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', flexDirection: 'column', display: 'flex', gap: 46}}>
      {items.map((t, i) => {
        const p = sp(frame, fps, i * 14, 10);
        const bar = interpolate(frame, [i * 14 + 6, i * 14 + 20], [0, 1], {...clamp, easing: OUT});
        const x = i % 2 === 0 ? -1 : 1;
        return (
          <div key={t} style={{position: 'relative', transform: `translateX(${(1 - p) * 500 * x}px) rotate(${(1 - p) * -8 * x}deg) scale(${0.9 + 0.1 * p})`, opacity: p}}>
            <div style={{position: 'absolute', inset: '-18px -40px', background: i === 1 ? WHITE : V, transform: `scaleX(${bar})`, transformOrigin: 'left center', borderRadius: 18, boxShadow: `0 0 50px ${V}`}} />
            <div style={{position: 'relative', fontFamily: FONT, fontWeight: 900, fontSize: 130, textTransform: 'uppercase', letterSpacing: -4, color: i === 1 ? '#0d0717' : WHITE, padding: '0 20px', lineHeight: 1}}>
              {t}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------- Scène 7 · Fin (27–30 s) ----------
const SceneEnd: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const heart = interpolate(sp(frame, fps, 0, 9), [0, 1], [0.4, 1.2]);
  const cta = sp(frame, fps, 36, 12);
  const fadeOut = interpolate(frame, [75, 90], [1, 0], clamp);
  return (
    <AbsoluteFill style={{opacity: fadeOut}}>
      <div style={{position: 'absolute', top: 480, width: '100%', display: 'flex', justifyContent: 'center', transform: `scale(${heart})`}}>
        <Heart size={260} glow={1.4} />
      </div>
      <Words text="Ta musique," size={110} top={900} delay={10} />
      <Words text="sans limite." size={110} top={1050} delay={20} color={V2} />
      <div style={{position: 'absolute', top: 1270, width: '100%', display: 'flex', justifyContent: 'center', opacity: cta, transform: `translateY(${(1 - cta) * 60}px) scale(${0.9 + 0.1 * cta})`}}>
        <div style={{padding: '34px 70px', borderRadius: 999, background: `linear-gradient(90deg, ${VD}, ${V})`, boxShadow: `0 0 60px ${V}`, fontFamily: FONT, fontWeight: 900, fontSize: 56, textTransform: 'uppercase', color: WHITE}}>
          Écoute maintenant
        </div>
      </div>
      <div style={{position: 'absolute', bottom: 200, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 48, color: GREY, letterSpacing: 8, textTransform: 'uppercase', opacity: sp(frame, fps, 50, 14)}}>
        Deezer
      </div>
    </AbsoluteFill>
  );
};

// ---------- Flash de transition entre scènes ----------
const Flash: React.FC<{at: number}> = ({at}) => {
  const frame = useCurrentFrame();
  const f = frame - at;
  const op = f >= 0 && f < 8 ? interpolate(f, [0, 2, 7], [0, 0.7, 0], clamp) : 0;
  return <AbsoluteFill style={{background: `radial-gradient(circle, ${V2}, ${V})`, opacity: op, mixBlendMode: 'screen'}} />;
};

// ---------- Scène complète ----------
export const DeezerAd: React.FC = () => (
  <AbsoluteFill>
    <Background />
    <Sequence from={0} durationInFrames={90}><SceneHook /></Sequence>
    <Sequence from={90} durationInFrames={120}><SceneSlogan /></Sequence>
    <Sequence from={210} durationInFrames={150}><SceneWeb /></Sequence>
    <Sequence from={360} durationInFrames={180}><Scene3D /></Sequence>
    <Sequence from={540} durationInFrames={150}><ScenePlay /></Sequence>
    <Sequence from={690} durationInFrames={120}><SceneFeatures /></Sequence>
    <Sequence from={810} durationInFrames={90}><SceneEnd /></Sequence>
    {[90, 210, 360, 540, 690, 810].map((t) => (
      <Flash key={t} at={t} />
    ))}
  </AbsoluteFill>
);

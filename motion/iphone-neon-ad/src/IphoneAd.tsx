import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

// ---------- Réglages ----------
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const IPHONE_AD_DURATION = 450; // 15 s

const BG = '#05070d';
const BLUE = '#2aa8ff';
const BLUE_SOFT = '#8fd6ff';
const WHITE = '#ffffff';
const GREY = '#8a93a6';
const RED = '#ff3b6b';
const FONT = '-apple-system, "SF Pro Display", Helvetica, Arial, sans-serif';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const EASE = Easing.bezier(0.65, 0, 0.35, 1);
const OUT = Easing.bezier(0.16, 1, 0.3, 1);

const PHONE_W = 440;
const PHONE_H = 900;

// Hasard déterministe (même résultat à chaque rendu)
const rnd = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

// Ressort simple, en frames
const sp = (frame: number, fps: number, start: number, damping = 16) =>
  spring({frame: frame - start, fps, config: {damping, stiffness: 140}});

// ---------- Fond : grille, halo et poussières ----------
const Background: React.FC<{frame: number}> = ({frame}) => {
  const drift = (frame * 1.4) % 120;
  const pulse = 0.5 + 0.5 * Math.sin(frame / 22);
  return (
    <AbsoluteFill style={{background: BG, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 46%, rgba(42,168,255,${0.2 + 0.08 * pulse}), transparent 58%)`,
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${BLUE}26 2px, transparent 2px), linear-gradient(90deg, ${BLUE}26 2px, transparent 2px)`,
          backgroundSize: '120px 120px',
          backgroundPosition: `0px ${drift}px`,
          transform: 'perspective(800px) rotateX(64deg) scale(2.6)',
          transformOrigin: 'center 70%',
          opacity: 0.4,
          maskImage: 'linear-gradient(to top, black, transparent 65%)',
        }}
      />
      {Array.from({length: 46}, (_, i) => {
        const x = rnd(i) * WIDTH;
        const y = (HEIGHT - ((frame * (0.6 + rnd(i + 7))) + rnd(i + 3) * HEIGHT)) % HEIGHT;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: y < 0 ? y + HEIGHT : y,
              width: 3 + rnd(i + 11) * 4,
              height: 3 + rnd(i + 11) * 4,
              borderRadius: 4,
              background: i % 3 === 0 ? BLUE_SOFT : BLUE,
              opacity: 0.25 + rnd(i + 5) * 0.5,
              boxShadow: `0 0 12px ${BLUE}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// ---------- Mots qui apparaissent un à un ----------
const WordReveal: React.FC<{text: string; start: number; size: number; color?: string; top: number}> = ({
  text,
  start,
  size,
  color = WHITE,
  top,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const words = text.split(' ');
  return (
    <div
      style={{
        position: 'absolute',
        top,
        width: '100%',
        textAlign: 'center',
        fontFamily: FONT,
        fontWeight: 800,
        fontSize: size,
        color,
        lineHeight: 1.1,
        letterSpacing: -1,
      }}
    >
      {words.map((w, i) => {
        const p = sp(frame, fps, start + i * 4, 18);
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              marginRight: size * 0.22,
              opacity: p,
              transform: `translateY(${(1 - p) * 60}px)`,
              filter: `blur(${(1 - p) * 10}px)`,
              textShadow: `0 0 30px ${BLUE}88`,
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

// ---------- Logo : grand au centre, puis rangé en haut ----------
// Le logo fourni est sur fond blanc : on le pose sur une tuile blanche en mode multiply
const LogoMark: React.FC<{frame: number}> = ({frame}) => {
  const top = interpolate(frame, [50, 100], [HEIGHT / 2 - 200, 96], {...clamp, easing: EASE});
  const h = interpolate(frame, [50, 100], [340, 130], {...clamp, easing: EASE});
  const op = interpolate(frame, [0, 22, 400, 430], [0, 1, 1, 0.9], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        left: WIDTH / 2 - h / 2,
        top,
        width: h,
        height: h,
        borderRadius: h * 0.24,
        background: '#ffffff',
        opacity: op,
        boxShadow: `0 0 50px ${BLUE}88, 0 20px 40px rgba(0,0,0,0.6)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }}
    >
      <Img
        src={staticFile('logo.png')}
        style={{width: '78%', height: '78%', objectFit: 'contain', mixBlendMode: 'multiply', filter: 'brightness(1.1) contrast(1.25)'}}
      />
    </div>
  );
};

// ---------- Cœur SVG ----------
const Heart: React.FC<{size: number; color: string; filled?: boolean}> = ({size, color, filled = true}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path
      d="M12 21s-7.5-4.6-9.5-9.2C1 8.6 2.9 5 6.4 5c2 0 3.6 1.1 4.6 2.7C12 6.1 13.6 5 15.6 5 19.1 5 21 8.6 21.5 11.8 19.5 16.4 12 21 12 21z"
      fill={filled ? color : 'none'}
      stroke={color}
      strokeWidth={filled ? 0 : 2}
    />
  </svg>
);

// ---------- Mockup iPhone 3D ----------
const PhoneMockup: React.FC<{rx: number; ry: number; y: number; s: number; children: React.ReactNode}> = ({
  rx,
  ry,
  y,
  s,
  children,
}) => (
  <div
    style={{
      position: 'absolute',
      left: WIDTH / 2 - PHONE_W / 2,
      top: HEIGHT / 2 - PHONE_H / 2 + y,
      width: PHONE_W,
      height: PHONE_H,
      transform: `perspective(1800px) rotateX(${rx}deg) rotateY(${ry}deg) scale(${s})`,
    }}
  >
    <div
      style={{
        position: 'absolute',
        inset: -10,
        borderRadius: 86,
        boxShadow: `0 70px 120px rgba(0,0,0,0.85), 0 0 100px ${BLUE}66`,
      }}
    />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        borderRadius: 76,
        padding: 12,
        background: 'linear-gradient(145deg, #8a909b, #1b1e25 30%, #4a505b 55%, #15171c 80%, #6a707b)',
      }}
    >
      <div
        style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          borderRadius: 64,
          background: '#000',
          overflow: 'hidden',
          boxShadow: 'inset 0 0 0 2px #000',
        }}
      >
        {children}
        <div
          style={{
            position: 'absolute',
            top: 14,
            left: '50%',
            transform: 'translateX(-50%)',
            width: 124,
            height: 36,
            borderRadius: 20,
            background: '#000',
            zIndex: 50,
          }}
        />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            zIndex: 49,
            pointerEvents: 'none',
            background:
              'linear-gradient(115deg, rgba(255,255,255,0.14) 0%, rgba(255,255,255,0) 32%, rgba(255,255,255,0) 70%, rgba(255,255,255,0.06) 100%)',
          }}
        />
      </div>
    </div>
  </div>
);

const StatusBar: React.FC = () => (
  <div
    style={{
      position: 'absolute',
      top: 18,
      left: 36,
      right: 36,
      display: 'flex',
      justifyContent: 'space-between',
      color: WHITE,
      fontFamily: FONT,
      fontWeight: 700,
      fontSize: 20,
      zIndex: 40,
    }}
  >
    <span>9:41</span>
    <span style={{letterSpacing: 2}}>●●● ▮</span>
  </div>
);

// ---------- Écran 1 : profil ----------
const ProfileScreen: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const follow = interpolate(frame, [150, 160], [0, 1], clamp);
  const notif = sp(frame, fps, 172, 14);
  return (
    <div style={{position: 'absolute', inset: 0, background: '#000', color: WHITE, fontFamily: FONT, padding: '70px 24px 0'}}>
      <StatusBar />
      <div style={{display: 'flex', alignItems: 'center', gap: 18}}>
        <div
          style={{
            width: 96,
            height: 96,
            borderRadius: 48,
            padding: 4,
            background: `conic-gradient(${BLUE}, #b06bff, ${BLUE_SOFT}, ${BLUE})`,
            transform: `scale(${sp(frame, fps, 6, 12)})`,
          }}
        >
          <div style={{width: '100%', height: '100%', borderRadius: 44, background: 'linear-gradient(135deg, #1c2c4a, #0a0f1c)', border: '3px solid #000', boxSizing: 'border-box'}} />
        </div>
        <div style={{display: 'flex', flex: 1, justifyContent: 'space-around', textAlign: 'center'}}>
          {[['128', 'posts'], ['24,6 k', 'abonnés'], ['312', 'abonnements']].map(([n, l], i) => (
            <div key={l} style={{opacity: sp(frame, fps, 12 + i * 4, 20)}}>
              <div style={{fontWeight: 800, fontSize: 24}}>{n}</div>
              <div style={{color: GREY, fontSize: 15}}>{l}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={{marginTop: 14, fontWeight: 700, fontSize: 22}}>votre.marque</div>
      <div style={{color: GREY, fontSize: 17, marginTop: 4}}>Design · Tech · Nouveautés</div>

      <div style={{position: 'relative', display: 'flex', gap: 10, marginTop: 18}}>
        <div style={{position: 'relative', flex: 1, height: 46, borderRadius: 12, overflow: 'hidden'}}>
          <div style={{position: 'absolute', inset: 0, background: `linear-gradient(90deg, ${BLUE}, #5b7bff)`, opacity: 1 - follow}} />
          <div style={{position: 'absolute', inset: 0, background: '#262a33', opacity: follow}} />
          <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 18}}>
            {follow > 0.5 ? 'Abonné' : 'Suivre'}
          </div>
        </div>
        <div style={{flex: 1, height: 46, borderRadius: 12, background: '#262a33', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 18}}>
          Message
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 4, marginTop: 18}}>
        {Array.from({length: 9}, (_, i) => {
          const p = sp(frame, fps, 30 + i * 4, 14);
          const hue = [205, 265, 320, 25, 170, 215, 285, 15, 190][i];
          return (
            <div
              key={i}
              style={{
                aspectRatio: '1 / 1',
                borderRadius: 6,
                background: `linear-gradient(160deg, hsl(${hue} 80% 55%), hsl(${hue + 30} 70% 15%))`,
                opacity: p,
                transform: `scale(${0.6 + 0.4 * p})`,
              }}
            />
          );
        })}
      </div>

      <div
        style={{
          position: 'absolute',
          top: 150,
          left: 20,
          right: 20,
          padding: '14px 18px',
          borderRadius: 22,
          background: 'rgba(40,46,58,0.92)',
          display: 'flex',
          alignItems: 'center',
          gap: 14,
          transform: `translateY(${(1 - notif) * -160}px)`,
          opacity: notif,
          zIndex: 45,
        }}
      >
        <div style={{width: 42, height: 42, borderRadius: 21, background: BLUE, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800}}>V</div>
        <div style={{fontSize: 18, lineHeight: 1.3}}>
          <b>Léa</b> a commencé à te suivre
        </div>
      </div>
    </div>
  );
};

// ---------- Écran 2 : fil avec double-tap et cœurs ----------
const FeedScreen: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const liked = frame >= 252;
  const tap = frame - 250;
  const heartPop = sp(frame, fps, 250, 10);
  const fade = interpolate(tap, [10, 34], [1, 0], clamp);
  const count = frame >= 252 ? 1205 : 1204;
  return (
    <div style={{position: 'absolute', inset: 0, background: '#000', color: WHITE, fontFamily: FONT, padding: '70px 20px 0'}}>
      <StatusBar />
      <div style={{fontWeight: 800, fontSize: 30, marginBottom: 16}}>Fil</div>
      <div style={{display: 'flex', alignItems: 'center', gap: 12, opacity: sp(frame, fps, 200, 18)}}>
        <div style={{width: 44, height: 44, borderRadius: 22, background: `linear-gradient(135deg, ${BLUE}, #b06bff)`}} />
        <div style={{fontWeight: 700, fontSize: 19}}>votre.marque</div>
      </div>
      <div
        style={{
          position: 'relative',
          marginTop: 14,
          height: 400,
          borderRadius: 22,
          overflow: 'hidden',
          background: 'linear-gradient(180deg, #1e3d6b 0%, #0b1424 60%, #05070d 100%)',
          transform: `scale(${interpolate(sp(frame, fps, 205, 16), [0, 1], [0.92, 1])})`,
        }}
      >
        <div style={{position: 'absolute', left: 150, top: 60, width: 120, height: 120, borderRadius: 60, background: 'radial-gradient(circle, #ffd27a, #ff8a3d 70%, transparent 72%)', boxShadow: '0 0 60px #ff9a4d'}} />
        <svg viewBox="0 0 380 400" width="100%" height="100%" style={{position: 'absolute', inset: 0}}>
          <path d="M0 290 Q 90 230 180 270 T 380 250 L380 400 L0 400Z" fill="#183a63" />
          <path d="M0 330 Q 110 280 210 320 T 380 300 L380 400 L0 400Z" fill="#0f2a4d" />
        </svg>
        {/* Cœur qui explose au double-tap */}
        <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: frame >= 250 && frame < 290 ? fade : 0}}>
          <div style={{transform: `scale(${heartPop * 1.2})`, filter: `drop-shadow(0 0 24px ${RED})`}}>
            <Heart size={150} color={RED} />
          </div>
        </div>
        {Array.from({length: 18}, (_, i) => {
          const t = interpolate(tap, [0, 34], [0, 1], clamp);
          const ang = rnd(i) * Math.PI * 2;
          const dist = 80 + rnd(i + 20) * 160;
          const size = 14 + rnd(i + 40) * 22;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: '50%',
                top: '50%',
                transform: `translate(${Math.cos(ang) * dist * OUT(t)}px, ${Math.sin(ang) * dist * OUT(t) - 60 * t}px) rotate(${ang * 60}deg)`,
                opacity: frame >= 250 && frame < 290 ? 1 - t : 0,
              }}
            >
              <Heart size={size} color={i % 2 ? RED : '#ff7aa2'} />
            </div>
          );
        })}
      </div>
      <div style={{display: 'flex', gap: 22, marginTop: 16, alignItems: 'center'}}>
        <div style={{transform: `scale(${liked ? 1 + 0.25 * sp(frame, fps, 252, 8) : 1})`}}>
          <Heart size={34} color={liked ? RED : WHITE} filled={liked} />
        </div>
        <Heart size={32} color={WHITE} filled={false} />
        <div style={{width: 30, height: 30, borderRadius: 4, border: `3px solid ${WHITE}`, boxSizing: 'border-box'}} />
      </div>
      <div style={{marginTop: 12, fontWeight: 700, fontSize: 19}}>{count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '\u202f')} J'aime</div>
      <div style={{marginTop: 6, fontSize: 18, color: '#d7dbe5', lineHeight: 1.35}}>
        <b>votre.marque</b> Le nouvel écran, en mouvement.
      </div>
    </div>
  );
};

// ---------- Écran 3 : messages ----------
const ChatScreen: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const bubbles = [
    {t: 306, side: 'left', text: 'Tu es dispo pour le lancement ?'},
    {t: 318, side: 'right', text: 'Oui, on part sur la sortie !'},
    {t: 332, side: 'left', text: 'Parfait, on envoie tout ce soir.'},
  ];
  const notif = sp(frame, fps, 352, 14);
  return (
    <div style={{position: 'absolute', inset: 0, background: '#000', color: WHITE, fontFamily: FONT, padding: '70px 20px 0'}}>
      <StatusBar />
      <div style={{fontWeight: 800, fontSize: 26, marginBottom: 18}}>Léa</div>
      {bubbles.map((b, i) => {
        const p = sp(frame, fps, b.t, 14);
        const isRight = b.side === 'right';
        return (
          <div
            key={i}
            style={{
              display: 'flex',
              justifyContent: isRight ? 'flex-end' : 'flex-start',
              marginBottom: 14,
              opacity: p,
              transform: `translateY(${(1 - p) * 30}px) scale(${0.9 + 0.1 * p})`,
            }}
          >
            <div
              style={{
                maxWidth: '76%',
                padding: '14px 18px',
                borderRadius: 24,
                fontSize: 19,
                background: isRight ? `linear-gradient(135deg, ${BLUE}, #3b6cff)` : '#262a33',
                boxShadow: isRight ? `0 0 24px ${BLUE}66` : 'none',
              }}
            >
              {b.text}
            </div>
          </div>
        );
      })}
      <div style={{display: 'flex', gap: 6, paddingLeft: 10, opacity: sp(frame, fps, 326, 14)}}>
        {[0, 1, 2].map((i) => (
          <div key={i} style={{width: 9, height: 9, borderRadius: 5, background: GREY, transform: `translateY(${Math.sin((frame + i * 5) / 3) * 4}px)`}} />
        ))}
      </div>
      <div
        style={{
          position: 'absolute',
          top: 150,
          left: 20,
          right: 20,
          padding: '14px 18px',
          borderRadius: 22,
          background: 'rgba(40,46,58,0.92)',
          fontSize: 18,
          transform: `translateY(${(1 - notif) * -160}px)`,
          opacity: notif,
          zIndex: 45,
        }}
      >
        <b>Nouveau message</b> · Léa
      </div>
    </div>
  );
};

// ---------- Écrans empilés avec slide ----------
const Screens: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
  const xProfile = interpolate(frame, [225, 255], [0, -PHONE_W + 24], {...clamp, easing: OUT});
  const xFeedIn = interpolate(frame, [225, 255], [PHONE_W, 0], {...clamp, easing: OUT});
  const xFeedOut = interpolate(frame, [295, 325], [0, -PHONE_W], {...clamp, easing: OUT});
  const xChatIn = interpolate(frame, [295, 325], [PHONE_W, 0], {...clamp, easing: OUT});
  const inner = PHONE_W - 24;
  return (
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
      <div style={{position: 'absolute', inset: 0, transform: `translateX(${xProfile}px)`}}>
        <div style={{position: 'absolute', inset: 0, width: inner}}>
          <ProfileScreen frame={frame} fps={fps} />
        </div>
      </div>
      <div style={{position: 'absolute', inset: 0, transform: `translateX(${frame < 295 ? xFeedIn : xFeedOut}px)`}}>
        <FeedScreen frame={frame} fps={fps} />
      </div>
      <div style={{position: 'absolute', inset: 0, transform: `translateX(${xChatIn}px)`}}>
        <ChatScreen frame={frame} fps={fps} />
      </div>
    </div>
  );
};

// ---------- Scène complète ----------
export const IphoneAd: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Caméra : entrée 3D, panoramique, puis retour de face
  const enter = interpolate(frame, [70, 150], [0, 1], {...clamp, easing: OUT});
  const rx = interpolate(enter, [0, 1], [38, 10]) + interpolate(frame, [260, 330], [0, 6], {...clamp, easing: EASE}) - interpolate(frame, [330, 400], [0, 6], {...clamp, easing: EASE});
  const ry =
    interpolate(enter, [0, 1], [-38, -12]) +
    interpolate(frame, [110, 200], [0, 24], {...clamp, easing: EASE}) +
    interpolate(frame, [200, 260], [0, -18], {...clamp, easing: EASE}) +
    interpolate(frame, [260, 340], [0, 26], {...clamp, easing: EASE}) +
    interpolate(frame, [340, 400], [0, -26], {...clamp, easing: EASE});
  const y = interpolate(frame, [70, 150], [340, 0], {...clamp, easing: OUT}) + interpolate(frame, [380, 420], [0, -70], {...clamp, easing: EASE});
  const s = interpolate(enter, [0, 1], [0.85, 1]) * interpolate(frame, [380, 420], [1, 0.94], {...clamp, easing: EASE});

  // Titre du haut (mots qui apparaissent) et bas (CTA)
  const ctaP = sp(frame, fps, 392, 12);
  const sub = interpolate(frame, [400, 425], [0, 1], clamp);

  return (
    <AbsoluteFill>
      <Background frame={frame} />

      {/* Titres animés */}
      {frame >= 92 && frame < 200 && <WordReveal text="Ton réseau, en direct." start={92} size={86} top={300} />}
      {frame >= 296 && frame < 392 && <WordReveal text="Connecté à tout." start={296} size={94} top={300} />}

      {frame >= 60 && (
        <PhoneMockup rx={rx} ry={ry} y={y} s={s}>
          <Screens frame={frame} fps={fps} />
        </PhoneMockup>
      )}

      <LogoMark frame={frame} />

      {/* Bas : offre et CTA */}
      <div
        style={{
          position: 'absolute',
          bottom: 250,
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 22,
          fontFamily: FONT,
        }}
      >
        <div style={{color: BLUE_SOFT, fontSize: 30, letterSpacing: 6, opacity: sub}}>NOUVEAU · LANCEMENT</div>
        <div
          style={{
            padding: '34px 80px',
            borderRadius: 999,
            border: `4px solid ${BLUE}`,
            background: `${BLUE}22`,
            color: WHITE,
            fontSize: 52,
            fontWeight: 700,
            opacity: ctaP,
            transform: `translateY(${(1 - ctaP) * 80}px) scale(${0.9 + 0.1 * ctaP})`,
            boxShadow: `0 0 40px ${BLUE}88`,
          }}
        >
          Découvrir l'iPhone →
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Thème global : format, palette, timeline et zones de sécurité TikTok / Reels.
export const W = 1080;
export const H = 1920;
export const FPS = 30;
export const DURATION = 360; // 12 s

export const C = {
  bg: '#0B0B0F',
  product: '#E8E8EC',
  accent: '#7DD3FC',
  text: '#FFFFFF',
  muted: 'rgba(255,255,255,0.6)',
};

// Débuts des scènes (en frames)
export const T = {hook: 0, hero: 60, features: 150, end: 270};
// Coupes (flash + impact audio)
export const CUTS = [60, 150, 270];

// Zones de sécurité (px) : haut, bas, droite
export const SAFE = {top: 200, bottom: 400, right: 150, left: 80};

export const FONT = 'Inter, "Helvetica Neue", Arial, sans-serif';

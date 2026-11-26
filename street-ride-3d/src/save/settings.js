import { load, save } from './storage.js';

// Codes physiques (event.code) : indépendants de la disposition. Sur AZERTY, 'KeyW' = touche Z, 'KeyA' = Q.
export const DEFAULT_BINDINGS = {
  forward: 'KeyW', back: 'KeyS', left: 'KeyA', right: 'KeyD',
  push: 'Space', brake: 'KeyS', flickUp: 'ArrowUp', flickDown: 'ArrowDown', flickLeft: 'ArrowLeft', flickRight: 'ArrowRight',
  interact: 'KeyE', reset: 'KeyR', camera: 'KeyC', run: 'ShiftLeft', help: 'KeyH',
};
export const ACTION_LABELS = {
  forward: 'Avancer / équilibre avant', back: 'Reculer / équilibre arrière', left: 'Tourner à gauche', right: 'Tourner à droite',
  push: 'Pousser (skate) / Sauter (à pied)', brake: 'Freiner', flickUp: 'Stick droit haut', flickDown: 'Stick droit bas',
  flickLeft: 'Stick droit gauche', flickRight: 'Stick droit droite', interact: 'Monter / descendre du skate',
  reset: 'Réinitialiser le personnage', camera: 'Changer de caméra', run: 'Courir (à pied)', help: 'Afficher l’aide',
};
export const QUALITY = {
  faible: { shadows: false, shadowMap: 512, pixelRatio: 0.7, viewDist: 120 },
  moyen:  { shadows: true, shadowMap: 1024, pixelRatio: 0.9, viewDist: 200 },
  eleve:  { shadows: true, shadowMap: 2048, pixelRatio: 1, viewDist: 300 },
  ultra:  { shadows: true, shadowMap: 4096, pixelRatio: 2, viewDist: 450 },
};
const DEFAULTS = { quality: 'eleve', resolutionScale: 1, viewDist: 300, shadows: true, mouseSens: 1, invertY: false, bindings: { ...DEFAULT_BINDINGS } };

export const settings = load('settings', DEFAULTS);
settings.bindings = { ...DEFAULT_BINDINGS, ...settings.bindings };
export function saveSettings() { save('settings', settings); }

// Libellés AZERTY pour l'affichage (fallback si l'API Keyboard Layout n'existe pas)
const AZERTY = { KeyW: 'Z', KeyA: 'Q', KeyQ: 'A', KeyZ: 'W', KeyM: ',', Semicolon: 'M', Space: 'Espace', ShiftLeft: 'Maj gauche', ShiftRight: 'Maj droite',
  ArrowUp: '↑', ArrowDown: '↓', ArrowLeft: '←', ArrowRight: '→', Escape: 'Échap', ControlLeft: 'Ctrl', Tab: 'Tab', Enter: 'Entrée' };
let layoutMap = null;
navigator.keyboard?.getLayoutMap?.().then(m => { layoutMap = m; }).catch(() => {});
export function keyLabel(code) {
  if (AZERTY[code] && !layoutMap?.get(code)) return AZERTY[code];
  const l = layoutMap?.get(code); if (l) return l.toUpperCase();
  return code.replace(/^Key|^Digit/, '');
}

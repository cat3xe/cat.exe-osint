// Reconnaissance de gestes "Flick-It" sur le stick droit (module pur, sans Three.js -> testable).
// Entrée : vecteur (x, y) avec y>0 = haut. Sortie : nom de trick ou null.
export const ZONES = ['R', 'UR', 'U', 'UL', 'L', 'DL', 'D', 'DR'];

export function zoneOf(x, y, dead = 0.55) {
  if (Math.hypot(x, y) < dead) return 'C';
  const a = Math.atan2(y, x); // 0 = droite
  const i = ((Math.round(a / (Math.PI / 4)) % 8) + 8) % 8;
  return ZONES[i];
}

const isUp = z => z === 'U' || z === 'UL' || z === 'UR';
const isDown = z => z === 'D' || z === 'DL' || z === 'DR';

export class GestureRecognizer {
  constructor(windowMs = 380) { this.windowMs = windowMs; this.hist = []; this.last = 'C'; }
  reset() { this.hist = []; this.last = 'C'; }
  // Renvoie un trick quand un geste est terminé.
  update(x, y, now) {
    const z = zoneOf(x, y);
    if (z === this.last) return null;
    this.last = z;
    this.hist.push({ z, t: now });
    this.hist = this.hist.filter(h => now - h.t <= this.windowMs);
    return this.match(now);
  }
  match() {
    const seq = this.hist.map(h => h.z).filter(z => z !== 'C');
    const raw = this.hist.map(h => h.z);
    if (seq.length < 2) return null;
    const lastZ = raw[raw.length - 1];
    // Point de départ : premier D (regular) ou U (nollie) dans la fenêtre
    const di = seq.findIndex(isDown), ui = seq.findIndex(isUp);
    const end = seq[seq.length - 1];
    // Zones intermédiaires : comptées seulement si le stick y reste >= 80 ms (évite les transitions parasites au clavier)
    const nc = this.hist.filter(h => h.z !== 'C');
    const mid = nc.slice(1, -1).filter((h, i) => (nc[i + 2].t - h.t) >= 80).map(h => h.z);
    const hasL = mid.includes('L') || mid.includes('DL'), hasR = mid.includes('R') || mid.includes('DR');
    // Pop regular : bas -> haut
    if (di === 0 && isUp(end)) {
      this.reset();
      if (end === 'UL') return hasL ? 'varial_kickflip' : 'kickflip';
      if (end === 'UR') return hasR ? 'varial_heelflip' : 'heelflip';
      if (hasL) return 'pop_shove_bs';
      if (hasR) return 'pop_shove_fs';
      return 'ollie';
    }
    // Nollie : haut -> bas
    if (ui === 0 && isDown(end)) {
      this.reset();
      if (end === 'DL') return 'nollie_kickflip';
      if (end === 'DR') return 'nollie_heelflip';
      return 'nollie';
    }
    // Shove-it sans pop : bas -> côté puis retour au centre
    if (lastZ === 'C' && di === 0 && seq.length >= 2) {
      const e = seq[seq.length - 1];
      if (e === 'L') { this.reset(); return 'shove_bs'; }
      if (e === 'R') { this.reset(); return 'shove_fs'; }
    }
    return null;
  }
}

// Définition des tricks skateboard : pop (impulsion), flip (tours sur l'axe long), shove (rotation plateau)
export const SKATE_TRICKS = {
  ollie:            { name: 'Ollie',            pop: 5.4, flip: 0,  shove: 0,  pts: 100 },
  nollie:           { name: 'Nollie',           pop: 5.0, flip: 0,  shove: 0,  pts: 150 },
  kickflip:         { name: 'Kickflip',         pop: 5.4, flip: 1,  shove: 0,  pts: 300 },
  heelflip:         { name: 'Heelflip',         pop: 5.4, flip: -1, shove: 0,  pts: 300 },
  nollie_kickflip:  { name: 'Nollie Kickflip',  pop: 5.0, flip: 1,  shove: 0,  pts: 400 },
  nollie_heelflip:  { name: 'Nollie Heelflip',  pop: 5.0, flip: -1, shove: 0,  pts: 400 },
  shove_bs:         { name: 'BS Shove-it',      pop: 2.6, flip: 0,  shove: 1,  pts: 150 },
  shove_fs:         { name: 'FS Shove-it',      pop: 2.6, flip: 0,  shove: -1, pts: 150 },
  pop_shove_bs:     { name: 'BS Pop Shove-it',  pop: 5.2, flip: 0,  shove: 1,  pts: 250 },
  pop_shove_fs:     { name: 'FS Pop Shove-it',  pop: 5.2, flip: 0,  shove: -1, pts: 250 },
  varial_kickflip:  { name: 'Varial Kickflip',  pop: 5.4, flip: 1,  shove: 1,  pts: 500 },
  varial_heelflip:  { name: 'Varial Heelflip',  pop: 5.4, flip: -1, shove: -1, pts: 500 },
};

import { load, save } from '../save/storage.js';
// Système de score "ligne" : les tricks s'enchaînent, le multiplicateur = nombre de tricks distincts.
// La ligne est encaissée après 1,3 s de roulage sans trick ; une chute fait perdre la ligne.
export class ScoreSystem {
  constructor() {
    this.stats = load('stats', { best: 0, bestLine: 0, total: 0, bails: 0, tricks: 0 });
    this.reset(); this.session = 0;
  }
  reset() { this.line = 0; this.names = []; this.distinct = new Set(); this.idle = 0; this.sustained = null; this.active = false; }
  get mult() { return Math.max(1, this.distinct.size); }
  trick({ name, pts, sustained }) {
    this.active = true; this.idle = 0;
    if (sustained) { this.sustained = name; }
    this.names.push(name); this.distinct.add(name.replace(/^(Switch |FS \d+ |BS \d+ )+/, '')); this.line += pts; this.stats.tricks++;
  }
  sustain(name, pts) { this.line += pts; this.idle = 0; }
  sustainEnd() { this.sustained = null; }
  bail() { this.stats.bails++; this.reset(); save('stats', this.stats); }
  update(dt, grounded) {
    if (!this.active) return null;
    if (grounded && !this.sustained) this.idle += dt; else this.idle = 0;
    if (this.idle > 1.3) {
      const banked = Math.round(this.line * this.mult); this.session += banked;
      this.stats.total += banked; this.stats.bestLine = Math.max(this.stats.bestLine, banked); this.stats.best = Math.max(this.stats.best, this.session);
      save('stats', this.stats); this.reset(); return banked;
    }
    return null;
  }
}

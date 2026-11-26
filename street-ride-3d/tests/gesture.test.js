import { test } from 'node:test';
import assert from 'node:assert/strict';
import { GestureRecognizer, zoneOf } from '../src/core/gesture.js';

// Simule un mouvement de stick : liste de [x, y] espacés de 30 ms
function run(path, start = 0) {
  const g = new GestureRecognizer(); let out = null, t = start;
  for (const [x, y] of path) { const r = g.update(x, y, t); if (r) out = r; t += 100; }
  return out;
}
test('zones', () => { assert.equal(zoneOf(0, 0), 'C'); assert.equal(zoneOf(0, -1), 'D'); assert.equal(zoneOf(-0.7, 0.7), 'UL'); });
test('ollie : bas puis haut', () => assert.equal(run([[0, 0], [0, -1], [0, 0], [0, 1]]), 'ollie'));
test('nollie : haut puis bas', () => assert.equal(run([[0, 0], [0, 1], [0, 0], [0, -1]]), 'nollie'));
test('kickflip : bas puis haut-gauche', () => assert.equal(run([[0, -1], [-0.7, 0.7]]), 'kickflip'));
test('heelflip : bas puis haut-droite', () => assert.equal(run([[0, -1], [0.7, 0.7]]), 'heelflip'));
test('pop shove-it BS', () => assert.equal(run([[0, -1], [-1, 0], [0, 1]]), 'pop_shove_bs'));
test('varial kickflip', () => assert.equal(run([[0, -1], [-1, 0], [-0.7, 0.7]]), 'varial_kickflip'));
test('shove-it sans pop', () => assert.equal(run([[0, -1], [-1, 0], [0, 0]]), 'shove_bs'));
test('nollie heelflip', () => assert.equal(run([[0, 1], [0.7, -0.7]]), 'nollie_heelflip'));
test('geste trop lent = rien', () => {
  const g = new GestureRecognizer(); g.update(0, -1, 0); g.update(0, 0, 200); assert.equal(g.update(0, 1, 900), null);
});
test('manual (mi-course) ne déclenche pas de trick', () => assert.equal(run([[0, -0.4], [0, -0.3], [0, 0]]), null));
test('kickflip clavier : transition L très brève ignorée', () => {
  const g = new GestureRecognizer(); g.update(0, -1, 0); g.update(-0.7, -0.7, 40); g.update(-1, 0, 41);
  assert.equal(g.update(-0.7, 0.7, 42), 'kickflip');
});

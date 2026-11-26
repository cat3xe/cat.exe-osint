// Test manette : simule une manette standard via navigator.getGamepads.
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const browser = await chromium.launch(); const page = await browser.newPage({ viewport: { width: 400, height: 225 } });
await page.addInitScript(() => {
  localStorage.setItem('streetride3d:settings', JSON.stringify({ quality: 'faible', shadows: false, resolutionScale: 0.5, viewDist: 120 }));
  window.__pad = { id: 'Manette test (standard)', connected: true, mapping: 'standard', axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0 })) };
  navigator.getGamepads = () => [window.__pad];
});
const errors = []; page.on('pageerror', e => errors.push(e.message));
await page.goto(process.env.URL || 'http://localhost:4173/'); await page.waitForFunction(() => window.__game);
let ok = 0, ko = 0; const check = (n, c, i = '') => { console.log((c ? '✔ ' : '✘ ') + n + (i ? '  ' + i : '')); c ? ok++ : ko++; };
const btn = (i, v) => page.evaluate(([i, v]) => { __pad.buttons[i] = { pressed: v, value: v ? 1 : 0 }; }, [i, v]);
const press = async i => { await btn(i, true); await page.waitForTimeout(700); await btn(i, false); await page.waitForTimeout(700); };
const axes = a => page.evaluate(a => { __pad.axes = a; }, a);
const wait = async ms => { const t0 = await page.evaluate(() => __game.simTime); await page.waitForFunction(([t0, d]) => __game.paused || __game.simTime >= t0 + d, [t0, ms / 1000], { timeout: 60000 }); };
const st = () => page.evaluate(() => { const b = __game.player.board; return { state: b.state, speed: b.speed, yaw: b.yaw, mode: __game.player.mode, names: __game.score.names.slice(), session: __game.score.session, paused: __game.paused, screen: __game.menu.screen }; });
// Menu principal : A sur "Jouer"
await page.waitForTimeout(300); await press(0);
let s = await st(); check('Menu : A lance la partie', !s.paused, JSON.stringify(s));
// Pousser avec A
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); });
for (let i = 0; i < 3; i++) await press(0);
s = await st(); check('A pousse le skate', s.speed > 3, 'vitesse=' + s.speed.toFixed(2));
// Tourner au stick gauche
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); b.speed = 2; }); const y0 = Math.PI; await axes([1, 0, 0, 0]); await wait(400); await axes([0, 0, 0, 0]);
s = await st(); check('Stick gauche tourne', Math.abs(s.yaw - y0) > 0.3, 'Δ=' + (s.yaw - y0).toFixed(2));
// Ollie au stick droit : bas puis haut (échantillonné en continu)
for (let k = 0; k < 3; k++) {
  await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); b.speed = 5; __game.score.reset(); });
  await axes([0, 0, 0, 1]); await wait(25); await axes([0, 0, 0, -1]); await wait(25); await axes([0, 0, 0, 0]);
  await wait(1100); s = await st(); if (s.names.includes('Ollie')) break;
} check('Ollie au stick droit', s.names.includes('Ollie') || s.session > 0, JSON.stringify(s.names));
// Kickflip au stick droit : bas puis haut-gauche
for (let k = 0; k < 3; k++) {
  await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); b.speed = 5; __game.score.reset(); });
  await axes([0, 0, 0, 1]); await wait(25); await axes([0, 0, -0.7, -0.7]); await wait(25); await axes([0, 0, 0, 0]);
  await wait(1100); s = await st(); if (s.names.some(n => n.includes('Kickflip'))) break;
} check('Kickflip au stick droit', s.names.some(n => n.includes('Kickflip')), JSON.stringify(s.names));
// X : descendre / remonter
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); });
await press(2); s = await st(); check('X descend du skate', s.mode === 'walk');
const z0 = await page.evaluate(() => __game.player.walk.pos.z);
await axes([0, -1, 0, 0]); await wait(600); await axes([0, 0, 0, 0]);
const z1 = await page.evaluate(() => __game.player.walk.pos.z); check('Stick gauche fait marcher', Math.abs(z1 - z0) > 0.5, 'Δz=' + (z1 - z0).toFixed(2));
const cy = await page.evaluate(() => __game.cam.yaw); await axes([0, 0, 1, 0]); await wait(400); await axes([0, 0, 0, 0]);
check('Stick droit tourne la caméra à pied', Math.abs(await page.evaluate(() => __game.cam.yaw) - cy) > 0.3);
await press(2); s = await st(); check('X remonte sur le skate', s.mode === 'board');
// Start : pause, navigation, B : reprendre
await press(9); s = await st(); check('Start ouvre la pause', s.paused && s.screen === 'pause');
await press(13); await press(13); await press(13);
const focused = await page.evaluate(() => document.activeElement.id); check('D-pad déplace la sélection', focused === 'p-settings', focused);
await press(0); s = await st(); check('A ouvre les paramètres', s.screen === 'settingsScreen');
await page.evaluate(() => document.getElementById('s-q').focus()); await press(15);
const q = await page.evaluate(() => JSON.parse(localStorage.getItem('streetride3d:settings')).quality); check('D-pad droite change la qualité', q === 'moyen', q);
await press(1); s = await st(); check('B revient à la pause', s.screen === 'pause');
await press(1); s = await st(); check('B reprend la partie', !s.paused);
await press(9); await press(9); s = await st(); check('Start reprend la partie', !s.paused);
check('Aucune erreur JavaScript', errors.length === 0, errors.join(' | '));
console.log(`\n${ok} réussis, ${ko} échoués`); await browser.close(); process.exit(ko ? 1 : 0);

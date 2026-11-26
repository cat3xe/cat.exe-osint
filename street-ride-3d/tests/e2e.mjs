// Test de bout en bout dans un vrai navigateur : lance le jeu et vérifie les mécaniques.
// Usage : npm run build && npx vite preview --port 4173 & node tests/e2e.mjs
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const URL = process.env.URL || 'http://localhost:4173/';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 400, height: 225 } });
await page.addInitScript(() => { if (!localStorage.getItem('streetride3d:settings')) localStorage.setItem('streetride3d:settings', JSON.stringify({ quality: 'faible', shadows: false, resolutionScale: 0.5, viewDist: 120 })); });
const errors = []; page.on('pageerror', e => errors.push(e.message)); page.on('console', m => m.type() === 'error' && errors.push(m.text()));
await page.goto(URL); await page.waitForFunction(() => window.__game);
let ok = 0, ko = 0; const check = (name, cond, info = '') => { console.log((cond ? '✔ ' : '✘ ') + name + (info ? '  ' + info : '')); cond ? ok++ : ko++; };
const st = () => page.evaluate(() => { const b = __game.player.board; return { state: b.state, speed: b.speed, y: b.pos.y, z: b.pos.z, x: b.pos.x, sw: b.switch, mode: __game.player.mode, line: __game.score.line, names: __game.score.names.slice(), session: __game.score.session }; });
// Attente en temps de SIMULATION (le navigateur de test logiciel est lent)
const wait = async ms => { const t0 = await page.evaluate(() => __game.simTime); await page.waitForFunction(([t0, d]) => __game.paused || __game.simTime >= t0 + d, [t0, ms / 1000], { timeout: 60000 }); };
await page.click('#m-play'); await page.waitForTimeout(300);
console.log('FPS approx :', await page.evaluate(() => new Promise(r => { const t0 = __game.simTime, p0 = performance.now(); setTimeout(() => r(((__game.simTime - t0) / ((performance.now() - p0) / 1000)).toFixed(2) + ' s simulées / s réelle'), 1000); })));
check('Partie lancée', await page.evaluate(() => !__game.paused));
// Pousser
for (let i = 0; i < 3; i++) { await page.keyboard.down('Space'); await wait(120); await page.keyboard.up('Space'); await wait(500); }
let s = await st(); check('Pousser fait avancer', s.speed > 4, `vitesse=${s.speed.toFixed(2)}`);
// Ollie : flèche bas puis haut
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); b.speed = 5; }); await wait(100);
// 1) le clavier produit bien des échantillons horodatés (bas, centre, haut)
await page.evaluate(() => { __game.paused = true; __game.input.flickQueue.length = 0; });
await page.keyboard.down('ArrowDown'); await page.keyboard.up('ArrowDown'); await page.keyboard.down('ArrowUp'); await page.keyboard.up('ArrowUp');
const q = await page.evaluate(() => __game.input.flickQueue.map(e => [e.x, e.y]));
check('Clavier : flèches -> échantillons stick droit', JSON.stringify(q) === '[[0,-1],[0,0],[0,1],[0,0]]', JSON.stringify(q));
await page.evaluate(() => { __game.input.flickQueue.length = 0; __game.paused = false; });
// 2) geste injecté avec un rythme humain (60 ms entre échantillons)
const flick = pts => page.evaluate(pts => { const t = performance.now(); __game.input.flickQueue.push(...pts.map(([x, y], i) => ({ x, y, t: t + i * 60 }))); }, pts);
await flick([[0, -1], [0, 0], [0, 1], [0, 0]]); await wait(30);
s = await st();
check('Ollie : décollage', s.state === 'air', s.state);
await page.evaluate(() => { window.__maxY = 0; const f = () => { __maxY = Math.max(__maxY, __game.player.board.pos.y); if (__game.player.board.state === 'air') requestAnimationFrame(f); }; requestAnimationFrame(f); });
await wait(1000); const maxY = await page.evaluate(() => __maxY);
s = await st(); check('Ollie : hauteur atteinte', maxY > 0.6, `y max=${maxY.toFixed(2)}`);
check('Ollie : réception propre et comptée', s.state === 'ride' && (s.names.includes('Ollie') || s.session > 0), JSON.stringify(s.names));
// Kickflip
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); b.speed = 5; });
await wait(100);
await flick([[0, -1], [-0.7, 0.7], [0, 0]]); await wait(1200);
s = await st(); check('Kickflip réussi', s.names.some(n => n.includes('Kickflip')) && s.state === 'ride', JSON.stringify(s.names) + ' ' + s.state);
// Encaissement de la ligne
await wait(1800); s = await st(); check('Ligne encaissée dans le score', s.session > 0, 'session=' + s.session);
// Grind : positionne le rider au-dessus du rail (x=4, z de -4 à -16, h=0.45) en mouvement le long du rail
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(4, 0.9, -5), Math.PI); b.state = 'air'; b.airTime = 0.3; b.vel.set(0, -1, -5); });
await wait(250); s = await st(); check('Grind accroché sur le rail', s.state === 'grind', s.state + ' ' + JSON.stringify(s.names.slice(-2)));
let tMax = 0; for (let i = 0; i < 70; i++) { await wait(100); const q = await page.evaluate(() => { const b = __game.player.board; if (b.grind) b.balance *= 0.5; return b.grind?.t ?? -1; }); tMax = Math.max(tMax, q); if (q < 0) break; }
s = await st(); check('Grind : glisse le long du rail puis en sort', s.state !== 'grind' && s.state !== 'bail' && tMax > 0.8, s.state + ' t max=' + tMax.toFixed(2));
// Chute forcée : kickflip lancé trop près du sol -> doit chuter
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); b.speed = 3; b.onGesture('kickflip'); b.vel.y = 1.2; });
await wait(400); s = await st(); check('Chute si flip pas terminé', s.state === 'bail', s.state);
await wait(2500); s = await st(); check('Réapparition après chute', s.state === 'ride', s.state);
// Mur : rouler vite vers le mur du fond
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(20, 0, -48), Math.PI); b.speed = 4; });
await wait(1500); s = await st(); check('Collision mur (ne traverse pas)', s.z > -51.8, 'z=' + s.z.toFixed(2));
// Rampe : rouler sur le kicker (0,-12) -> doit décoller
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(0, 0, -6), Math.PI); b.speed = 8; });
let air = false; for (let i = 0; i < 30; i++) { await wait(50); if ((await st()).state === 'air') air = true; }
check('Le kicker fait décoller', air);
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); b.speed = 4; }); await wait(100);
await flick([[0, -1], [-1, 0], [0, 1], [0, 0]]); await wait(1200); s = await st();
check('Pop shove-it réussi', s.names.some(n => n.includes('Pop Shove-it')) && s.state === 'ride', JSON.stringify(s.names));
// Descendre du skate et marcher
await page.evaluate(() => { const b = __game.player.board; b.reset(new b.pos.constructor(-20, 0, 30), Math.PI); });
await page.keyboard.press('KeyE'); await wait(200); s = await st(); check('Descendre du skate (E)', s.mode === 'walk');
await page.keyboard.down('KeyW'); await wait(800); await page.keyboard.up('KeyW');
const wp = await page.evaluate(() => __game.player.walk.pos.z); check('Marche avec Z (KeyW)', wp < 29.5, 'z=' + wp.toFixed(2));
await page.keyboard.press('KeyE'); await wait(200); s = await st(); check('Remonter sur le skate', s.mode === 'board');
// Menus
await page.keyboard.press('Escape'); await page.waitForTimeout(200); check('Échap ouvre la pause', await page.evaluate(() => __game.paused && __game.menu.screen === 'pause'));
await page.click('#p-settings'); await page.selectOption('#s-q', 'faible'); await page.waitForTimeout(200);
await page.selectOption('#s-q', 'moyen'); await page.waitForTimeout(100); check('Qualité moyen réactive les ombres', await page.evaluate(() => __game.renderer.shadowMap.enabled)); await page.selectOption('#s-q', 'faible'); await page.waitForTimeout(100);
check('Réglage qualité appliqué + sauvegardé', await page.evaluate(() => !__game.renderer.shadowMap.enabled && JSON.parse(localStorage.getItem('streetride3d:settings')).quality === 'faible'));
await page.click('#b'); await page.click('#p-resume'); await wait(300);
await page.screenshot({ path: process.env.SHOT || 'tests/screenshot.png' });
check('Aucune erreur JavaScript', errors.length === 0, errors.join(' | '));
console.log(`\n${ok} réussis, ${ko} échoués`); await browser.close(); process.exit(ko ? 1 : 0);

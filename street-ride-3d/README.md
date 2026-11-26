# STREET RIDE 3D

Jeu 3D de skateboard et trottinette freestyle en monde ouvert. **État actuel : prototype jouable, phases 1 et 2 (skateboard).**

## Lancer
- Windows : double-clic sur `LANCER_JEU.bat` (Node.js 18+ requis).
- Sinon : `npm install` puis `npm run dev`, ouvrir http://localhost:5173
- Tests : `npm test` (gestes Flick-It) · `npm run build && npx vite preview --port 4173` puis `node tests/e2e.mjs` (22 vérifications dans un vrai navigateur) · `node tests/gamepad.mjs` (17 vérifications avec manette simulée).

## Choix technologique
| Option | Pour | Contre |
|---|---|---|
| **Unreal Engine 5** | Graphismes au plus haut niveau, réseau intégré | Lourd, C++, impossible à piloter dans cet environnement cloud (pas de GPU, pas d'éditeur) |
| **Unity** | Très bon pour les jeux de glisse, gros écosystème | Éditeur graphique obligatoire, licence |
| **Godot 4** | Libre, léger, export Windows simple | Rendu moins avancé qu'UE5 |
| **Three.js (choisi)** | Codable et **testable automatiquement** ici, itérations rapides, multijoueur web natif (WebSocket), exécutable Windows via Electron/Tauri | Limites ci-dessous |

**Limites assumées de Three.js** : pas d'éditeur de niveaux ni d'outils d'animation intégrés ; pas de moteur physique complet (physique sur mesure ici, Rapier prévu pour les objets dynamiques) ; rendu « réaliste » plafonné par WebGL (pas de Lumen/Nanite) ; streaming d'un très grand monde à construire nous-mêmes. La logique de jeu étant isolée en modules sans dépendance au rendu (ex. `core/gesture.js`), un portage vers Godot ou Unity reste possible si l'ambition graphique l'exige.

## Architecture (`src/`)
| Module | Rôle |
|---|---|
| `core/input.js` | Clavier AZERTY (codes physiques), souris, manette ; touches reconfigurables |
| `core/gesture.js` | Reconnaissance Flick-It du stick droit (pur, testé) + table des tricks skate |
| `core/score.js` | Lignes, multiplicateur, encaissement, statistiques |
| `world/` | Skatepark de test, textures procédurales originales, requêtes de collision |
| `vehicles/skateboard*.js` | Modèle 3D + physique et tricks du skate (indépendant de la future trottinette) |
| `player/` | Personnage à squelette, poses/animations procédurales, mode à pied |
| `camera/` | Caméras suiveuse / basse (fisheye) / orbitale |
| `ui/` | Menus et HUD fonctionnels |
| `save/` | Sauvegarde locale avec copie de secours, paramètres |

Aucune clé ni mot de passe dans le client. Toutes les ressources sont générées par le code (aucun fichier sous licence).

## Manette
Compatible manettes Xbox / PlayStation / génériques reconnues par Windows (disposition standard). Jeu ET menus entièrement jouables à la manette, vibrations sur réception/grind/chute, détection branchement/débranchement (pause auto). Détail des boutons : menu Commandes.

## Ce qui fonctionne (testé)
Pousser, freiner, tourner · ollie, nollie, kickflip, heelflip, shove-it, pop shove-it, varials, nollie flips · rotations 180/360 en l'air · stance switch/fakie · manual et nose manual avec équilibre · 50-50, 5-0, nosegrind, crooked, boardslide sur rails/ledges/coping avec équilibre · réceptions validées (flip fini, alignement, rotation) · chutes et réapparition · collisions murs · rampes qui font décoller · descendre du skate, marcher, courir, sauter · score par ligne et record sauvegardés · menus pause, paramètres graphiques (faible→ultra, résolution, distance, ombres), touches reconfigurables.

## Limites actuelles
- Personnage en formes simples (pas encore de modèle skinné glTF) ; animations procédurales.
- Quarter pipes limités à 62° (pas de vert).
- Le grind se déclenche sur rails/ledges marqués, pas sur n'importe quelle arête.
- Pas de son, pas de trottinette (phase 3).

## Graphismes (passe 1)
Textures PBR réalistes CC0 (Poly Haven, voir public/assets/LICENSES.txt), éclairage par ciel HDR réel avec reflets, ombres douces, occlusion ambiante (GTAO), bloom, étalonnage couleur + vignette + grain, flou de vitesse, anticrénelage SMAA. Poussière à la réception et au grind, décor de rue (trottoirs, lampadaires, bancs). Effets réglés par le préréglage de qualité (désactivés en Faible).

## Feuille de route
1. ✅ Base · 2. ✅ Physique skate (à affiner : vert, reverts, grabs) · 3. Trottinette (physique/commandes/tricks séparés : tailwhip, barspin, bri flip) · 4. Monde ouvert en tuiles chargées progressivement · 5. Personnalisation (modèle glTF skinné + vêtements attachés aux os) · 6. Photo, replays (enregistrement d'états à 30 Hz), audio, météo, jour/nuit, PNJ · 7. Progression, économie, magasins · 8. Créateur de park, crews, S.K.A.T.E. · 9. Serveur Node.js autoritaire (WebSocket) · 10. Optimisation, build Windows (Electron).

## Ressources 3D à produire
Personnage skinné (Mixamo-compatible, licence propre) + vêtements par slot · animations : push, ollie, flips catch, grind, bail, marche/course · trottinette modulaire · kit modulaire de ville (façades, trottoirs, mobilier) · sons de roues/grind/réceptions (enregistrements originaux ou CC0).

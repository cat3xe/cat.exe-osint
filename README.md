# CAT.EXE OSINT · GEOINT

Outil OSINT et GEOINT en ligne de commande (Python 3.14, Rich). Il regroupe des modules de recherche sur des **données publiques**, à utiliser sur soi-même ou sur des cibles autorisées.

## Usage légal
- Testez l'outil sur **vous-même** ou sur des données publiques.
- Ne l'utilisez pas pour surveiller, harceler ou identifier une personne sans son accord.
- L'auteur n'est pas responsable d'un usage abusif.

## Ce que fait le code, et vers où il envoie
Chaque module interroge des services publics. Liste principale :
- **E-mail** : vérification MX/SPF/DMARC, fuites (XposedOrNot), comptes (Holehe reproduit en interne, sur une liste de sites).
- **IP en lot** : extrait les IP d'un journal ou d'un texte, les recoupe et les résume par pays et opérateur.
- **IP / domaine** : ipwho.is, ip-api.com, ipinfo.io, freeipapi.com, RIPEstat, DNS chiffré (Google, Cloudflare, Quad9), Open-Meteo (relief, fuseaux), crt.sh, HackerTarget, CertSpotter, urlscan.io, web.archive.org.
- **Banque / véhicule / appareil** : openiban.com (IBAN), NHTSA vPIC (VIN), macvendors.com (MAC).
- **Entreprises** : BODACC (OpenDataSoft).
- **Anonymat** : passe par Tor (ports 9050/9150) si Tor est installé ; sinon le module le signale.

Aucune donnée n'est envoyée à l'auteur. Les résultats sont enregistrés localement dans `OUT/`.
Les clés API (Hunter, Windy) sont demandées à l'utilisateur et stockées sur sa machine uniquement.

## Fiabilité des résultats
Chaque résultat indique sa source et son niveau :
- **A · vérifié à la source** : DNS lu en direct, GPS mesuré par l'appareil, pays d'une IP confirmé par toutes les bases.
- **B · existe, lien à confirmer** : un compte existe bien sous ce pseudo ou cet email, mais rien ne prouve encore à qui il appartient.
- **C · estimation** : position donnée par une IA, ville d'une IP, pseudo déduit d'un email.

Les recherches de comptes (pseudo, email) passent un test de contrôle avec un identifiant inexistant : un site qui répond « trouvé » à tout est écarté.
Les calculs géographiques (distance, azimut, soleil) sont exacts : ellipsoïde WGS84 et algorithme NOAA.

Outils dédiés à la vérification : **Même personne ?** (recoupement de profils), **Cohérence d'une photo**, **Ligne de vue** (relief réel), **Relèvement** (position par azimuts), **Mesures sur photo** (distance, taille, hauteur), **DNS recoupé** (3 résolveurs), **Capture de preuve** (copie, empreinte, journal chaîné), **Chronologie**, **Export des lieux** (KML, GeoJSON, CSV), **Bilan de fiabilité** du dossier.

Le graphe d'enquête affiche le niveau de chaque élément par une pastille A / B / C, avec une légende cliquable et un mode « couleurs par fiabilité ».

## Quel fichier lancer
| Ce que tu veux | Fichier à lancer | Ce qu'il fait |
|---|---|---|
| Utiliser l'outil (Windows) | **`LANCER.bat`** | Installe Python 3.14 et les modules si besoin, puis démarre l'outil |
| Utiliser l'outil (Mac / Linux) | **`lancer.sh`** | Installe les modules, puis démarre l'outil |
| Créer le `.exe` (Windows) | **`CREER_EXE.bat`** | Crée le dossier `CatExe-OSINT` avec `CatExe-OSINT.exe` |
| Lancer les tests | `python osint_tool.py --test` | Vérifie les calculs et les contrôles |

Les autres fichiers `.py` (`geo_core.py`, `pages_html.py`, `textes.py`) sont chargés automatiquement par `osint_tool.py` : il n'y a rien à lancer, il faut seulement les garder dans le même dossier.

## Mise à jour automatique
Au démarrage (avec `LANCER.bat` ou `lancer.sh`), l'outil compare son dossier au dernier commit de ce dépôt, fichier par fichier, et propose de télécharger ce qui a changé.

- **Tes données ne sont jamais touchées** : `resultats/`, `config.json`, `cours/`, `projets/`, `cache/`, `lang/`, la progression, l'historique et les fichiers `.log`.
- **Rien n'est supprimé** : un fichier que le dépôt ne connaît pas reste en place.
- **Rien d'incomplet n'est installé** : chaque fichier téléchargé est contrôlé par son empreinte, et le code doit se lire correctement. À la moindre anomalie, la mise à jour est annulée et rien ne change.
- **Retour arrière possible** : les anciens fichiers sont gardés dans `sauvegarde_maj/`.
- L'outil demande toujours avant d'installer. Pour ne plus vérifier au démarrage : Réglages → « Vérifier au démarrage ».

Elle ne s'applique pas au `.exe` (il faut retélécharger le `.exe`) ni à un dossier cloné avec Git (utilise `git pull`).

## Structure
| Fichier | Rôle |
|---|---|
| `osint_tool.py` | Programme principal : menus, recherches réseau, rapports |
| `geo_core.py` | Calculs purs : géodésie, soleil, coordonnées, ligne de vue, relèvement, DNS, recoupement, fiabilité |
| `pages_html.py` | Modèles des pages web (cartes, graphe d'enquête) |
| `textes.py` | Tutos des modules et cours |
| `tests/` | 161 tests automatiques, réseau simulé |

Les quatre fichiers `.py` doivent rester dans le même dossier.

## Tests
```
python -m unittest discover -s tests
```
ou `python osint_tool.py --test`. Les tests tournent aussi automatiquement sur GitHub à chaque envoi (onglet Actions).

Ce que les tests couvrent : calculs géographiques contre des valeurs de référence publiées, contrôles anti-faux-positifs (pseudos, emails), recoupement des sources IP, lecture des réponses de services, reprise après coupure réseau, traçabilité du graphe.
Ce qu'ils ne couvrent pas : les sites réels. Un site qui change son format peut fausser un résultat sans faire échouer un test.

## Recherche de pseudo : deux moteurs
La recherche de pseudo interroge deux bases indépendantes, WhatsMyName et Sherlock : environ 870 sites distincts, dont 213 présents dans les deux.

Un compte n'est affiché que s'il passe ces filtres :
1. **Forme du pseudo** : si le site n'accepte pas cette forme (par exemple un point), il n'est pas interrogé.
2. **Page anti-robot** : une page d'attente ou de blocage ne compte jamais comme un compte.
3. **Test de contrôle** : le site doit répondre « absent » à un pseudo qui n'existe pas.

Chaque compte reçoit ensuite une confiance : **forte** si les deux bases sont d'accord ou si la page contient bien le pseudo, **moyenne** sinon.

## Justesse mesurée du tri des profils
La recherche de personne trie les profils trouvés : retenu (le nom affiché correspond) ou écarté (homonyme partiel, autre personne). Ce tri est mesuré sur 213 cas étiquetés à la main, choisis pour leurs pièges : noms composés, particules, accents, initiales, pseudos, villes voisines.

| Lot | Cas | Résultat à la première mesure |
|---|---|---|
| Profils, lot de contrôle (jamais vu par le code) | 50 | précision 100 % · rappel 96 % |
| Villes, lot de contrôle (jamais vu par le code) | 40 | 95 % justes |
| Profils et villes, lot de réglage | 123 | 100 % après réglage |

Les 3 erreurs du lot de contrôle ont ensuite été corrigées ; les tests exigent désormais au moins 95 % sur chaque lot (`tests/test_precision.py`).

Ce que ces chiffres veulent dire : quand l'outil **retient** un profil, le nom affiché est bien celui cherché. Ce qu'ils ne disent pas : la part des personnes que l'outil **retrouve**. Elle dépend de ce que chacun publie sous son vrai nom, et aucun outil ne peut la garantir.

## Installation
```
py -3.14 -m pip install -r requirements.txt
py -3.14 osint_tool.py
```
Windows : lancez `LANCER.bat`. `CREER_EXE.bat` produit un `.exe` avec PyInstaller.

## Vérifier le fichier
Le `.exe` publié a une empreinte SHA256 indiquée dans les Releases. Vérifiez-la avec :
```
certutil -hashfile CATEXE.exe SHA256
```

## Faux positifs antivirus
Les programmes Python compilés (PyInstaller) sont parfois signalés à tort par les antivirus. Le code source complet est ici : vous pouvez le lire et le compiler vous-même.

## Licence
MIT, voir `LICENSE`.

## Crédits
Bases de sites pour la recherche de pseudo : [WhatsMyName](https://github.com/WebBreacher/WhatsMyName) et [Sherlock](https://github.com/sherlock-project/sherlock) (licence MIT), téléchargées à l'usage et gardées 7 jours en cache.
Photos des défis : Wikimedia Commons et Unsplash, détail dans `challenges/CREDITS.txt`.

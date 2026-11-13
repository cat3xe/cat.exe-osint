# CAT.EXE OSINT · GEOINT

Outil OSINT et GEOINT en ligne de commande (Python 3.14, Rich). Il regroupe des modules de recherche sur des **données publiques**, à utiliser sur soi-même ou sur des cibles autorisées.

## Usage légal
- Testez l'outil sur **vous-même** ou sur des données publiques.
- Ne l'utilisez pas pour surveiller, harceler ou identifier une personne sans son accord.
- L'auteur n'est pas responsable d'un usage abusif.

## Ce que fait le code, et vers où il envoie
Chaque module interroge des services publics. Liste principale :
- **E-mail** : vérification MX/SPF/DMARC, fuites (XposedOrNot), comptes (Holehe reproduit en interne, sur une liste de sites).
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

## Structure
| Fichier | Rôle |
|---|---|
| `osint_tool.py` | Programme principal : menus, recherches réseau, rapports |
| `geo_core.py` | Calculs purs : géodésie, soleil, coordonnées, ligne de vue, relèvement, DNS, recoupement, fiabilité |
| `pages_html.py` | Modèles des pages web (cartes, graphe d'enquête) |
| `textes.py` | Tutos des modules et cours |
| `tests/` | 96 tests automatiques, réseau simulé |

Les quatre fichiers `.py` doivent rester dans le même dossier.

## Tests
```
python -m unittest discover -s tests
```
ou `python osint_tool.py --test`. Les tests tournent aussi automatiquement sur GitHub à chaque envoi (onglet Actions).

Ce que les tests couvrent : calculs géographiques contre des valeurs de référence publiées, contrôles anti-faux-positifs (pseudos, emails), recoupement des sources IP, lecture des réponses de services, reprise après coupure réseau, traçabilité du graphe.
Ce qu'ils ne couvrent pas : les sites réels. Un site qui change son format peut fausser un résultat sans faire échouer un test.

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
Photos des défis : Wikimedia Commons et Unsplash, détail dans `challenges/CREDITS.txt`.

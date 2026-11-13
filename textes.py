"""Textes longs de CAT.EXE : tutos des modules, cours Python, parcours « crée ton outil ». Données seulement."""

PY_LESSONS = {
"bases": """# Installer et premier programme
**Python** est le langage de Cat.exe : simple à lire, et parfait pour l'OSINT, l'automatisation et l'IA.

## Installer
- Windows : `winget install Python.Python.3.14` (ou python.org, coche **Add to PATH**).
- Vérifie dans un terminal : `python --version`
- Éditeur conseillé : **VS Code** + l'extension Python.

## Premier programme
Crée un fichier `salut.py` :
```python
print("Salut, je suis Cat.exe !")
nom = input("Ton pseudo : ")
print("Bienvenue", nom)
```
Lance-le : `python salut.py`

## À retenir
- `print()` affiche, `input()` demande quelque chose à l'utilisateur.
- Python lit le fichier **de haut en bas**, ligne par ligne.
- Les commentaires commencent par `#` : Python les ignore.
""",
"variables": """# Variables et types
Une **variable** est une boîte avec un nom, dans laquelle on range une valeur.
```python
pseudo = "cat.3xe"      # texte (str)
abonnes = 1500          # nombre entier (int)
note = 4.5              # nombre à virgule (float)
verifie = True          # booléen (True / False)
```
## Opérations
```python
total = abonnes + 200
print(total * 2, total / 3, total // 3, total % 3)   # multiplier, diviser, division entière, reste
```
## Textes
```python
print(pseudo.upper())            # CAT.3XE
print(len(pseudo))               # 7 caractères
print(f"{pseudo} a {abonnes} abonnés")   # f-string : la façon moderne d'assembler du texte
```
## Convertir
`input()` renvoie toujours du **texte** :
```python
age = int(input("Âge : "))   # texte → nombre
print(str(age) + " ans")     # nombre → texte
```
**Piège classique** : `"5" + 3` plante. Il faut convertir d'abord.
""",
"conditions": """# Conditions
Faire des choix avec `if`, `elif`, `else`. **L'indentation (4 espaces) est obligatoire.**
```python
score = int(input("Score : "))
if score >= 2900:
    print("Maître Cat.exe 👑")
elif score >= 1000:
    print("Chat de garde")
else:
    print("Chaton")
```
## Comparaisons
`==` égal · `!=` différent · `<` `>` `<=` `>=` · `in` (contient)
```python
mail = "test@gmail.com"
if "@" in mail and mail.endswith(".com"):
    print("ça ressemble à un email")
if not mail:
    print("vide")
```
- `and` : les deux doivent être vrais · `or` : au moins un · `not` : l'inverse.
""",
"boucles": """# Boucles
## for : répéter pour chaque élément
```python
sites = ["github.com", "reddit.com", "twitch.tv"]
for site in sites:
    print("Je teste", site)

for i in range(5):        # 0, 1, 2, 3, 4
    print(i)
```
## while : répéter tant qu'une condition est vraie
```python
essais = 0
while essais < 3:
    mdp = input("Mot de passe : ")
    if mdp == "chat":
        print("Accès autorisé")
        break             # sortir de la boucle
    essais += 1
else:
    print("Bloqué !")    # exécuté si la boucle n'a pas fait break
```
- `continue` passe directement au tour suivant.
- `enumerate(liste)` donne la position **et** l'élément : `for i, s in enumerate(sites):`
""",
"fonctions": """# Fonctions
Une fonction = un morceau de code réutilisable, avec un nom.
```python
def saluer(pseudo, emoji="🐱"):
    return f"Salut {pseudo} {emoji}"

print(saluer("cat.3xe"))
print(saluer("neo", "🕶"))
```
- `def` crée la fonction, les **paramètres** sont entre parenthèses.
- `return` renvoie un résultat (sinon la fonction renvoie `None`).
- Un paramètre peut avoir une **valeur par défaut** (`emoji="🐱"`).

## Exemple OSINT
```python
def est_email(texte):
    return "@" in texte and "." in texte.split("@")[-1]

for t in ["a@b.fr", "pas un mail", "x@y"]:
    print(t, "→", est_email(t))
```
**Règle d'or** : une fonction = une seule tâche, avec un nom clair.
""",
"listes": """# Listes et dictionnaires
## Listes : plusieurs valeurs dans l'ordre
```python
pseudos = ["cat", "neo", "trinity"]
pseudos.append("morpheus")     # ajouter
print(pseudos[0], pseudos[-1]) # premier, dernier
print(len(pseudos))
pseudos.remove("neo")
print(sorted(pseudos))
courts = [p for p in pseudos if len(p) <= 4]   # liste en compréhension
```
## Dictionnaires : des clés → des valeurs
```python
compte = {"pseudo": "cat.3xe", "site": "Instagram", "abonnes": 1500}
print(compte["pseudo"])
compte["verifie"] = True
for cle, valeur in compte.items():
    print(cle, "=", valeur)
print(compte.get("bio", "pas de bio"))   # valeur par défaut si la clé manque
```
C'est exactement le format **JSON** que renvoient les API du web.
""",
"fichiers": """# Fichiers
Toujours avec `with` : le fichier se ferme tout seul.
```python
# écrire
with open("resultats.txt", "w", encoding="utf-8") as f:
    f.write("github : trouvé\\n")

# lire ligne par ligne
with open("resultats.txt", encoding="utf-8") as f:
    for ligne in f:
        print(ligne.strip())
```
## JSON (sauvegarder des données)
```python
import json
data = {"pseudo": "cat", "comptes": ["github", "twitch"]}
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
data2 = json.load(open("data.json", encoding="utf-8"))
```
## CSV (tableur)
```python
import csv
with open("comptes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["site", "statut"])
    w.writerow(["github", "trouvé"])
```
""",
"erreurs": """# Gérer les erreurs
Sans protection, une erreur arrête tout le programme. `try / except` l'attrape :
```python
try:
    age = int(input("Âge : "))
except ValueError:
    print("Ce n'est pas un nombre !")
else:
    print("OK", age)
finally:
    print("fini")   # toujours exécuté
```
## Erreurs réseau (très courant en OSINT)
```python
import requests
try:
    r = requests.get("https://site-qui-existe-pas.xyz", timeout=5)
except requests.RequestException as e:
    print("Site injoignable :", type(e).__name__)
```
- Attrape des erreurs **précises** (`ValueError`, `KeyError`…), pas tout en vrac.
- Lis toujours le message d'erreur : la **dernière ligne** dit le type et la cause.
""",
"modules": """# Modules et paquets
Un **module** = un fichier Python qu'on importe. Python en a des centaines inclus :
```python
import random, datetime, os
print(random.choice(["pile", "face"]))
print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
print(os.listdir("."))
```
## Installer des bibliothèques (pip)
```
pip install requests rich pillow
```
- `requests` : le web · `rich` : de belles couleurs dans le terminal · `pillow` : les images.
## Ton propre module
`outils.py` :
```python
def crier(t):
    return t.upper() + " !"
```
`main.py` :
```python
from outils import crier
print(crier("salut"))
```
## Le point d'entrée
```python
if __name__ == "__main__":
    main()   # ne s'exécute que si on lance CE fichier
```
""",
"web": """# Le web : requêtes et API
C'est le cœur de l'OSINT : interroger des sites et des **API** (des adresses qui renvoient du JSON).
```python
import requests
r = requests.get("https://ipwho.is/8.8.8.8", timeout=10)
print(r.status_code)        # 200 = OK, 404 = introuvable
info = r.json()             # JSON → dictionnaire Python
print(info["country"], info["city"], info["connection"]["isp"])
```
## Paramètres et en-têtes
```python
r = requests.get("https://api.github.com/users/torvalds",
                 headers={"User-Agent": "MonOutil/1.0"}, timeout=10)
u = r.json()
print(u["name"], u["public_repos"], u["created_at"])
```
## Les codes HTTP
`200` OK · `301/302` redirection · `403` interdit · `404` introuvable · `429` trop de requêtes (ralentis !) · `500` erreur du serveur.

**Éthique** : respecte les sites (pas de spam de requêtes) et n'enquête que sur toi ou avec accord.
""",
"regex": """# Expressions régulières (regex)
Une **regex** décrit un motif de texte. Indispensable pour extraire des infos.
```python
import re
texte = "Contact : jean@exemple.fr ou admin@site.com, IP 192.168.1.10"
emails = re.findall(r"[\\w.+-]+@[\\w-]+\\.[\\w.]+", texte)
ips = re.findall(r"\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b", texte)
print(emails, ips)
```
## Les briques
| Motif | Signifie |
|---|---|
| `\\d` | un chiffre |
| `\\w` | lettre, chiffre ou _ |
| `\\s` | espace |
| `.` | n'importe quel caractère |
| `+` `*` `?` | 1 ou plus · 0 ou plus · 0 ou 1 |
| `{2,4}` | entre 2 et 4 fois |
| `[abc]` | a, b ou c |
| `^` `$` | début · fin |
| `( )` | groupe à récupérer |

```python
m = re.search(r"(\\d{2})/(\\d{2})/(\\d{4})", "né le 14/07/2001")
print(m.group(3))   # 2001
```
Teste tes regex sur **regex101.com**.
""",
"objets": """# Classes et objets
Une **classe** est un plan ; un **objet** est une chose construite avec ce plan.
```python
class Compte:
    def __init__(self, site, pseudo):
        self.site = site
        self.pseudo = pseudo
        self.trouve = False

    def url(self):
        return f"https://{self.site}/{self.pseudo}"

    def __str__(self):
        return f"{self.site}: {'✓' if self.trouve else '✗'}"

c = Compte("github.com", "torvalds")
c.trouve = True
print(c.url())
print(c)
```
- `__init__` s'exécute à la création, `self` = l'objet lui-même.
- **Héritage** : `class CompteGitHub(Compte):` reprend tout et peut modifier des méthodes.
""",
"projet": """# Mini-projet OSINT : vérificateur de pseudo
On combine tout : fonctions, boucles, dictionnaires, web, erreurs et threads.
```python
import requests, concurrent.futures as cf

SITES = {
    "GitHub": "https://github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}/about.json",
    "Chess.com": "https://api.chess.com/pub/player/{}",
    "Lichess": "https://lichess.org/api/user/{}",
}

def tester(site, url, pseudo):
    try:
        r = requests.get(url.format(pseudo), timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        return site, "trouvé" if r.status_code == 200 else "absent" if r.status_code == 404 else f"? ({r.status_code})"
    except requests.RequestException:
        return site, "erreur"

pseudo = input("Pseudo : ").strip()
with cf.ThreadPoolExecutor(8) as ex:          # 8 tests en même temps
    for site, statut in ex.map(lambda kv: tester(kv[0], kv[1], pseudo), SITES.items()):
        print(f"{site:<10} {statut}")
```
## Améliore-le
1. Ajoute 5 sites.
2. Enregistre les résultats dans un fichier JSON.
3. Affiche un tableau en couleurs avec `rich`.
4. Ajoute les variantes du pseudo (`_` ↔ `.`).
""",
}


PROJECT = [
    ("menu", "Un menu stylé avec rich", "menu.py", """Le terminal peut être beau : la bibliothèque **rich** gère couleurs, tableaux et panneaux (c'est elle qu'utilise Cat.exe).
`pip install rich`""", '''from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

con = Console()
con.print(Panel("[bold #00e5ff]MON OUTIL OSINT[/]\\n[#7480a8]v1.0 · fait maison", border_style="#b388ff"))
t = Table(title="Menu")
t.add_column("N°", style="bold #00e5ff")
t.add_column("Module")
for i, m in enumerate(["Pseudo", "Mon IP", "GPS d'une photo", "Carte"], 1):
    t.add_row(str(i), m)
con.print(t)
choix = Prompt.ask("Ton choix", choices=["1", "2", "3", "4"])
con.print(f"[bold]Tu as choisi le module {choix}[/] 🐱")
'''),
    ("api", "Interroger une API : où est cette IP ?", "ip.py", """Une **API** répond en JSON. Ici on localise une adresse IP (ou la tienne si tu laisses vide) avec ipwho.is, gratuit et sans clé.""", '''import requests

ip = input("Adresse IP (Entrée = la mienne) : ").strip()
r = requests.get(f"https://ipwho.is/{ip}", timeout=10)
d = r.json()
if not d.get("success", True):
    print("Erreur :", d.get("message"))
else:
    print(f"IP        : {d['ip']}")
    print(f"Lieu      : {d['city']}, {d['region']}, {d['country']} {d['flag']['emoji']}")
    print(f"Opérateur : {d['connection']['isp']}")
    print(f"Carte     : https://www.google.com/maps?q={d['latitude']},{d['longitude']}")
'''),
    ("pseudo", "Chercher un pseudo sur plusieurs sites", "pseudo.py", """Le principe des outils comme Sherlock : on teste l'adresse du profil sur chaque site. Code **200** = le compte existe, **404** = non.
Avec des *threads*, tous les sites sont testés en même temps.""", '''import requests, concurrent.futures as cf

SITES = {
    "GitHub": "https://api.github.com/users/{}",
    "GitLab": "https://gitlab.com/api/v4/users?username={}",
    "Chess.com": "https://api.chess.com/pub/player/{}",
    "Lichess": "https://lichess.org/api/user/{}",
    "Scratch": "https://api.scratch.mit.edu/users/{}",
    "Keybase": "https://keybase.io/_/api/1.0/user/lookup.json?usernames={}",
}

def test(item, pseudo):
    site, url = item
    try:
        r = requests.get(url.format(pseudo), timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        ok = r.status_code == 200 and r.text not in ("[]", "") and '"them":[null]' not in r.text
        return site, ok
    except requests.RequestException:
        return site, None

pseudo = input("Pseudo : ").strip()
with cf.ThreadPoolExecutor(10) as ex:
    for site, ok in ex.map(lambda it: test(it, pseudo), SITES.items()):
        print(f"{'✅' if ok else '❌' if ok is False else '⚠'}  {site}")
'''),
    ("exif", "Lire le GPS caché d'une photo", "gps_photo.py", """Les photos de téléphone contiennent souvent leur **position GPS** dans les métadonnées EXIF. On les lit avec Pillow (`pip install pillow`).""", '''from PIL import Image

def dms(v, ref):
    d, m, s = (float(x) for x in v)
    r = d + m / 60 + s / 3600
    return -r if ref in ("S", "W") else r

chemin = input("Photo (glisse-la ici) : ").strip().strip('"')
exif = Image.open(chemin).getexif()
print("Appareil :", exif.get(271), exif.get(272))
print("Date     :", exif.get(306))
gps = exif.get_ifd(0x8825)
if gps and 2 in gps:
    lat, lon = dms(gps[2], gps[1]), dms(gps[4], gps[3])
    print(f"GPS      : {lat:.6f}, {lon:.6f}")
    print(f"Carte    : https://www.google.com/maps?q={lat},{lon}")
else:
    print("Pas de GPS dans cette photo (ou supprimé par le réseau social).")
'''),
    ("carte", "Afficher des points sur une carte", "carte.py", """On génère une page HTML avec **Leaflet** (bibliothèque de cartes) et on l'ouvre dans le navigateur. Fond Esri : marche même en ouvrant le fichier en local (sans clé, sans « Referer »).""", '''import json, webbrowser, pathlib

points = [
    {"nom": "Tour Eiffel", "lat": 48.8584, "lon": 2.2945},
    {"nom": "Notre-Dame", "lat": 48.8530, "lon": 2.3499},
    {"nom": "Sacré-Cœur", "lat": 48.8867, "lon": 2.3431},
]
html = """<!doctype html><html><head><meta charset="utf-8"><title>Ma carte</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>html,body,#m{height:100%;margin:0}</style></head><body><div id="m"></div><script>
const P = __POINTS__;
const map = L.map('m');
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {attribution: '© Esri, OpenStreetMap'}).addTo(map);
const g = L.featureGroup(P.map(p => L.marker([p.lat, p.lon]).bindPopup(p.nom))).addTo(map);
map.fitBounds(g.getBounds(), {padding: [40, 40]});
</script></body></html>""".replace("__POINTS__", json.dumps(points))
f = pathlib.Path("ma_carte.html")
f.write_text(html, encoding="utf-8")
webbrowser.open(f.resolve().as_uri())
print("Carte ouverte :", f.resolve())
'''),
    ("fleches", "Un menu aux flèches (comme Cat.exe)", "menu_fleches.py", """Lire les touches du clavier une par une : `msvcrt` sur Windows, `termios` sur Mac/Linux. Le menu se redessine à chaque appui.""", '''import os, sys

def touche():
    if os.name == "nt":
        import msvcrt
        c = msvcrt.getwch()
        if c in ("\\x00", "\\xe0"):
            return {"H": "haut", "P": "bas"}.get(msvcrt.getwch(), "")
        return "entree" if c == "\\r" else c
    import termios, tty
    fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        c = sys.stdin.read(1)
        if c == "\\x1b":
            return {"[A": "haut", "[B": "bas"}.get(sys.stdin.read(2), "")
        return "entree" if c in ("\\r", "\\n") else c
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

options = ["Chercher un pseudo", "Mon IP", "GPS d'une photo", "Quitter"]
pos = 0
while True:
    os.system("cls" if os.name == "nt" else "clear")
    print("=== MON OUTIL ===  (↑ ↓ puis Entrée)\\n")
    for i, o in enumerate(options):
        print(("\\033[30;42m ❯ " if i == pos else "   ") + o + "\\033[0m")
    k = touche()
    if k == "haut": pos = (pos - 1) % len(options)
    elif k == "bas": pos = (pos + 1) % len(options)
    elif k == "entree":
        print("\\nTu as choisi :", options[pos])
        break
'''),
    ("exe", "Transformer ton outil en .exe", "creer_exe.bat", """**PyInstaller** emballe ton script + Python dans un seul `.exe`, lançable sur n'importe quel PC Windows sans rien installer.
Lance ce .bat dans le dossier de ton script (remplace `menu.py` par ton fichier).""", '''@echo off
cd /d "%~dp0"
python -m pip install -q pyinstaller rich requests pillow
python -m PyInstaller --noconfirm --onefile --console --name MonOutil menu.py
echo.
echo Ton .exe est dans le dossier dist\\MonOutil.exe
pause
'''),
]


_ORIG_PHOTO = """
### 📸 Récupérer la photo ORIGINALE (avec GPS)
C'est le point le plus important :
- **Captures d'écran = GPS perdu.** Il faut le fichier d'origine.
- **iPhone** : Photos → la photo → Partager → *Options* → active **Toutes les données de la photo** → *Enregistrer dans Fichiers* (ou AirDrop vers le PC).
- **Android** : Galerie → Partager → envoie **en fichier** (Gmail, Drive, câble USB). Sur Google Photos : *⋮ → Télécharger*.
- **WhatsApp** : demande l'envoi **en Document** (trombone → Document), pas en photo : en photo, WhatsApp efface le GPS.
- **Discord / Telegram (en fichier)** : clic droit → *Enregistrer l'image* garde souvent les données.
- **Instagram, TikTok, X, Facebook, Snapchat** effacent toujours le GPS → l'outil passe alors à l'**IA** (GeoCLIP + vision) et aux indices visuels.
- **Sur PC** : glisse le fichier directement dans la fenêtre noire, le chemin se colle tout seul."""


TUTOS = {
"mod_bodacc": """### 🎯 À quoi ça sert
Chercher dans le **BODACC**, le bulletin officiel des annonces légales : créations, ventes, changements de dirigeant, redressements et liquidations d'entreprises françaises.
### 🧰 Ce qu'il te faut
Un **nom d'entreprise**, un **nom de dirigeant** ou un **SIREN** (9 chiffres).
### ▶ Étapes
1. Tape le nom ou le SIREN.
2. Les annonces sortent de la plus récente à la plus ancienne (n / p pour les pages).
### 💡 Astuces
- Une **liquidation** ou un **redressement** récent sur un vendeur en ligne est un signal d'alerte.
- Chercher un nom de personne montre les sociétés où elle apparaît.""",
"mod_iban": """### 🎯 À quoi ça sert
Vérifier un **IBAN** avant un virement : clé de contrôle, pays, banque, guichet. Utile contre les **faux RIB**.
### 🧰 Ce qu'il te faut
L'IBAN (les espaces ne gênent pas).
### ▶ Étapes
1. Colle l'IBAN.
2. Lis la clé (valide ou fausse), le pays et la banque.
### 💡 Astuces
- Un pays inattendu (ex : un artisan français avec un IBAN LT ou MT) doit te faire vérifier.
- Un IBAN valide ne prouve pas à qui est le compte : rappelle l'entreprise sur un numéro connu.""",
"mod_vin": """### 🎯 À quoi ça sert
Décoder le **numéro de série d'un véhicule (VIN)** : constructeur, pays, année, modèle. Utile pour vérifier une annonce de voiture d'occasion.
### 🧰 Ce qu'il te faut
Le VIN de 17 caractères : case **E** de la carte grise, bas du pare-brise ou montant de porte.
### ▶ Étapes
1. Tape le VIN.
2. Compare avec l'annonce : marque, année, énergie.
### 💡 Astuces
- Un VIN qui ne correspond pas à l'annonce = fuis.
- Historique officiel en France : HistoVec (demande le rapport au vendeur).""",
"mod_mac": """### 🎯 À quoi ça sert
Trouver le **fabricant d'un appareil** à partir de son adresse MAC (box, caméra, téléphone, objet connecté inconnu sur ton Wi-Fi).
### 🧰 Ce qu'il te faut
L'adresse MAC : dans l'interface de ta box (appareils connectés) ou les réglages de l'appareil.
### ▶ Étapes
1. Colle l'adresse.
2. Lis le fabricant et le type d'adresse.
### 💡 Astuces
- Les téléphones récents utilisent une adresse **aléatoire** par réseau : pas de fabricant, c'est normal.
- Un fabricant de caméras inconnu sur ton Wi-Fi mérite une vérification.""",
"mod_wayurls": """### 🎯 À quoi ça sert
Lister les **fichiers et pages d'un site gardés par la Wayback Machine** : vieux PDF, tableaux, sauvegardes oubliées, pages supprimées.
### 🧰 Ce qu'il te faut
Un **domaine** (ex : `exemple.fr`).
### ▶ Étapes
1. Tape le domaine, choisis le type de fichiers.
2. Ouvre la colonne « Copie » pour voir le fichier tel qu'il était.
3. La liste complète est enregistrée en CSV (Excel).
### 💡 Astuces
- Les documents contiennent souvent des noms, emails et métadonnées : passe-les dans le module Métadonnées.
- Ne consulte que ce qui est public : pas de connexion à des espaces privés.""",

"mod_revimg": """### 🎯 À quoi ça sert
Retrouver **où une image apparaît sur internet** : l'original, sa première publication, ses copies recadrées. Comme Google Lens, sur 6 moteurs à la fois.
### 🧰 Ce qu'il te faut
- Soit le **lien direct de l'image** : clic droit sur l'image → *Copier l'adresse de l'image*.
- Soit la **photo sur ton PC** : l'outil ouvre les moteurs, tu glisses la photo dedans.
### ▶ Étapes
1. Choisis *Sur internet* ou *Sur mon PC*.
2. Colle le lien → les pages de résultats s'ouvrent.
### 💡 Astuces
- **Yandex** est souvent le meilleur pour les lieux et bâtiments, **TinEye** pour trouver la date la plus ancienne.
- Recadre sur un détail (bâtiment, logo, objet) pour de meilleurs résultats.
- Les moteurs reçoivent l'image : n'y mets pas de photo privée.""",
"mod_webcams": """### 🎯 À quoi ça sert
Trouver les **webcams publiques officielles** autour d'un lieu (météo, tourisme, stations de ski, ports) pour **vérifier un lieu** : météo, lumière, décor, comparaison avec une photo.
### 🧰 Ce qu'il te faut
- Un **lieu** (ville, adresse ou coordonnées).
- Facultatif : une **clé gratuite Windy** (api.windy.com/keys → Webcams API) pour avoir la carte avec aperçus. Sans clé, l'outil ouvre la carte Windy.
### ▶ Étapes
1. Tape le lieu et le rayon.
2. Avec clé : liste + carte avec aperçu et lecteur de chaque webcam (direct ou time-lapse de la journée).
### 💡 Astuces
- Le **time-lapse de la journée** permet de comparer la météo à l'heure d'une photo.
- À utiliser pour vérifier un lieu, pas pour suivre des personnes.""",
"mod_holehe": """### 🎯 À quoi ça sert
Savoir **sur quels sites un email a un compte** (Instagram, Spotify, Amazon, Discord…), comme l'outil **Holehe**. La personne n'est pas prévenue.
### 🧰 Ce qu'il te faut
- Un **email**.
- Rien d'autre : 7 sites sont testés directement (Gravatar, Duolingo, Chess.com, Spotify, WordPress, X, Adobe).
- Pour **120 sites de plus**, l'outil propose d'installer **Holehe** tout seul (version Python, pas le .exe).
### ▶ Étapes
1. Tape l'email.
2. Attends 20 à 60 s : la liste des sites où un compte existe s'affiche (avec email / téléphone de secours partiels quand le site les montre) et va dans le graphe.
### 💡 Astuces
- Certains sites bloquent les tests répétés : ils sont comptés à part.
- Continue avec **Epieos** (lien donné) pour le compte Google.
- Reste dans un cadre légal : ton email, ou une enquête autorisée.""",
"mod_harvest": """### 🎯 À quoi ça sert
Récolter tout ce qui est public sur un **domaine**, comme **theHarvester** : sous-domaines, emails, serveurs mail, personnes (avec Hunter).
### 🧰 Ce qu'il te faut
- Un **domaine** (ex : `exemple.fr`).
- Facultatif : une **clé Hunter.io** gratuite (50 recherches / mois) pour les noms et postes.
### ▶ Étapes
1. Tape le domaine.
2. L'outil interroge les certificats SSL, HackerTarget, CertSpotter, les pages contact / mentions légales du site, et Hunter.
### 💡 Astuces
- Les sous-domaines `dev`, `admin`, `vpn`, `mail` sont souvent les plus intéressants.
- Les emails trouvés donnent le **format** de l'entreprise (prenom.nom@…).""",
"mod_urlscan": """### 🎯 À quoi ça sert
Voir **ce que contient un site** sans le visiter : capture d'écran, IP, serveur, domaines contactés, verdict, avec **URLScan.io**.
### 🧰 Ce qu'il te faut
- Un **domaine ou un lien**.
- Pour un nouveau scan : une **clé gratuite urlscan.io**. L'historique public marche sans clé.
### ▶ Étapes
1. *Scans existants* : tous les scans publics du domaine (dates, IP, pays).
2. *Nouveau scan* : l'outil scanne le lien (en non listé) et donne capture + rapport.
### 💡 Astuces
- Idéal pour un **lien de phishing** : tu vois la page sans cliquer.
- Les anciennes IP du site s'ajoutent au graphe.""",
"mod_autoscan": """### 🎯 À quoi ça sert
Lancer **toutes les recherches d'un coup** sur une cible, comme **SpiderFoot** : l'outil détecte le type, lance toutes les transformations, puis recommence sur ce qu'il trouve.
### 🧰 Ce qu'il te faut
Une cible : pseudo, email, domaine, IP, lien, « Prénom Nom » ou coordonnées.
### ▶ Étapes
1. Tape la cible → le type est détecté.
2. Profondeur **1** (rapide) ou **2** (complet, plus long).
3. Ouvre le graphe pour voir la toile.
### 💡 Astuces
- Commence en profondeur 1, puis creuse à la main dans le graphe (clic droit).
- Vérifie toujours : un même pseudo n'est pas forcément la même personne.""",
"mod_prosrc": """### 🎯 À quoi ça sert
Ouvrir d'un coup les **sources pros** adaptées à ta cible : Censys, Hunter, Epieos, Intelligence X, DeHashed, SecurityTrails, GreyNoise, BuiltWith, OSINT Framework, Bellingcat…
### 🧰 Ce qu'il te faut
Une cible : email, domaine, IP, pseudo…
### ▶ Étapes
1. Tape la cible → l'outil détecte son type et prépare les bons liens.
2. *Tout ouvrir* les lance dans le navigateur.
### 💡 Astuces
- Certaines sources demandent un compte gratuit (Censys, Hunter, IntelX).
- **OSINT Framework** et **Bellingcat Toolkit** sont des annuaires d'outils à garder en favori.""",

"mod_anon": """### 🎯 À quoi ça sert
Réduire ce que les sites voient de toi : ton IP réelle est remplacée par une sortie Tor, et tu peux en changer à la demande.
**Ce n'est pas l'anonymat total** : te connecter à ton compte (Google, Instagram…) ou donner ton nom te reconnaît quand même.
### 🧰 Ce qu'il te faut
- **Tor Browser** (gratuit, officiel) : à télécharger sur torproject.org. Il lance Tor tout seul.
- Ou **Firefox** installé : l'outil le lance sur Tor, mais il est moins protégé.
- Le module **PySocks** : `pip install pysocks` (déjà dans requirements.txt).
### ▶ Étapes
1. Ouvre **Tor Browser** (ou Tor en fond).
2. **🔍 Test d'exposition** : compare ton IP réelle et ton IP via Tor. Si le statut dit « passé par Tor », c'est bon.
3. **🔄 Changer d'IP** : demande une nouvelle sortie Tor. Tor limite le rythme : attends une dizaine de secondes entre deux changements.
4. **🧅 Ouvrir un navigateur protégé** : lance Tor Browser (ou Firefox sur Tor).
5. **🧪 Tests de fuites** : ouvre les liens dans ce navigateur pour vérifier WebRTC et DNS.
### 💡 Astuces
- Ne te connecte pas à tes comptes perso dans le navigateur d'anonymat.
- Un VPN seul ne suffit pas : le fournisseur voit ton trafic. Tor sépare mieux.
- Le changement d'IP passe par le port de contrôle, que Tor Browser ouvre tout seul.""",

"mod_social": """### 🎯 À quoi ça sert
Sortir la **fiche détaillée** d'un pseudo sur 17 plateformes : date de création, bio, abonnés, liens, emails (GitHub), heures d'activité (Reddit)…
### 🧰 Ce qu'il te faut
Un **pseudo** (sans le @). Pour Mastodon : `pseudo@instance` (ex : `cat@piaille.fr`).
### 🔎 Où le trouver
- Dans l'URL du profil : `instagram.com/`**`pseudo`**, `tiktok.com/@`**`pseudo`**.
- Sur l'appli : profil → *Partager le profil* → *Copier le lien*.
- Dans une bio Linktree / un email (la partie avant le @ est souvent le pseudo).
### ▶ Étapes
1. Choisis **⚡ Toutes les plateformes** (ou une seule pour aller vite).
2. Colle le pseudo → la 1re page résume trouvé / absent, puis **n** pour voir une fiche par page.
### 💡 Astuces
- **GitHub** : regarde *Emails trouvés dans les commits* (souvent le vrai email).
- **Reddit** : le *creux d'activité* donne le fuseau horaire probable.
- Même pseudo ≠ même personne : compare photo, bio et liens.
- Instagram / Reddit bloquent parfois : réessaie plus tard ou sans VPN.""",

"mod_wmn": """### 🎯 À quoi ça sert
Tester un pseudo sur **plus de 600 sites** d'un coup (base **WhatsMyName**, utilisée par les pros).
### 🧰 Ce qu'il te faut
Un **pseudo** + internet. La base se télécharge toute seule (et se met à jour chaque semaine).
### ▶ Étapes
1. Tape le pseudo → barre de progression (≈ 20 s).
2. Résultats classés par catégorie, **n / p** pour tourner les pages.
3. Propose une **page HTML cliquable** pour ouvrir chaque compte.
### 💡 Astuces
- Teste aussi les **variantes** : `pseudo_`, `pseudo.fr`, `pseudo123`, ancien pseudo (module Prevname).
- Les résultats vont aussi dans le **Graphe d'enquête** : tu vois les recoupements.""",

"mod_person": """### 🎯 À quoi ça sert
À partir d'un **prénom + nom** : emails probables (vérifiés via Gravatar), pseudos probables et recherches prêtes (LinkedIn, Pages Blanches, Copains d'avant, dirigeants…).
### 🧰 Ce qu'il te faut
- Prénom et nom (obligatoires), ville (facultatif).
- **Domaine de l'entreprise** si tu cherches un email pro.
### 🔎 Comment trouver le domaine
Le site de l'entreprise (`societe.fr`) ou la fin d'un email d'un collègue (`@societe.fr`). Module **Entreprises** pour retrouver le site officiel.
### ▶ Étapes
1. Remplis les champs → 1re page : emails qui existent, serveur mail, pseudos.
2. **n** pour toutes les combinaisons d'emails, puis les recherches prêtes.
3. Le menu final ouvre la recherche choisie ou teste les pseudos sur les réseaux.
### ⚠️ Cadre
Pour toi-même, un contact pro ou une vérification. Jamais pour harceler quelqu'un (c'est puni par la loi).""",

"mod_discord": """### 🎯 À quoi ça sert
Analyser une **invitation Discord** (serveur, ID, date de création, membres, qui a créé l'invitation), dater **n'importe quel ID**, voir les membres en ligne d'un **widget**.
### 🔎 Où trouver les infos
- **Invitation** : le lien `discord.gg/xxxx` (le code seul marche aussi).
- **ID** : Discord → *Paramètres → Avancés → Mode développeur* : ON. Ensuite **clic droit** sur un serveur, salon, message ou membre → *Copier l'identifiant*.
- **Compte par ID** : il faut un **token de bot** (Réglages) : discord.com/developers → *New Application* → *Bot* → *Reset Token*.
### 💡 Astuces
- L'ID contient la **date exacte** de création : pratique pour repérer un compte créé la veille (faux compte).
- Le widget ne marche que si le serveur l'a activé.""",

"mod_user": """### 🎯 À quoi ça sert
Chercher un pseudo sur **95 sites** avec ses variantes (`_` `.` `-`) et donner un niveau d'exposition.
### 🧰 Ce qu'il te faut
Un pseudo (voir le tuto *Lookup réseaux sociaux* pour le trouver).
### 💡 Astuces
Plus rapide que *600+ sites*, avec une checklist IA pour réduire ton exposition. Pour aller plus loin : **Pseudo sur 600+ sites**.""",

"mod_prevname": """### 🎯 À quoi ça sert
Retrouver les **anciens pseudos** d'un compte (archives web, redirections, Bluesky, Steam…).
### 🧰 Ce qu'il te faut
Le pseudo **actuel** (et si tu en connais, des pseudos possibles).
### 💡 Astuces
- Les sites qui **redirigent** l'ancien pseudo vers le nouveau trahissent le changement.
- **Steam** : la page *steamhistory* liste les anciens noms.
- Un ancien pseudo ouvre souvent de **vieux comptes** oubliés : relance *600+ sites* dessus.""",

"mod_email": """### 🎯 À quoi ça sert
Vérifier un email : **fuites de données**, photo **Gravatar**, serveur mail, comptes liés.
### 🧰 Ce qu'il te faut
Une adresse email complète.
### 🔎 Où la trouver
Bio Instagram / TikTok (bouton *Email*), pied de page d'un site, mentions légales, CV, commits GitHub (module *Lookup réseaux sociaux*).
### 💡 Astuces
Si l'email apparaît dans une fuite : **change le mot de passe** partout où il était utilisé et active la double authentification.""",

"mod_pwned": """### 🎯 À quoi ça sert
Savoir si un **mot de passe** a déjà fuité, **sans jamais l'envoyer** (seuls 5 caractères de son empreinte partent : méthode k-anonymat de *Have I Been Pwned*).
### ▶ Étapes
Tape le mot de passe (il ne s'affiche pas) → nombre de fuites + force estimée.
### 💡 Astuces
Trouvé dans une fuite = **à changer partout**. Utilise le générateur de la *Boîte à outils* et un gestionnaire (Bitwarden, gratuit).""",

"mod_phone": """### 🎯 À quoi ça sert
Analyser un numéro : **pays, type** (mobile, fixe, VoIP), opérateur d'origine, format, recherches prêtes.
### 🧰 Ce qu'il te faut
Le numéro au format international de préférence : `+33 6 12 34 56 78`.
### 💡 Astuces
- Un numéro **VoIP** ou virtuel = souvent arnaque ou compte jetable.
- L'opérateur affiché est celui d'**origine** (le numéro a pu être porté ailleurs).
- Les recherches prêtes cherchent le numéro sur le web, WhatsApp, Telegram.""",

"mod_crypto": """### 🎯 À quoi ça sert
Voir le **solde et les transactions** d'une adresse Bitcoin / Ethereum (données publiques de la blockchain).
### 🔎 Où trouver l'adresse
Message d'arnaque, page de don, bio, QR code (scanne-le avec ton téléphone et copie le texte).
### 💡 Astuces
- Bitcoin commence par `1`, `3` ou `bc1` ; Ethereum par `0x`.
- Beaucoup d'entrées récentes sur une adresse d'« investissement » = arnaque qui tourne.""",

"mod_ids": """### 🎯 À quoi ça sert
Retrouver la **date cachée** dans un lien ou un ID : TikTok, X, Instagram, Discord, Bluesky, LinkedIn, Mastodon…
### 🔎 Où trouver l'ID
- **TikTok** : lien de la vidéo → le grand nombre après `/video/`.
- **X / Twitter** : le nombre après `/status/`.
- **Discord** : mode développeur → clic droit → *Copier l'identifiant*.
- **LinkedIn** : lien du post (`activity-7234…`).
### 💡 Astuces
Colle **le lien entier**, l'outil trouve l'ID tout seul. Pratique pour savoir si une vidéo « d'aujourd'hui » date en fait de 2019.""",

"mod_img2gps": """### 🎯 À quoi ça sert
Donner une image → l'outil sort **directement ses coordonnées** : GPS du fichier, sinon estimation par IA locale (top 5 GeoCLIP + IA de vision), avec adresse et carte.
### 🧰 Ce qu'il te faut
Un fichier image (JPG, PNG, HEIC, WebP) **ou un lien direct** vers l'image.
""" + _ORIG_PHOTO + """
### 🔎 Récupérer une image d'un réseau social
- **PC** : clic droit → *Enregistrer l'image sous* ; ou *Copier l'adresse de l'image* et colle le lien.
- **Instagram** : ouvre le post sur PC → F12 → onglet *Réseau* → filtre *img* → la plus grande image.
- **Vidéo** : module **Vidéo → images** pour en sortir les meilleures images.
### 💡 Astuces
- L'IA donne une **zone probable**, pas une adresse : vérifie sur Street View (lien fourni).
- Pour une analyse poussée (monuments, ombres, triangulation) : réponds *oui* à la géoloc complète.
- L'IA locale s'installe au 1er usage (GeoCLIP ~1 Go, Ollama ~2 à 6 Go).""",

"mod_geo": """### 🎯 À quoi ça sert
La **géolocalisation complète** d'une photo : GPS, IA GeoCLIP, IA de vision (monuments, panneaux, langue), triangulation, carte interactive.
### 🧰 Ce qu'il te faut
Une photo (le mieux : l'**originale**). Un PC avec 8 Go de RAM pour l'IA locale.
""" + _ORIG_PHOTO + """
### ▶ Étapes
1. Glisse la photo dans la fenêtre → Entrée.
2. Si le GPS existe : position exacte. Sinon l'IA prend le relais (10 s à 2 min).
3. Ouvre la **carte** : chaque hypothèse est un point, avec Street View.
### 💡 Astuces (comme les pros de GeoGuessr)
- Regarde : **langue** des panneaux, côté de **conduite**, **plaques**, marquage au sol, poteaux, végétation.
- Confirme l'heure avec **Ombres & soleil**, la météo avec **Météo passée**.
- Inconnu ? Note les indices dans **Recherche par indices**.""",

"mod_video": """### 🎯 À quoi ça sert
Découper une vidéo en **images nettes** (pour les analyser) et lire les **métadonnées** (date, appareil, **GPS** caché des vidéos de téléphone).
### 🧰 Ce qu'il te faut
Le fichier vidéo (MP4, MOV, WebM…). **ffmpeg** se télécharge tout seul au 1er usage (version LANCER.bat).
### 🔎 Récupérer la vidéo
- **iPhone / Android** : envoie la vidéo **en fichier** (AirDrop, câble, Drive) pour garder le GPS.
- **TikTok** : bouton *Partager → Enregistrer la vidéo* (sans GPS, mais les images restent analysables).
- **YouTube / X / autres** : outils comme *yt-dlp* (gratuit) : `yt-dlp LIEN`.
### 💡 Astuces
Envoie ensuite la meilleure image dans **Image → coordonnées** ou **Recherche de logo**.""",

"mod_logo": """### 🎯 À quoi ça sert
Identifier une **marque / un logo** ou retrouver une image ailleurs sur le web (**recherche inversée** : Google Lens, Bing, Yandex, TinEye).
### 🧰 Ce qu'il te faut
Une image (le mieux : **recadrée sur le logo** ou l'objet).
### 💡 Astuces
- **Yandex** est le meilleur pour les visages et les lieux, **Google Lens** pour les objets, **TinEye** pour la 1re apparition d'une image.
- Retrouver l'image publiée plus tôt ailleurs = souvent la **vraie source** (et la fin d'une fausse info).""",

"mod_meta": """### 🎯 À quoi ça sert
Lire les **métadonnées** d'un fichier (photo, PDF, Word, Excel…) : auteur, logiciel, dates, appareil, GPS — et **les nettoyer** avant de publier.
### 🧰 Ce qu'il te faut
Le fichier original (voir ci-dessous pour les photos).
""" + _ORIG_PHOTO + """
### 💡 Astuces
- Un PDF ou un Word contient souvent le **nom de l'auteur** ou de l'entreprise.
- Nettoie **tes** photos avant de les poster : l'outil crée une copie sans données.""",

"mod_ela": """### 🎯 À quoi ça sert
Repérer une **retouche** (analyse ELA) : les zones collées ou modifiées ressortent plus claires.
### 🧰 Ce qu'il te faut
Un **JPG** le moins recompressé possible (l'original, pas une capture).
### 💡 Astuces
- Une zone **beaucoup plus lumineuse** que le reste = suspecte.
- Les images passées par WhatsApp / Facebook sont recompressées : l'ELA devient moins fiable.""",

"mod_sun": """### 🎯 À quoi ça sert
Utiliser le **soleil et les ombres** : trouver l'**heure** d'une photo connaissant le lieu, ou vérifier si une photo colle avec un lieu et une date.
### 🧰 Ce qu'il te faut
- Le **lieu** (adresse ou coordonnées) et la **date**.
- La **direction de l'ombre** : sur Google Maps, repère la rue et l'orientation (le nord est en haut).
- Optionnel : hauteur d'un objet et longueur de son ombre (rapport ombre / hauteur).
### 💡 Astuces
Ombre courte = midi ; ombre très longue = matin ou soir. Ombre vers le nord-ouest le matin en France ? Impossible → photo truquée ou lieu faux.""",

"mod_weather": """### 🎯 À quoi ça sert
Connaître la **météo d'un jour passé** à un endroit pour **vérifier une photo** (« il pleuvait ce jour-là ? »).
### 🧰 Ce qu'il te faut
Le **lieu** et la **date** (et l'heure si possible).
### 🔎 Où trouver la date
Métadonnées du fichier (module *Métadonnées*), date de publication, **Décodeur d'ID** pour la date d'un post.
### 💡 Astuces
Grand soleil sur la photo mais 12 mm de pluie ce jour-là = photo d'un autre jour.""",

"mod_place": """### 🎯 À quoi ça sert
Tout sur un lieu : **adresse**, coordonnées dans tous les formats, altitude, fuseau, et **12 cartes** (Google, Street View, satellite, cadastre, IGN…).
### 🧰 Ce qu'il te faut
Une adresse, un nom de lieu **ou** des coordonnées (`48.8584, 2.2945`, `48°51'30"N 2°17'40"E`, Plus Code…).
### 🔎 Copier des coordonnées
Google Maps : **clic droit** sur le point → clique sur les chiffres en haut, c'est copié.""",

"mod_satellite": """### 🎯 À quoi ça sert
Voir un lieu **en vue satellite à différentes dates depuis 2014** : constructions, travaux, bâtiments disparus…
### 🧰 Ce qu'il te faut
Une adresse ou des coordonnées (voir *Infos d'un lieu*).
### 💡 Astuces
Pratique pour **dater une photo** : si un bâtiment visible sur la photo n'existe pas sur l'image satellite de 2018, la photo est plus récente.""",

"mod_bearing": """### 🎯 À quoi ça sert
Calculer **distance et direction** entre deux points, et savoir si un objet est **visible** malgré la courbure de la Terre (montagne, tour, île vue depuis une côte).
### 🧰 Ce qu'il te faut
Deux positions (coordonnées) et, pour la visibilité, les **hauteurs** (altitude du regard, hauteur de l'objet).
### 🔎 Où trouver les hauteurs
Altitude : *Infos d'un lieu* ; hauteur d'un bâtiment : Wikipédia ou estimation (≈ 3 m par étage).""",

"mod_clues": """### 🎯 À quoi ça sert
Trouver un lieu **à partir d'indices** vus sur une image (enseigne, langue, plaque, paysage) : l'outil cherche et place les candidats sur la carte.
### 🧰 Ce qu'il te faut
Jusqu'à 4 indices précis : *« pharmacie verte + boulangerie Paul + rond-point »*, *« panneau en polonais + tramway »*…
### 💡 Astuces
Commence par l'indice **le plus rare** (nom d'enseigne locale, numéro de route).""",

"mod_planes": """### 🎯 À quoi ça sert
Voir les **avions en direct** (ADS-B) autour d'un lieu : immatriculation, altitude, vitesse, trajet.
### 🧰 Ce qu'il te faut
Un lieu. Pour identifier un avion sur une photo : **lieu + heure** de la photo, puis recoupe sur ADS-B Exchange / FlightRadar24 (historique).""",

"mod_iplookup": """### 🎯 À quoi ça sert
Tout sur une **IP ou un domaine** : pays, ville, opérateur, ASN, **VPN / proxy / Tor / datacenter**, ports ouverts et failles connues, autres sites sur la même IP.
### 🔎 Où trouver une IP
- **Ta propre IP** : laisse vide et appuie sur Entrée.
- **D'un email reçu** : module *En-têtes d'email* (l'IP de l'expéditeur est dans les en-têtes).
- **D'un site** : tape simplement le domaine (`exemple.fr`).
- **Logs** de ta box, de ton serveur ou d'un panneau d'administration.
### 💡 Astuces
- La position d'une IP = **l'opérateur**, jamais l'adresse d'une personne.
- *Datacenter* ou *VPN* = la personne cache sa vraie connexion.""",

"mod_domain": """### 🎯 À quoi ça sert
Audit d'un **domaine** : DNS, emails (SPF / DMARC), certificat SSL, sous-domaines, ports, failles connues, propriétaire (RDAP).
### 🧰 Ce qu'il te faut
Le domaine sans `https://` (ex : `exemple.fr`).
### 💡 Astuces
Les **sous-domaines** (via les certificats) révèlent souvent des pages oubliées : `test.`, `admin.`, `dev.`.""",

"mod_link": """### 🎯 À quoi ça sert
Vérifier un **lien suspect** avant de cliquer : redirections, vrai domaine, âge du domaine, ressemblance avec une marque (phishing).
### 🔎 Copier un lien sans l'ouvrir
- **PC** : clic droit → *Copier l'adresse du lien*.
- **Téléphone** : **appui long** sur le lien → *Copier*.
- **SMS** : appui long sur le message → *Copier*.
### 💡 Astuces
Domaine créé il y a quelques jours + nom qui imite une marque (`amaz0n-securite.com`) = **arnaque**.""",

"mod_headers": """### 🎯 À quoi ça sert
Lire les **en-têtes d'un email** pour savoir **d'où il vient vraiment** et s'il est du **phishing** (SPF, DKIM, DMARC, serveurs traversés, IP d'origine).
### 🔎 Récupérer les en-têtes
- **Gmail** : ouvre le mail → **⋮** → *Afficher l'original* → *Copier dans le presse-papiers*.
- **Outlook (web)** : **…** → *Afficher* → *Afficher la source du message*.
- **Outlook (appli)** : Fichier → *Propriétés* → zone *En-têtes Internet*.
- **Apple Mail** : *Présentation → Message → Toutes les en-têtes*.
- **Thunderbird** : *Ctrl + U*.
- **Orange / SFR / Free** : menu du message → *Afficher la source*.
### ▶ Étapes
Colle tout, puis tape **FIN** sur une ligne seule → verdict.""",

"mod_extract": """### 🎯 À quoi ça sert
Sortir **tous les indices** d'une page web, d'un fichier ou d'un texte : emails, réseaux, IP, téléphones, cryptos, IBAN, identifiants Google Analytics…
### 🧰 Ce qu'il te faut
Une **URL**, un **fichier** (PDF, Word, TXT, HTML…) ou du **texte collé**.
### 💡 Astuces
Le **code Google Analytics / Ads** d'un site permet de trouver ses **autres sites** (même propriétaire) via des recherches inversées.""",

"mod_archive": """### 🎯 À quoi ça sert
Voir les **anciennes versions** d'une page ou d'un site (Wayback Machine) : texte supprimé, ancienne équipe, anciens contacts.
### 🧰 Ce qu'il te faut
Une URL (page précise ou site entier).
### 💡 Astuces
Un profil supprimé ou une page « À propos » d'il y a 5 ans contient souvent noms, emails et téléphones.""",

"mod_net": """### 🎯 À quoi ça sert
Outils réseau : **ton IP publique**, propriétaire d'une IP (RIPE), **ASN**, et **fabricant d'un appareil** à partir de son adresse MAC.
### 🔎 Trouver une adresse MAC
- **Windows** : `ipconfig /all` (ligne *Adresse physique*).
- **Box internet** : page des appareils connectés (192.168.1.1 ou 192.168.1.254).
- **Téléphone** : Réglages → À propos → Wi-Fi (attention : adresse souvent **aléatoire**).""",

"mod_dorks": """### 🎯 À quoi ça sert
Générer des **recherches Google avancées** (dorks) : fichiers PDF d'un site, pages de connexion, mentions d'un pseudo, documents exposés…
### 💡 Les opérateurs à connaître
`site:exemple.fr` · `filetype:pdf` · `"phrase exacte"` · `-mot` (exclure) · `intitle:` · `inurl:` · `before:2020`.
### ⚠️ Cadre
Ne télécharge et n'utilise pas des documents qui ne te sont pas destinés.""",

"mod_decode": """### 🎯 À quoi ça sert
Décoder automatiquement un texte bizarre : **Base64, hexa, binaire, Morse, ROT13, César, URL, JWT…** même empilés.
### 🧰 Ce qu'il te faut
Le texte codé (copie-le tel quel).
### 💡 Reconnaître un codage
- Finit par `=` ou `==` → **Base64**.
- Que des 0 et 1 → **binaire** ; que `0-9 a-f` → **hexa**.
- Points et tirets → **Morse** ; trois blocs séparés par des points (`eyJ…`) → **JWT**.""",

"mod_toolbox": """### 🎯 À quoi ça sert
Outils **hors ligne** : stéganographie (message caché dans une image), strings d'un fichier, calculateur réseau, timestamps, mots de passe, coordonnées.
### 💡 Astuces
- **Stéganographie** : utilise le **fichier original** (une image recompressée perd le message). Regarde aussi le *plan de bits* créé.
- **Strings** : sur un `.exe` suspect, filtre `http` pour voir à quels sites il parle.
- **Timestamp** : les nombres à 10 chiffres sont des secondes, à 13 des millisecondes.""",

"mod_hash": """### 🎯 À quoi ça sert
Calculer l'**empreinte** (hash) d'un fichier, trouver son **vrai type** (un `.pdf` qui est en fait un `.exe`) et sa **réputation** (déjà connu comme virus ?).
### 💡 Astuces
- Ne double-clique jamais sur un fichier suspect : analyse-le ici d'abord.
- Le hash permet aussi de chercher le fichier sur **VirusTotal** (lien fourni) sans l'envoyer.""",

"mod_biz": """### 🎯 À quoi ça sert
Trouver une **entreprise** : SIREN, dirigeants, adresse, activité, annonces légales (BODACC), Pages Jaunes, Pappers.
### 🧰 Ce qu'il te faut
Un nom d'entreprise, un SIREN / SIRET ou un nom de dirigeant.
### 🔎 Où trouver le SIREN
Mentions légales d'un site, bas de facture ou de devis, Kbis.
### 💡 Astuces
Un « artisan » créé il y a 2 mois, sans avis et avec une adresse de domiciliation = prudence.""",

"mod_challenges": """### 🎯 À quoi ça sert
**11 défis OSINT** (facile → difficile) pour t'entraîner. Chaque défi donne un **flag** `CATEXE{...}` à poster sur le Discord.
### ▶ Étapes
Choisis un défi → lis l'énoncé → ouvre le fichier joint → utilise les modules de l'outil → *Répondre*.
### 💡 Astuces
Bloqué ? *Indice*. Chaque défi a été pensé pour un module précis (métadonnées, décodeur, géoloc…).""",

"mod_maplink": """### 🎯 À quoi ça sert
Transformer **n'importe quel lien de carte** en coordonnées précises, adresse et liens vers 8 autres cartes.
### 🔎 Récupérer le lien
- **Google Maps (téléphone)** : appui long sur le lieu → *Partager* → *Copier le lien* (lien court `maps.app.goo.gl`, accepté).
- **Google Maps (PC)** : copie l'adresse dans la barre du navigateur.
- **Waze** : *Partager le lieu* → *Copier*. **Apple Plans** : *Partager* → *Copier*.
- Un lien reçu par **SMS / WhatsApp** : appui long → *Copier*.
### 💡 Astuces
Ouvre ensuite le lieu dans **Mapillary** (photos de rue récentes) ou **Peakvisor** (identifier des montagnes à l'horizon).""",

"mod_photobatch": """### 🎯 À quoi ça sert
Lire **toutes les photos d'un dossier** : dates, GPS, appareils → **chronologie** + **trajet** sur une carte + fichier Excel.
### 🧰 Ce qu'il te faut
Un dossier de photos **originales** (pas des captures).
### 🔎 Récupérer les photos
- **iPhone → PC** : câble + application *Photos* de Windows → *Importer* (garde le GPS).
- **Google Photos** : *takeout.google.com* → exporte l'album (les fichiers gardent leurs données).
- **Android** : câble USB → dossier `DCIM/Camera`.
### 💡 Astuces
Plusieurs **appareils** différents dans un même lot = plusieurs auteurs. Un trou dans la chronologie = photos supprimées ?""",

"mod_imgcompare": """### 🎯 À quoi ça sert
Savoir si **deux images sont la même** (recadrée, recompressée, filtrée) et **où elles diffèrent** (retouche, objet ajouté ou effacé).
### 🧰 Ce qu'il te faut
Deux images : par exemple celle qui circule et celle trouvée par **recherche inversée** (module Recherche de logo).
### 💡 Astuces
- Ressemblance > 80 % = même photo de base.
- La version **la plus grande / la plus lourde / la plus ancienne** est souvent l'originale.
- Les zones claires de la *carte des différences* = parties modifiées.""",

"mod_vidinfo": """### 🎯 À quoi ça sert
Trouver la **date exacte** de mise en ligne d'une vidéo (YouTube, Shorts, TikTok), sa chaîne, ses vues, ses **mots-clés cachés**, et ses **miniatures** pour la recherche inversée (méthode InVID / Amnesty).
### 🔎 Récupérer le lien
- **YouTube** : *Partager* → *Copier le lien*. **TikTok** : *Partager* → *Copier le lien* (même le lien court `vm.tiktok.com`).
### 💡 Astuces
Lance la recherche inversée sur **chaque miniature** : si une version plus ancienne existe, la vidéo « du jour » est en fait une **vieille vidéo republiée**.""",

"mod_breaches": """### 🎯 À quoi ça sert
Savoir si un **site ou un service** a déjà été **piraté**, quand, combien de comptes, et quelles données ont fuité.
### 🧰 Ce qu'il te faut
Le nom du site (`deezer.com`) ou du service (`Canva`).
### 💡 Astuces
Tu avais un compte dessus ? Change ce mot de passe **partout** où tu l'as réutilisé, et teste-le avec **Fuite de mot de passe**.""",

"mod_graph": """### 🎯 À quoi ça sert
Une **fenêtre à part** (façon Obsidian / Maltego) qui dessine ton enquête en toile : pseudos, comptes, emails, IP, lieux, reliés entre eux.
### ▶ Étapes
1. **Ouvrir le graphe** → une fenêtre s'ouvre (Edge ou Chrome en mode application).
2. Laisse-la ouverte et lance d'autres modules : **elle se remplit toute seule**, en direct.
3. Dans la fenêtre : **clic** = fiche + notes, **double-clic** = ouvrir le lien, **molette** = zoom, **glisser** = déplacer.
4. **Clic droit** sur un élément = **transformations** (comme Maltego) : chercher un pseudo sur 17 réseaux ou 600+ sites, profil Gravatar d'un email, DNS et sous-domaines d'un domaine, IP lookup, sites sur la même IP… Les résultats s'ajoutent tout seuls.
5. **Ctrl + clic** sur deux éléments puis **🧭 Chemin** : ce qui les relie.
6. Dispositions : libre, arbre, cercle, par type · **▣ Regrouper** par type · **⇅ Données** : export JSON / Excel, import.
7. *+ Élément* et *⟷ Relier* pour ajouter tes propres trouvailles.
### 💡 Astuces
- Un point relié à **plusieurs pistes** (même email, même IP) = recoupement important.
- Une enquête par sujet : *Changer d'enquête*.
- *⇩ Image* pour exporter le graphe en PNG.""",

"mod_report": """### 🎯 À quoi ça sert
Regrouper **tout ce que tu as trouvé pendant la session** dans un rapport **PDF** (lisible sur iPhone) ou **HTML**, avec une synthèse IA.
### 💡 Astuces
Lance le rapport **avant de quitter** : la session n'est pas gardée à la fermeture (le graphe, lui, est sauvegardé).""",

"mod_settings": """### 🎯 À quoi ça sert
Choisir la **langue**, les **modèles d'IA locale** (Ollama), les animations, le token Discord.
### 🧰 IA locale : ce qu'il faut savoir
- Tout tourne **sur ton PC** : rien n'est envoyé sur internet.
- **8 Go de RAM** : `qwen2.5:3b` (conseillé). **16 Go** : `qwen2.5:7b` (plus intelligent).
- Ollama s'installe depuis **ollama.com** (l'outil propose de l'ouvrir) ; le modèle se télécharge une fois.""",

"mod_learn": """### 🎯 À quoi ça sert
Apprendre à **programmer** et à **créer tes propres outils**, dans 23 langages, sans limite : cours, exercices corrigés, prof IA, parcours « crée ton outil OSINT ».
### 🧰 Ce qu'il te faut
Rien pour le cours **Python** (hors ligne). Pour les leçons générées et le prof : l'**IA locale** (Réglages).
### 💡 Astuces
Commence par **Python** : c'est le langage de cet outil. Fais les exercices, pas seulement la lecture.""",
}

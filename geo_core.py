"""Calculs purs de CAT.EXE : géodésie, soleil, coordonnées, ligne de vue, relèvement, DNS, recoupement de profils,
fiabilité des IP et des photos. Aucun réseau, aucun affichage : ce module est testé dans tests/."""
import math, re, datetime, random, secrets, unicodedata
from collections import Counter


def haversine(a, b, c, d):
    """Distance rapide sur une sphère (km), erreur max ≈ 0,5 %. Pour une mesure exacte : geodesic()."""
    r = math.radians
    h = math.sin(r(c - a) / 2) ** 2 + math.cos(r(a)) * math.cos(r(c)) * math.sin(r(d - b) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(min(1.0, h)))


WGS_A, WGS_F = 6378137.0, 1 / 298.257223563


WGS_B = WGS_A * (1 - WGS_F)


def geodesic(lat1, lon1, lat2, lon2):
    """Distance exacte sur l'ellipsoïde WGS84 (Vincenty, précision ≈ 1 mm).
    Renvoie (km, azimut de départ °, azimut d'arrivée °)."""
    if abs(lat1 - lat2) < 1e-12 and abs((lon1 - lon2 + 180) % 360 - 180) < 1e-12:
        return 0.0, 0.0, 0.0
    f, a, b = WGS_F, WGS_A, WGS_B
    U1, U2 = math.atan((1 - f) * math.tan(math.radians(lat1))), math.atan((1 - f) * math.tan(math.radians(lat2)))
    L = math.radians((lon2 - lon1 + 180) % 360 - 180)
    sU1, cU1, sU2, cU2 = math.sin(U1), math.cos(U1), math.sin(U2), math.cos(U2)
    lam = L
    for _ in range(200):
        sl, cl = math.sin(lam), math.cos(lam)
        ss = math.hypot(cU2 * sl, cU1 * sU2 - sU1 * cU2 * cl)
        if ss == 0:
            return 0.0, 0.0, 0.0
        cs = sU1 * sU2 + cU1 * cU2 * cl
        sig = math.atan2(ss, cs)
        sa = cU1 * cU2 * sl / ss
        c2a = 1 - sa * sa
        c2m = cs - 2 * sU1 * sU2 / c2a if c2a else 0.0
        C = f / 16 * c2a * (4 + f * (4 - 3 * c2a))
        new = L + (1 - C) * f * sa * (sig + C * ss * (c2m + C * cs * (-1 + 2 * c2m * c2m)))
        if abs(new - lam) < 1e-12:
            lam = new
            break
        lam = new
    else:  # points presque aux antipodes : la série ne converge pas, on retombe sur la sphère
        from_ = haversine(lat1, lon1, lat2, lon2)
        return from_, _sph_bearing(lat1, lon1, lat2, lon2), (_sph_bearing(lat2, lon2, lat1, lon1) + 180) % 360
    sl, cl = math.sin(lam), math.cos(lam)
    u2 = c2a * (a * a - b * b) / (b * b)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    ds = B * ss * (c2m + B / 4 * (cs * (-1 + 2 * c2m * c2m) - B / 6 * c2m * (-3 + 4 * ss * ss) * (-3 + 4 * c2m * c2m)))
    dist = b * A * (sig - ds)
    az1 = math.degrees(math.atan2(cU2 * sl, cU1 * sU2 - sU1 * cU2 * cl)) % 360
    az2 = math.degrees(math.atan2(cU1 * sl, -sU1 * cU2 + cU1 * sU2 * cl)) % 360
    return dist / 1000, az1, az2


def _sph_bearing(a, b, c, d):
    y = math.sin(math.radians(d - b)) * math.cos(math.radians(c))
    x = math.cos(math.radians(a)) * math.sin(math.radians(c)) - math.sin(math.radians(a)) * math.cos(math.radians(c)) * math.cos(math.radians(d - b))
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def geodesic_dest(lat, lon, brg, km):
    """Point d'arrivée exact sur l'ellipsoïde WGS84 (Vincenty direct)."""
    f, a, b = WGS_F, WGS_A, WGS_B
    al, s_ = math.radians(brg), km * 1000
    tU1 = (1 - f) * math.tan(math.radians(lat))
    cU1 = 1 / math.sqrt(1 + tU1 * tU1)
    sU1 = tU1 * cU1
    sig1 = math.atan2(tU1, math.cos(al))
    sa = cU1 * math.sin(al)
    c2a = 1 - sa * sa
    u2 = c2a * (a * a - b * b) / (b * b)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    sig = s_ / (b * A)
    for _ in range(200):
        c2m = math.cos(2 * sig1 + sig)
        ss, cs = math.sin(sig), math.cos(sig)
        ds = B * ss * (c2m + B / 4 * (cs * (-1 + 2 * c2m * c2m) - B / 6 * c2m * (-3 + 4 * ss * ss) * (-3 + 4 * c2m * c2m)))
        new = s_ / (b * A) + ds
        if abs(new - sig) < 1e-12:
            sig = new
            break
        sig = new
    c2m, ss, cs = math.cos(2 * sig1 + sig), math.sin(sig), math.cos(sig)
    t = sU1 * ss - cU1 * cs * math.cos(al)
    lat2 = math.atan2(sU1 * cs + cU1 * ss * math.cos(al), (1 - f) * math.hypot(sa, t))
    lam = math.atan2(ss * math.sin(al), cU1 * cs - sU1 * ss * math.cos(al))
    C = f / 16 * c2a * (4 + f * (4 - 3 * c2a))
    L = lam - (1 - C) * f * sa * (sig + C * ss * (c2m + C * cs * (-1 + 2 * c2m * c2m)))
    return math.degrees(lat2), (lon + math.degrees(L) + 540) % 360 - 180


# ------------------------------------------------------------ FIABILITÉ (affichée partout : résultats, graphe, rapport)
# A = lu directement à la source et recoupé · B = l'élément existe, son lien avec la cible reste à prouver · C = estimation / hypothèse
FIAB = {"A": "vérifié à la source", "B": "existe · lien avec la cible à confirmer", "C": "estimation · à vérifier"}


def ctrl_name(n=12):
    """Pseudo de contrôle qui n'existe nulle part : sert à repérer les sites qui répondent « trouvé » à tout."""
    import secrets as _s
    return "zq" + _s.token_hex(n // 2)


def fmt_dist(m):
    return f"{m:.0f} m" if m < 1000 else f"{m / 1000:.1f} km" if m < 20000 else f"{m / 1000:.0f} km"


def cardinal(deg):
    return ["nord", "nord-est", "est", "sud-est", "sud", "sud-ouest", "ouest", "nord-ouest"][int((deg % 360 + 22.5) // 45) % 8]


def _norm_city(c):
    import unicodedata
    c = "".join(ch for ch in unicodedata.normalize("NFD", str(c or "")) if unicodedata.category(ch) != "Mn").lower()
    return re.sub(r"[^a-z]", "", c)


def ip_consensus(src):
    """src : {nom: données}. Recoupe les sources et dit ce qui est sûr (pays) et ce qui ne l'est pas (ville, point)."""
    ok = {k: v for k, v in src.items() if v and v.get("cc")}
    out = {"n": len(ok), "sources": ok, "cc": None, "country": None, "city": None, "lat": None, "lon": None, "spread_km": None,
           "cc_agree": 0, "city_agree": 0, "radius_km": None, "level": "C", "resume": "aucune source de géolocalisation n'a répondu"}
    if not ok:
        return out
    from collections import Counter
    cc, n_cc = Counter(str(v["cc"]).upper() for v in ok.values()).most_common(1)[0]
    same = {k: v for k, v in ok.items() if str(v["cc"]).upper() == cc}
    out.update(cc=cc, cc_agree=n_cc, country=next((v.get("country") for v in same.values() if v.get("country")), cc))
    cities = Counter(_norm_city(v.get("city")) for v in same.values() if v.get("city"))
    if cities:
        ck, n_city = cities.most_common(1)[0]
        out.update(city=next(v["city"] for v in same.values() if _norm_city(v.get("city")) == ck), city_agree=n_city)
    has_pt = lambda v: v.get("lat") is not None and v.get("lon") is not None
    pts = [(float(v["lat"]), float(v["lon"])) for v in same.values() if has_pt(v)]
    all_spread = max((haversine(a[0], a[1], b[0], b[1]) for a in pts for b in pts), default=0)
    if out["city_agree"] >= 2 and out["city_agree"] > len(same) / 2:
        # une majorité de sources donne la même ville : on mesure la zone sur elles, la source isolée est signalée à part
        pts = [(float(v["lat"]), float(v["lon"])) for v in same.values() if has_pt(v) and _norm_city(v.get("city")) == ck] or pts
    if pts:
        # point médian = celui qui minimise la distance aux autres (robuste à une source aberrante)
        best = min(pts, key=lambda p: sum(haversine(p[0], p[1], q[0], q[1]) for q in pts))
        spread = max((haversine(a[0], a[1], b[0], b[1]) for a in pts for b in pts), default=0)
        out.update(lat=best[0], lon=best[1], spread_km=spread, radius_km=max(25.0, spread))
    pays_sur = n_cc >= 2 and n_cc == len(ok)
    ville_sure = out["city_agree"] >= 2 and out["city_agree"] > len(same) / 2 and (out["spread_km"] or 0) <= 60
    out["level"] = "A" if pays_sur else "C"
    out["pays_txt"] = (f"{n_cc}/{len(ok)} sources d'accord" if len(ok) > 1 else "1 seule source a répondu : non recoupé")
    out["ville_txt"] = ("—" if not out["city"] else f"{out['city_agree']}/{len(same)} sources d'accord"
                        + (f", écart max {all_spread:.0f} km entre toutes les sources" if len(same) > 1 and all_spread >= 1 else ""))
    out["ville_sure"] = ville_sure
    out["resume"] = (f"pays {'sûr' if pays_sur else 'à confirmer'} ({out['pays_txt']}) · ville {'probable' if ville_sure else 'incertaine'} ({out['ville_txt']})")
    return out


_NUM = r"(\d+(?:[.,]\d+)?)"


_HEMI_SUF = re.compile(_NUM + r"\s*°?\s*(?:" + _NUM + r"\s*['’′]\s*)?(?:" + _NUM + r"\s*(?:\"|”|″|'')\s*)?\s*([NSEWO])(?![A-Za-z])", re.I)


_HEMI_PRE = re.compile(r"(?<![A-Za-z])([NSEWO])\s*" + _NUM + r"\s*°?\s*(?:" + _NUM + r"\s*['’′]\s*)?(?:" + _NUM + r"\s*(?:\"|”|″|''))?", re.I)


def coords_valid(lat, lon):
    return -90 <= lat <= 90 and -180 <= lon <= 180


def coords_only(s):
    """Lit des coordonnées écrites (décimal, DMS, avec ou sans N/S/E/O, dans n'importe quel ordre).
    Renvoie (lat, lon), None si ce n'est pas des coordonnées, ou False si elles sont impossibles."""
    s = (s or "").strip().replace("，", ",")
    if not s:
        return None
    f = lambda x: float((x or "0").replace(",", "."))
    if re.fullmatch(r"[\d\s°'’′\"”″.,;:/NSEWOnsewo+-]+", s) and re.search(r"[NSEWO]", s, re.I):
        parts = [(d, mi, se, h) for d, mi, se, h in _HEMI_SUF.findall(s)]
        if len(parts) != 2:
            parts = [(d, mi, se, h) for h, d, mi, se in _HEMI_PRE.findall(s)]
        if len(parts) == 2:
            lat = lon = None
            for d, mi, se, h in parts:
                if f(mi) >= 60 or f(se) >= 60:
                    return False
                v = f(d) + f(mi) / 60 + f(se) / 3600
                if h.upper() in "NS":
                    lat = -v if h.upper() == "S" else v
                else:
                    lon = -v if h.upper() in "WO" else v
            if lat is None or lon is None:
                return False
            return (lat, lon) if coords_valid(lat, lon) else False
    m = re.fullmatch(r"([+-]?\d{1,3}(?:\.\d+)?)\s*[,;]\s*([+-]?\d{1,3}(?:\.\d+)?)", s) or \
        re.fullmatch(r"([+-]?\d{1,3}\.\d+)\s+([+-]?\d{1,3}\.\d+)", s) or \
        re.fullmatch(r"([+-]?\d{1,3},\d+)\s*[; ]\s*([+-]?\d{1,3},\d+)", s)
    if m:
        lat, lon = f(m[1]), f(m[2])
        return (lat, lon) if coords_valid(lat, lon) else False
    return None


# ============================================================ SOLEIL & OMBRES
def sun_pos(dt, lat, lon, refraction=True):
    """dt en UTC (naïf). Renvoie (azimut ° depuis le nord, hauteur °).
    Algorithme NOAA complet (Meeus) : écart < 0,01° sur la position du soleil entre 1900 et 2100.
    refraction=True : hauteur APPARENTE (celle qu'on voit et que les ombres suivent), corrigée de l'atmosphère."""
    jd = (dt - datetime.datetime(2000, 1, 1, 12)).total_seconds() / 86400 + 2451545.0
    T = (jd - 2451545.0) / 36525
    r, d = math.radians, math.degrees
    L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360
    Mn = 357.52911 + T * (35999.05029 - 0.0001537 * T)
    e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T)
    C = math.sin(r(Mn)) * (1.914602 - T * (0.004817 + 0.000014 * T)) + math.sin(r(2 * Mn)) * (0.019993 - 0.000101 * T) + math.sin(r(3 * Mn)) * 0.000289
    om = 125.04 - 1934.136 * T
    lam = L0 + C - 0.00569 - 0.00478 * math.sin(r(om))
    eps = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60 + 0.00256 * math.cos(r(om))
    de = math.asin(math.sin(r(eps)) * math.sin(r(lam)))
    y = math.tan(r(eps / 2)) ** 2
    eq = 4 * d(y * math.sin(2 * r(L0)) - 2 * e * math.sin(r(Mn)) + 4 * e * y * math.sin(r(Mn)) * math.cos(2 * r(L0))
               - 0.5 * y * y * math.sin(4 * r(L0)) - 1.25 * e * e * math.sin(2 * r(Mn)))
    mins = dt.hour * 60 + dt.minute + dt.second / 60 + dt.microsecond / 6e7
    ha = r(((mins + eq + 4 * lon) % 1440) / 4 - 180)
    p = r(lat)
    cz = math.sin(p) * math.sin(de) + math.cos(p) * math.cos(de) * math.cos(ha)
    el = 90 - d(math.acos(max(-1, min(1, cz))))
    az = (d(math.atan2(math.sin(ha), math.cos(ha) * math.sin(p) - math.tan(de) * math.cos(p))) + 180) % 360
    if refraction:
        if el > 85:
            rf = 0
        elif el > 5:
            t = math.tan(r(el))
            rf = 58.1 / t - 0.07 / t ** 3 + 0.000086 / t ** 5
        elif el > -0.575:
            rf = 1735 + el * (-518.2 + el * (103.4 + el * (-12.79 + el * 0.711)))
        else:
            rf = -20.772 / math.tan(r(el))
        el += rf / 3600
    return az, el


SUN_RISE = -0.267  # hauteur apparente du centre du soleil quand son bord supérieur touche l'horizon (lever / coucher officiels)


# ------------------------------------------------------------ RECHERCHE DE PERSONNE
def _strip_acc(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


# ============================================================ OUTILS DE PRÉCISION (recouper, mesurer, prouver)
# ------------------------------------------------------------ 🧬 MÊME PERSONNE ? (recoupement de profils)
def _norm_name(s):
    return re.sub(r"[^a-z0-9 ]", "", _strip_acc(str(s or ""))).strip()


def _profile_text(d):
    return " ".join(str(v) for k, v in d.items() if v and k not in ("_img",)).lower()


def _profile_handles(name, d):
    """Façons dont ce profil peut être cité par un autre : son adresse, et pseudo@plateforme."""
    out = set()
    u = str(d.get("_url") or "").lower()
    if u:
        out.add(re.sub(r"^https?://(www\.)?", "", u).rstrip("/"))
    return out


def profile_match(a, b, same_avatar=None):
    """Compare deux profils (nom de plateforme, fiche). Renvoie (score 0-100, [preuves], niveau A/B/C).
    Une preuve « déclarée » (un profil cite l'autre) vaut bien plus qu'une ressemblance."""
    (na, da), (nb, db) = a, b
    score, why, declared = 0, [], False
    ta, tb = _profile_text(da), _profile_text(db)
    for (n1, d1, t1), (n2, d2, t2) in (((na, da, ta), (nb, db, tb)), ((nb, db, tb), (na, da, ta))):
        tx = " ".join(str(v) for k, v in d1.items() if v and not k.startswith("_")).lower()
        if any(h and h in tx for h in _profile_handles(n2, d2)):
            score += 55
            declared = True
            why.append(f"le profil {n1} affiche un lien vers le profil {n2} (déclaré par son propriétaire)")
    ea, eb = set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", ta)), set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", tb))
    common = {e for e in ea & eb if "noreply" not in e}
    if common:
        score += 45
        declared = True
        why.append(f"même email sur les deux profils : {', '.join(sorted(common)[:2])}")
    if same_avatar is True:
        score += 40
        why.append("même photo de profil (empreinte visuelle identique)")
    n1, n2 = _norm_name(da.get("Nom")), _norm_name(db.get("Nom"))
    if n1 and n1 == n2:
        if len(n1.split()) >= 2:
            score += 20
            why.append(f"même nom complet affiché : {da.get('Nom')}")
        elif len(n1) >= 4:
            score += 6
            why.append(f"même nom affiché (un seul mot, peu distinctif) : {da.get('Nom')}")
    sa = {re.sub(r"^https?://(www\.)?", "", x).rstrip("/") for x in re.findall(r"https?://[^\s\"'<>)]+", " ".join(str(da.get(k) or "") for k in ("Site", "Lien", "Bio")).lower())}
    sb = {re.sub(r"^https?://(www\.)?", "", x).rstrip("/") for x in re.findall(r"https?://[^\s\"'<>)]+", " ".join(str(db.get(k) or "") for k in ("Site", "Lien", "Bio")).lower())}
    if sa & sb:
        score += 30
        why.append(f"même site personnel indiqué : {sorted(sa & sb)[0]}")
    l1, l2 = _norm_name(da.get("Lieu")), _norm_name(db.get("Lieu"))
    if l1 and l1 == l2:
        score += 8
        why.append(f"même lieu indiqué : {da.get('Lieu')}")
    score = min(score, 100)
    level = "A" if declared and score >= 55 else "B" if score >= 40 else "C"
    return score, why, level


def match_verdict(score, level):
    if level == "A":
        return "même personne : établi (lien déclaré par le titulaire du compte)"
    if score >= 60:
        return "même personne : très probable (plusieurs indices concordants)"
    if score >= 40:
        return "même personne : probable, à confirmer par un indice de plus"
    if score >= 15:
        return "lien possible, pas prouvé"
    return "aucun lien démontré : le pseudo identique ne prouve rien"


EDITORS = ("photoshop", "lightroom", "gimp", "snapseed", "picsart", "pixelmator", "affinity", "canva", "facetune", "paint.net", "capture one", "luminar", "darktable", "remini")


def photo_checks(t, gps, tz_s, lum):
    """Contrôles de cohérence. t = exif_times(), gps = (lat, lon) ou None, tz_s = décalage horaire réel du lieu (s) ou None,
    lum = luminosité moyenne du haut de l'image (0-255) ou None. Renvoie [(état ok/warn/bad/info, titre, détail)]."""
    R_ = []
    utc = t.get("gps_utc")
    loc = t.get("local")
    if loc and utc:
        diff = (loc - utc).total_seconds()
        if t.get("offset_s") is not None:
            ok = abs(diff - t["offset_s"]) <= 120
            R_.append(("ok" if ok else "bad", "Heure de l'appareil ↔ heure GPS",
                       f"l'écart ({diff / 3600:+.2f} h) correspond au fuseau enregistré" if ok else
                       f"écart de {diff / 3600:+.2f} h alors que le fichier annonce UTC{t['offset_s'] / 3600:+.2f} : dates modifiées ou appareil mal réglé"))
        if tz_s is not None:
            d2 = abs(diff - tz_s)
            st = "ok" if d2 <= 180 else "warn" if abs(d2 - 3600) <= 180 else "bad"
            R_.append((st, "Heure de l'appareil ↔ fuseau du lieu GPS",
                       f"l'appareil était bien à l'heure locale du lieu (UTC{tz_s / 3600:+.2f})" if st == "ok" else
                       "1 h d'écart : appareil resté à l'heure d'été / d'hiver, ou pas remis à l'heure" if st == "warn" else
                       f"l'appareil affiche UTC{diff / 3600:+.2f} mais le lieu GPS est en UTC{tz_s / 3600:+.2f} : appareil réglé sur un autre fuseau (voyage) ou métadonnées retouchées"))
    elif loc and not utc:
        R_.append(("info", "Heure GPS", "absente : l'heure vient seulement de l'horloge de l'appareil, que son propriétaire peut régler comme il veut"))
    if utc is None and loc and (t.get("offset_s") is not None or tz_s is not None):
        utc = loc - datetime.timedelta(seconds=t["offset_s"] if t.get("offset_s") is not None else tz_s)
    if utc and gps:
        az, el = sun_pos(utc, gps[0], gps[1])
        phase = "nuit noire" if el < -12 else "crépuscule" if el < -0.8 else "soleil très bas (lever / coucher)" if el < 6 else "plein jour"
        det = f"à ce moment et à cet endroit : {phase}, soleil à {el:.1f}° de hauteur, azimut {az:.0f}° ({cardinal(az)})"
        if el > 3:
            det += f" · une ombre mesure {1 / math.tan(math.radians(el)):.2f} × la hauteur de l'objet et pointe vers le {cardinal((az + 180) % 360)} ({(az + 180) % 360:.0f}°)"
        R_.append(("info", "Position du soleil calculée", det))
        if lum is not None:
            if el < -8 and lum > 140:
                R_.append(("warn", "Luminosité ↔ heure", f"ciel très clair (luminosité {lum:.0f}/255) alors qu'il faisait nuit : incohérent pour une photo d'extérieur (normal en intérieur éclairé)"))
            elif el > 12 and lum < 30:
                R_.append(("warn", "Luminosité ↔ heure", f"image très sombre (luminosité {lum:.0f}/255) alors qu'il faisait plein jour : incohérent pour une photo d'extérieur (normal en intérieur sombre)"))
            else:
                R_.append(("ok", "Luminosité ↔ heure", f"la luminosité de l'image ({lum:.0f}/255) est compatible avec l'heure"))
    if t.get("modified") and loc and abs((t["modified"] - loc).total_seconds()) > 120:
        R_.append(("warn", "Date de modification", f"fichier ré-enregistré le {t['modified']:%d/%m/%Y %H:%M} (prise de vue : {loc:%d/%m/%Y %H:%M}) : il est passé par un logiciel"))
    sw = (t.get("software") or "").lower()
    if any(e in sw for e in EDITORS):
        R_.append(("warn", "Logiciel", f"« {t['software']} » : logiciel de retouche, l'image a pu être modifiée"))
    elif t.get("software"):
        R_.append(("info", "Logiciel", f"« {t['software']} » (logiciel de l'appareil ou d'export)"))
    if loc and loc > datetime.datetime.now() + datetime.timedelta(days=1):
        R_.append(("bad", "Date", "la photo est datée dans le futur : horloge fausse ou date modifiée"))
    if not loc and not utc:
        R_.append(("info", "Dates", "aucune date dans le fichier (normal pour une image passée par un réseau social ou une messagerie : les métadonnées sont effacées)"))
    return R_


def los_compute(d_km, elev, obs_h, tgt_h, k=0.13):
    """Ligne de vue entre le premier et le dernier point d'un profil.
    d_km : distances depuis l'observateur · elev : altitudes du sol (m) · k : réfraction de l'air (0,13 = standard).
    Renvoie {visible, marge_m, i_bloc, cache_m (hauteur de la cible masquée), besoin_m (hauteur mini de la cible pour être vue)}."""
    D = d_km[-1]
    Reff = 6371.0088 / (1 - k)
    hA, hB = elev[0] + obs_h, elev[-1] + tgt_h
    marge, i_bloc, need_top = float("inf"), None, elev[-1]
    for i in range(1, len(d_km) - 1):
        d = d_km[i]
        obst = elev[i] + d * (D - d) / (2 * Reff) * 1000  # sol + bombement de la Terre vu depuis la corde A-B
        line = hA + (hB - hA) * d / D
        if line - obst < marge:
            marge, i_bloc = line - obst, i
        need_top = max(need_top, hA + (obst - hA) * D / d)
    cache = max(0.0, need_top - elev[-1])
    return {"visible": marge > 0, "marge_m": marge, "i_bloc": i_bloc, "cache_m": min(cache, tgt_h) if tgt_h else cache, "besoin_m": cache}


# ------------------------------------------------------------ 📐 RELÈVEMENT : position par recoupement d'azimuts
def resect(obs, sigma=3.0, n_mc=400, seed=1):
    """obs : [(lat, lon, azimut)] = repères connus et direction (° depuis le nord) dans laquelle on les voit.
    Renvoie {lat, lon, r95_m (rayon contenant 95 % des tirages), angle_min (° entre les lignes), behind (repères incohérents)}."""
    if len(obs) < 2:
        return None
    la0 = sum(o[0] for o in obs) / len(obs)
    lo0 = sum(o[1] for o in obs) / len(obs)
    kx, ky = 111.320 * math.cos(math.radians(la0)), 110.574  # km par degré, plan local
    P = [((o[1] - lo0) * kx, (o[0] - la0) * ky) for o in obs]

    def solve(bs):
        a11 = a12 = a22 = b1 = b2 = 0.0
        for (px, py), b in zip(P, bs):
            nx, ny = math.cos(math.radians(b)), -math.sin(math.radians(b))  # normale à la ligne de visée
            c = nx * px + ny * py
            a11 += nx * nx
            a12 += nx * ny
            a22 += ny * ny
            b1 += nx * c
            b2 += ny * c
        det = a11 * a22 - a12 * a12
        if abs(det) < 1e-9:
            return None
        return (b1 * a22 - b2 * a12) / det, (a11 * b2 - a12 * b1) / det
    bs = [o[2] for o in obs]
    X = solve(bs)
    if X is None:
        return None
    behind = [i for i, ((px, py), b) in enumerate(zip(P, bs)) if (px - X[0]) * math.sin(math.radians(b)) + (py - X[1]) * math.cos(math.radians(b)) <= 0]
    amin = min((min(abs((b1 - b2) % 180), 180 - abs((b1 - b2) % 180)) for i, b1 in enumerate(bs) for b2 in bs[i + 1:]), default=0)
    rnd = random.Random(seed)
    ds = []
    for _ in range(n_mc):
        Y_ = solve([b + rnd.gauss(0, sigma) for b in bs])
        if Y_:
            ds.append(math.hypot(Y_[0] - X[0], Y_[1] - X[1]))
    ds.sort()
    r95 = ds[int(len(ds) * 0.95) - 1] * 1000 if ds else float("inf")
    return {"lat": la0 + X[1] / ky, "lon": lo0 + X[0] / kx, "r95_m": r95, "angle_min": amin, "behind": behind}


def dns_agree(answers):
    """answers : {résolveur: ensemble ou None}. Renvoie (état, valeurs communes, valeurs vues par certains seulement)."""
    ok = {k: v for k, v in answers.items() if v is not None}
    if not ok:
        return "aucune réponse", set(), set()
    sets = list(ok.values())
    common, union = set.intersection(*sets), set.union(*sets)
    if len(ok) < 2:
        return "1 seul résolveur a répondu : non recoupé", common, set()
    if common == union:
        return f"identique sur {len(ok)} résolveurs", common, set()
    return ("réponses différentes selon le résolveur", common, union - common)




# ============================================================ MESURES SUR PHOTO (photogrammétrie simple)
def focal_px(f35, w, h):
    """Focale en pixels à partir de la focale « équivalent 35 mm » : le grand côté de l'image correspond à 36 mm."""
    if not f35 or f35 <= 0 or not w or not h:
        return None
    return f35 * max(w, h) / 36.0


def dist_from_size(real_m, size_px, fpx):
    """Distance de l'objet (m) quand on connaît sa taille réelle et sa taille sur la photo."""
    if not fpx or size_px <= 0 or real_m <= 0:
        return None
    return real_m * fpx / size_px


def size_from_dist(dist_m, size_px, fpx):
    """Taille réelle de l'objet (m) quand on connaît sa distance."""
    if not fpx or size_px <= 0 or dist_m <= 0:
        return None
    return size_px * dist_m / fpx


def measure_range(fn, a, size_px, fpx, px_err=2.0, focal_err=0.05):
    """Fourchette (min, max) d'une mesure pour une erreur de ± px_err pixels et ± focal_err sur la focale."""
    vals = [fn(a, max(size_px + dp, 0.5), fpx * (1 + df)) for dp in (-px_err, px_err) for df in (-focal_err, focal_err)]
    vals = [v for v in vals if v]
    return (min(vals), max(vals)) if vals else None


def height_from_shadow(shadow_m, sun_el):
    """Hauteur d'un objet vertical d'après la longueur de son ombre au sol et la hauteur du soleil (°)."""
    if shadow_m <= 0 or not 0.5 <= sun_el < 89.5:
        return None
    return shadow_m * math.tan(math.radians(sun_el))


# ============================================================ CHRONOLOGIE D'UN DOSSIER
_DATE_FR = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})(?:[ T](\d{1,2}):(\d{2}))?")
_DATE_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?")


def find_dates(text):
    """Dates écrites dans un texte (JJ/MM/AAAA ou AAAA-MM-JJ, heure facultative). Renvoie [(datetime, précise à l'heure ?)]."""
    out = []
    for rx, order in ((_DATE_FR, (2, 1, 0)), (_DATE_ISO, (0, 1, 2))):
        for m in rx.finditer(str(text or "")):
            g = m.groups()
            try:
                y, mo, d = int(g[order[0]]), int(g[order[1]]), int(g[order[2]])
                if not 1970 <= y <= 2100:
                    continue
                out.append((datetime.datetime(y, mo, d, int(g[3] or 0), int(g[4] or 0)), g[3] is not None))
            except (ValueError, TypeError):
                continue
    return out


TL_SKIP = ("vérifié le", "_", "note")


def timeline_events(g):
    """Événements datés d'un dossier : [(datetime, heure connue ?, élément, type, nature de la date)], du plus ancien au plus récent.
    Les dates de vérification et d'ajout au dossier sont exclues : ce sont les dates de l'enquête, pas celles des faits."""
    ev = []
    for nid, n in (g.get("nodes") or {}).items():
        if n.get("type") == "enquete":
            continue
        for k, v in (n.get("data") or {}).items():
            if k.startswith("_") or k in TL_SKIP or not isinstance(v, (str, int, float)):
                continue
            for d, precise in find_dates(v):
                ev.append((d, precise, n.get("label", nid), n.get("type", "autre"), k))
        for d, precise in find_dates(n.get("label", "")):
            ev.append((d, precise, n.get("label", nid), n.get("type", "autre"), "dans le nom"))
    seen, out = set(), []
    for e in sorted(ev, key=lambda x: x[0]):
        key = (e[0], e[2], e[4])
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


# ============================================================ EXPORT DES LIEUX (KML / GeoJSON / CSV)
def places_of(g):
    """Lieux d'un dossier qui ont des coordonnées : [{name, lat, lon, fiab, source, marge}]."""
    out = []
    for nid, n in (g.get("nodes") or {}).items():
        if n.get("type") != "lieu":
            continue
        d = n.get("data") or {}
        c = coords_only(str(d.get("coordonnées") or "")) or coords_only(n.get("label", ""))
        if not c:
            continue
        out.append({"name": n.get("label", nid), "lat": c[0], "lon": c[1], "fiab": d.get("_fiab") or "?",
                    "source": str(d.get("source") or ""), "marge": str(d.get("marge") or "")})
    return out


def _xml(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


KML_COL = {"A": "ff7aaf4c", "B": "ffff9d5b", "C": "ff3aa8e0", "?": "ff79706b"}  # format KML : aabbggrr


def to_kml(places, title="Dossier"):
    """Fichier KML lisible par Google Earth : une épingle par lieu, colorée selon sa fiabilité."""
    styles = "".join(f'<Style id="f{k}"><IconStyle><color>{c}</color><scale>1.1</scale></IconStyle></Style>' for k, c in KML_COL.items())
    marks = "".join(
        f'<Placemark><name>{_xml(p["name"])}</name><styleUrl>#f{p["fiab"] if p["fiab"] in KML_COL else "?"}</styleUrl>'
        f'<description>{_xml("Fiabilité : " + FIAB.get(p["fiab"], "non évaluée") + (" · marge " + p["marge"] if p["marge"] else "") + (" · source : " + p["source"] if p["source"] else ""))}</description>'
        f'<Point><coordinates>{p["lon"]:.7f},{p["lat"]:.7f},0</coordinates></Point></Placemark>' for p in places)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>{_xml(title)}</name>{styles}{marks}</Document></kml>\n'


def to_geojson(places):
    """Dictionnaire GeoJSON (ordre longitude, latitude imposé par la norme)."""
    return {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(p["lon"], 7), round(p["lat"], 7)]},
         "properties": {"nom": p["name"], "fiabilite": p["fiab"], "source": p["source"], "marge": p["marge"]}} for p in places]}


# ============================================================ JOURNAL DE PREUVES (chaîne d'empreintes)
def evidence_entry(prev_hash, data, meta, when=None):
    """Nouvelle ligne du journal de preuves. Chaque ligne contient l'empreinte de la précédente :
    modifier ou supprimer une ancienne ligne casse la chaîne, ce que evidence_verify() détecte."""
    import hashlib
    import json
    e = {"n": None, "date_utc": (when or datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "sha256": hashlib.sha256(data).hexdigest(), "taille": len(data), "prec": prev_hash or "", **{k: v for k, v in meta.items() if v not in (None, "")}}
    body = json.dumps({k: v for k, v in e.items() if k not in ("n", "chaine")}, sort_keys=True, ensure_ascii=False)
    e["chaine"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return e


def evidence_verify(journal, files=None):
    """Contrôle un journal. files : {nom de fichier: contenu en octets} pour vérifier aussi les copies enregistrées.
    Renvoie (ok ?, [problèmes])."""
    import hashlib
    import json
    pb, prev = [], ""
    for i, e in enumerate(journal, 1):
        body = json.dumps({k: v for k, v in e.items() if k not in ("n", "chaine")}, sort_keys=True, ensure_ascii=False)
        if hashlib.sha256(body.encode("utf-8")).hexdigest() != e.get("chaine"):
            pb.append(f"preuve n°{i} : la ligne du journal a été modifiée")
        if e.get("prec", "") != prev:
            pb.append(f"preuve n°{i} : la chaîne est rompue (une ligne a été supprimée, ajoutée ou déplacée avant elle)")
        prev = e.get("chaine", "")
        if files is not None and e.get("fichier"):
            data = files.get(e["fichier"])
            if data is None:
                pb.append(f"preuve n°{i} : le fichier {e['fichier']} est introuvable")
            elif hashlib.sha256(data).hexdigest() != e.get("sha256"):
                pb.append(f"preuve n°{i} : le fichier {e['fichier']} a été modifié depuis la capture")
    return not pb, pb


# ============================================================ RECHERCHE DE PERSONNE : trier les vrais profils des homonymes
def name_tokens(s):
    """Mots d'un nom, sans accents ni majuscules ni ponctuation (« Jean-Noël DUPONT » → ["jean", "noel", "dupont"])."""
    return [t for t in re.split(r"[^a-z0-9]+", _strip_acc(str(s or ""))) if t]


_PARTICLES = {"de", "du", "des", "le", "la", "les", "en", "sur", "sous", "aux", "l", "d"}
_ABBR = {"st": "saint", "ste": "sainte"}
# après une ville, « le / la » annonce un quartier de cette ville (« Cannes la Bocca »), pas une autre commune
_CITY_LINK = {"de", "du", "des", "d", "en", "sur", "sous", "aux", "les"}


def _groups(s):
    """Découpe un texte en mots entiers. Un mot à traits d'union (« Dupont-Aignan », « Sainte-Foy-lès-Lyon ») reste UN seul bloc,
    l'apostrophe colle les lettres (« O'Connor » → « oconnor »). Renvoie [(mot collé sans accents, mot d'origine)]."""
    out = []
    for w in re.findall(r"[^\W_]+(?:[-'’][^\W_]+)*", str(s or ""), re.UNICODE):
        parts = [_ABBR.get(p, p) for p in re.split(r"-", _strip_acc(w).replace("'", "").replace("’", "")) if p]
        glue = "".join(parts)
        if re.search(r"[a-z]", glue):
            glue = re.sub(r"\d+$", "", glue)  # « jean69 » → « jean » : chiffres ajoutés à un nom dans un pseudo
        if glue:
            out.append((glue, w))
    return out


def _runs(groups, target):
    """Positions (début, fin) où une suite de mots entiers, collés, donne exactement `target`."""
    res = []
    for a in range(len(groups)):
        acc = ""
        for b in range(a, len(groups)):
            acc += groups[b][0]
            if acc == target:
                res.append((a, b + 1))
            if len(acc) >= len(target):
                break
    return res


def _glue(s):
    return "".join(g[0] for g in _groups(s))


def name_match(shown, first, last):
    """Compare un nom affiché sur un profil au nom cherché. Renvoie 3 (prénom et nom entiers présents),
    2 (nom de famille + initiale du prénom), 1 (un seul des deux) ou 0 (rien).
    Un nom composé n'est pas confondu avec une de ses parties : « Dupont-Aignan » n'est pas « Dupont »."""
    gr = _groups(shown)
    tf, tl = _glue(first), _glue(last)
    if not gr or not tf or not tl:
        return 0
    if len(gr) == 1 and gr[0][0] in (tf + tl, tl + tf):
        return 3
    lasts = []
    for a, b in _runs(gr, tl):
        glued = b - a > len(_groups(last))  # plusieurs mots recollés pour former le nom (« du Pont » → « Dupont »)
        if glued and b < len(gr) and gr[b][0] in _PARTICLES:
            continue  # le nom continue après (« du Pont de Nemours ») : ce n'est pas le même nom
        lasts.append((a, b))
    firsts = _runs(gr, tf)
    for la, lb in lasts:
        if any(fb <= la or fa >= lb for fa, fb in firsts):
            return 3
    if lasts:
        initials = "".join(g[0][:1] for g in _groups(first))
        la, lb = lasts[0]
        for k, (w, _) in enumerate(gr):
            if not la <= k < lb and len(w) <= 2 and (w == initials or w == tf[:1] or (len(w) == 2 and w == initials[:2])):
                return 2
        return 1
    return 1 if firsts else 0


def city_match(text, city):
    """La ville cherchée apparaît-elle dans ce texte (lieu, bio) comme nom entier ?
    « Lyon » n'est pas trouvé dans « Sainte-Foy-lès-Lyon », « Tours » pas dans « Joué-lès-Tours », « Nice » pas dans « very nice »."""
    tc = _glue(city)
    gr = _groups(text)
    if not tc or not gr:
        return False
    capitals = sum(1 for _, w in gr if w[:1].isupper())
    for a, b in _runs(gr, tc):
        if b < len(gr) and gr[b][0] in _CITY_LINK and b + 1 < len(gr):
            continue  # « Saint Étienne du Rouvray », « Toulon sur Arroux » : une autre commune
        if a > 0 and gr[a - 1][0] in ("les", "sur", "sous") and a > 1:
            continue  # « Joué lès Tours » : une autre commune
        if len(gr) >= 3 and capitals and not any(w[:1].isupper() for _, w in gr[a:b]):
            continue  # mot commun en minuscules dans une phrase (« very nice guy »), pas un nom de ville
        return True
    return False


def person_usernames(first, last, limit=8):
    """Pseudos les plus courants pour ce nom, du plus probable au moins probable."""
    f, l = "".join(name_tokens(first)), "".join(name_tokens(last))
    if not f or not l:
        return []
    cand = [f + l, f"{f}.{l}", f"{f}_{l}", l + f, f[:1] + l, f"{l}.{f}", f"{f}-{l}", l + f[:1], f"{f}{l[:1]}", f"{l}_{f}"]
    return list(dict.fromkeys(c for c in cand if 3 <= len(c) <= 30))[:limit]


PERSON_VERDICT = {"fort": "nom et ville correspondent", "moyen": "nom identique, ville non confirmée : homonyme possible",
                  "faible": "nom partiel seulement : à écarter sauf autre indice", "aucun": "même pseudo, autre nom : probablement quelqu'un d'autre"}


def person_score(profile, first, last, city=""):
    """Note un profil public par rapport à la personne cherchée. Renvoie (score 0-100, verdict, [raisons], niveau B/C/None).
    Jamais « A » : un nom et une ville identiques ne prouvent pas que le compte appartient à cette personne."""
    shown = profile.get("Nom") or ""
    lvl = name_match(shown, first, last)
    score, why = {3: 60, 2: 30, 1: 10, 0: 0}[lvl], []
    if lvl == 3:
        why.append(f"nom affiché identique : {shown}")
    elif lvl == 2:
        why.append(f"nom de famille + initiale : {shown}")
    elif lvl == 1:
        why.append(f"un seul des deux noms : {shown}")
    elif shown:
        why.append(f"nom affiché différent : {shown}")
    else:
        why.append("aucun nom affiché sur le profil")
    in_place = bool(city) and city_match(profile.get("Lieu"), city)
    in_bio = bool(city) and not in_place and city_match(" ".join(str(profile.get(k) or "") for k in ("Bio", "À propos", "Entreprise", "Site", "Lien")), city)
    if in_place:
        score += 30
        why.append(f"lieu indiqué : {profile.get('Lieu')}")
    elif in_bio:
        score += 18
        why.append(f"« {city} » cité dans la présentation")
    elif city and profile.get("Lieu"):
        score -= 15
        why.append(f"autre lieu indiqué : {profile.get('Lieu')}")
    score = max(0, min(score, 100))
    if lvl == 3 and (in_place or in_bio):
        verdict, level = "fort", "B"
    elif lvl == 3:
        verdict, level = "moyen", "C"
    elif lvl == 2 and (in_place or in_bio):
        verdict, level = "moyen", "C"
    elif lvl >= 1:
        verdict, level = "faible", None
    else:
        verdict, level = "aucun", None
    return score, verdict, why, level


# ============================================================ MISE À JOUR DEPUIS LE DÉPÔT (comparaison fichier par fichier)
# Jamais écrasés ni supprimés par une mise à jour : les données de l'utilisateur
UPDATE_PROTECTED_DIRS = ("resultats", "cache", "cours", "projets", "lang", "sauvegarde_maj", "CatExe-OSINT", "build", "dist", ".git", "__pycache__")
UPDATE_PROTECTED_FILES = ("config.json", "historique_noms.json", "progression.json", "progression_cours.json", "marques.txt")


def git_blob_sha(data):
    """Empreinte qu'utilise Git pour un fichier : permet de savoir, sans rien télécharger, si un fichier local est identique à celui du dépôt."""
    import hashlib
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def update_safe_path(path):
    """Chemin du dépôt acceptable pour une mise à jour ? Refuse tout ce qui sortirait du dossier de l'outil."""
    p = str(path or "")
    if not p or p.startswith(("/", "\\")) or "\\" in p or ":" in p or "\0" in p:
        return False
    parts = p.split("/")
    return all(x not in ("", ".", "..") for x in parts)


def update_protected(path):
    """Ce chemin fait-il partie des données de l'utilisateur (résultats, réglages, journaux…) ?"""
    parts = str(path).split("/")
    return parts[0] in UPDATE_PROTECTED_DIRS or (len(parts) == 1 and parts[0] in UPDATE_PROTECTED_FILES) or parts[-1].lower().endswith(".log")


def update_plan(tree, read_local):
    """tree : liste de fichiers du dépôt [{"path", "sha", "type"}] · read_local(chemin) → octets ou None si absent.
    Renvoie les fichiers à télécharger [(chemin, sha, "nouveau" | "modifié")]. Les données de l'utilisateur n'y figurent jamais."""
    plan = []
    for f in tree or []:
        p = f.get("path")
        if f.get("type") != "blob" or not update_safe_path(p) or update_protected(p):
            continue
        local = read_local(p)
        if local is None:
            plan.append((p, f["sha"], "nouveau"))
        elif git_blob_sha(local) != f["sha"] and git_blob_sha(local.replace(b"\r\n", b"\n")) != f["sha"]:
            plan.append((p, f["sha"], "modifié"))
    return plan


# ============================================================ MOTEUR SHERLOCK (règles de détection, sans réseau)
# Pages d'attente ou de blocage : elles répondent « 200 » à tout et fabriquent des faux positifs
WAF_MARKS = ("just a moment...", "attention required! | cloudflare", "cf-browser-verification", "cf-challenge", "/cdn-cgi/challenge-platform",
             "checking your browser before accessing", "access denied", "request unsuccessful. incapsula", "captcha-delivery.com", "px-captcha",
             "are you a robot", "unusual traffic", "ddos protection by")


def looks_blocked(text):
    """La réponse est-elle une page anti-robot plutôt que la vraie page du site ?"""
    t = str(text or "")[:20000].lower()
    return any(m in t for m in WAF_MARKS)


def sherlock_valid(site, username):
    """Le pseudo respecte-t-il la forme imposée par ce site ? (sinon le compte ne peut pas exister : inutile d'interroger le site)"""
    rx = site.get("regexCheck")
    if not rx:
        return True
    try:
        return re.search(rx, username) is not None
    except re.error:
        return True


def sherlock_verdict(site, status, text, username=""):
    """Applique la règle Sherlock d'un site à une réponse. Renvoie True (compte présent), False (absent) ou None (réponse inexploitable).
    status = code HTTP · text = corps de la réponse."""
    if status is None:
        return None
    if status in (403, 429, 503) or looks_blocked(text):
        return None
    kind = site.get("errorType")
    if kind == "message":
        errs = site.get("errorMsg")
        errs = [errs] if isinstance(errs, str) else list(errs or [])
        if not errs:
            return None
        if any(e and e in (text or "") for e in errs):
            return False
        return True if 200 <= status < 300 else None
    if kind == "status_code":
        codes = site.get("errorCode")
        codes = [codes] if isinstance(codes, int) else list(codes or [])
        if status in codes:
            return False
        return 200 <= status < 300
    if kind == "response_url":
        return 200 <= status < 300  # la requête est faite sans suivre les redirections
    return None


def echoes(username, text, url=""):
    """Le pseudo apparaît-il vraiment dans la page ou dans son adresse finale ? Une vraie page de profil le contient presque toujours."""
    u = str(username or "").lower()
    if len(u) < 3:
        return False
    hay = (str(text or "")[:600000] + " " + str(url or "")).lower()
    return re.search(r"(?<![a-z0-9])" + re.escape(u) + r"(?![a-z0-9])", hay) is not None


def host_key(url):
    """Nom de site comparable entre deux bases (« https://www.GitHub.com/x » → « github.com »)."""
    m = re.match(r"^[a-z]+://([^/?#]+)", str(url or "").lower())
    h = (m.group(1) if m else "").split("@")[-1].split(":")[0]
    return h[4:] if h.startswith("www.") else h


def merge_hits(hits):
    """Fusionne les résultats de plusieurs moteurs. hits : [{site, cat, url, engine, echo}].
    Renvoie une ligne par site : {site, cat, url, engines (triés), echo, conf}.
    conf = « forte » si deux moteurs indépendants sont d'accord ou si la page contient le pseudo, sinon « moyenne »."""
    by = {}
    for h in hits:
        k = host_key(h.get("url")) or str(h.get("site", "")).lower()
        e = by.setdefault(k, {"site": h.get("site"), "cat": h.get("cat") or "", "url": h.get("url"), "engines": set(), "echo": False})
        e["engines"].add(h.get("engine"))
        e["echo"] = e["echo"] or bool(h.get("echo"))
        e["cat"] = e["cat"] or h.get("cat") or ""
    out = []
    for e in by.values():
        e["engines"] = sorted(x for x in e["engines"] if x)
        e["conf"] = "forte" if len(e["engines"]) >= 2 or e["echo"] else "moyenne"
        out.append(e)
    out.sort(key=lambda e: (e["conf"] != "forte", str(e["site"]).lower()))
    return out


# ============================================================ ADRESSES IP EN LOT
def extract_ips(text, limit=None):
    """Adresses IP publiques trouvées dans un texte, sans doublon, dans l'ordre d'apparition.
    Les adresses privées, locales ou réservées sont écartées (elles n'existent que dans un réseau interne)."""
    import ipaddress
    out, seen = [], set()
    cand = re.findall(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])|(?<![0-9a-fA-F:])(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}(?![0-9a-fA-F:])", str(text or ""))
    for c in cand:
        try:
            ip = ipaddress.ip_address(c)
        except ValueError:
            continue
        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast or ip.is_link_local or ip.is_unspecified:
            continue
        s = str(ip)
        if s not in seen:
            seen.add(s)
            out.append(s)
            if limit and len(out) >= limit:
                break
    return out


def ip_summary(rows):
    """rows : [{ip, cc, country, asn, isp, level, flags}]. Renvoie les décomptes par pays, par opérateur et par signalement."""
    by_cc, by_asn, flags = Counter(), Counter(), Counter()
    for r in rows:
        by_cc[r.get("country") or r.get("cc") or "inconnu"] += 1
        by_asn[(f"AS{r['asn']} " if r.get("asn") else "") + str(r.get("isp") or "inconnu")] += 1
        for f in r.get("flags") or []:
            flags[f] += 1
    return {"total": len(rows), "pays": by_cc.most_common(), "operateurs": by_asn.most_common(), "signalements": flags.most_common(),
            "surs": sum(1 for r in rows if r.get("level") == "A")}

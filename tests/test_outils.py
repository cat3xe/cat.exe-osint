"""Chemin « réseau qui répond » des nouveaux outils : aucune exception, et le contenu attendu.
Les réponses réseau sont simulées (aucun site réel n'est interrogé)."""
import contextlib
import io
import json
import unittest

import test_sites  # charge osint_tool une seule fois
O = test_sites.O


class Rep:
    def __init__(self, text):
        self.text, self.status_code, self.ok, self.content, self.history, self.url = text, 200, True, text.encode(), [], ""

    def json(self):
        return json.loads(self.text)


def faux_json(url, timeout=12, **kw):
    p = kw.get("params") or {}
    if "elevation" in url:
        return {"elevation": [100 + 3 * i for i in range(len(p["latitude"].split(",")))]}
    if "dns" in url or "cloudflare" in url or "quad9" in url:
        t = p.get("type")
        ans = [{"type": 1, "data": "93.184.216.34"}] if t == "A" else [{"type": 15, "data": "10 mail.example.com."}] if t == "MX" else []
        return {"Status": 0, "AD": False, "Answer": ans}
    if "prefix-overview" in url:
        return {"data": {"asns": [{"asn": 15169, "holder": "GOOGLE"}], "resource": "8.8.8.0/24"}}
    if "internetdb" in url:
        return {"ports": [53, 443], "vulns": [], "hostnames": ["dns.google"]}
    if "abuse" in url:
        return {"data": {"abuse_contacts": ["abuse@example.org"]}}
    return {}


class Outils(unittest.TestCase):
    def setUp(self):
        self.sauv = {k: getattr(O, k) for k in ("get", "get_json", "ask_text", "ask_num", "ask_yes", "ask_pos", "pause", "select",
                                                "table_pages", "view_pages", "save_open", "add_report", "tz_offset", "_quiet_social", "ip_geo")}
        self.rapports = []
        O.get_json = faux_json
        O.get = lambda url, timeout=12, **kw: Rep("")
        O.pause = lambda *a, **k: None
        O.select = lambda *a, **k: None
        O.save_open = lambda *a, **k: None
        O.table_pages = lambda *a, **k: None
        O.view_pages = lambda *a, **k: None
        O.add_report = lambda mod, titre, texte: self.rapports.append((mod, str(texte)))
        O.tz_offset = lambda la, lo, d: (7200, "Europe/Paris")
        O.ask_yes = lambda q, default=False: False
        O.ask_num = lambda q, default="0": float(default)
        O._quiet_social = lambda u: ([("GitHub", "x", {"Nom": "Alice Martin", "_url": "https://github.com/alice",
                                                        "Emails trouvés dans les commits": "alice@ex.com (A)"}),
                                      ("Mastodon", "x", {"Nom": "Alice Martin", "Bio": "https://github.com/alice",
                                                         "_url": "https://m.social/@alice"})], [])

    def tearDown(self):
        for k, v in self.sauv.items():
            setattr(O, k, v)

    def lance(self, f, textes=(), positions=()):
        t, p = list(textes), list(positions)
        O.ask_text = lambda q, default=None, password=False: t.pop(0) if t else (default or "")
        O.ask_pos = lambda label="Lieu": p.pop(0) if p else (48.8566, 2.3522)
        with contextlib.redirect_stdout(io.StringIO()):
            f()

    def test_meme_personne_trouve_le_lien_declare(self):
        self.lance(O.mod_sameperson, ["alice", "alice"])
        textes = " ".join(t for m, t in self.rapports if m == "Même personne")
        self.assertIn("lien déclaré", textes.replace("déclaré par son propriétaire", "lien déclaré"))

    def test_ligne_de_vue_sans_erreur(self):
        self.lance(O.mod_los, [], [(48.8566, 2.3522), (48.9, 2.4)])
        self.assertTrue(any(m == "Ligne de vue" for m, _ in self.rapports))

    def test_dns_recoupe_identique(self):
        O.ask_text = lambda q, default=None, password=False: "example.com"
        with contextlib.redirect_stdout(io.StringIO()):
            O.mod_dnscheck()
        texte = " ".join(t for m, t in self.rapports if m == "DNS recoupé")
        self.assertIn("identique sur 3 résolveurs", texte)

    def test_ip_pays_recoupe(self):
        O.ip_geo = lambda ip: O.ip_consensus({
            "ipwho.is": {"cc": "US", "country": "United States", "city": "Mountain View", "lat": 37.4, "lon": -122.07},
            "ip-api.com": {"cc": "US", "country": "United States", "city": "Mountain View", "lat": 37.41, "lon": -122.08},
            "ipinfo.io": {"cc": "US", "country": "United States", "city": "Mountain View", "lat": 37.4, "lon": -122.07}})
        self.lance(O.mod_iplookup, ["8.8.8.8"])
        texte = " ".join(t for m, t in self.rapports if m == "IP lookup")
        self.assertIn("pays sûr", texte)

    def test_bilan_vide_sans_exception(self):
        O.CFG["enquete"] = "test_bilan_vide"
        O._G.clear()
        self.lance(O.mod_fiab)


if __name__ == "__main__":
    unittest.main()

"""Décodeurs, formats et lecture des réponses de services (réponses simulées au format documenté par chaque service)."""
import datetime
import json
import unittest

import test_sites  # charge osint_tool une seule fois
O = test_sites.O


class Rep:
    def __init__(self, data, code=200, headers=None):
        self.text = data if isinstance(data, str) else json.dumps(data)
        self.status_code, self.ok, self.headers, self.history, self.url = code, code < 400, headers or {}, [], ""
        self.content = self.text.encode()

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise O.requests.HTTPError(str(self.status_code))


class Formats(unittest.TestCase):
    def test_iban_valides_et_faux(self):
        self.assertTrue(O.iban_ok("GB82 WEST 1234 5698 7654 32"))
        self.assertTrue(O.iban_ok("FR7630006000011234567890189"))
        self.assertFalse(O.iban_ok("GB82 WEST 1234 5698 7654 33"))
        self.assertFalse(O.iban_ok("pas un iban !"))

    def test_geohash_reference(self):
        self.assertEqual(O.geohash(57.64911, 10.40744, 11), "u4pruydqqvj")

    def test_utm_tour_cn(self):
        # exemple classique : tour CN, Toronto → zone 17T, 630084 E, 4833438 N
        z, e, n = O.to_utm(43.642566, -79.387139).split()
        self.assertEqual(z, "17T")
        self.assertAlmostEqual(int(e[:-1]), 630084, delta=2)
        self.assertAlmostEqual(int(n[:-1]), 4833438, delta=2)

    def test_dms(self):
        self.assertEqual(O.dms(48.858333, "N", "S")[:6], "48°51'")
        self.assertTrue(O.dms(-2.5, "E", "O").endswith("O"))

    def test_variantes_de_pseudo(self):
        v = O.variants("jean.dupont")
        self.assertIn("jean.dupont", v)
        self.assertIn("jeandupont", v)
        self.assertIn("jean_dupont", v)

    def test_extraction_d_indices(self):
        r = O.extract_iocs("Contact : jean@exemple.fr, serveur 93.184.216.34, logo@2x.png, IBAN GB82WEST12345698765432 et GB82WEST12345698765433")
        self.assertEqual(r.get("Emails"), ["jean@exemple.fr"])
        self.assertIn("93.184.216.34", r.get("IPv4", []))
        self.assertEqual(r.get("IBAN"), ["GB82WEST12345698765432"])


class Identifiants(unittest.TestCase):
    def test_snowflake_discord_exemple_officiel(self):
        # exemple de la documentation Discord : 175928847299117063 → 30/04/2016 11:18:25 UTC
        out = O.decode_id("https://discord.com/channels/175928847299117063/175928847299117063")
        d = next(x[1] for x in out if x[0].startswith("Discord"))
        self.assertEqual(d.replace(microsecond=0), datetime.datetime(2016, 4, 30, 11, 18, 25))

    def test_ancien_tweet_sans_date(self):
        out = O.decode_id("https://twitter.com/jack/status/20")
        self.assertIsNone(out[0][1])

    def test_objectid_mongodb(self):
        out = O.decode_id("507f1f77bcf86cd799439011")
        self.assertEqual(out[0][1], datetime.datetime(2012, 10, 17, 21, 13, 27))

    def test_uuid_aleatoire_sans_date(self):
        out = O.decode_id("550e8400-e29b-41d4-a716-446655440000")
        self.assertIsNone(out[0][1])


class SourcesIP(unittest.TestCase):
    def setUp(self):
        self._gj = O.get_json

    def tearDown(self):
        O.get_json = self._gj

    def test_ipwho(self):
        O.get_json = lambda *a, **k: {"success": True, "country_code": "FR", "country": "France", "city": "Paris", "latitude": 48.85,
                                      "longitude": 2.35, "connection": {"asn": 3215, "isp": "Orange", "org": "Orange S.A."}}
        r = O._ipsrc_who("1.2.3.4")
        self.assertEqual((r["cc"], r["city"], r["asn"], r["isp"]), ("FR", "Paris", 3215, "Orange"))

    def test_ipwho_echec_signale(self):
        O.get_json = lambda *a, **k: {"success": False, "message": "Reserved range"}
        self.assertIsNone(O._ipsrc_who("10.0.0.1"))

    def test_ip_api(self):
        O.get_json = lambda *a, **k: {"status": "success", "countryCode": "FR", "country": "France", "city": "Lyon", "lat": 45.7, "lon": 4.8,
                                      "as": "AS3215 Orange S.A.", "isp": "Orange", "proxy": False, "hosting": False, "mobile": True}
        r = O._ipsrc_api("1.2.3.4")
        self.assertEqual((r["cc"], r["asn"], r["mobile"]), ("FR", 3215, True))

    def test_ipinfo(self):
        O.get_json = lambda *a, **k: {"country": "FR", "city": "Paris", "loc": "48.8534,2.3488", "org": "AS3215 Orange S.A."}
        r = O._ipsrc_info("1.2.3.4")
        self.assertEqual((r["cc"], r["asn"], r["isp"]), ("FR", 3215, "Orange S.A."))
        self.assertAlmostEqual(r["lat"], 48.8534)

    def test_ipinfo_sans_position(self):
        O.get_json = lambda *a, **k: {"bogon": True}
        self.assertIsNone(O._ipsrc_info("10.0.0.1"))

    def test_une_source_en_panne_n_arrete_pas_le_recoupement(self):
        def gj(url, *a, **k):
            if "ipwho" in url:
                raise O.requests.ConnectionError()
            if "ip-api" in url:
                return {"status": "success", "countryCode": "FR", "country": "France", "city": "Paris", "lat": 48.85, "lon": 2.35}
            if "ipinfo" in url:
                return {"country": "FR", "city": "Paris", "loc": "48.85,2.35"}
            return {}
        O.get_json = gj
        c = O.ip_geo("1.2.3.4")
        self.assertEqual((c["n"], c["cc"], c["level"]), (2, "FR", "A"))


class Reprise(unittest.TestCase):
    def setUp(self):
        self._get, self._w = O.get, O.RETRY_WAIT
        O.RETRY_WAIT = 0

    def tearDown(self):
        O.get, O.RETRY_WAIT = self._get, self._w

    def test_retente_apres_une_coupure(self):
        appels = []

        def g(url, timeout=12, **kw):
            appels.append(1)
            if len(appels) == 1:
                raise O.requests.ConnectionError()
            return Rep({"ok": 1})
        O.get = g
        self.assertEqual(O.get_json("https://x.test"), {"ok": 1})
        self.assertEqual(len(appels), 2)

    def test_retente_apres_un_service_sature(self):
        appels = []

        def g(url, timeout=12, **kw):
            appels.append(1)
            return Rep("", 429, {"Retry-After": "1"}) if len(appels) == 1 else Rep({"ok": 2})
        O.get = g
        self.assertEqual(O.get_json("https://x.test"), {"ok": 2})

    def test_panne_durable_remonte_l_erreur(self):
        def g(url, timeout=12, **kw):
            raise O.requests.ConnectionError()
        O.get = g
        with self.assertRaises(O.requests.ConnectionError):
            O.get_json("https://x.test")

    def test_erreur_definitive_non_retentee(self):
        appels = []

        def g(url, timeout=12, **kw):
            appels.append(1)
            return Rep("", 404)
        O.get = g
        with self.assertRaises(O.requests.HTTPError):
            O.get_json("https://x.test")
        self.assertEqual(len(appels), 1)


class Profils(unittest.TestCase):
    def setUp(self):
        self._get, self._gj = O.get, O.get_json

    def tearDown(self):
        O.get, O.get_json = self._get, self._gj

    def test_hacker_news_profil(self):
        O.get_json = lambda *a, **k: {"id": "pg", "created": 1160418092, "karma": 157000, "about": "Bug <i>fixer</i>.", "submitted": [1, 2, 3]}
        r = O.sl_hn("pg")
        self.assertEqual((r["Karma"], r["Contributions"], r["Créé le"]), (157000, 3, "09/10/2006"))
        self.assertNotIn("<", r["À propos"])

    def test_hacker_news_absent(self):
        O.get_json = lambda *a, **k: None
        self.assertIsNone(O.sl_hn("personne_inexistante"))

    def test_pseudo_invalide_refuse_sans_requete(self):
        def interdit(*a, **k):
            raise AssertionError("aucune requête ne doit partir pour un pseudo invalide")
        O.get, O.get_json = interdit, interdit
        self.assertIsNone(O.sl_hn("../../etc/passwd"))
        self.assertIsNone(O.sl_github("a b"))

    def test_github_absent(self):
        O.get = lambda *a, **k: Rep({"message": "Not Found"}, 404)
        self.assertIsNone(O.sl_github("compte-qui-n-existe-pas"))

    def test_github_limite_atteinte_signalee(self):
        O.get = lambda *a, **k: Rep({"message": "API rate limit exceeded"}, 403)
        with self.assertRaises(RuntimeError):
            O.sl_github("torvalds")


if __name__ == "__main__":
    unittest.main()

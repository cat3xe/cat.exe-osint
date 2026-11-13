"""Second moteur de recherche de pseudo (règles Sherlock), fusion des moteurs, pages anti-robot, IP en lot."""
import contextlib
import io
import unittest

import conftest_path  # noqa: F401
import geo_core as g
import test_sites
O = test_sites.O


class ReglesSherlock(unittest.TestCase):
    def test_code_http(self):
        s = {"errorType": "status_code"}
        self.assertIs(g.sherlock_verdict(s, 200, "profil"), True)
        self.assertIs(g.sherlock_verdict(s, 404, ""), False)
        self.assertIs(g.sherlock_verdict(s, 301, ""), False)

    def test_code_d_erreur_particulier(self):
        s = {"errorType": "status_code", "errorCode": 200}
        self.assertIs(g.sherlock_verdict(s, 200, "page"), False)
        self.assertIs(g.sherlock_verdict({"errorType": "status_code", "errorCode": [201, 202]}, 201, ""), False)

    def test_message_d_absence(self):
        s = {"errorType": "message", "errorMsg": "Sorry, nobody on Reddit goes by that name."}
        self.assertIs(g.sherlock_verdict(s, 200, "<html>Sorry, nobody on Reddit goes by that name.</html>"), False)
        self.assertIs(g.sherlock_verdict(s, 200, "<html>u/alice · karma 12</html>"), True)

    def test_plusieurs_messages(self):
        s = {"errorType": "message", "errorMsg": ['{"taken":false}', "The resource is being rate limited"]}
        self.assertIs(g.sherlock_verdict(s, 200, '{"taken":false}'), False)
        self.assertIs(g.sherlock_verdict(s, 200, '{"taken":true}'), True)

    def test_erreur_serveur_sans_message_n_est_pas_un_compte(self):
        s = {"errorType": "message", "errorMsg": "introuvable"}
        self.assertIsNone(g.sherlock_verdict(s, 500, "Internal Server Error"))

    def test_site_bloque_ne_conclut_rien(self):
        s = {"errorType": "status_code"}
        self.assertIsNone(g.sherlock_verdict(s, 403, "Forbidden"))
        self.assertIsNone(g.sherlock_verdict(s, 429, ""))
        self.assertIsNone(g.sherlock_verdict(s, 200, "<title>Just a moment...</title>"))
        self.assertIsNone(g.sherlock_verdict(s, None, ""))

    def test_redirection(self):
        s = {"errorType": "response_url"}
        self.assertIs(g.sherlock_verdict(s, 200, ""), True)
        self.assertIs(g.sherlock_verdict(s, 302, ""), False)

    def test_regle_inconnue(self):
        self.assertIsNone(g.sherlock_verdict({"errorType": "autre"}, 200, ""))
        self.assertIsNone(g.sherlock_verdict({"errorType": "message"}, 200, "x"))

    def test_forme_du_pseudo(self):
        gh = {"regexCheck": "^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$"}
        self.assertTrue(g.sherlock_valid(gh, "alice-m"))
        self.assertFalse(g.sherlock_valid(gh, "alice.m"))
        self.assertFalse(g.sherlock_valid(gh, "-alice"))
        self.assertTrue(g.sherlock_valid({}, "n'importe quoi"))
        self.assertTrue(g.sherlock_valid({"regexCheck": "(mal formée"}, "alice"))


class PagesEtFusion(unittest.TestCase):
    def test_pages_anti_robot(self):
        self.assertTrue(g.looks_blocked("<title>Just a moment...</title>"))
        self.assertTrue(g.looks_blocked("Attention Required! | Cloudflare"))
        self.assertFalse(g.looks_blocked("<h1>alice</h1> 12 abonnés"))
        self.assertFalse(g.looks_blocked(""))
        self.assertFalse(g.looks_blocked(None))

    def test_pseudo_present_dans_la_page(self):
        self.assertTrue(g.echoes("alice_m", "<title>Alice (@Alice_M)</title>"))
        self.assertTrue(g.echoes("alice", "", "https://site.test/u/alice"))
        self.assertFalse(g.echoes("alice", "<title>malice</title> alicette"))
        self.assertFalse(g.echoes("al", "al al al"))
        self.assertFalse(g.echoes("alice", "page générique du site"))

    def test_nom_de_site_comparable(self):
        self.assertEqual(g.host_key("https://www.GitHub.com/alice"), "github.com")
        self.assertEqual(g.host_key("http://github.com:443/alice?x=1"), "github.com")
        self.assertEqual(g.host_key("pas une adresse"), "")

    def test_fusion_deux_moteurs(self):
        rows = g.merge_hits([
            {"site": "GitHub", "cat": "coding", "url": "https://github.com/alice", "engine": "WhatsMyName", "echo": False},
            {"site": "GitHub", "cat": "", "url": "https://www.github.com/alice", "engine": "Sherlock", "echo": False},
            {"site": "Forum", "cat": "social", "url": "https://forum.test/alice", "engine": "WhatsMyName", "echo": True},
            {"site": "Vide", "cat": "", "url": "https://vide.test/alice", "engine": "Sherlock", "echo": False},
        ])
        d = {r["site"]: r for r in rows}
        self.assertEqual(len(rows), 3)
        self.assertEqual((d["GitHub"]["engines"], d["GitHub"]["conf"], d["GitHub"]["cat"]), (["Sherlock", "WhatsMyName"], "forte", "coding"))
        self.assertEqual(d["Forum"]["conf"], "forte")
        self.assertEqual(d["Vide"]["conf"], "moyenne")
        self.assertEqual(rows[-1]["site"], "Vide")  # les confiances fortes d'abord

    def test_fusion_vide(self):
        self.assertEqual(g.merge_hits([]), [])


class Rep:
    def __init__(self, code, text="", url=""):
        self.status_code, self.text, self.url, self.ok, self.content, self.history = code, text, url, code < 400, text.encode(), []


def faux(url, **kw):
    nom = url.rstrip("/").split("/")[-1]
    if "menteur" in url:
        return Rep(200, "page générique", url)
    if "robot" in url:
        return Rep(200, "<title>Just a moment...</title>", url)
    if "panne" in url:
        raise O.requests.ConnectionError()
    if "message" in url:
        return Rep(200, f"profil de {nom}" if nom == "alice" else "Utilisateur introuvable", url)
    return Rep(200 if nom == "alice" else 404, f"<h1>{nom}</h1>" if nom == "alice" else "", url)


class MoteurSherlock(unittest.TestCase):
    def setUp(self):
        self._http = O.HTTP

        class H:
            get = staticmethod(faux)
            post = staticmethod(faux)
        O.HTTP = H()
        O._SH_CTRL.clear()
        O._WMN_CTRL.clear()
        O._WMN_STATS.clear()

    def tearDown(self):
        O.HTTP = self._http

    def test_compte_reel(self):
        h = O.sherlock_hit("Bon", {"errorType": "status_code", "url": "https://bon.test/{}"}, "alice")
        self.assertEqual(h, {"url": "https://bon.test/alice", "echo": True})

    def test_compte_absent(self):
        self.assertIsNone(O.sherlock_hit("Bon", {"errorType": "status_code", "url": "https://bon.test/{}"}, "bob"))

    def test_site_qui_dit_oui_a_tout_ecarte(self):
        self.assertIsNone(O.sherlock_hit("Menteur", {"errorType": "status_code", "url": "https://menteur.test/{}"}, "alice"))
        self.assertEqual(O._WMN_STATS.get("drop"), 1)

    def test_page_anti_robot_ecartee(self):
        self.assertIsNone(O.sherlock_hit("Robot", {"errorType": "status_code", "url": "https://robot.test/{}"}, "alice"))

    def test_site_en_panne(self):
        self.assertIsNone(O.sherlock_hit("Panne", {"errorType": "status_code", "url": "https://panne.test/{}"}, "alice"))

    def test_regle_par_message(self):
        s = {"errorType": "message", "errorMsg": "Utilisateur introuvable", "url": "https://message.test/{}"}
        self.assertIsNotNone(O.sherlock_hit("Msg", s, "alice"))
        self.assertIsNone(O.sherlock_hit("Msg", s, "bob"))

    def test_pseudo_de_forme_impossible_sans_requete(self):
        def interdit(*a, **k):
            raise AssertionError("aucune requête ne doit partir")
        O.HTTP.get = staticmethod(interdit)
        self.assertIsNone(O.sherlock_hit("GH", {"errorType": "status_code", "url": "https://bon.test/{}", "regexCheck": "^[a-z]+$"}, "alice.m"))

    def test_deux_moteurs_fusionnes(self):
        wd, sd = O.wmn_data, O.sherlock_data
        O.wmn_data = lambda: [{"name": "Bon", "uri_check": "https://bon.test/{account}", "e_code": 200, "e_string": "", "cat": "social"},
                              {"name": "Menteur", "uri_check": "https://menteur.test/{account}", "e_code": 200, "e_string": "", "cat": "social"}]
        O.sherlock_data = lambda: {"Bon": {"errorType": "status_code", "url": "https://www.bon.test/{}"},
                                   "Autre": {"errorType": "status_code", "url": "https://autre.test/{}"},
                                   "Robot": {"errorType": "status_code", "url": "https://robot.test/{}"}}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rows, n, dropped = O.pseudo_scan("alice")
        finally:
            O.wmn_data, O.sherlock_data = wd, sd
        d = {r["site"]: r for r in rows}
        self.assertEqual(sorted(d), ["Autre", "Bon"])
        self.assertEqual(d["Bon"]["engines"], ["Sherlock", "WhatsMyName"])
        self.assertEqual(n, 5)
        self.assertEqual(dropped, 1)

    def test_bases_injoignables(self):
        wd, sd = O.wmn_data, O.sherlock_data

        def panne():
            raise RuntimeError("x")
        O.wmn_data, O.sherlock_data = panne, lambda: {}
        try:
            with self.assertRaises(RuntimeError):
                O.pseudo_scan("alice")
        finally:
            O.wmn_data, O.sherlock_data = wd, sd


class IpEnLot(unittest.TestCase):
    def test_extraction(self):
        t = "connexion de 93.184.216.34 puis 8.8.8.8, encore 93.184.216.34 ; interne 192.168.1.10 et 10.0.0.1, boucle 127.0.0.1, v6 2001:4860:4860::8888, faux 999.1.1.1 et version 1.2.3.4.5"
        self.assertEqual(g.extract_ips(t), ["93.184.216.34", "8.8.8.8", "2001:4860:4860::8888"])

    def test_limite(self):
        self.assertEqual(g.extract_ips("1.1.1.1 8.8.8.8 9.9.9.9", limit=2), ["1.1.1.1", "8.8.8.8"])

    def test_texte_sans_ip(self):
        self.assertEqual(g.extract_ips("rien ici, version 3.14 et heure 12:30:05"), [])
        self.assertEqual(g.extract_ips(None), [])

    def test_resume(self):
        rows = [{"ip": "1", "country": "France", "asn": 3215, "isp": "Orange", "level": "A", "flags": []},
                {"ip": "2", "country": "France", "asn": 3215, "isp": "Orange", "level": "A", "flags": ["mobile"]},
                {"ip": "3", "country": None, "cc": None, "asn": None, "isp": None, "level": "C", "flags": ["Tor"]}]
        s = g.ip_summary(rows)
        self.assertEqual((s["total"], s["surs"]), (3, 2))
        self.assertEqual(s["pays"][0], ("France", 2))
        self.assertEqual(s["operateurs"][0], ("AS3215 Orange", 2))
        self.assertEqual(dict(s["signalements"]), {"mobile": 1, "Tor": 1})

    def test_module_recoupe_chaque_ip(self):
        sauv = (O.ip_geo, O.tor_exits)
        O.tor_exits = lambda: {"8.8.8.8"}
        O.ip_geo = lambda ip: O.ip_consensus({"a": {"cc": "FR", "country": "France", "city": "Paris", "lat": 48.85, "lon": 2.35, "isp": "Orange", "asn": 3215},
                                              "ip-api.com": {"cc": "FR", "country": "France", "city": "Paris", "lat": 48.86, "lon": 2.34, "hosting": ip == "1.1.1.1"}})
        try:
            rows = O.ip_bulk_rows(["8.8.8.8", "1.1.1.1"])
        finally:
            O.ip_geo, O.tor_exits = sauv
        self.assertEqual([r["ip"] for r in rows], ["8.8.8.8", "1.1.1.1"])
        self.assertEqual((rows[0]["level"], rows[0]["flags"], rows[1]["flags"]), ("A", ["Tor"], ["hébergeur"]))


if __name__ == "__main__":
    unittest.main()

"""Contrôles anti-faux-positifs des pseudos, de WhatsMyName et des emails.
Le réseau est remplacé par des réponses simulées : aucun site réel n'est interrogé."""
import importlib.util
import json
import unittest
from pathlib import Path

import conftest_path  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent


def load_tool():
    """Charge osint_tool.py. Le contrôle « Python 3.14 minimum » est assoupli ici seulement (en mémoire),
    pour que les tests tournent aussi sur 3.11+ ; le fichier sur le disque n'est pas modifié."""
    src = (ROOT / "osint_tool.py").read_text(encoding="utf-8").replace("sys.version_info < (3, 14)", "sys.version_info < (3, 11)")
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader("osint_tool", loader=None))
    mod.__file__ = str(ROOT / "osint_tool.py")
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


O = load_tool()


class Rep:
    def __init__(self, code, text="", url="", history=()):
        self.status_code, self.text, self.url, self.history = code, text, url, list(history)
        self.ok = code < 400

    def json(self):
        return json.loads(self.text)


REELS = {"torvalds"}


def faux_get(url, timeout=12, **kw):
    dernier = url.rstrip("/").split("/")[-1]
    if "toujours200" in url:
        return Rep(200, "ok", url)
    if "redirige" in url:
        return Rep(200, "accueil", "https://redirige.test/login", [1])
    if "panne" in url:
        raise O.requests.ConnectionError()
    return Rep(200 if dernier in REELS else 404, "", url)


class Pseudos(unittest.TestCase):
    def setUp(self):
        self._get = O.get
        O.get = faux_get
        O._CTRL.clear()

    def tearDown(self):
        O.get = self._get

    @staticmethod
    def site(nom, dom):
        return (nom, "test", f"https://{dom}/{{u}}", None, O.SC, None)

    def test_compte_reel_confirme(self):
        self.assertEqual(O.check_site(self.site("Bon", "bon.test"), "torvalds")[0], "trouvé")

    def test_pseudo_inexistant_absent(self):
        self.assertEqual(O.check_site(self.site("Bon", "bon.test"), "personne123")[0], "absent")

    def test_site_qui_repond_oui_a_tout_est_ecarte(self):
        self.assertEqual(O.check_site(self.site("Menteur", "toujours200.test"), "torvalds")[0], "à vérifier")

    def test_redirection_vers_accueil_non_fiable(self):
        self.assertEqual(O.check_site(self.site("Redir", "redirige.test"), "torvalds")[0], "à vérifier")

    def test_site_en_panne(self):
        self.assertEqual(O.check_site(self.site("Mort", "panne.test"), "torvalds")[0], "injoignable")


class WhatsMyName(unittest.TestCase):
    def setUp(self):
        self._get = O.get
        self._http = O.HTTP
        O.get = faux_get
        O._WMN_CTRL.clear()

        class H:
            get = staticmethod(faux_get)
            post = staticmethod(faux_get)
        O.HTTP = H()

    def tearDown(self):
        O.get, O.HTTP = self._get, self._http

    @staticmethod
    def site(nom, dom):
        return {"name": nom, "uri_check": f"https://{dom}/{{account}}", "e_code": 200, "e_string": "", "m_string": ""}

    def test_vrai_compte(self):
        self.assertIsNotNone(O.wmn_check(self.site("ok", "bon.test"), "torvalds"))

    def test_faux_positif_ecarte(self):
        self.assertIsNone(O.wmn_check(self.site("menteur", "toujours200.test"), "torvalds"))


class Emails(unittest.TestCase):
    def setUp(self):
        self._acc = O.ACC_CHECKS
        O.ACC_CHECKS = [
            ("Vrai", "vrai.com", lambda e: (e.startswith("moi"), "")),
            ("Menteur", "menteur.com", lambda e: (True, "")),
            ("Casse", "casse.com", lambda e: 1 / 0),
        ]

    def tearDown(self):
        O.ACC_CHECKS = self._acc

    def test_vrai_confirme_menteur_ecarte_casse_compte(self):
        found, limited, checked, _ = O.email_accounts("moi@gmail.com", deep=False)
        self.assertEqual(found, [("vrai.com", "")])
        self.assertEqual(O.EMAIL_DROP, ["menteur.com"])
        self.assertEqual(limited, 1)
        self.assertEqual(checked, 3)


if __name__ == "__main__":
    unittest.main()

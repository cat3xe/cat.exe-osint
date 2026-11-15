"""Outils externes (h8mail, GitFive, Toutatis) : commandes, sortie nettoyée, secrets jamais enregistrés."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

import conftest_path  # noqa: F401
import geo_core as g
import test_sites
O = test_sites.O


class Commandes(unittest.TestCase):
    def test_h8mail_lance_en_module(self):
        self.assertEqual(g.ext_argv("py", "h8mail", ["-t", "a@b.fr"]), ["py", "-m", "h8mail", "-t", "a@b.fr"])

    def test_gitfive_et_toutatis_lances_par_leur_fonction_principale(self):
        a = g.ext_argv("py", "gitfive", ["user", "alice"])
        self.assertEqual((a[0], a[1], a[-2:]), ("py", "-c", ["user", "alice"]))
        self.assertIn("from gitfive.gitfive import main", a[2])
        self.assertIn("from toutatis.core import main", g.ext_argv("py", "toutatis", [])[2])

    def test_code_de_lancement_valide(self):
        for t in ("gitfive", "toutatis"):
            compile(g.EXT[t]["run"][1], t, "exec")

    def test_outil_inconnu_refuse(self):
        with self.assertRaises(ValueError):
            g.ext_argv("py", "rm -rf", [])

    def test_couleurs_retirees(self):
        self.assertEqual(g.strip_ansi("\x1b[31mrouge\x1b[0m et \x1b[1;32mvert\x1b[0m\r"), "rouge et vert")
        self.assertEqual(g.strip_ansi(None), "")

    def test_secrets_masques(self):
        self.assertEqual(g.redact("session=ABCD1234 ok ABCD1234", ["ABCD1234"]), "session=••• ok •••")
        self.assertEqual(g.redact("texte", ["", None, "abc"]), "texte")  # secrets vides ou trop courts ignorés
        self.assertEqual(g.redact("texte", None), "texte")

    def test_fichier_de_cles_protege_des_mises_a_jour(self):
        self.assertTrue(g.update_protected("h8mail_config.ini"))


class Lancement(unittest.TestCase):
    def setUp(self):
        g.EXT["faux"] = {"pip": "x", "mod": "module_qui_n_existe_pas_du_tout", "titre": "t", "besoin": "b",
                         "run": ("-c", "import sys; print('ligne 1'); print('session=ABCD1234'); print(chr(27) + '[31mrouge' + chr(27) + '[0m'); "
                                       "print('arguments', sys.argv[1:]); sys.exit(3)")}

    def tearDown(self):
        g.EXT.pop("faux", None)

    def test_sortie_lue_nettoyee_et_code_de_retour(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code, out = O.ext_run("faux", ["-u", "alice"], secrets=["ABCD1234"], python=sys.executable)
        self.assertEqual(code, 3)
        self.assertEqual(out.splitlines(), ["ligne 1", "session=•••", "rouge", "arguments ['-u', 'alice']"])
        self.assertNotIn("ABCD1234", out)

    def test_outil_non_installe_detecte(self):
        self.assertFalse(O.ext_installed("faux"))

    def test_enregistrement_sans_secret(self):
        sauv = (O.OUT, O.add_report)
        vus = []
        with tempfile.TemporaryDirectory() as d:
            O.OUT, O.add_report = Path(d), lambda m, t, x: vus.append((m, t, x))
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    code, out = O.ext_run("faux", [], secrets=["ABCD1234"], python=sys.executable)
                    f = O.ext_save("Toutatis", "alice/../x", out)
                txt = f.read_text(encoding="utf-8")
            finally:
                O.OUT, O.add_report = sauv
        self.assertNotIn("ABCD1234", txt)
        self.assertNotIn("/", f.name)            # le nom de la cible ne peut pas sortir du dossier
        self.assertEqual(vus[0][:2], ("Toutatis", "alice/../x"))


if __name__ == "__main__":
    unittest.main()

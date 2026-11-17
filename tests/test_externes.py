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


class PhunterFichiers(unittest.TestCase):
    def test_manifeste_complet_et_epingle(self):
        self.assertEqual(len(g.PHUNTER_SHA), 40)
        self.assertIn(g.PHUNTER_SHA, g.PHUNTER_RAW)
        for need in ("phunter.py", "lib/cli.py", "lib/lookup.py", "lib/country.json", "useragents.txt", "config.json", "LICENSE"):
            self.assertIn(need, g.PHUNTER_FILES)
        self.assertTrue(all(len(v) == 40 for v in g.PHUNTER_FILES.values()))

    def test_fichiers_modifies_ou_absents_detectes(self):
        fichiers = {"phunter.py": b"x"}
        self.assertEqual(set(g.phunter_check(fichiers.get)), set(g.PHUNTER_FILES))   # rien n'a la bonne empreinte
        self.assertEqual(g.phunter_check(lambda p: None), list(g.PHUNTER_FILES))

    def test_installation_refusee_si_un_fichier_differe(self):
        class Rep:
            status_code = 200
            content = b"code piege"
        sauv = (O.BASE, O.get, O.ask_yes, O.con.status)
        with tempfile.TemporaryDirectory() as d:
            O.BASE, O.get, O.ask_yes = Path(d), lambda url, timeout=12, **kw: Rep(), lambda q, default=False: True
            O.con.status = lambda *a, **k: contextlib.nullcontext()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    ok = O.phunter_install()
                rien = not (Path(d) / "outils_externes").exists()
            finally:
                O.BASE, O.get, O.ask_yes, O.con.status = sauv
        self.assertFalse(ok)
        self.assertTrue(rien, "aucun fichier ne doit être écrit si l'empreinte ne correspond pas")

    def test_lancement_refuse_si_modifie(self):
        sauv = O.BASE
        with tempfile.TemporaryDirectory() as d:
            O.BASE = Path(d)
            try:
                with self.assertRaises(RuntimeError):
                    O.ext_run("phunter", ["-t", "+33612345678"])
            finally:
                O.BASE = sauv

    def test_dossier_protege_des_mises_a_jour(self):
        self.assertTrue(g.update_protected("outils_externes/Phunter/phunter.py"))

    def test_commande(self):
        self.assertEqual(g.ext_argv("py", "phunter", ["-t", "+33612345678"]), ["py", "phunter.py", "-t", "+33612345678"])


class PhunterLecture(unittest.TestCase):
    SORTIE = ("\x1b[0m📞 Phone number: +1 650\n [>] Possible: ✔️\n [>] Valid: ✔️\n [>] Operator: Orange\n [>] Possible location: United States, Canada, Bahamas\n"
              " [>] Line type: Mobile\n [>] Reputation: Dangerous\n [>] Spamcalls\n  └── ! Spammer\n")

    def niveaux(self, notes):
        return [lv for lv, _ in notes]

    def test_plusieurs_pays_ne_sont_pas_un_lieu(self):
        n = g.phunter_notes(self.SORTIE, {"pays": "États-Unis", "region": "Californie", "type": "mobile"})
        t = " ".join(x for _, x in n)
        self.assertIn("3 pays qui partagent cet indicatif", t)
        self.assertIn("États-Unis (Californie)", t)

    def test_spammer_explique(self):
        t = " ".join(x for _, x in g.phunter_notes(self.SORTIE, {}))
        self.assertIn("spamcalls.net a une page", t)
        self.assertNotIn("Not spammer", t)

    def test_pas_spammer(self):
        n = g.phunter_notes("  └── > Not spammer\n", {})
        self.assertEqual(self.niveaux(n), ["info"])
        self.assertIn("ne prouve pas", n[0][1])

    def test_pays_unique_coherent_sans_remarque(self):
        n = g.phunter_notes(" [>] Possible location: France\n [>] Line type: Mobile\n", {"pays": "France", "type": "mobile"})
        self.assertEqual(n, [])

    def test_pays_unique_contradictoire(self):
        n = g.phunter_notes(" [>] Possible location: Germany\n", {"pays": "France"})
        self.assertIn("France", n[0][1])

    def test_type_de_ligne_contradictoire(self):
        n = g.phunter_notes(" [>] Line type: Fixed\n", {"type": "mobile"})
        self.assertEqual(self.niveaux(n), ["attention"])

    def test_plantage_signale(self):
        n = g.phunter_notes("Traceback (most recent call last):\nAttributeError: 'NoneType' object has no attribute 'findAll'\n", {})
        self.assertIn("s'est arrêté sur une erreur", n[0][1])

    def test_sortie_vide(self):
        self.assertEqual(g.phunter_notes("", None), [])
        self.assertEqual(g.phunter_notes(None, None), [])

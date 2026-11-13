"""Mise à jour automatique : ne télécharge que ce qui a changé, ne touche jamais aux données, n'installe rien d'incomplet."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import conftest_path  # noqa: F401
import geo_core as g
import test_sites
O = test_sites.O


class Empreintes(unittest.TestCase):
    def test_empreinte_git_valeurs_connues(self):
        self.assertEqual(g.git_blob_sha(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
        self.assertEqual(g.git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_chemins_dangereux_refuses(self):
        for p in ("../evil.py", "a/../../b", "/etc/passwd", "C:\\x", "a\\b.py", "", "a//b", "./x"):
            self.assertFalse(g.update_safe_path(p), p)
        for p in ("osint_tool.py", "tests/test_geo.py", ".github/workflows/tests.yml"):
            self.assertTrue(g.update_safe_path(p), p)

    def test_donnees_de_l_utilisateur_protegees(self):
        for p in ("config.json", "resultats/enquetes/x.json", "cache/wmn-data.json", "cours/python.md", "projets/a.py", "progression.json",
                  "historique_noms.json", "lang/en.json", "sauvegarde_maj/x/osint_tool.py", "debug.log", "logs/erreur.LOG", "marques.txt"):
            self.assertTrue(g.update_protected(p), p)
        for p in ("osint_tool.py", "geo_core.py", "README.md", "tests/test_geo.py", "challenges/challenges.json"):
            self.assertFalse(g.update_protected(p), p)


class Plan(unittest.TestCase):
    def tree(self, **files):
        return [{"path": p, "type": "blob", "sha": g.git_blob_sha(d)} for p, d in files.items()]

    def test_rien_a_faire_si_identique(self):
        f = {"a.py": b"x = 1\n", "b/c.txt": b"salut"}
        self.assertEqual(g.update_plan(self.tree(**f), f.get), [])

    def test_fichier_modifie_et_nouveau(self):
        distant = {"a.py": b"x = 2\n", "new.py": b"y = 1\n", "same.py": b"z\n"}
        local = {"a.py": b"x = 1\n", "same.py": b"z\n"}
        plan = g.update_plan(self.tree(**distant), local.get)
        self.assertEqual([(p, k) for p, _, k in plan], [("a.py", "modifié"), ("new.py", "nouveau")])

    def test_fins_de_ligne_windows_ne_comptent_pas(self):
        self.assertEqual(g.update_plan(self.tree(**{"a.py": b"x = 1\ny = 2\n"}), {"a.py": b"x = 1\r\ny = 2\r\n"}.get), [])

    def test_donnees_jamais_dans_le_plan(self):
        distant = {"config.json": b"{}", "resultats/x.json": b"{}", "lang/en.json": b"", "trace.log": b"", "osint_tool.py": b"v2"}
        plan = g.update_plan(self.tree(**distant), {"osint_tool.py": b"v1"}.get)
        self.assertEqual([p for p, _, _ in plan], ["osint_tool.py"])

    def test_dossiers_et_chemins_pieges_ignores(self):
        t = [{"path": "tests", "type": "tree", "sha": "x"}, {"path": "../evil.py", "type": "blob", "sha": "x"}]
        self.assertEqual(g.update_plan(t, lambda p: None), [])
        self.assertEqual(g.update_plan(None, lambda p: None), [])


class Rep:
    def __init__(self, content, code=200):
        self.content, self.status_code = content, code


class Installation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self._base, self._get = O.BASE, O.get
        O.BASE = self.base
        (self.base / "osint_tool.py").write_bytes(b"x = 1\n")
        (self.base / "config.json").write_bytes(b'{"theme": "le mien"}')
        (self.base / "resultats").mkdir()
        (self.base / "resultats" / "enquete.json").write_bytes(b"mes resultats")
        (self.base / "notes.log").write_bytes(b"mon journal")
        (self.base / "perso.txt").write_bytes(b"fichier que le depot ne connait pas")
        self.distant = {"osint_tool.py": b"x = 2\n", "geo_core.py": b"y = 3\n", "tests/t.py": b"z = 4\n"}

    def tearDown(self):
        O.BASE, O.get = self._base, self._get
        self.tmp.cleanup()

    def info(self):
        return {"sha": "abc", "plan": g.update_plan([{"path": p, "type": "blob", "sha": g.git_blob_sha(d)} for p, d in self.distant.items()],
                                                    lambda p: (self.base / p).read_bytes() if (self.base / p).is_file() else None)}

    def test_installe_et_preserve_les_donnees(self):
        O.get = lambda url, timeout=12, **kw: Rep(self.distant[url.split("/abc/")[1]])
        bak = O.update_apply(self.info())
        self.assertEqual((self.base / "osint_tool.py").read_bytes(), b"x = 2\n")
        self.assertEqual((self.base / "geo_core.py").read_bytes(), b"y = 3\n")
        self.assertEqual((self.base / "tests" / "t.py").read_bytes(), b"z = 4\n")
        self.assertEqual((self.base / "config.json").read_bytes(), b'{"theme": "le mien"}')
        self.assertEqual((self.base / "resultats" / "enquete.json").read_bytes(), b"mes resultats")
        self.assertEqual((self.base / "notes.log").read_bytes(), b"mon journal")
        self.assertEqual((self.base / "perso.txt").read_bytes(), b"fichier que le depot ne connait pas")
        self.assertEqual((bak / "osint_tool.py").read_bytes(), b"x = 1\n")  # ancienne version gardée
        self.assertFalse(list(self.base.glob("*.maj")))

    def test_telechargement_incomplet_n_installe_rien(self):
        O.get = lambda url, timeout=12, **kw: Rep(b"x = " if "geo_core" in url else self.distant[url.split("/abc/")[1]])
        with self.assertRaises(RuntimeError):
            O.update_apply(self.info())
        self.assertEqual((self.base / "osint_tool.py").read_bytes(), b"x = 1\n")
        self.assertFalse((self.base / "geo_core.py").exists())
        self.assertFalse((self.base / "sauvegarde_maj").exists())

    def test_code_illisible_n_installe_rien(self):
        self.distant["geo_core.py"] = b"def (:\n"
        O.get = lambda url, timeout=12, **kw: Rep(self.distant[url.split("/abc/")[1]])
        with self.assertRaises(RuntimeError):
            O.update_apply(self.info())
        self.assertEqual((self.base / "osint_tool.py").read_bytes(), b"x = 1\n")

    def test_erreur_du_serveur_n_installe_rien(self):
        O.get = lambda url, timeout=12, **kw: Rep(b"", 404)
        with self.assertRaises(RuntimeError):
            O.update_apply(self.info())
        self.assertEqual((self.base / "osint_tool.py").read_bytes(), b"x = 1\n")

    def test_verification_compare_au_depot(self):
        tree = [{"path": p, "type": "blob", "sha": g.git_blob_sha(d)} for p, d in self.distant.items()]
        gj = O.get_json
        O.get_json = lambda url, *a, **k: ({"sha": "abc", "commit": {"message": "Nouveau\n\ndétail", "committer": {"date": "2026-11-13T10:00:00Z"}}}
                                           if "/commits/" in url else {"tree": tree, "truncated": False})
        try:
            info = O.update_check()
        finally:
            O.get_json = gj
        self.assertEqual((info["sha"], info["date"], info["message"]), ("abc", "2026-11-13", "Nouveau"))
        self.assertEqual(sorted(p for p, _, _ in info["plan"]), ["geo_core.py", "osint_tool.py", "tests/t.py"])

    def test_github_injoignable_sans_plantage(self):
        gj = O.get_json

        def panne(*a, **k):
            raise O.requests.ConnectionError()
        O.get_json = panne
        try:
            self.assertIsNone(O.update_check())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(O.mod_update(startup=True))
        finally:
            O.get_json = gj

    def test_depot_git_non_touche(self):
        (self.base / ".git").mkdir()
        self.assertIn("git pull", O.update_blocked())


if __name__ == "__main__":
    unittest.main()

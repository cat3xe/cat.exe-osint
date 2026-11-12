"""Traçabilité des niveaux de fiabilité dans le graphe d'enquête (écrit dans un dossier temporaire)."""
import tempfile
import unittest
from pathlib import Path

import test_sites  # charge osint_tool une seule fois
O = test_sites.O


class Dossier(unittest.TestCase):
    def setUp(self):
        self._out, self._cfg = O.OUT, dict(O.CFG)
        self._tmp = tempfile.TemporaryDirectory()
        O.OUT = Path(self._tmp.name)
        O.CFG["enquete"] = "test_tracabilite"
        O._G.clear()

    def tearDown(self):
        O.OUT = self._out
        O.CFG.clear()
        O.CFG.update(self._cfg)
        O._G.clear()
        self._tmp.cleanup()

    def noeud(self, nid):
        return O.gload()["nodes"][nid]["data"]

    def test_chaque_niveau_a_une_date_et_une_limite(self):
        nid = O.gnode("pseudo", "alice", None, None, "", fiab="B", src="profil lu")
        d = self.noeud(nid)
        self.assertIn("vérifié le", d)
        self.assertIn("rien ne prouve", d["fiabilité"])
        self.assertEqual(d["source"], "profil lu")

    def test_niveau_le_plus_sur_garde(self):
        nid = O.gnode("ip", "1.2.3.4", None, None, "", fiab="C", src="estimation")
        O.gnode("ip", "1.2.3.4", None, None, "", fiab="A", src="DNS")
        d = self.noeud(nid)
        self.assertEqual(d["_fiab"], "A")
        self.assertEqual(d["source"], "DNS")

    def test_estimation_pas_ecrasee_par_une_moins_sure(self):
        nid = O.gnode("ip", "5.6.7.8", None, None, "", fiab="A", src="DNS")
        O.gnode("ip", "5.6.7.8", None, None, "", fiab="C", src="pire")
        self.assertEqual(self.noeud(nid)["_fiab"], "A")

    def test_hypothese_marquee_a_verifier(self):
        nid = O.gnode("pseudo", "al", None, None, "", fiab="C", src="hypothèse")
        self.assertEqual(self.noeud(nid).get("_statut"), "check")


if __name__ == "__main__":
    unittest.main()

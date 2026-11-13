"""Recherche de personne : trier les vrais profils des homonymes."""
import contextlib
import io
import unittest

import conftest_path  # noqa: F401
import geo_core as g


class Noms(unittest.TestCase):
    def test_nom_complet_dans_les_deux_ordres(self):
        self.assertEqual(g.name_match("Jean Dupont", "Jean", "Dupont"), 3)
        self.assertEqual(g.name_match("DUPONT Jean", "jean", "dupont"), 3)
        self.assertEqual(g.name_match("jeandupont", "Jean", "Dupont"), 3)

    def test_accents_tirets_et_majuscules(self):
        self.assertEqual(g.name_match("Jean-Noël  DUPONT", "Jean Noel", "Dupont"), 3)
        self.assertEqual(g.name_match("Éloïse Léger", "Eloise", "Leger"), 3)

    def test_initiale(self):
        self.assertEqual(g.name_match("J. Dupont", "Jean", "Dupont"), 2)

    def test_un_seul_des_deux(self):
        self.assertEqual(g.name_match("Jean Martin", "Jean", "Dupont"), 1)
        self.assertEqual(g.name_match("Marie Dupont", "Jean", "Dupont"), 1)

    def test_rien_en_commun(self):
        self.assertEqual(g.name_match("Bob", "Jean", "Dupont"), 0)
        self.assertEqual(g.name_match("", "Jean", "Dupont"), 0)
        self.assertEqual(g.name_match(None, "Jean", "Dupont"), 0)

    def test_nom_contenu_dans_un_autre_mot_ne_compte_pas(self):
        # « Dupontel » n'est pas « Dupont »
        self.assertEqual(g.name_match("Jeanne Dupontel", "Jean", "Dupont"), 0)

    def test_ville_mot_entier(self):
        self.assertTrue(g.city_match("Grenoble, France", "Grenoble"))
        self.assertTrue(g.city_match("Saint-Étienne (42)", "saint etienne"))
        self.assertFalse(g.city_match("Nicewood", "Nice"))
        self.assertFalse(g.city_match("", "Nice"))
        self.assertFalse(g.city_match("Paris", ""))

    def test_pseudos_generes(self):
        u = g.person_usernames("Jean-Noël", "Dupont")
        self.assertEqual(u[0], "jeannoeldupont")
        self.assertIn("jeannoel.dupont", u)
        self.assertEqual(len(u), len(set(u)))
        self.assertEqual(g.person_usernames("", "Dupont"), [])


class Verdicts(unittest.TestCase):
    def test_nom_et_ville_fort(self):
        sc, v, why, lvl = g.person_score({"Nom": "Jean Dupont", "Lieu": "Lyon, France"}, "Jean", "Dupont", "Lyon")
        self.assertEqual((v, lvl), ("fort", "B"))
        self.assertGreaterEqual(sc, 85)

    def test_nom_seul_homonyme_possible(self):
        sc, v, why, lvl = g.person_score({"Nom": "Jean Dupont"}, "Jean", "Dupont", "Lyon")
        self.assertEqual((v, lvl), ("moyen", "C"))

    def test_nom_identique_autre_ville_penalise(self):
        ici = g.person_score({"Nom": "Jean Dupont", "Lieu": "Lyon"}, "Jean", "Dupont", "Lyon")[0]
        ailleurs = g.person_score({"Nom": "Jean Dupont", "Lieu": "Montréal"}, "Jean", "Dupont", "Lyon")
        self.assertLess(ailleurs[0], ici)
        self.assertEqual(ailleurs[1], "moyen")
        self.assertTrue(any("autre lieu" in w for w in ailleurs[2]))

    def test_ville_dans_la_bio(self):
        sc, v, why, lvl = g.person_score({"Nom": "Dupont Jean", "Bio": "Développeur à Lyon"}, "Jean", "Dupont", "Lyon")
        self.assertEqual(v, "fort")

    def test_meme_pseudo_autre_nom_ecarte(self):
        sc, v, why, lvl = g.person_score({"Nom": "Bob Smith", "Lieu": "Lyon"}, "Jean", "Dupont", "Lyon")
        self.assertEqual((v, lvl), ("aucun", None))

    def test_profil_sans_nom_ecarte(self):
        self.assertEqual(g.person_score({"Bio": "gamer"}, "Jean", "Dupont", "Lyon")[1], "aucun")

    def test_jamais_niveau_A(self):
        for p in ({"Nom": "Jean Dupont", "Lieu": "Lyon", "Bio": "Lyon"}, {"Nom": "Jean Dupont"}, {}):
            self.assertNotEqual(g.person_score(p, "Jean", "Dupont", "Lyon")[3], "A")

    def test_sans_ville_cherchee(self):
        sc, v, why, lvl = g.person_score({"Nom": "Jean Dupont", "Lieu": "Lyon"}, "Jean", "Dupont", "")
        self.assertEqual(v, "moyen")


class Module(unittest.TestCase):
    def test_tri_de_bout_en_bout(self):
        import test_sites
        O = test_sites.O
        sauv = O._quiet_social
        fiches = {"jeandupont": [("GitHub", "x", {"Nom": "Jean Dupont", "Lieu": "Lyon", "_url": "https://github.com/jeandupont"}),
                                 ("Steam", "x", {"Nom": "xX_Killer_Xx", "_url": "https://steamcommunity.com/id/jeandupont"})],
                  "jean.dupont": [("Mastodon", "x", {"Nom": "Jean Dupont", "Lieu": "Québec", "_url": "https://m.social/@jean.dupont"})]}
        O._quiet_social = lambda u: (fiches.get(u, []), [])
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                res = O.person_profiles("Jean", "Dupont", "Lyon", ["jeandupont", "jean.dupont", "jdupont"])
        finally:
            O._quiet_social = sauv
        self.assertEqual([(r[2], r[1]) for r in res], [("GitHub", "fort"), ("Mastodon", "moyen"), ("Steam", "aucun")])


if __name__ == "__main__":
    unittest.main()

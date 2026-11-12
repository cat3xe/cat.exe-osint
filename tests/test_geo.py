"""Calculs géographiques : distances, destinations, coordonnées, soleil, ligne de vue, relèvement."""
import datetime
import math
import unittest

import conftest_path  # noqa: F401
import geo_core as g


class Geodesie(unittest.TestCase):
    def test_vincenty_reference_geoscience_australia(self):
        # Flinders Peak -> Buninyong : valeur de référence publiée (54972.271 m)
        km, az1, _ = g.geodesic(-37.95103341666667, 144.42486788888888, -37.65282113888889, 143.92649552777777)
        self.assertAlmostEqual(km * 1000, 54972.271, places=2)
        self.assertAlmostEqual(az1, 306.868158, places=4)

    def test_destination_inverse_du_calcul(self):
        la, lo = g.geodesic_dest(-37.95103341666667, 144.42486788888888, 306.86815833, 54.972271)
        self.assertAlmostEqual(la, -37.65282113888889, places=6)
        self.assertAlmostEqual(lo, 143.92649552777777, places=6)

    def test_meme_point(self):
        self.assertEqual(g.geodesic(10, 20, 10, 20)[0], 0.0)

    def test_presque_antipodes_ne_plante_pas(self):
        km, _, _ = g.geodesic(0, 0, 0.5, 179.7)
        self.assertGreater(km, 19000)

    def test_haversine_proche_de_vincenty(self):
        a = g.geodesic(48.8566, 2.3522, 40.7128, -74.0060)[0]
        b = g.haversine(48.8566, 2.3522, 40.7128, -74.0060)
        self.assertLess(abs(a - b) / a, 0.005)


class Coordonnees(unittest.TestCase):
    CAS = [
        ("48.858, 2.294", (48.858, 2.294)),
        ("48°51'30\"N 2°17'40\"E", (48.858333, 2.294444)),
        ("2°17'40\"E 48°51'30\"N", (48.858333, 2.294444)),
        ("48.858N 2.294E", (48.858, 2.294)),
        ("N48.858 W2.294", (48.858, -2.294)),
        ("48,858; 2,294", (48.858, 2.294)),
        ("-33.87 151.21", (-33.87, 151.21)),
        ("48°51.5'N 2°17.6'E", (48.858333, 2.293333)),
        ("48°51′30″S 2°17′40″O", (-48.858333, -2.294444)),
    ]

    def test_formats_lus(self):
        for s, exp in self.CAS:
            with self.subTest(s=s):
                r = g.coords_only(s)
                self.assertIsNotNone(r)
                self.assertAlmostEqual(r[0], exp[0], places=5)
                self.assertAlmostEqual(r[1], exp[1], places=5)

    def test_valeurs_impossibles_refusees(self):
        self.assertIs(g.coords_only("95.2, 3.1"), False)
        self.assertIs(g.coords_only("48°71'0\"N 2°0'0\"E"), False)

    def test_texte_qui_n_est_pas_une_coordonnee(self):
        for s in ("12 rue de la Paix", "Paris", "75011", "33 6 12 34 56 78", "0 800 123", "Nice"):
            with self.subTest(s=s):
                self.assertIsNone(g.coords_only(s))


class Soleil(unittest.TestCase):
    def test_midi_solaire_paris_solstice(self):
        az, el = g.sun_pos(datetime.datetime(2025, 6, 21, 12, 0), 48.8566, 2.3522, refraction=False)
        self.assertAlmostEqual(el, 64.5, delta=0.3)
        self.assertAlmostEqual(az, 184.0, delta=1.0)

    def test_refraction_releve_la_hauteur(self):
        dt = datetime.datetime(2025, 6, 21, 12, 0)
        _, sans = g.sun_pos(dt, 48.8566, 2.3522, refraction=False)
        _, avec = g.sun_pos(dt, 48.8566, 2.3522, refraction=True)
        self.assertGreater(avec, sans)
        self.assertLess(avec - sans, 0.05)


class LigneDeVue(unittest.TestCase):
    def test_mer_plate_cible_au_sol_masquee(self):
        dk = [i * 0.5 for i in range(41)]
        r = g.los_compute(dk, [0.0] * 41, 1.7, 0)
        self.assertFalse(r["visible"])
        self.assertTrue(15 < r["besoin_m"] < 22)  # courbure de la Terre sur 20 km

    def test_mer_plate_cible_haute_visible(self):
        dk = [i * 0.5 for i in range(41)]
        self.assertTrue(g.los_compute(dk, [0.0] * 41, 1.7, 100)["visible"])

    def test_colline_bloque_la_vue(self):
        dk = [i * 0.5 for i in range(41)]
        el = [0.0] * 41
        el[20] = 300
        r = g.los_compute(dk, el, 1.7, 100)
        self.assertFalse(r["visible"])
        self.assertEqual(r["i_bloc"], 20)
        self.assertTrue(590 < r["besoin_m"] < 620)


class Releve(unittest.TestCase):
    def setUp(self):
        self.me = (48.8566, 2.3522)
        self.obs = [(*g.geodesic_dest(*self.me, b, 2.0), b) for b in (20, 110, 250)]

    def test_position_retrouvee(self):
        r = g.resect(self.obs, 3)
        self.assertLess(g.geodesic(*self.me, r["lat"], r["lon"])[0] * 1000, 5)
        self.assertEqual(r["behind"], [])

    def test_direction_inversee_detectee(self):
        o = self.obs[0]
        r = g.resect([(o[0], o[1], (o[2] + 180) % 360), self.obs[1]], 3)
        self.assertIn(0, r["behind"])

    def test_lignes_paralleles_sans_point(self):
        self.assertIsNone(g.resect([(48.0, 2.0, 90), (48.1, 2.0, 90)], 3))

    def test_moins_de_deux_reperes(self):
        self.assertIsNone(g.resect(self.obs[:1], 3))


class Fiabilite(unittest.TestCase):
    def test_dns_identique(self):
        st, common, part = g.dns_agree({"G": {"1.1.1.1"}, "C": {"1.1.1.1"}, "Q": None})
        self.assertTrue(st.startswith("identique"))
        self.assertEqual(common, {"1.1.1.1"})
        self.assertEqual(part, set())

    def test_dns_different(self):
        st, common, part = g.dns_agree({"G": {"a", "b"}, "C": {"a", "c"}, "Q": {"a"}})
        self.assertIn("différentes", st)
        self.assertEqual(common, {"a"})
        self.assertEqual(part, {"b", "c"})

    def test_dns_aucune_reponse(self):
        self.assertEqual(g.dns_agree({"G": None})[0], "aucune réponse")

    def test_ip_pays_sur_si_toutes_les_sources_d_accord(self):
        c = g.ip_consensus({"a": {"cc": "FR", "country": "France", "city": "Paris", "lat": 48.85, "lon": 2.35},
                            "b": {"cc": "fr", "city": "Paris", "lat": 48.86, "lon": 2.34},
                            "c": {"cc": "FR", "city": "Lyon", "lat": 45.76, "lon": 4.83}})
        self.assertEqual(c["cc"], "FR")
        self.assertEqual(c["level"], "A")
        self.assertTrue(c["ville_sure"] is False or c["city_agree"] == 2)

    def test_ip_pays_contradictoire_reste_estimation(self):
        c = g.ip_consensus({"a": {"cc": "FR", "city": "Paris", "lat": 48.85, "lon": 2.35},
                            "b": {"cc": "DE", "city": "Berlin", "lat": 52.5, "lon": 13.4}})
        self.assertEqual(c["level"], "C")
        self.assertIn("à confirmer", c["resume"])

    def test_ip_aucune_source(self):
        self.assertEqual(g.ip_consensus({})["n"], 0)

    def test_profil_lien_declare_donne_niveau_A(self):
        gh = {"Nom": "Alice Martin", "Site": "https://alice.dev", "_url": "https://github.com/alicem"}
        ma = {"Nom": "Alice Martin", "Bio": "mon code : https://github.com/alicem", "_url": "https://mastodon.social/@alicem"}
        sc, why, lv = g.profile_match(("GitHub", gh), ("Mastodon", ma))
        self.assertEqual(lv, "A")
        self.assertGreaterEqual(sc, 70)

    def test_meme_pseudo_seul_ne_prouve_rien(self):
        gh = {"Nom": "Alice Martin", "_url": "https://github.com/alicem"}
        steam = {"Nom": "Bob", "_url": "https://steamcommunity.com/id/alicem"}
        sc, why, lv = g.profile_match(("GitHub", gh), ("Steam", steam))
        self.assertEqual(sc, 0)
        self.assertEqual(lv, "C")
        self.assertIn("ne prouve rien", g.match_verdict(sc, lv))

    def test_meme_photo_seule_reste_B(self):
        gh = {"Nom": "Bob", "_url": "https://github.com/x"}
        steam = {"Nom": "Carl", "_url": "https://steamcommunity.com/id/y"}
        sc, _, lv = g.profile_match(("GitHub", gh), ("Steam", steam), True)
        self.assertEqual((sc, lv), (40, "B"))


class Photo(unittest.TestCase):
    def test_coherente(self):
        t = {"local": datetime.datetime(2025, 6, 21, 14, 0), "offset_s": 7200, "gps_utc": datetime.datetime(2025, 6, 21, 12, 0),
             "software": "17.5", "modified": None}
        res = g.photo_checks(t, (48.8566, 2.3522), 7200, 180)
        self.assertTrue(all(st in ("ok", "info") for st, _, _ in res))

    def test_retouche_et_decalage_signales(self):
        t = {"local": datetime.datetime(2025, 6, 21, 23, 30), "offset_s": 7200, "gps_utc": datetime.datetime(2025, 6, 21, 12, 0),
             "software": "Adobe Photoshop 25", "modified": datetime.datetime(2025, 7, 1, 9, 0)}
        res = g.photo_checks(t, (48.8566, 2.3522), 7200, 180)
        self.assertEqual(sum(1 for r in res if r[0] == "bad"), 2)
        self.assertEqual(sum(1 for r in res if r[0] == "warn"), 2)

    def test_luminosite_incoherente_avec_la_nuit(self):
        t = {"local": datetime.datetime(2025, 12, 21, 23, 0), "offset_s": None, "gps_utc": None, "software": None, "modified": None}
        res = g.photo_checks(t, (48.8566, 2.3522), 3600, 200)
        self.assertTrue(any(r[0] == "warn" and "Luminosité" in r[1] for r in res))


if __name__ == "__main__":
    unittest.main()

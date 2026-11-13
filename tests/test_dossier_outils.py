"""Mesures sur photo, chronologie, export des lieux, journal de preuves."""
import datetime
import json
import math
import unittest
import xml.dom.minidom

import conftest_path  # noqa: F401
import geo_core as g


class MesuresPhoto(unittest.TestCase):
    def test_focale_en_pixels(self):
        # 36 mm de focale équivalente = champ de 53° : la focale en pixels vaut la largeur de l'image
        self.assertAlmostEqual(g.focal_px(36, 4000, 3000), 4000)
        self.assertAlmostEqual(g.focal_px(36, 3000, 4000), 4000)  # image en portrait : même grand côté
        self.assertIsNone(g.focal_px(0, 4000, 3000))

    def test_distance_et_taille_sont_inverses(self):
        fpx = g.focal_px(26, 4000, 3000)
        d = g.dist_from_size(2.0, 200, fpx)
        self.assertAlmostEqual(d, 2.0 * fpx / 200)
        self.assertAlmostEqual(g.size_from_dist(d, 200, fpx), 2.0)

    def test_geometrie_verifiee(self):
        # un objet de 2 m vu à 10 m sous-tend un angle dont la tangente vaut 0,2 → 0,2 × focale pixels
        fpx = 3000.0
        self.assertAlmostEqual(g.dist_from_size(2.0, 0.2 * fpx, fpx), 10.0)

    def test_fourchette_encadre_la_valeur(self):
        fpx = g.focal_px(26, 4000, 3000)
        v = g.dist_from_size(1.7, 150, fpx)
        lo, hi = g.measure_range(g.dist_from_size, 1.7, 150, fpx)
        self.assertLess(lo, v)
        self.assertGreater(hi, v)
        self.assertLess((hi - lo) / v, 0.2)

    def test_petit_objet_fourchette_large(self):
        fpx = g.focal_px(26, 4000, 3000)
        petit = g.measure_range(g.dist_from_size, 1.7, 10, fpx)
        grand = g.measure_range(g.dist_from_size, 1.7, 400, fpx)
        self.assertGreater((petit[1] - petit[0]) / petit[0], (grand[1] - grand[0]) / grand[0])

    def test_valeurs_impossibles(self):
        self.assertIsNone(g.dist_from_size(2, 0, 3000))
        self.assertIsNone(g.dist_from_size(-1, 100, 3000))
        self.assertIsNone(g.size_from_dist(10, 100, None))

    def test_hauteur_par_l_ombre(self):
        self.assertAlmostEqual(g.height_from_shadow(10, 45), 10.0)
        self.assertAlmostEqual(g.height_from_shadow(10, 30), 10 * math.tan(math.radians(30)))
        self.assertIsNone(g.height_from_shadow(10, 0))
        self.assertIsNone(g.height_from_shadow(0, 45))


class Chronologie(unittest.TestCase):
    G = {"nodes": {
        "enquete:x": {"type": "enquete", "label": "x", "data": {}},
        "compte:a": {"type": "compte", "label": "GitHub · a", "data": {"Créé le": "12/03/2015", "vérifié le": "13/11/2026 10:00", "_fiab": "B"}},
        "fuite:b": {"type": "fuite", "label": "Leak (2021)", "data": {"date": "2021-06-01", "note": "vu le 01/01/2030"}},
        "image:c": {"type": "image", "label": "photo.jpg", "data": {"Prise le": "21/06/2025 14:05"}},
        "lieu:d": {"type": "lieu", "label": "sans date", "data": {"coordonnées": "48.85, 2.35"}},
    }}

    def test_dates_lues_dans_les_deux_formats(self):
        d = g.find_dates("créé le 12/03/2015 puis 2021-06-01T08:30 et 99/99/2020")
        self.assertEqual([x[0] for x in d], [datetime.datetime(2015, 3, 12), datetime.datetime(2021, 6, 1, 8, 30)])
        self.assertEqual([x[1] for x in d], [False, True])

    def test_ordre_chronologique(self):
        ev = g.timeline_events(self.G)
        self.assertEqual([e[0].year for e in ev], [2015, 2021, 2025])
        self.assertEqual(ev[2][1], True)

    def test_dates_de_l_enquete_exclues(self):
        ev = g.timeline_events(self.G)
        self.assertFalse(any(e[0].year in (2026, 2030) for e in ev))

    def test_dossier_vide(self):
        self.assertEqual(g.timeline_events({"nodes": {}}), [])
        self.assertEqual(g.timeline_events({}), [])


class ExportLieux(unittest.TestCase):
    G = {"nodes": {
        "lieu:a": {"type": "lieu", "label": "Tour <Eiffel> & Cie", "data": {"coordonnées": "48.8584, 2.2945", "_fiab": "A", "source": "GPS EXIF"}},
        "lieu:b": {"type": "lieu", "label": "48°51'30\"N 2°17'40\"E", "data": {"_fiab": "C", "marge": "± 25 km"}},
        "lieu:c": {"type": "lieu", "label": "Paris, France", "data": {}},
        "ip:d": {"type": "ip", "label": "1.2.3.4", "data": {"coordonnées": "1, 2"}},
    }}

    def test_seuls_les_lieux_avec_coordonnees(self):
        p = g.places_of(self.G)
        self.assertEqual(len(p), 2)
        self.assertEqual(p[0]["fiab"], "A")
        self.assertAlmostEqual(p[1]["lat"], 48.858333, places=5)

    def test_kml_valide_et_ordre_longitude_latitude(self):
        k = g.to_kml(g.places_of(self.G), "Dossier & test")
        doc = xml.dom.minidom.parseString(k)  # échoue si le XML est mal formé (caractères < > & non protégés)
        coords = [c.firstChild.data for c in doc.getElementsByTagName("coordinates")]
        self.assertEqual(coords[0], "2.2945000,48.8584000,0")
        self.assertEqual(len(doc.getElementsByTagName("Placemark")), 2)
        self.assertIn("Tour <Eiffel> & Cie", doc.getElementsByTagName("name")[1].firstChild.data)

    def test_geojson(self):
        j = g.to_geojson(g.places_of(self.G))
        json.dumps(j)
        self.assertEqual(j["features"][0]["geometry"]["coordinates"], [2.2945, 48.8584])
        self.assertEqual(j["features"][1]["properties"]["fiabilite"], "C")

    def test_aucun_lieu(self):
        self.assertEqual(g.places_of({"nodes": {}}), [])
        xml.dom.minidom.parseString(g.to_kml([]))


class JournalDePreuves(unittest.TestCase):
    def journal(self):
        t = datetime.datetime(2026, 1, 1, 12, 0, 0)
        j, prev = [], ""
        for i, data in enumerate((b"page un", b"page deux", b"page trois"), 1):
            e = g.evidence_entry(prev, data, {"type": "page web", "url": f"https://x.test/{i}", "fichier": f"p{i}.html"}, t)
            e["n"] = i
            j.append(e)
            prev = e["chaine"]
        return j, {"p1.html": b"page un", "p2.html": b"page deux", "p3.html": b"page trois"}

    def test_journal_intact(self):
        j, files = self.journal()
        self.assertEqual(g.evidence_verify(j, files), (True, []))

    def test_empreinte_connue(self):
        e = g.evidence_entry("", b"abc", {})
        self.assertEqual(e["sha256"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(e["taille"], 3)

    def test_fichier_modifie_detecte(self):
        j, files = self.journal()
        files["p2.html"] = b"page deux modifiee"
        ok, pb = g.evidence_verify(j, files)
        self.assertFalse(ok)
        self.assertTrue(any("p2.html" in x and "modifié" in x for x in pb))

    def test_ligne_modifiee_detectee(self):
        j, files = self.journal()
        j[1]["url"] = "https://autre.test"
        ok, pb = g.evidence_verify(j, files)
        self.assertFalse(ok)
        self.assertTrue(any("n°2" in x for x in pb))

    def test_ligne_supprimee_detectee(self):
        j, files = self.journal()
        del j[1]
        ok, pb = g.evidence_verify(j, files)
        self.assertFalse(ok)
        self.assertTrue(any("chaîne est rompue" in x for x in pb))

    def test_date_modifiee_detectee(self):
        j, files = self.journal()
        j[0]["date_utc"] = "2020-01-01T00:00:00Z"
        self.assertFalse(g.evidence_verify(j, files)[0])

    def test_fichier_manquant_detecte(self):
        j, files = self.journal()
        del files["p3.html"]
        ok, pb = g.evidence_verify(j, files)
        self.assertTrue(any("introuvable" in x for x in pb))

    def test_journal_vide(self):
        self.assertEqual(g.evidence_verify([]), (True, []))


if __name__ == "__main__":
    unittest.main()

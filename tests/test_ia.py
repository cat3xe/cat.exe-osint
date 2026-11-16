"""IA locales spécialisées : données, contrôles des réponses et recoupement. Les modèles eux-mêmes sont remplacés par des réponses simulées."""
import contextlib
import io
import unittest

import conftest_path  # noqa: F401
import geo_core as g
import test_sites
O = test_sites.O


class Pays(unittest.TestCase):
    def test_liste_coherente(self):
        fr = [a for a, _ in g.COUNTRIES]
        en = [b for _, b in g.COUNTRIES]
        self.assertEqual(len(fr), len(set(fr)))
        self.assertEqual(len(en), len(set(en)))
        self.assertGreaterEqual(len(fr), 170)
        self.assertTrue(g.LEFT_DRIVING <= set(fr), g.LEFT_DRIVING - set(fr))

    def test_noms_ramenes_au_francais(self):
        for src, exp in (("germany", "Allemagne"), ("USA", "États-Unis"), ("United Kingdom", "Royaume-Uni"), ("england", "Royaume-Uni"), ("Côte d’Ivoire", "Côte d'Ivoire"),
                         ("viet nam", "Viêt Nam"), ("Vietnam", "Viêt Nam"), ("  FRANCE ", "France"), ("Czechia", "République tchèque")):
            self.assertEqual(g.country_fr(src), exp, src)
        self.assertIsNone(g.country_fr("Atlantide"))
        self.assertIsNone(g.country_fr(""))

    def test_sens_de_circulation(self):
        self.assertIn("Japon", g.LEFT_DRIVING)
        self.assertIn("Royaume-Uni", g.LEFT_DRIVING)
        self.assertNotIn("France", g.LEFT_DRIVING)
        self.assertNotIn("États-Unis", g.LEFT_DRIVING)


class IndicesDeTexte(unittest.TestCase):
    def pays(self, t):
        c = g.text_clues(t)
        return c[0]["pays"] if c else []

    def test_ecritures(self):
        self.assertEqual(self.pays("ถนนสุขุมวิท"), ["Thaïlande"])
        self.assertEqual(self.pays("서울역"), ["Corée du Sud", "Corée du Nord"])
        self.assertEqual(self.pays("駅前通り ラーメン"), ["Japon"])           # les kana priment sur les caractères chinois
        self.assertEqual(self.pays("Αθήνα"), ["Grèce", "Chypre"])
        self.assertEqual(self.pays("თბილისი"), ["Géorgie"])
        self.assertEqual(self.pays("תל אביב"), ["Israël"])

    def test_lettres_propres_a_une_langue(self):
        self.assertEqual(self.pays("Вулиця Хрещатик їжа"), ["Ukraine"])       # « ї » : ukrainien, plus précis que « cyrillique »
        self.assertEqual(self.pays("Straße geschlossen"), ["Allemagne", "Autriche"])
        self.assertEqual(self.pays("Rua da Conceição"), ["Portugal", "Brésil"])
        self.assertEqual(self.pays("Łódź Główna"), ["Pologne"])
        self.assertEqual(self.pays("İstanbul Çıkış"), ["Turquie"])

    def test_lettres_ambigues_restent_larges(self):
        c = g.text_clues("über")                                             # « ü » ne suffit pas à désigner un seul pays
        self.assertEqual(c[0]["force"], "moyenne")
        self.assertIn("Allemagne", c[0]["pays"])

    def test_texte_sans_indice(self):
        self.assertEqual(g.text_clues("EXIT 12"), [])
        self.assertEqual(g.text_clues(""), [])
        self.assertEqual(g.text_clues(None), [])


class Entites(unittest.TestCase):
    TEXTE = "Jean Dupont, directeur de la société Acme SARL, a rencontré Marie Curie à Lyon le 12 mars 2024. Contact : @jdupont."

    def test_mise_en_forme(self):
        e = g.normalize_entities({"personnes": ["Jean Dupont", "jean dupont", " ", {"nom": "Marie Curie"}], "organisations": "Acme SARL", "lieux": None, "inconnu": ["x"], "dates": [12]})
        self.assertEqual(e["personnes"], ["Jean Dupont", "Marie Curie"])
        self.assertEqual(e["organisations"], ["Acme SARL"])
        self.assertEqual(e["lieux"], [])
        self.assertEqual(e["dates"], ["12"])
        self.assertNotIn("inconnu", e)

    def test_reponse_inexploitable(self):
        for bad in (None, [], "texte", 3):
            self.assertTrue(all(v == [] for v in g.normalize_entities(bad).values()))

    def test_entites_inventees_ecartees(self):
        ents = g.normalize_entities({"personnes": ["Jean Dupont", "Marie Curie", "Paul Martin"], "organisations": ["Acme SARL", "Globex"], "lieux": ["Lyon", "Paris"], "pseudos": ["@jdupont"]})
        kept, dropped = g.ground_entities(ents, self.TEXTE)
        self.assertEqual(kept["personnes"], ["Jean Dupont", "Marie Curie"])
        self.assertEqual(kept["organisations"], ["Acme SARL"])
        self.assertEqual(kept["lieux"], ["Lyon"])
        self.assertEqual(kept["pseudos"], ["@jdupont"])
        self.assertEqual(sorted(v for _, v in dropped), ["Globex", "Paris", "Paul Martin"])

    def test_accents_et_casse_ne_font_pas_ecarter(self):
        kept, dropped = g.ground_entities({"personnes": ["JEAN DUPONT"], "lieux": ["lyon"]}, self.TEXTE)
        self.assertEqual(dropped, [])

    def test_morceau_de_mot_n_est_pas_une_entite(self):
        kept, dropped = g.ground_entities({"lieux": ["Ly"], "personnes": ["Jean Dup"]}, self.TEXTE)
        self.assertEqual(sorted(v for _, v in dropped), ["Jean Dup", "Ly"])


class FicheIndices(unittest.TestCase):
    def test_mise_en_forme(self):
        c = g.normalize_clues({"textes": ["Rue de la Paix", {"texte": "PHARMACIE"}, "", "none"], "conduite": "à droite", "plaque": "blanche  avec bande bleue",
                               "pays": [{"pays": "germany", "confiance": "30", "raisons": "plaque"}, {"pays": "France", "confiance": 80, "raisons": ["texte en français"]},
                                        {"pays": "Atlantide", "confiance": 99}, "Belgique", {"pays": "france", "confiance": 5}]})
        self.assertEqual(c["textes"], ["Rue de la Paix", "PHARMACIE"])
        self.assertEqual(c["conduite"], "droite")
        self.assertEqual(c["indices"]["plaque"], "blanche avec bande bleue")
        self.assertEqual([p["pays"] for p in c["pays"]], ["France", "Allemagne", "Belgique"])   # trié, pays inconnu et doublon écartés
        self.assertEqual(c["pays"][1]["raisons"], ["plaque"])

    def test_reponses_cassees(self):
        for bad in (None, "texte", [], {"pays": "France"}, {"pays": [None, 3, {"confiance": 10}]}, {"conduite": None, "textes": 5}):
            c = g.normalize_clues(bad)
            self.assertEqual((c["pays"], c["conduite"]), ([], "inconnue"), bad)

    def test_confiance_bornee(self):
        c = g.normalize_clues({"pays": [{"pays": "France", "confiance": 450}, {"pays": "Italie", "confiance": "beaucoup"}]})
        self.assertEqual([(p["pays"], p["confiance"]) for p in c["pays"]], [("France", 100), ("Italie", 0)])


class Recoupement(unittest.TestCase):
    def test_pays_cite_par_plusieurs_sources_en_tete(self):
        v = g.country_votes({"IA de vision": ["Espagne", "Portugal"], "StreetCLIP": ["Portugal", "Brésil"], "écriture lue": ["Portugal", "Brésil"]})
        self.assertEqual(v[0]["pays"], "Portugal")
        self.assertEqual(len(v[0]["sources"]), 3)
        self.assertEqual(v[1]["pays"], "Brésil")

    def test_conduite_a_gauche_contredit_un_pays(self):
        v = g.country_votes({"IA de vision": ["France", "Royaume-Uni"], "StreetCLIP": ["France"]}, "gauche")
        self.assertEqual(v[0]["pays"], "Royaume-Uni")           # cohérent avec la conduite, passe devant
        self.assertTrue(v[0]["coherent"])
        self.assertFalse(next(x for x in v if x["pays"] == "France")["coherent"])

    def test_conduite_inconnue_ne_penalise_personne(self):
        self.assertTrue(all(x["coherent"] for x in g.country_votes({"a": ["Japon", "France"]})))

    def test_noms_anglais_et_francais_comptent_ensemble(self):
        v = g.country_votes({"a": ["Germany"], "b": ["Allemagne"]})
        self.assertEqual((v[0]["pays"], len(v[0]["sources"])), ("Allemagne", 2))

    def test_seuls_les_trois_premiers_comptent(self):
        v = g.country_votes({"a": ["France", "Italie", "Espagne", "Portugal"]})
        self.assertNotIn("Portugal", [x["pays"] for x in v])

    def test_aucune_source(self):
        self.assertEqual(g.country_votes({}), [])

    def test_verdict_du_classement(self):
        self.assertEqual(g.rank_labels(["a", "b", "c"], [0.8, 0.1, 0.1])[1], "net")
        self.assertEqual(g.rank_labels(["a", "b", "c"], [0.4, 0.35, 0.25])[1], "partagé")
        self.assertEqual(g.rank_labels(["a", "b", "c", "d", "e"], [0.2] * 5)[1], "indécis")
        self.assertEqual(g.rank_labels([], []), ([], "aucune réponse"))
        self.assertEqual(g.rank_labels(["a", "b"], [0.1, 0.9], 1)[0], [("b", 0.9)])


class Dossier(unittest.TestCase):
    G = {"nodes": {"enquete:x": {"type": "enquete", "label": "x", "data": {}},
                   "ip:1": {"type": "ip", "label": "1.2.3.4", "data": {"_fiab": "A", "source": "DNS", "pays": "France"}},
                   "lieu:2": {"type": "lieu", "label": "Paris (zone IP)", "data": {"_fiab": "C", "marge": "± 25 km"}},
                   "compte:3": {"type": "compte", "label": "Fausse piste", "data": {"_fiab": "B", "_statut": "faux"}},
                   "note:4": {"type": "note", "label": "à voir", "data": {}}},
         "edges": [{"from": "ip:1", "to": "lieu:2", "label": "≈ position"}, {"from": "ip:1", "to": "compte:3", "label": "x"}]}

    def test_niveaux_transmis_et_fausses_pistes_exclues(self):
        txt, n = g.dossier_brief(self.G)
        self.assertEqual(n, 3)
        self.assertIn("[A] ip | 1.2.3.4", txt)
        self.assertIn("[C] lieu | Paris (zone IP)", txt)
        self.assertIn("[?] note | à voir", txt)
        self.assertNotIn("Fausse piste", txt)
        self.assertIn("1.2.3.4 -> Paris (zone IP) (≈ position)", txt)
        self.assertIn("A = vérifié à la source", txt)

    def test_dossier_vide(self):
        self.assertEqual(g.dossier_brief({})[1], 0)


class AvecModelesSimules(unittest.TestCase):
    def setUp(self):
        self.sauv = {k: getattr(O, k) for k in ("ask_ai_json", "ask_vision", "streetclip_probs")}

    def tearDown(self):
        for k, v in self.sauv.items():
            setattr(O, k, v)

    def test_entites_l_invention_est_ecartee(self):
        O.ask_ai_json = lambda prompt, system=None: {"personnes": ["Jean Dupont", "Nom Inventé"], "lieux": ["Lyon"]}
        kept, dropped = O.ai_entities("Jean Dupont habite à Lyon.")
        self.assertEqual((kept["personnes"], kept["lieux"]), (["Jean Dupont"], ["Lyon"]))
        self.assertEqual(dropped, [("personnes", "Nom Inventé")])

    def test_entites_reponse_vide(self):
        O.ask_ai_json = lambda prompt, system=None: None
        kept, dropped = O.ai_entities("Un texte sans rien de spécial.")
        self.assertTrue(all(v == [] for v in kept.values()))

    def test_fiche_indices(self):
        from PIL import Image
        O.ask_vision = lambda prompt, b64, json_fmt=True, engine=None: ('{"textes": ["Straße"], "conduite": "droite", "pays": [{"pays": "Germany", "confiance": 70}]}', "Ollama · test")
        cl, eng = O.ai_clues(Image.new("RGB", (32, 32)))
        self.assertEqual((cl["textes"], cl["conduite"], cl["pays"][0]["pays"], eng), (["Straße"], "droite", "Allemagne", "Ollama · test"))

    def test_fiche_indices_reponse_illisible(self):
        from PIL import Image
        O.ask_vision = lambda *a, **k: ("désolé, je ne peux pas", "Ollama · test")
        cl, _ = O.ai_clues(Image.new("RGB", (32, 32)))
        self.assertEqual(cl["pays"], [])

    def test_streetclip_classe_les_pays(self):
        fr = [a for a, _ in g.COUNTRIES]
        probs = [0.001] * len(fr)
        probs[fr.index("Japon")] = 0.7
        probs[fr.index("Taïwan")] = 0.1
        O.streetclip_probs = lambda img, labels: probs if labels == [b for _, b in g.COUNTRIES] else None
        top, verdict = O.streetclip_countries(None, 3)
        self.assertEqual(([p for p, _ in top][:2], verdict), (["Japon", "Taïwan"], "net"))

    def test_module_indique_quoi_installer_sans_ia(self):
        def absent(*a, **k):
            raise RuntimeError("IA locale indisponible : installe Ollama")
        O.ask_ai_json = absent
        sauv = (O.select, O.ask_multiline, O.pause)
        choix = ["ent", "t", None]
        O.select = lambda *a, **k: choix.pop(0)
        O.ask_multiline = lambda *a, **k: "Jean Dupont habite à Lyon depuis longtemps."
        O.pause = lambda *a, **k: None
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                O.con.file = buf
                O.mod_aispec()
        finally:
            O.select, O.ask_multiline, O.pause = sauv
        self.assertIn("Ollama", buf.getvalue())


if __name__ == "__main__":
    unittest.main()

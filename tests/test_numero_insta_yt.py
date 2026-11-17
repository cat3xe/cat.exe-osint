"""Lecture des pages : réputation d'un numéro, Instagram (session et plan de secours), YouTube. Aucune requête réseau."""
import unittest

import conftest_path  # noqa: F401
import geo_core as g


class Tellows(unittest.TestCase):
    def test_note_lue(self):
        h = "<h1>+33 6 12 34 56 78</h1><div>Score de cet appelant : <b>8</b> / 9</div>"
        r = g.parse_tellows(h)
        self.assertEqual((r["score"], r["titre"]), (8, "+33 6 12 34 56 78"))

    def test_pas_de_note_on_ne_devine_pas(self):
        self.assertIsNone(g.parse_tellows("<h1>Numéro</h1><p>Aucun avis.</p>")["score"])
        self.assertIsNone(g.parse_tellows("")["score"])

    def test_chiffre_hors_score_ignore(self):
        self.assertIsNone(g.parse_tellows("<p>Page 3 sur 12 · 2024</p>")["score"])


class Spamcalls(unittest.TestCase):
    def test_page_presente(self):
        r = g.parse_spamcalls(200, "<p>Numéro signalé</p>")
        self.assertTrue(r["page"])
        self.assertEqual(r["extrait"], "Numéro signalé")

    def test_pas_de_page(self):
        self.assertEqual(g.parse_spamcalls(404, "<p>x</p>"), {"page": False, "extrait": None})


class FreeLookup(unittest.TestCase):
    def test_resume_lu(self):
        h = '<ul class="report-summary__list"><div>Opérateur</div><div>SFR</div></ul>'
        self.assertEqual(g.parse_free_lookup(h), "Opérateur SFR")

    def test_page_sans_bloc(self):
        self.assertIsNone(g.parse_free_lookup("<div>autre chose</div>"))


class Reputation(unittest.TestCase):
    def test_note_haute_signalee(self):
        n = g.phone_reputation_notes({"tellows": {"score": 8, "titre": None}, "spamcalls": {"page": False}})
        self.assertEqual(n[0][0], "attention")
        self.assertIn("8/9", n[0][1])

    def test_pas_de_note_ni_erreur(self):
        n = g.phone_reputation_notes({"tellows": {"score": None}, "spamcalls": {"erreur": "délai"}})
        self.assertEqual([lv for lv, _ in n], ["info"])
        self.assertIn("pas de note", n[0][1])

    def test_page_spamcalls_avertit(self):
        n = g.phone_reputation_notes({"tellows": {"score": 2}, "spamcalls": {"page": True}})
        self.assertIn("attention", [lv for lv, _ in n])
        self.assertTrue(any("nombre de signalements" in t for _, t in n))


class Instagram(unittest.TestCase):
    def test_fiche_avec_session(self):
        j = {"user": {"username": "alice", "pk": 42, "full_name": "Alice", "follower_count": 10, "following_count": 3,
                      "media_count": 5, "is_private": False, "public_email": "", "contact_phone_number": "+33612345678"}}
        d = g.parse_ig_user(j)
        self.assertEqual((d["_username"], d["_url"], d["Abonnés / abonnements"]), ("alice", "https://www.instagram.com/alice", "10 / 3"))
        self.assertEqual(d["Téléphone public du compte"], "+33612345678")
        self.assertIsNone(d["Email public du compte"])

    def test_reponse_sans_compte(self):
        self.assertIsNone(g.parse_ig_user({"status": "fail"}))
        self.assertIsNone(g.parse_ig_user({"user": {}}))
        self.assertIsNone(g.parse_ig_user(None))


class YouTube(unittest.TestCase):
    def test_identifiant_de_chaine(self):
        h = '{"metadata":{"channelId":"UCabcdefghijklmnopqrstuv"}}'
        self.assertEqual(g.yt_channel_id(h), "UCabcdefghijklmnopqrstuv")
        self.assertEqual(g.yt_channel_id('{"browseId":"UCabcdefghijklmnopqrstuv"}'), "UCabcdefghijklmnopqrstuv")

    def test_pas_d_identifiant(self):
        self.assertIsNone(g.yt_channel_id("<html>rien</html>"))

    def test_abonnes_avec_objets_imbriques(self):
        h = '{"subscriberCountText":{"accessibility":{"accessibilityData":{"label":"1,2 M"}},"simpleText":"1,2 M abonnés"}}'
        self.assertEqual(g.yt_subscribers(h), "1,2 M abonnés")

    def test_abonnes_forme_de_secours(self):
        self.assertEqual(g.yt_subscribers('{"simpleText":"12 k subscribers"}'), "12 k subscribers")

    def test_abonnes_absents(self):
        self.assertIsNone(g.yt_subscribers("<p>rien</p>"))


if __name__ == "__main__":
    unittest.main()

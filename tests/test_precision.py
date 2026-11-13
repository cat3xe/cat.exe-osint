"""Banc de mesure du tri des profils : précision (ce qui est retenu est-il le bon ?) et rappel (les bons sont-ils retenus ?).
Chaque cas est étiqueté à la main : True = ce profil doit être retenu pour la personne cherchée, False = il doit être écarté.
Les cas visent les pièges réels : homonymes partiels, accents, noms composés, particules, initiales, ordre, emojis, villes voisines."""
import unittest

import conftest_path  # noqa: F401
import geo_core as g

# (prénom, nom, ville cherchés, nom affiché, lieu affiché, bio, doit être retenu ?)
CAS = [
    # --- le bon profil, écrit de toutes les façons
    ("Jean", "Dupont", "Lyon", "Jean Dupont", "Lyon", "", True),
    ("Jean", "Dupont", "Lyon", "DUPONT Jean", "Lyon, France", "", True),
    ("Jean", "Dupont", "Lyon", "Dupont, Jean", "Lyon 3e", "", True),
    ("Jean", "Dupont", "Lyon", "jean dupont", "69003 Lyon", "", True),
    ("Jean", "Dupont", "Lyon", "Jean Dupont 🚀", "", "Dev web à Lyon", True),
    ("Jean", "Dupont", "Lyon", "Jean Dupont | Photographe", "Lyon, Auvergne-Rhône-Alpes", "", True),
    ("Jean", "Dupont", "Lyon", "JeanDupont", "Lyon", "", True),
    ("Jean", "Dupont", "Lyon", "Jean M. Dupont", "Lyon", "", True),
    ("Jean", "Dupont", "Lyon", "Jean Michel Dupont", "Lyon", "", True),
    ("Jean", "Dupont", "Lyon", "Dr Jean Dupont", "LYON", "", True),
    ("Jean", "Dupont", "", "Jean Dupont", "", "", True),
    ("Jean", "Dupont", "", "Dupont Jean", "Marseille", "", True),
    ("Jean", "Dupont", "Lyon", "Jean Dupont", "", "", True),            # nom seul : retenu comme homonyme possible
    ("Jean", "Dupont", "Lyon", "Jean Dupont", "Paris", "", True),       # idem (la personne a pu déménager)
    ("Jean-Noël", "Dupont", "Lyon", "Jean-Noël Dupont", "Lyon", "", True),
    ("Jean-Noël", "Dupont", "Lyon", "Jean Noel DUPONT", "Lyon", "", True),
    ("Jean Noel", "Dupont", "Lyon", "Jean-Noël Dupont", "Lyon", "", True),
    ("Jean-Noël", "Dupont", "Lyon", "JeanNoel Dupont", "Lyon", "", True),
    ("Éloïse", "Léger", "Nice", "Eloise Leger", "Nice", "", True),
    ("Eloise", "Leger", "Nice", "Éloïse LÉGER", "Nice, Côte d'Azur", "", True),
    ("Marie", "de La Fontaine", "Tours", "Marie de La Fontaine", "Tours", "", True),
    ("Marie", "de La Fontaine", "Tours", "Marie Delafontaine", "Tours", "", True),
    ("Marie", "Delafontaine", "Tours", "Marie de la Fontaine", "Tours", "", True),
    ("Sean", "O'Connor", "Brest", "Sean O'Connor", "Brest", "", True),
    ("Sean", "OConnor", "Brest", "Sean O'Connor", "Brest", "", True),
    ("Sean", "O'Connor", "Brest", "Sean OConnor", "Brest, Bretagne", "", True),
    ("Anne", "Le Gall", "Quimper", "Anne LE GALL", "Quimper", "", True),
    ("Anne", "Le Gall", "Quimper", "Anne Legall", "Quimper", "", True),
    ("Paul", "Martin-Durand", "Lille", "Paul Martin-Durand", "Lille", "", True),
    ("Paul", "Martin-Durand", "Lille", "Paul Martin Durand", "Lille", "", True),
    ("Lucas", "Bernard", "Saint-Étienne", "Lucas Bernard", "St-Etienne", "", True),
    ("Lucas", "Bernard", "St Etienne", "Lucas Bernard", "Saint-Étienne (42)", "", True),
    ("Lucas", "Bernard", "Aix-en-Provence", "Lucas Bernard", "Aix en Provence", "", True),
    ("Lucas", "Bernard", "Aix en Provence", "Bernard Lucas", "Aix-en-Provence, France", "", True),
    ("Inès", "Moreau", "Grenoble", "Inès Moreau", "Grenoble, Isère", "", True),
    ("Ines", "Moreau", "Grenoble", "Inès Moreau", "", "Étudiante à Grenoble INP", True),
    ("Tom", "Roux", "Paris", "Tom Roux", "Paris 11", "", True),
    ("Tom", "Roux", "Paris", "Tom ROUX", "Paris, Île-de-France", "", True),
    ("Tom", "Roux", "Paris", "Roux Tom", "", "Basé à Paris.", True),
    ("Léa", "Petit", "Sainte-Foy-lès-Lyon", "Léa Petit", "Ste Foy les Lyon", "", True),
    ("Nora", "Ben Ali", "Toulouse", "Nora Ben Ali", "Toulouse", "", True),
    ("Nora", "Ben Ali", "Toulouse", "Nora BENALI", "Toulouse", "", True),
    ("Hugo", "Fournier", "Nantes", "Hugo Fournier", "Nantes, FR", "", True),
    ("Hugo", "Fournier", "Nantes", "hugo fournier", "", "nantes", True),
    ("Zoé", "Girard", "Metz", "Zoe Girard", "Metz", "", True),
    # --- homonymes partiels et comptes d'autres personnes : à écarter
    ("Jean", "Dupont", "Lyon", "Jean Dupond", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Jean Dupontel", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Jeanne Dupont", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Jeannot Dupont", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Marie Dupont", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Jean Martin", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Pierre Durand", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "xX_Killer_Xx", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Dupont", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Jean", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Dupont & Fils SARL", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Famille Dupont", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Jean-Marie Dupontin", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Dupont-Aignan Jean", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "Jean du Pont de Nemours", "Lyon", "", False),
    ("Jean", "Dupont", "", "J. Dupont", "", "", False),
    ("Jean", "Dupont", "Lyon", "J. Dupont", "Paris", "", False),
    ("Jean", "Dupont", "Lyon", "Julie Dupont", "Lyon", "", False),
    ("Jean", "Dupont", "Lyon", "J Dupont", "", "", False),
    ("Éloïse", "Léger", "Nice", "Élodie Léger", "Nice", "", False),
    ("Éloïse", "Léger", "Nice", "Eloise Legere", "Nice", "", False),
    ("Marie", "de La Fontaine", "Tours", "Marie Fontaine", "Tours", "", False),
    ("Marie", "de La Fontaine", "Tours", "Marine de La Fontaine", "Tours", "", False),
    ("Sean", "O'Connor", "Brest", "Sean Connor", "Brest", "", False),
    ("Sean", "O'Connor", "Brest", "Shawn O'Connor", "Brest", "", False),
    ("Anne", "Le Gall", "Quimper", "Anne Gall", "Quimper", "", False),
    ("Anne", "Le Gall", "Quimper", "Annie Le Gall", "Quimper", "", False),
    ("Paul", "Martin-Durand", "Lille", "Paul Martin", "Lille", "", False),
    ("Paul", "Martin-Durand", "Lille", "Paul Durand", "Lille", "", False),
    ("Paul", "Martin", "Lille", "Paul Martinez", "Lille", "", False),
    ("Tom", "Roux", "Paris", "Tom Leroux", "Paris", "", False),
    ("Tom", "Roux", "Paris", "Tommy Roux", "Paris", "", False),
    ("Tom", "Roux", "Paris", "Thomas Roux", "Paris", "", False),
    ("Léa", "Petit", "Lyon", "Léa Petitjean", "Lyon", "", False),
    ("Léa", "Petit", "Lyon", "Léane Petit", "Lyon", "", False),
    ("Nora", "Ben Ali", "Toulouse", "Nora Ali", "Toulouse", "", False),
    ("Nora", "Ben Ali", "Toulouse", "Nora Ben Amar", "Toulouse", "", False),
    ("Hugo", "Fournier", "Nantes", "Hugo Fourniret", "Nantes", "", False),
    ("Hugo", "Fournier", "Nantes", "Hugues Fournier", "Nantes", "", False),
    ("Zoé", "Girard", "Metz", "Zoé Girardin", "Metz", "", False),
    ("Zoé", "Girard", "Metz", "Chloé Girard", "Metz", "", False),
    ("Inès", "Moreau", "Grenoble", "Inès Morel", "Grenoble", "", False),
    ("Inès", "Moreau", "Grenoble", "Agnès Moreau", "Grenoble", "", False),
    ("Lucas", "Bernard", "Lyon", "Luca Bernard", "Lyon", "", False),
    ("Lucas", "Bernard", "Lyon", "Lucas Bernardi", "Lyon", "", False),
]

# (ville cherchée, texte du profil, la ville correspond ?)
VILLES = [
    ("Lyon", "Lyon", True), ("Lyon", "Lyon 3e", True), ("Lyon", "69003 Lyon", True), ("Lyon", "LYON, France", True),
    ("Lyon", "Grand Lyon", True), ("Lyon", "Villeurbanne", False), ("Lyon", "Lyons-la-Forêt", False), ("Lyon", "Sainte-Foy-lès-Lyon", False),
    ("Nice", "Nice", True), ("Nice", "Nicewood", False), ("Nice", "Venice", False), ("Nice", "Very nice guy", False),
    ("Paris", "Paris 11", True), ("Paris", "Parisot", False), ("Paris", "Cormeilles-en-Parisis", False),
    ("Saint-Étienne", "St Etienne", True), ("St-Etienne", "Saint Étienne", True), ("Saint-Étienne", "Saint-Étienne-du-Rouvray", False),
    ("Sainte-Foy-lès-Lyon", "Ste Foy les Lyon", True), ("Aix-en-Provence", "Aix en Provence", True), ("Aix-en-Provence", "Aix-les-Bains", False),
    ("Grenoble", "Grenoble, Isère", True), ("Grenoble", "Université Grenoble Alpes", True), ("Grenoble", "", False),
    ("Tours", "Tours", True), ("Tours", "Tourcoing", False), ("Tours", "Joué-lès-Tours", False), ("Metz", "Metz", True), ("Metz", "Metzervisse", False),
    ("Toulouse", "toulouse", True), ("Brest", "Brest, Bretagne", True), ("Nantes", "Nanterre", False),
]


# ---- LOT DE CONTRÔLE : écrit après coup, jamais utilisé pour régler le code. C'est lui qui donne le taux honnête.
CAS_CONTROLE = [
    ("Mohamed", "El Amrani", "Lille", "Mohamed El Amrani", "Lille", "", True),
    ("Mohamed", "El Amrani", "Lille", "Mohamed Elamrani", "Lille", "", True),
    ("Mohamed", "El Amrani", "Lille", "EL AMRANI Mohamed", "Lille, Nord", "", True),
    ("Mohamed", "El Amrani", "Lille", "Mohammed El Amrani", "Lille", "", False),
    ("Mohamed", "El Amrani", "Lille", "Mohamed Amrani", "Lille", "", False),
    ("Mohamed", "El Amrani", "Lille", "Mohamed El Amri", "Lille", "", False),
    ("Anne-Sophie", "Lefèvre", "Rouen", "Anne-Sophie Lefèvre", "Rouen", "", True),
    ("Anne-Sophie", "Lefèvre", "Rouen", "Anne Sophie LEFEVRE", "Rouen", "", True),
    ("Anne-Sophie", "Lefèvre", "Rouen", "AnneSophie Lefevre", "Rouen", "", True),
    ("Anne-Sophie", "Lefèvre", "Rouen", "Anne Lefèvre", "Rouen", "", False),
    ("Anne-Sophie", "Lefèvre", "Rouen", "Anne-Sophie Lefebvre", "Rouen", "", False),
    ("Anne-Sophie", "Lefèvre", "Rouen", "Sophie Lefèvre", "Rouen", "", False),
    ("Minh", "Nguyen", "Paris", "Minh Nguyen", "Paris 13", "", True),
    ("Minh", "Nguyen", "Paris", "Nguyen Minh", "Paris", "", True),
    ("Minh", "Nguyen", "Paris", "Nguyen Van Minh", "Paris", "", True),
    ("Minh", "Nguyen", "Paris", "Minh-Anh Nguyen", "Paris", "", False),
    ("Minh", "Nguyen", "Paris", "Linh Nguyen", "Paris", "", False),
    ("Minh", "Nguyen", "Paris", "Minh Tran", "Paris", "", False),
    ("Pieter", "van der Berg", "Lille", "Pieter van der Berg", "Lille", "", True),
    ("Pieter", "van der Berg", "Lille", "Pieter Vanderberg", "Lille", "", True),
    ("Pieter", "van der Berg", "Lille", "Pieter Berg", "Lille", "", False),
    ("Pieter", "van der Berg", "Lille", "Pieter van den Berg", "Lille", "", False),
    ("Lucia", "D'Angelo", "Nice", "Lucia D'Angelo", "Nice", "", True),
    ("Lucia", "D'Angelo", "Nice", "Lucia Dangelo", "Nice 06000", "", True),
    ("Lucia", "D'Angelo", "Nice", "Lucia Angelo", "Nice", "", False),
    ("Lucia", "D'Angelo", "Nice", "Lucie D'Angelo", "Nice", "", False),
    ("Karim", "Benzema", "Bron", "Karim Benzema (@kb9)", "Bron", "", True),
    ("Karim", "Benzema", "Bron", "karim_benzema", "Bron", "", True),
    ("Karim", "Benzema", "Bron", "karim.benzema", "", "", True),
    ("Karim", "Benzema", "Bron", "Karim ✨ Benzema", "Bron, Rhône", "", True),
    ("Karim", "Benzema", "Bron", "Me Karim Benzema, avocat", "Bron", "", True),
    ("Karim", "Benzema", "Bron", "Karim BENZEMA - Consultant SEO", "", "Bron et alentours", True),
    ("Karim", "Benzema", "Bron", "Karim Benzema Jr", "Bron", "", True),
    ("Karim", "Benzema", "Bron", "benzema.karim69", "Bron", "", True),
    ("Karim", "Benzema", "Bron", "Karima Benzema", "Bron", "", False),
    ("Karim", "Benzema", "Bron", "Karim Benzemat", "Bron", "", False),
    ("Karim", "Benzema", "Bron", "Kamel Benzema", "Bron", "", False),
    ("Karim", "Benzema", "Bron", "KB", "Bron", "", False),
    ("Claire", "Dubois", "Angers", "Claire Dubois", "Angers", "", True),
    ("Claire", "Dubois", "Angers", "Claire Dubois-Martin", "Angers", "", False),
    ("Claire", "Dubois", "Angers", "Marie-Claire Dubois", "Angers", "", False),
    ("Claire", "Dubois", "Angers", "Clair Dubois", "Angers", "", False),
    ("Claire", "Dubois", "Angers", "Claire du Bois", "Angers", "", True),
    ("Claire", "Dubois", "Angers", "Claire Duboys", "Angers", "", False),
    ("Yanis", "Haddad", "Marseille", "Yanis Haddad", "Marseille 13008", "", True),
    ("Yanis", "Haddad", "Marseille", "HADDAD Yanis", "", "né à Marseille", True),
    ("Yanis", "Haddad", "Marseille", "Yannis Haddad", "Marseille", "", False),
    ("Yanis", "Haddad", "Marseille", "Yanis Hadad", "Marseille", "", False),
    ("Yanis", "Haddad", "Marseille", "Y. Haddad", "", "", False),
    ("Yanis", "Haddad", "Marseille", "Anis Haddad", "Marseille", "", False),
]

VILLES_CONTROLE = [
    ("Le Mans", "Le Mans", True), ("Le Mans", "le mans", True), ("Le Mans", "Mansfield", False),
    ("La Rochelle", "La Rochelle, Charente-Maritime", True), ("La Rochelle", "La Roche-sur-Yon", False),
    ("Saint-Denis", "St Denis (93)", True), ("Saint-Denis", "Saint-Denis-de-la-Réunion", False), ("Saint-Denis", "Saint Denis de la Réunion", False),
    ("Bordeaux", "Bordeaux Métropole", True), ("Bordeaux", "Bordeaux, Gironde", True), ("Bordeaux", "Vin de bordeaux et gastronomie", False),
    ("Angers", "Angers", True), ("Angers", "Tangers", False), ("Reims", "REIMS", True), ("Pau", "Paul", False), ("Pau", "Pau, 64", True),
    ("Lille", "Lillers", False), ("Lille", "Métropole lilloise", False), ("Lille", "Lille-Flandres", False), ("Rennes", "Rennes 2", True),
    ("Brest", "Brest-Litovsk", False), ("Caen", "Caen la mer", True), ("Cannes", "Cannes la Bocca", True), ("Montpellier", "Montpellier Hérault", True),
    ("Vienne", "Vienne (38)", True), ("Marseille", "Marseille 8e", True), ("Marseille", "Marseillan", False), ("Dijon", "Dijon / Paris", True),
    ("Strasbourg", "Eurométropole de Strasbourg", True), ("Nancy", "Nancy, Lorraine", True), ("Orléans", "Orleans", True), ("Orléans", "La Nouvelle-Orléans", False),
    ("Clermont-Ferrand", "Clermont Ferrand", True), ("Clermont-Ferrand", "Clermont", False), ("Annecy", "Annecy-le-Vieux", False), ("Annecy", "annecy", True),
    ("Mulhouse", "Mulhouse Alsace", True), ("Toulon", "Toulon sur Arroux", False), ("Toulon", "Toulon, Var", True), ("Limoges", "Limoges", True),
]


def mesure(cas=None):
    vp = fp = fn = vn = 0
    erreurs = []
    for first, last, city, shown, lieu, bio, attendu in (cas if cas is not None else CAS):
        verdict = g.person_score({"Nom": shown, "Lieu": lieu, "Bio": bio}, first, last, city)[1]
        retenu = verdict in ("fort", "moyen")
        if retenu and attendu:
            vp += 1
        elif retenu and not attendu:
            fp += 1
            erreurs.append(f"RETENU À TORT  : {first} {last} / {city} ← « {shown} » ({lieu}) → {verdict}")
        elif attendu:
            fn += 1
            erreurs.append(f"ÉCARTÉ À TORT  : {first} {last} / {city} ← « {shown} » ({lieu}) → {verdict}")
        else:
            vn += 1
    return vp, fp, fn, vn, erreurs


class Precision(unittest.TestCase):
    def test_tri_des_profils_au_dessus_de_95_pour_cent(self):
        vp, fp, fn, vn, erreurs = mesure()
        precision = vp / (vp + fp) if vp + fp else 0
        rappel = vp / (vp + fn) if vp + fn else 0
        print(f"\ntri des profils : {len(CAS)} cas · précision {precision:.1%} · rappel {rappel:.1%} · {len(erreurs)} erreur(s)")
        for e in erreurs:
            print("  ", e)
        self.assertGreaterEqual(precision, 0.95, "trop de profils retenus à tort")
        self.assertGreaterEqual(rappel, 0.95, "trop de bons profils écartés")

    def test_villes_au_dessus_de_95_pour_cent(self):
        faux = [(c, t, a) for c, t, a in VILLES if g.city_match(t, c) != a]
        taux = 1 - len(faux) / len(VILLES)
        print(f"\nvilles : {len(VILLES)} cas · {taux:.1%} justes")
        for c, t, a in faux:
            print(f"   ERREUR : « {c} » dans « {t} » → attendu {a}")
        self.assertGreaterEqual(taux, 0.95)

    def test_lot_de_controle_au_dessus_de_95_pour_cent(self):
        vp, fp, fn, vn, erreurs = mesure(CAS_CONTROLE)
        precision = vp / (vp + fp) if vp + fp else 0
        rappel = vp / (vp + fn) if vp + fn else 0
        print(f"\nLOT DE CONTRÔLE profils : {len(CAS_CONTROLE)} cas · précision {precision:.1%} · rappel {rappel:.1%} · {len(erreurs)} erreur(s)")
        for e in erreurs:
            print("  ", e)
        self.assertGreaterEqual(precision, 0.95, "trop de profils retenus à tort")
        self.assertGreaterEqual(rappel, 0.95, "trop de bons profils écartés")

    def test_villes_de_controle_au_dessus_de_95_pour_cent(self):
        faux = [(c, t, a) for c, t, a in VILLES_CONTROLE if g.city_match(t, c) != a]
        taux = 1 - len(faux) / len(VILLES_CONTROLE)
        print(f"\nLOT DE CONTRÔLE villes : {len(VILLES_CONTROLE)} cas · {taux:.1%} justes")
        for c, t, a in faux:
            print(f"   ERREUR : « {c} » dans « {t} » → attendu {a}")
        self.assertGreaterEqual(taux, 0.95)

    def test_ville_seule_ne_suffit_jamais(self):
        # même ville, autre nom : jamais retenu, quel que soit le cas
        for first, last, city, shown, lieu, bio, attendu in CAS:
            if not attendu and g.name_match(shown, first, last) < 2:
                self.assertNotIn(g.person_score({"Nom": shown, "Lieu": lieu, "Bio": bio}, first, last, city)[1], ("fort", "moyen"))


if __name__ == "__main__":
    unittest.main()

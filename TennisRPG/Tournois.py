""" Ce fichier contient la liste de tous les tournois que l'on peut retrouver sur une année"""

import math
import random


# Todo: Cette fonction sera à revoir lorsque l'on aura le système de blessure et d'objectifs
def est_eligible_pour_tournoi(joueur, tournoi, classement):
    seuils = {
        # Ce fix est moche (passage de 128 à 130 joueurs éligible) sera amélioré plus tard
        "GrandSlam": 130,  # Top 128 pour les Grands Chelems
        "ATP Finals": 8,  # Top 8 pour l'ATP Finals
        "ATP1000 #6": 60,  # Top 60 pour les Masters 1000 à 6 tours
        "ATP1000 #7": 100,  # Top 100 pour les Masters 1000 à 7 tours
        "ATP500 #6": 100,  # Top 100 pour les ATP 500 à 6 tours
        "ATP500 #5": 100,  # Top 100 pour les ATP 500 à 5 tours
        "ATP250 #6": 200,  # Top 200 pour les ATP 250 à 6 tours
        "ATP250 #5": 200,  # Top 200 pour les ATP 250 à 5 tours
    }
    
    classement_joueur = classement.obtenir_rang(joueur, type="atp")
    
    return classement_joueur <= seuils.get(tournoi.categorie)


def seed(n):
    """returns list of n in standard tournament seed order

    Note that n need not be a power of 2 - 'byes' are returned as zero
    """
    ol = [1]

    for i in range(math.ceil(math.log(n) / math.log(2))):
        l = 2 * len(ol) + 1
        ol = [e if e <= n else 0 for s in [[el, l - el] for el in ol] for e in s]

    ol = [e if e <= n else 0 for e in ol]

    return ol


def selectionner_joueurs_pour_tournoi(
    tournoi, joueurs_disponibles, classement, type="elo"
):
    joueurs_eligibles = [j for j in joueurs_disponibles if est_eligible_pour_tournoi(j, tournoi, classement) and j.peut_jouer()]
    joueur_tries = sorted(
        joueurs_eligibles, key=lambda j: classement.obtenir_rang(j, type)
    )
    if tournoi.categorie == "ATP Finals":
        joueur_tries = sorted(
            joueurs_eligibles, key=lambda j: classement.obtenir_rang(j, "atp_race")
        )
    return joueur_tries[: tournoi.nb_joueurs]


class Tournoi:
    POINTS_ATP = {
        "GrandSlam": {
            1: 10,
            2: 50,
            3: 100,
            4: 200,
            5: 400,
            6: 800,
            7: 1300,
            "Vainqueur": 2000,
        },
        "ATP1000 #7": {
            1: 10,
            2: 30,
            3: 50,
            4: 100,
            5: 200,
            6: 400,
            7: 650,
            "Vainqueur": 1000,
        },
        "ATP1000 #6": {1: 10, 2: 50, 3: 100, 4: 200, 5: 400, 6: 650, "Vainqueur": 1000},
        "ATP500 #6": {1: 0, 2: 25, 3: 50, 4: 100, 5: 200, 6: 330, "Vainqueur": 500},
        "ATP500 #5": {1: 0, 2: 50, 3: 100, 4: 200, 5: 330, "Vainqueur": 500},
        "ATP250 #6": {1: 0, 2: 13, 3: 25, 4: 50, 5: 100, 6: 165, "Vainqueur": 250},
        "ATP250 #5": {1: 0, 2: 25, 3: 50, 4: 100, 5: 165, "Vainqueur": 250},
    }
    
    # Todo: Ajuster le tableau pour avoir quelque chose de cohérent (Mieux mais pas encore sûr de la cohérence)
    XP_PAR_TOUR = {
        "GrandSlam": {1: 100, 2: 200, 3: 400, 4: 600, 5: 750, 6: 900, 7: 1000, "Vainqueur": 1250},
        "ATP1000 #7": {1: 30, 2: 60, 3: 100, 4: 125, 5: 150, 6: 200, 7: 225, "Vainqueur": 250},
        "ATP1000 #6": {1: 30, 2: 60, 3: 100, 4: 125, 5: 150, 6: 200, "Vainqueur": 250},
        "ATP500 #6": {1: 25, 2: 50, 3: 75, 4: 100, 5: 125, 6: 130, "Vainqueur": 150},
        "ATP500 #5": {1: 25, 2: 50, 3: 75, 4: 100, 5: 125, "Vainqueur": 150},
        "ATP250 #6": {1: 10, 2: 20, 3: 40, 4: 80, 5: 100, 6: 110, "Vainqueur": 120},
        "ATP250 #5": {1: 10, 2: 20, 3: 40, 4: 80, 5: 100, "Vainqueur": 110},
        "ATP Finals": {1: 250, 2: 400, 3: 500, "Vainqueur": 1000}  # Ajusté pour l'ATP Finals
    }
    
    def __init__(self, categorie, nom, emplacement, nb_joueurs, surface, week):
        self.categorie = categorie
        self.nom = nom
        self.emplacement = emplacement
        self.nb_joueurs = nb_joueurs
        self.surface = surface
        self.week = week
        #self.vainqueurs = {}
    
    # We need to update the Calendar function to be able to use this function
    def jouer(self, joueur, participants, classement, type="atp"):
        # Si le joueur n'est pas dans la liste des participants, ont l'ajoute et on retire un participant
        # TODO: In the grand slam, we don't have the right number of participants.
        #  We must check why
        if joueur not in participants:
            participants.append(joueur)
        
            # qu'on trie par classement
            participants = sorted(
                participants, key=lambda j: classement.obtenir_rang(j, type)
            )
            
            if joueur == participants[-1]:  # Si le joueur est dernier du classement, on retire celui avant lui
                participants.pop(-2)
            else:
                participants.pop(-1)  # Sinon, on retire le dernier
                
        resultat = self.simuler_tournoi(participants, classement, type)  # On peut simuler le tournoi
        return resultat
    
    def simuler_tournoi(self, participants, classement, type="elo", preliminaire=False):
        if self.categorie == "ATP Finals":
            return self.simuler_tournoi_finals(participants, classement, preliminaire)
        
        nb_tours = math.ceil(math.log2(self.nb_joueurs))
        nb_tetes_de_serie = 2 ** (nb_tours - 2)
        
        noms_phases = {
            nb_tours: "en finale",
            nb_tours - 1: "en demi-finale",
            nb_tours - 2: "en quart de finale"
        }
        
        joueurs_tries = sorted(
            participants, key=lambda j: classement.obtenir_rang(j, type)
        )
        # Sélectionner les têtes de série
        tetes_de_serie = joueurs_tries[:nb_tetes_de_serie]

        # Sélectionner les autres participants aléatoirement
        autres_participants = joueurs_tries[nb_tetes_de_serie: self.nb_joueurs]

        ordre_placement = seed(self.nb_joueurs)

        # Créer le tableau du tournoi
        tableau = []
        participants = tetes_de_serie + autres_participants

        for i in range(0, len(ordre_placement), 2):
            if i + 1 < len(ordre_placement):
                pos1, pos2 = ordre_placement[i], ordre_placement[i + 1]
                if pos1 != 0 and pos2 != 0:
                    tableau.append((participants[pos1 - 1], participants[pos2 - 1]))
                elif pos1 != 0:
                    tableau.append((participants[pos1 - 1], None))
                elif pos2 != 0:
                    tableau.append((participants[pos2 - 1], None))

        derniers_tours = {joueur: 0 for joueur in participants}

        for tour in range(1, nb_tours + 1):
            prochain_tour = []
            for match in tableau:
                joueur1, joueur2 = match
                if joueur1 and joueur2:
                    gagnant = self.simuler_match(joueur1, joueur2)[0]
                    perdant = joueur2 if gagnant == joueur1 else joueur1
                    derniers_tours[perdant] = tour
                    if perdant.principal:
                        phase = noms_phases.get(tour, f"au tour {tour}")
                        accord = "e" if perdant.sexe.lower() == 'f' else ""
                        print(f"\n{perdant.prenom} {perdant.nom} a été éliminé{accord} {phase}")
                    prochain_tour.append(gagnant)
                elif joueur1:
                    prochain_tour.append(joueur1)
                elif joueur2:
                    prochain_tour.append(joueur2)

            tableau = [
                (
                    (prochain_tour[i], prochain_tour[i + 1])
                    if i + 1 < len(prochain_tour)
                    else (prochain_tour[i], None)
                )
                for i in range(0, len(prochain_tour), 2)
            ]

        vainqueur = prochain_tour[0]
        derniers_tours[vainqueur] = "Vainqueur"
        if not preliminaire:
            print(f"\nVainqueur du tournoi {self.nom}:\n{vainqueur.prenom} {vainqueur.nom}")
        
        resultats = {}
        for joueur, dernier_tour in derniers_tours.items():
            self.attribuer_points_atp(joueur, dernier_tour)
            xp_gagne = self.XP_PAR_TOUR[self.categorie].get(dernier_tour, 0)
            resultats[joueur] = self.POINTS_ATP.get(self.categorie, {}).get(dernier_tour, 0)
            joueur.gagner_experience(xp_gagne)
            
        # Note the return will be useful when we'll save the info in a database
        return resultats
    
    def simuler_tournoi_finals(self, participants, classement, preliminaire=False):
        # Todo: add a logic for the players that are injured (add the two substitutes)
        if len(participants) != 8:
            raise ValueError("L'ATP Finals nécessite exactement 8 participants")
        
        # Trier les joueurs par classement
        joueurs_tries = sorted(participants, key=lambda j: classement.obtenir_rang(j, "atp_race"))
        
        # répartir les joueurs en deux poules
        # Todo: rajouter de l'aléatoire dans la création des poules
        poule_a = [joueurs_tries[0], joueurs_tries[3], joueurs_tries[4], joueurs_tries[7]]
        poule_b = [joueurs_tries[1], joueurs_tries[2], joueurs_tries[5], joueurs_tries[6]]
        
        # Simuler les matchs de poules
        resultats_poule_a = self.simuler_matchs_poule(poule_a)
        resultats_poule_b = self.simuler_matchs_poule(poule_b)
        
        resultats = {}
        for poule in [resultats_poule_a, resultats_poule_b]:
            for joueur, resultat in poule.items():
                points_victoires = resultat["victoires"] * 200  # +200 pts par victoire en poule
                joueur.atp_points += points_victoires
                resultats[joueur] = points_victoires
                
        # Sélectionner les deux meilleurs de chaque poule
        qualifies_a = self.selectionner_qualifies(resultats_poule_a)
        qualifies_b = self.selectionner_qualifies(resultats_poule_b)

        # Demi finales
        demi_finale_1 = self.simuler_match(qualifies_a[0], qualifies_b[1])[0]
        demi_finale_2 = self.simuler_match(qualifies_b[0], qualifies_a[1])[0]
        
        for demi_finaliste in [demi_finale_1, demi_finale_2]:
            resultats[demi_finaliste] += 400  # 400 points pour une victoire en demi-finale
            demi_finaliste.atp_points += 400

        # Finale
        vainqueur = self.simuler_match(demi_finale_1, demi_finale_2)[0]
        resultats[vainqueur] += 500
        vainqueur.atp_points += 500  # +500pts si victoire en finale
        if not preliminaire:
            print(f"\nVainqueur du tournoi {self.nom}:\n{vainqueur.prenom} {vainqueur.nom}")
        
        # Progression des joueurs
        for joueur in participants:
            if joueur == vainqueur:
                xp_gagne = self.XP_PAR_TOUR["ATP Finals"]["Vainqueur"]
            elif joueur in [demi_finale_1, demi_finale_2]:
                xp_gagne = self.XP_PAR_TOUR["ATP Finals"][3]
            elif joueur in qualifies_a + qualifies_b:
                xp_gagne = self.XP_PAR_TOUR["ATP Finals"][2]
            else:
                xp_gagne = self.XP_PAR_TOUR["ATP Finals"][1]
            joueur.gagner_experience(xp_gagne)
        
        return resultats
    
    def simuler_matchs_poule(self, poule):
        resultats = {joueur: {'victoires': 0, 'sets_gagnes': 0, 'confrontations': {}} for joueur in poule}
        for i in range(len(poule)):
            for j in range(i+1, len(poule)):
                gagnant, perdant, sets_gagnant, sets_perdant = self.simuler_match(poule[i], poule[j])
                # Update infos sur le gagnant
                resultats[gagnant]['victoires'] += 1
                resultats[gagnant]['sets_gagnes'] += sets_gagnant
                resultats[gagnant]["confrontations"][perdant] = 'V'
                
                # Update infos sur le perdant
                resultats[perdant]['sets_gagnes'] += sets_perdant
                resultats[perdant]["confrontations"][gagnant] = 'D'
        return resultats
    
    @staticmethod
    def selectionner_qualifies(resultats_poule):
        joueurs_tries = sorted(resultats_poule.items(), key=lambda x: x[1]['victoires'], reverse=True)
        
        # Si pas d'égalité pour les deux premières places
        if joueurs_tries[1][1]['victoires'] > joueurs_tries[2][1]['victoires']:
            return [joueurs_tries[0][0], joueurs_tries[1][0]]
        
        # En cas d'égalités
        joueurs_a_egalite = [j for j, r in joueurs_tries if r['victoires'] == joueurs_tries[1][1]['victoires']]
        
        # À 2
        if len(joueurs_a_egalite) == 2:
            # On compare les confrontations directes
            if resultats_poule[joueurs_a_egalite[0]]["confrontations"][joueurs_a_egalite[1]] == 'V':
                if resultats_poule[joueurs_a_egalite[0]]['confrontations'][joueurs_a_egalite[1]] == 'V':
                    return [joueurs_tries[0][0], joueurs_a_egalite[0]]
                else:
                    return [joueurs_tries[0][0], joueurs_a_egalite[1]]
        # À 3
        else:
            
            return [joueurs_tries[0][0], joueurs_tries[1][0]]
        
    def attribuer_points_atp(self, joueur, dernier_tour):
        points = self.POINTS_ATP.get(self.categorie, {}).get(dernier_tour, 0)
        joueur.atp_points += points
        joueur.atp_race_points += points
    
    def simuler_match(self, joueur1, joueur2):
        elo1 = joueur1.calculer_elo(surface=self.surface)
        elo2 = joueur2.calculer_elo(surface=self.surface)

        proba1 = 1 / (1 + 10 ** ((elo2 - elo1) / 400))
        
        # Logique sur le score du match.
        # Note: On pourra se servir de cela pour simuler la fatigue d'un joueur
        #  (plus un match est long et plus les joueurs seront fatigués)
        sets_necessaires = 3 if self.categorie == "GrandSlam" else 2
        sets_joueur1, sets_joueur2 = 0, 0
        
        while max(sets_joueur1, sets_joueur2) < sets_necessaires:
            if random.random() < proba1:
                sets_joueur1 += 1
            else:
                sets_joueur2 += 1
            
        if sets_joueur1 > sets_joueur2:
            gagnant, perdant = joueur1, joueur2
            sets_gagnant, sets_perdant = sets_joueur1, sets_joueur2
        else:
            gagnant, perdant = joueur2, joueur1
            sets_gagnant, sets_perdant = sets_joueur2, sets_joueur1
        
        # Mise à jour des Elo
        k = 32
        elo_change = k * (1 - 1 / (1 + 10 ** ((perdant.elo - gagnant.elo) / 400)))

        gagnant.elo += elo_change
        perdant.elo -= elo_change

        return gagnant, perdant, sets_gagnant, sets_perdant
    

tournoi = {
    1: [
        Tournoi("ATP250 #5", "Brisbane International", "Brisbane", 32, "Hard", 1),
        Tournoi(
            "ATP250 #5", "Bank Of China Honk Kong Tennis Open", "Hong Kong", 28, "Hard", 1
        ),
    ],
    2: [
        Tournoi("ATP250 #5", "Adelaide International", "Adelaide", 28, "Hard", 2),
        Tournoi("ATP250 #5", "ASB Classic", "Auckland", 28, "Hard", 2),
    ],
    3: [Tournoi("GrandSlam", "Australian Open", "Melbourne", 128, "Hard", 3)],
    5: [Tournoi("ATP250 #5", "Open Sud de France", "Montpellier", 28, "Hard", 5)],
    6: [
        Tournoi("ATP250 #5", "Cordoba Open", "Cordoba", 28, "Clay", 6),
        Tournoi("ATP250 #5", "Dallas Open", "Dallas", 28, "Indoor Hard", 6),
        Tournoi("ATP250 #5", "Open 13 Provence", "Marseille", 28, "Indoor Hard", 6),
    ],
    7: [
        Tournoi("ATP500 #5", "ABN Amro Open", "Rotterdam", 32, "Indoor Hard", 7),
        Tournoi("ATP250 #5", "IEB+ Argentina Open", "Buenos Aires", 28, "Clay", 7),
        Tournoi("ATP250 #5", "Delray Beach Open", "Delray Beach", 28, "Hard", 7),
    ],
    8: [
        Tournoi("ATP500 #5", "Rio Open", "Rio de Janeiro", 32, "Clay", 8),
        Tournoi("ATP250 #5", "Qater Exxonmobil Open", "Doha", 28, "Hard", 8),
        Tournoi("ATP250 #5", "Mifel Tennis Open", "Los Cabos", 28, "Hard", 8),
    ],
    9: [
        Tournoi("ATP500 #5", "Abierto Mexicano", "Acapulco", 32, "Hard", 9),
        Tournoi(
            "ATP500 #5", "Dubai Duty Free Tennis Championships", "Dubai", 32, "Hard", 9
        ),
        Tournoi("ATP250 #5", "Movistar Chile Open", "Santiago", 28, "Clay", 9),
    ],
    10: [Tournoi("ATP1000 #7", "BNP Paribas Open", "Indian Wells", 96, "Hard", 10)],
    12: [Tournoi("ATP1000 #7", "Miami Open", "Miami", 96, "Hard", 12)],
    14: [
        Tournoi("ATP250 #5", "Millennium Estoril Open", "Estoril", 28, "Clay", 14),
        Tournoi("ATP250 #5", "Grand Prix Hassan II", "Marrakech", 28, "Clay", 14),
        Tournoi(
            "ATP250 #5", "Fayez Sarofim Clay Court Championships", "Houston", 28, "Clay", 14
        ),
    ],
    15: [Tournoi("ATP1000 #6", "Rolex Monte Carlo Masters", "Monte-Carlo", 56, "Clay", 15)],
    16: [
        Tournoi("ATP500 #6", "Barcelona Open Banc Sabadell", "Barcelona", 48, "Clay", 16),
        Tournoi("ATP250 #5", "BMW Open", "Munich", 28, "Clay", 16),
        Tournoi("ATP250 #5", "Tiriac Open", "Bucharest", 28, "Clay", 16),
    ],
    17: [Tournoi("ATP1000 #7", "Mutua Madrid Open", "Madrid", 96, "Clay", 17)],
    19: [Tournoi("ATP1000 #7", "Internazionali BNL d'Italia", "Rome", 96, "Clay", 19)],
    21: [
        Tournoi("ATP250 #5", "Gonet Geneva Open", "Geneva", 28, "Clay", 21),
        Tournoi("ATP250 #5", "Open Parc", "Lyon", 28, "Clay", 21),
    ],
    22: [Tournoi("GrandSlam", "Roland-Garros", "Paris", 128, "Clay", 22)],
    24: [
        Tournoi("ATP250 #5", "Libema Open", "'s-Hertogenbosch", 28, "Grass", 24),
        Tournoi("ATP250 #5", "Boss Open", "Stuttgart", 28, "Grass", 24),
    ],
    25: [
        Tournoi("ATP500 #5", "Terra Wortmann Open", "Halle", 32, "Grass", 25),
        Tournoi("ATP500 #5", "Cinch Championships", "London", 32, "Grass", 25),
    ],
    26: [
        Tournoi("ATP250 #5", "Mallorca Championships", "Mallorca", 28, "Grass", 26),
        Tournoi("ATP250 #5", "Rothesay International", "Eastbourne", 28, "Grass", 26),
    ],
    27: [Tournoi("GrandSlam", "Wimbledon", "London", 128, "Grass", 27)],
    29: [
        Tournoi("ATP500 #5", "Hamburg Open", "Hamburg", 32, "Clay", 29),
        Tournoi("ATP250 #5", "Nordea Open", "Bastad", 28, "Clay", 29),
        Tournoi("ATP250 #5", "EFG Swiss Open Gstaad", "Gstaad", 28, "Clay", 29),
        Tournoi("ATP250 #5", "Infosys Hall Of Fame Open", "Newport", 28, "Grass", 29),
    ],
    30: [
        Tournoi("ATP250 #5", "Plava Laguna Croatia Open Umag", "Umag", 28, "Clay", 30),
        Tournoi("ATP250 #5", "Generali Open", "Kitzbuhel", 28, "Clay", 30),
        Tournoi("ATP250 #5", "Atlanta Open", "Atlanta", 28, "Hard", 30),
    ],
    31: [Tournoi("ATP500 #6", "Mubadala Citi DC Open", "Washington DC", 48, "Hard", 31)],
    32: [Tournoi("ATP1000 #6", "National Bank Open", "Montreal", 56, "Hard", 32)],
    33: [Tournoi("ATP1000 #6", "Cincinnati Open", "Cincinnati", 56, "Hard", 33)],
    34: [Tournoi("ATP250 #6", "Winston Salem Open", "Winston Salem", 48, "Hard", 34)],
    35: [Tournoi("GrandSlam", "US Open", "New York", 128, "Hard", 35)],
    38: [
        Tournoi("ATP250 #5", "Chengdu Open", "Chengdu", 28, "Hard", 38),
        Tournoi("ATP250 #5", "Hangzhou Open", "Hangzhou", 28, "Hard", 38),
    ],
    39: [
        Tournoi("ATP500 #5", "Kinoshita Group Japan Open", "Tokyo", 32, "Hard", 39),
        Tournoi("ATP500 #5", "China Open", "Beijing", 32, "Hard", 39),
    ],
    40: [Tournoi("ATP1000 #7", "Rolex Shanghai Masters", "Shanghai", 96, "Hard", 40)],
    42: [
        Tournoi("ATP250 #5", "European Open", "Antwerp", 28, "Indoor Hard", 42),
        Tournoi("ATP250 #5", "Almaty Open", "Almaty", 28, "Indoor Hard", 42),
        Tournoi("ATP250 #5", "BNP Paribas Nordic Open", "Stockholm", 28, "Indoor Hard", 42),
    ],
    43: [
        Tournoi("ATP500 #5", "Swiss Indoors Basel", "Basel", 32, "Indoor Hard", 43),
        Tournoi("ATP500 #5", "Erste Bank Open", "Vienna", 32, "Indoor Hard", 43),
    ],
    44: [Tournoi("ATP1000 #6", "Rolex Paris Masters", "Paris", 56, "Indoor Hard", 44)],
    45: [
        Tournoi("ATP250 #5", "Moselle Open", "Metz", 28, "Indoor Hard", 45),
        Tournoi("ATP250 #5", "Watergen Gijon Open", "Gijon", 28, "Indoor Hard", 45),
    ],
    46: [Tournoi("ATP Finals", "Nitto ATP Finals", "Turin", 8, "Indoor Hard", 46)],
}

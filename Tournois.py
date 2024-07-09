""" Ce fichier contient la liste de tous les tournois que l'on peut retrouver sur une année"""

import math
import random


def determiner_placement(tours_joues, total_tours):
    if tours_joues == total_tours:
        return "Vainqueur"
    elif tours_joues == total_tours - 1:
        return "Finaliste"
    elif tours_joues == total_tours - 2:
        return "Demi-finaliste"
    elif tours_joues == total_tours - 3:
        return "Quart de finaliste"
    else:
        return f"Éliminé au tour {tours_joues}"


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
    joueur_tries = sorted(
        joueurs_disponibles, key=lambda j: classement.obtenir_rang(j, type)
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
    
    def __init__(self, categorie, nom, emplacement, nb_joueurs, surface):
        self.categorie = categorie
        self.nom = nom
        self.emplacement = emplacement
        self.nb_joueurs = nb_joueurs
        self.surface = surface
        #self.vainqueurs = {}

    # We need to update the Calendar function to be able to use this function
    def jouer(self, joueur, participants, classement, type="atp"):
        # Si le joueur n'est pas dans la liste des participants, ont l'ajoute et on retire un participants
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
                
        self.simuler_tournoi(participants, classement, type)  # On peut simuler le tournoi

    def simuler_tournoi(self, participants, classement, type="elo"):
        if self.categorie == "ATP Finals":
            return self.simuler_tournoi_finals(participants, classement)
        
        nb_tours = math.ceil(math.log2(self.nb_joueurs))
        nb_tetes_de_serie = 2 ** (nb_tours - 2)

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

        print(f"\nVainqueur du tournoi {self.nom}:\n{vainqueur.prenom} {vainqueur.nom}")

        for joueur, dernier_tour in derniers_tours.items():
            self.attribuer_points_atp(joueur, dernier_tour)
        
        # Note the return will be useful when we'll save the info in a database
        # Return vainqueur, dernier_tour
    
    def simuler_tournoi_finals(self, participants, classement):
        # Todo: add a logic for the players that are injured (add the two substitutes)
        if len(participants) != 8:
            raise ValueError("L'ATP Finals nécessite exactement 8 participants")
        
        # Trier les joueurs par classement
        # Todo: remplacer atp par atp race quand je l'aurai implémenter
        joueurs_tries = sorted(participants, key=lambda j: classement.obtenir_rang(j, "atp"))
        
        # répartir les joueurs en deux poules
        # Todo: rajouter de l'aléatoire dans la création des poules
        poule_a = [joueurs_tries[0], joueurs_tries[3], joueurs_tries[4], joueurs_tries[7]]
        poule_b = [joueurs_tries[1], joueurs_tries[2], joueurs_tries[5], joueurs_tries[6]]
        
        # Simuler les matchs de poules
        resultats_poule_a = self.simuler_matchs_poule(poule_a)
        resultats_poule_b = self.simuler_matchs_poule(poule_b)

        for poule in [resultats_poule_a, resultats_poule_b]:
            for joueur, resultat in poule.items():
                joueur.atp_points += resultat["victoires"] * 200  # +200 pts par victoire en poule

        # Sélectionner les deux meilleurs de chaque poule
        qualifies_a = self.selectionner_qualifies(resultats_poule_a)
        qualifies_b = self.selectionner_qualifies(resultats_poule_b)

        # Demi finales
        demi_finale_1 = self.simuler_match(qualifies_a[0], qualifies_b[1])[0]
        demi_finale_2 = self.simuler_match(qualifies_b[0], qualifies_a[1])[0]

        demi_finale_1.atp_points += 400  # +400pts si victoire en demi-finale
        demi_finale_2.atp_points += 400

        # Finale
        vainqueur = self.simuler_match(demi_finale_1, demi_finale_2)[0]
        vainqueur.atp_points += 500  # +500pts si victoire en finale
        print(f"\nVainqueur du tournoi {self.nom}:\n{vainqueur.prenom} {vainqueur.nom}")
        
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
        Tournoi("ATP250 #5", "Brisbane International", "Brisbane", 32, "Hard"),
        Tournoi(
            "ATP250 #5", "Bank Of China Honk Kong Tennis Open", "Hong Kong", 28, "Hard"
        ),
    ],
    2: [
        Tournoi("ATP250 #5", "Adelaide International", "Adelaide", 28, "Hard"),
        Tournoi("ATP250 #5", "ASB Classic", "Auckland", 28, "Hard"),
    ],
    3: [Tournoi("GrandSlam", "Australian Open", "Melbourne", 128, "Hard")],
    5: [Tournoi("ATP250 #5", "Open Sud de France", "Montpellier", 28, "Hard")],
    6: [
        Tournoi("ATP250 #5", "Cordoba Open", "Cordoba", 28, "Clay"),
        Tournoi("ATP250 #5", "Dallas Open", "Dallas", 28, "Indoor Hard"),
        Tournoi("ATP250 #5", "Open 13 Provence", "Marseille", 28, "Indoor Hard"),
    ],
    7: [
        Tournoi("ATP500 #5", "ABN Amro Open", "Rotterdam", 32, "Indoor Hard"),
        Tournoi("ATP250 #5", "IEB+ Argentina Open", "Buenos Aires", 28, "Clay"),
        Tournoi("ATP250 #5", "Delray Beach Open", "Delray Beach", 28, "Hard"),
    ],
    8: [
        Tournoi("ATP500 #5", "Rio Open", "Rio de Janeiro", 32, "Clay"),
        Tournoi("ATP250 #5", "Qater Exxonmobil Open", "Doha", 28, "Hard"),
        Tournoi("ATP250 #5", "Mifel Tennis Open", "Los Cabos", 28, "Hard"),
    ],
    9: [
        Tournoi("ATP500 #5", "Abierto Mexicano", "Acapulco", 32, "Hard"),
        Tournoi(
            "ATP500 #5", "Dubai Duty Free Tennis Championships", "Dubai", 32, "Hard"
        ),
        Tournoi("ATP250 #5", "Movistar Chile Open", "Santiago", 28, "Clay"),
    ],
    10: [Tournoi("ATP1000 #7", "BNP Paribas Open", "Indian Wells", 96, "Hard")],
    12: [Tournoi("ATP1000 #7", "Miami Open", "Miami", 96, "Hard")],
    14: [
        Tournoi("ATP250 #5", "Millennium Estoril Open", "Estoril", 28, "Clay"),
        Tournoi("ATP250 #5", "Grand Prix Hassan II", "Marrakech", 28, "Clay"),
        Tournoi(
            "ATP250 #5", "Fayez Sarofim Clay Court Championships", "Houston", 28, "Clay"
        ),
    ],
    15: [Tournoi("ATP1000 #6", "Rolex Monte Carlo Masters", "Monte-Carlo", 56, "Clay")],
    16: [
        Tournoi("ATP500 #6", "Barcelona Open Banc Sabadell", "Barcelona", 48, "Clay"),
        Tournoi("ATP250 #5", "BMW Open", "Munich", 28, "Clay"),
        Tournoi("ATP250 #5", "Tiriac Open", "Bucharest", 28, "Clay"),
    ],
    17: [Tournoi("ATP1000 #7", "Mutua Madrid Open", "Madrid", 96, "Clay")],
    19: [Tournoi("ATP1000 #7", "Internazionali BNL d'Italia", "Rome", 96, "Clay")],
    21: [
        Tournoi("ATP250 #5", "Gonet Geneva Open", "Geneva", 28, "Clay"),
        Tournoi("ATP250 #5", "Open Parc", "Lyon", 28, "Clay"),
    ],
    22: [Tournoi("GrandSlam", "Roland-Garros", "Paris", 128, "Clay")],
    24: [
        Tournoi("ATP250 #5", "Libema Open", "'s-Hertogenbosch", 28, "Grass"),
        Tournoi("ATP250 #5", "Boss Open", "Stuttgart", 28, "Grass"),
    ],
    25: [
        Tournoi("ATP500 #5", "Terra Wortmann Open", "Halle", 32, "Grass"),
        Tournoi("ATP500 #5", "Cinch Championships", "London", 32, "Grass"),
    ],
    26: [
        Tournoi("ATP250 #5", "Mallorca Championships", "Mallorca", 28, "Grass"),
        Tournoi("ATP250 #5", "Rothesay International", "Eastbourne", 28, "Grass"),
    ],
    27: [Tournoi("GrandSlam", "Wimbledon", "London", 128, "Grass")],
    29: [
        Tournoi("ATP500 #5", "Hamburg Open", "Hamburg", 32, "Clay"),
        Tournoi("ATP250 #5", "Nordea Open", "Bastad", 28, "Clay"),
        Tournoi("ATP250 #5", "EFG Swiss Open Gstaad", "Gstaad", 28, "Clay"),
        Tournoi("ATP250 #5", "Infosys Hall Of Fame Open", "Newport", 28, "Grass"),
    ],
    30: [
        Tournoi("ATP250 #5", "Plava Laguna Croatia Open Umag", "Umag", 28, "Clay"),
        Tournoi("ATP250 #5", "Generali Open", "Kitzbuhel", 28, "Clay"),
        Tournoi("ATP250 #5", "Atlanta Open", "Atlanta", 28, "Hard"),
    ],
    31: [Tournoi("ATP500 #6", "Mubadala Citi DC Open", "Washington DC", 48, "Hard")],
    32: [Tournoi("ATP1000 #6", "National Bank Open", "Montreal", 56, "Hard")],
    33: [Tournoi("ATP1000 #6", "Cincinnati Open", "Cincinnati", 56, "Hard")],
    34: [Tournoi("ATP250 #6", "Winston Salem Open", "Winston Salem", 48, "Hard")],
    35: [Tournoi("GrandSlam", "US Open", "New York", 128, "Hard")],
    38: [
        Tournoi("ATP250 #5", "Chengdu Open", "Chengdu", 28, "Hard"),
        Tournoi("ATP250 #5", "Hangzhou Open", "Hangzhou", 28, "Hard"),
    ],
    39: [
        Tournoi("ATP500 #5", "Kinoshita Group Japan Open", "Tokyo", 32, "Hard"),
        Tournoi("ATP500 #5", "China Open", "Beijing", 32, "Hard"),
    ],
    40: [Tournoi("ATP1000 #7", "Rolex Shanghai Masters", "Shanghai", 96, "Hard")],
    42: [
        Tournoi("ATP250 #5", "European Open", "Antwerp", 28, "Indoor Hard"),
        Tournoi("ATP250 #5", "Almaty Open", "Almaty", 28, "Indoor Hard"),
        Tournoi("ATP250 #5", "BNP Paribas Nordic Open", "Stockholm", 28, "Indoor Hard"),
    ],
    43: [
        Tournoi("ATP500 #5", "Swiss Indoors Basel", "Basel", 32, "Indoor Hard"),
        Tournoi("ATP500 #5", "Erste Bank Open", "Vienna", 32, "Indoor Hard"),
    ],
    44: [Tournoi("ATP1000 #6", "Rolex Paris Masters", "Paris", 56, "Indoor Hard")],
    45: [
        Tournoi("ATP250 #5", "Moselle Open", "Metz", 28, "Indoor Hard"),
        Tournoi("ATP250 #5", "Watergen Gijon Open", "Gijon", 28, "Indoor Hard"),
    ],
    46: [Tournoi("ATP Finals", "Nitto ATP Finals", "Turin", 8, "Indoor Hard")],
}

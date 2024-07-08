import random

from Tournois import tournoi, selectionner_joueurs_pour_tournoi


class Calendar:
    SEMAINES_PAR_AN = 52
    ACTIVITES = ["Entrainement", "Tournoi", "Repos"]

    def __init__(self, year):
        self.current_year = year
        self.current_week = 1
        self.tournois = tournoi

    def avancer_semaine(self):
        self.current_week += 1
        if self.current_week > self.SEMAINES_PAR_AN:
            self.current_year += 1
            self.current_week = 1

    def obtenir_tournois_semaine(self):
        return self.tournois.get(self.current_week, [])

    def choisir_activite(self, joueur, joueurs, classement):
        print(f"\nSemaine : {self.current_week} de l'année {self.current_year}")
        tournois_disponible = self.obtenir_tournois_semaine()

        # Garde-fou pour empêcher de sélectionner Tournoi s'il n'y en a pas
        if tournois_disponible:
            print(
                f"Tournois disponible : {[tournoi.nom for tournoi in tournois_disponible]}\n"
            )
            activites_possibles = self.ACTIVITES
        else:
            print("Tournois disponible : Pas de Tournois\n")
            activites_possibles = [act for act in self.ACTIVITES if act != "Tournoi"]

        for i, activite in enumerate(activites_possibles, 1):
            print(f"{i}. {activite}")

        while True:
            choix = input(
                f"\nChoisissez votre activité cette semaine (1-{len(activites_possibles)}) ou q pour quitter: "
            )
            if choix.lower() == "q":
                break
            if choix.isdigit() and 1 <= int(choix) <= len(activites_possibles):
                activite_choisie = activites_possibles[int(choix) - 1]
                self.executer_activite(joueur, activite_choisie, joueurs, classement)
                break
            else:
                print("\nChoix invalide, veuillez réessayer")

    def executer_activite(self, joueur, activite, joueurs, classement):
        if activite == "Entrainement":
            self.entrainement(joueur)
            self.simuler_tournois_semaine(joueurs, classement)
        elif activite == "Tournoi":
            self.participer_tournoi(joueur, joueurs, classement)
        else:
            self.repos(joueur)
            self.simuler_tournois_semaine(joueurs, classement)

        self.avancer_semaine()

    @staticmethod
    def entrainement(joueur):
        exp_gagnee = random.randint(50, 100)
        accord = "e" if joueur.sexe.lower() == 'f' else ""
        print(f"\n{joueur.prenom} s'est entraîné{accord} cette semaine.")
        joueur.gagner_experience(exp_gagnee)

    def choisir_tournoi(self):
        tournois = self.obtenir_tournois_semaine()
        print("\nTournoi disponible cette semaine:")
        for i, tournoi in enumerate(tournois, 1):
            print(f"{i}. {tournoi.nom}")

        while True:
            choix = input(
                f"\nChoisissez votre tournoi cette semaine (1-{len(tournois)}):"
            )
            if choix.isdigit() and 1 <= int(choix) <= len(tournois):
                tournoi_choisi = tournois[int(choix) - 1]
                return tournoi_choisi
            else:
                print("\nChoix invalide, veuillez réessayer")

    def participer_tournoi(self, joueur, joueurs, classement):
        tournois_semaine = self.obtenir_tournois_semaine()
        
        # ne laisse le choix de la sélection du tournoi que s'il y a plusieurs tournois
        if len(self.obtenir_tournois_semaine()) != 1:
            tournoi_choisi = self.choisir_tournoi()
        else:
            tournoi_choisi = tournois_semaine[0]
        accord = "e" if joueur.sexe.lower() == 'f' else ""
        print(f"\n{joueur.prenom} a participé{accord} au tournoi : {tournoi_choisi.nom}.")
        
        joueurs_disponible = set(joueurs.values())
        
        tournois_tries = sorted(
            tournois_semaine, key=lambda t: self.importance_tournoi(t), reverse=True
        )
        for tournoi in tournois_tries:
            participants = selectionner_joueurs_pour_tournoi(
                tournoi, joueurs_disponible, classement
            )
            
            if tournoi == tournoi_choisi:
                tournoi.jouer(joueur, participants, classement)
            else:
                tournoi.simuler_tournoi(participants, classement, type="atp")
            
            joueurs_disponible -= set(participants)
            
        exp_gagnee = random.randint(150, 300)
        joueur.gagner_experience(exp_gagnee)
    
        classement.update_classement("atp")
        classement.update_classement("elo")
        
        if tournoi_choisi.categorie in ["GrandSlam", "ATP1000 #7"]:
            self.avancer_semaine()
        
    def simuler_tournois_semaine(self, joueurs, classement):
        tournois_semaine = self.obtenir_tournois_semaine()
        joueurs_disponible = set(
            joueurs.values()
        )  # L'idée est de rentrer directement le pool de Joueur ds la fct

        # Liste des tournois triés par ordre d'importance
        tournoi_tries = sorted(
            tournois_semaine, key=lambda t: self.importance_tournoi(t), reverse=True
        )

        for tournoi in tournoi_tries:
            participants = selectionner_joueurs_pour_tournoi(
                tournoi, joueurs_disponible, classement
            )
            tournoi.simuler_tournoi(participants, classement)

            joueurs_disponible -= set(participants)

        classement.update_classement("atp")
        classement.update_classement("elo")

    @staticmethod
    def importance_tournoi(tournoi):
        importance = {
            "GrandSlam": 5,
            "ATP1000 #7": 4,
            "ATP1000 #6": 4,
            "ATP500 #6": 3,
            "ATP500 #5": 3,
            "ATP250 #6": 2,
            "ATP250 #5": 2,
        }
        return importance.get(tournoi.categorie, 1)

    @staticmethod
    def repos(joueur):
        recuperation = random.randint(1, 3)
        accord = "e" if joueur.sexe.lower() == 'f' else ""
        print(f"\n{joueur.prenom} s'est reposé{accord} cette semaine.")


calendar = Calendar(2024)
# from Personnage import Personnage
#
# personnage = Personnage("Theo", "Poussard", "France")

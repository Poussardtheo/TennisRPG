import random

from TennisRPG.Tournois import tournoi, selectionner_joueurs_pour_tournoi, est_eligible_pour_tournoi


class Calendar:
    SEMAINES_PAR_AN = 52
    ACTIVITES = ["Entrainement", "Tournoi", "Repos"]

    def __init__(self, year):
        self.current_year = year
        self.current_week = 1
        self.tournois = tournoi
        self.current_atp_points = None
        
    def avancer_semaine(self, classement, joueurs):
        if self.current_week == self.SEMAINES_PAR_AN:
            self.current_year += 1
            self.current_week = 0
            classement.reinitialiser_atp_race()
        self.current_week += 1
        for joueur_str, joueur_values in joueurs.items():
            joueur_values.atp_points -= self.current_atp_points.loc[joueur_str, self.current_week]

    def obtenir_tournois_semaine(self):
        return self.tournois.get(self.current_week, [])

    def choisir_activite(self, joueur, joueurs, classement):
        print(f"\nSemaine : {self.current_week} de l'année {self.current_year}")
        tournois_semaines = self.obtenir_tournois_semaine()
        tournois_elligible = [t for t in tournois_semaines if est_eligible_pour_tournoi(joueur, t, classement)]
        
        activites_possibles = [act for act in self.ACTIVITES if act != "Tournoi"]
        # Garde-fou pour empêcher de sélectionner Tournoi s'il n'y en a pas
        if tournois_elligible and tournois_semaines:
            print(f"Tournois cette semaine : {[tournoi.nom for tournoi in tournois_semaines]}\n")
            print(f"Tournois accessible : {[tournoi.nom for tournoi in tournois_elligible]}\n")
            activites_possibles = self.ACTIVITES
        elif tournois_semaines:
            print(f"Tournois cette semaine : {[tournoi.nom for tournoi in tournois_semaines]}\n")
            print(f"Aucun Tournoi accessible cette semaine\n")
        else:
            print("Pas de Tournois cette semaine\n")
        
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

        self.avancer_semaine(classement, joueurs)

    @staticmethod
    def entrainement(joueur):
        exp_gagnee = random.randint(3, 7)
        accord = "e" if joueur.sexe.lower() == 'f' else ""
        print(f"\n{joueur.prenom} s'est entraîné{accord} cette semaine.")
        joueur.gagner_experience(exp_gagnee)

    @staticmethod
    def choisir_tournoi(tournois_eligibles):
        print("\nTournoi disponible cette semaine:")
        for i, tournoi in enumerate(tournois_eligibles, 1):
            print(f"{i}. {tournoi.nom}")

        while True:
            choix = input(
                f"\nChoisissez votre tournoi cette semaine (1-{len(tournois_eligibles)}):"
            )
            if choix.isdigit() and 1 <= int(choix) <= len(tournois_eligibles):
                tournoi_choisi = tournois_eligibles[int(choix) - 1]
                return tournoi_choisi
            else:
                print("\nChoix invalide, veuillez réessayer")

    def participer_tournoi(self, joueur, joueurs, classement):
        tournois_semaine = self.obtenir_tournois_semaine()
        tournois_eligibles = [t for t in tournois_semaine if est_eligible_pour_tournoi(joueur, t, classement)]
        
        # ne laisse le choix de la sélection du tournoi que s'il y a plusieurs tournois
        if len(self.obtenir_tournois_semaine()) != 1:
            tournoi_choisi = self.choisir_tournoi(tournois_eligibles)
        else:
            tournoi_choisi = tournois_eligibles[0]
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
                if joueur in participants:
                    joueurs_restant = joueurs_disponible - set(participants)
                    participants.remove(joueur)
                    remplacant = self.trouver_remplacant(tournoi, joueurs_restant, classement)
                    if remplacant:
                        participants.append(remplacant)
                        joueurs_disponible.remove(remplacant)
                resultat = tournoi.simuler_tournoi(participants, classement, type="atp")
                
                for joueur, points in resultat.items():
                    self.current_atp_points.loc[f"{joueur.prenom} {joueur.nom}", self.current_week] = points
                    
            joueurs_disponible -= set(participants)
    
        classement.update_classement("atp")
        classement.update_classement("atp_race")
        classement.update_classement("elo")
        
        if tournoi_choisi.categorie in ["GrandSlam", "ATP1000 #7"]:
            self.avancer_semaine(classement, joueurs)
        
    def simuler_tournois_semaine(self, joueurs, classement, preliminaire=False):
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
            resultat = tournoi.simuler_tournoi(participants, classement, preliminaire=preliminaire)
            for joueur, points in resultat.items():
                self.current_atp_points.loc[f"{joueur.prenom} {joueur.nom}", self.current_week] = points

            joueurs_disponible -= set(participants)

        classement.update_classement("atp")
        classement.update_classement("atp_race")
        classement.update_classement("elo")

    @staticmethod
    def importance_tournoi(tournoi):
        importance = {
            "GrandSlam": 5,
            "ATP Finals": 5,
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
    
    def trouver_remplacant(self, tournoi, joueurs_disponibles, classement):
        joueurs_eligibles = [j for j in joueurs_disponibles if est_eligible_pour_tournoi(j, tournoi, classement)]
        if joueurs_eligibles:
            return min(joueurs_eligibles, key=lambda j: classement.obtenir_rang(j, "atp"))
        return None



calendar = Calendar(2024)
# from Personnage import Personnage
#
# personnage = Personnage("Theo", "Poussard", "France")

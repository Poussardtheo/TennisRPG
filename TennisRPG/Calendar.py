import random

import pandas as pd
from TennisRPG.Tournois import *


class Calendar:
    SEMAINES_PAR_AN = 52
    ACTIVITES = ["Entrainement", "Tournoi", "Repos"]

    def __init__(self, year):
        self.current_year = year
        self.current_week = 1
        self.tournois = tournois
        self.current_atp_points: None | pd.DataFrame = None

    def avancer_semaine(self, classement, joueurs):
        # Lorsque l'on entame une nouvelle année
        if self.current_week == self.SEMAINES_PAR_AN:
            self.current_year += 1      # Update l'année
            self.current_week = 0       # Reinitialize the week and the atp_race
            classement.reinitialiser_atp_race()
            # Update sur l'age et le déclin du joueur
            for joueur in joueurs.values():
                joueur.age += 1
                joueur.update_statistiques_declin()
                
            # Rotation on the age system (update the year, retirement, and generate new players)
            # Todo: Don't forget to add the newest players to the current_atp_points dataframe
            
        self.current_week += 1
        classement.update_classement("atp")
        classement.update_classement("atp_race")
        classement.update_classement("elo")
        
        for joueur_str, joueur in joueurs.items():
            joueur.se_reposer()
            joueur.atp_points -= self.current_atp_points.loc[joueur_str, self.current_week]  # Todo : On retire plus de points que ce qui est attribué.
            self.current_atp_points.loc[joueur_str, self.current_week] = 0
            assert joueur.atp_points == sum(self.current_atp_points.loc[joueur_str]), f"semaine {self.current_week} : {joueur_str}: {joueur.atp_points}, current_atp_points:  {sum(self.current_atp_points.loc[joueur_str])}"
        
            # réinitialiser l'aggravation à la fin de la semaine
            if joueur.blessure:
                joueur.blessure.blessure_agravee_cette_semaine = False

    def obtenir_tournois_semaine(self):
        return self.tournois.get(self.current_week, [])
                    
    def choisir_activite(self, joueur, joueurs, classement):
        print(f"\nSemaine : {self.current_week} de l'année {self.current_year}")

        if not joueur.peut_jouer():
            print(f"{joueur.prenom} {joueur.nom} ne peut pas jouer cette semaine et doit se reposer.")
            self.repos(joueur)
            self.simuler_tournois_semaine(joueur, joueurs, classement)
            self.avancer_semaine(classement, joueurs)
            return

        tournois_semaines = self.obtenir_tournois_semaine()
        tournois_elligible = [t for t in tournois_semaines if est_eligible_pour_tournoi(joueur, t, classement)]
        
        activites_possibles = [act for act in self.ACTIVITES if act != "Tournoi"]
        # Garde-fou pour empêcher de sélectionner Tournoi s'il n'y en a pas
        if tournois_elligible and tournois_semaines:
            # print(f"Tournois cette semaine : {[tournoi.nom for tournoi in tournois_semaines]}\n")
            print(f"\nTournois accessible cette semaine :")
            for t in tournois_elligible:
                print(f"  - {t.nom} ({t.__class__.__name__})")
            print("")
            activites_possibles = self.ACTIVITES
        elif tournois_semaines:
            print(f"\nTournois cette semaine :")
            for t in tournois_semaines:
                print(f"  - {t.nom} ({t.__class__.__name__})")
            print(f"\nAucun Tournoi accessible cette semaine\n")
        else:
            print("Pas de Tournois cette semaine\n")

        for i, activite in enumerate(activites_possibles, 1):
            print(f"{i}. {activite}")

        while True:
            choix = input(
                f"\nChoisissez votre activité cette semaine (1-{len(activites_possibles)}) ou q pour revenir au menu:\n"
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
            self.simuler_tournois_semaine(joueur, joueurs, classement)
        elif activite == "Tournoi":
            self.participer_tournoi(joueur, joueurs, classement)
        else:
            self.repos(joueur)
            self.simuler_tournois_semaine(joueur, joueurs, classement)

        self.avancer_semaine(classement, joueurs)

    @staticmethod
    def entrainement(joueur):
        exp_gagnee = random.randint(10, 15)
        joueur.gagner_experience(exp_gagnee)
        joueur.gerer_fatigue("Entrainement")
        
        if joueur.principal : 
            accord = "e" if joueur.sexe.lower() == 'f' else ""
            print(f"\n{joueur.prenom} s'est entraîné{accord} cette semaine.")
            
    @staticmethod
    def choisir_tournoi(tournois_eligibles):
        print("\nTournoi disponible cette semaine:\n")
        for i, tournoi in enumerate(tournois_eligibles, 1):
            print(f"{i}. {tournoi.nom} ({tournoi.__class__.__name__})")

        while True:
            choix = input(
                f"\nChoisissez votre tournoi cette semaine (1-{len(tournois_eligibles)}) "
                f"ou 'q' pour revenir au choix d'activité:"
            )
            if choix.lower() == "q":
                break
            elif choix.isdigit() and 1 <= int(choix) <= len(tournois_eligibles):
                tournoi_choisi = tournois_eligibles[int(choix) - 1]
                return tournoi_choisi
            else:
                print("\nChoix invalide, veuillez réessayer")
    
    @staticmethod
    def selectionner_joueurs_disponibles(joueur, joueurs):
        """Sélectionne tous les joueurs disponibles pour jouer le tournoi sans prendre en compte le personnage
        principal"""
        joueurs_disponibles = set(j for j in joueurs.values() if j.peut_jouer())
        if joueur in joueurs_disponibles:
            joueurs_disponibles.remove(joueur)
        return joueurs_disponibles
    
    def participer_tournoi(self, joueur, joueurs, classement):
        tournois_semaine = self.obtenir_tournois_semaine()
        tournois_eligibles = [t for t in tournois_semaine if est_eligible_pour_tournoi(joueur, t, classement)]
        
        # ne laisse le choix de la sélection du tournoi que s'il y a plusieurs tournois
        if len(tournois_eligibles) != 1:
            tournoi_choisi = self.choisir_tournoi(tournois_eligibles)
        else:
            tournoi_choisi = tournois_eligibles[0]
        accord = "e" if joueur.sexe.lower() == 'f' else ""
        print(f"\n{joueur.prenom} a participé{accord} au tournoi : {tournoi_choisi.nom}.")
        
        joueurs_disponibles = self.selectionner_joueurs_disponibles(joueur, joueurs)
        tournois_tries = sorted(tournois_semaine, key=lambda t: t.importance_tournoi)
        
        for tournoi in tournois_tries:
            participants = selectionner_joueurs_pour_tournoi(
                tournoi, joueurs_disponibles, classement
            )
            if tournoi == tournoi_choisi:
                resultats = tournoi.jouer(joueur, participants, classement)
            else:
                resultats = tournoi.simuler_tournoi(participants, classement, type="atp")
                
            for player, points in resultats.items():
                self.current_atp_points.loc[f"{player.prenom} {player.nom}", self.current_week] = points
                    
            joueurs_disponibles -= set(participants)
            
        if isinstance(tournoi_choisi, GrandSlam) or (isinstance(tournoi_choisi, Masters1000) and tournoi_choisi.nb_tours == 7):
            self.avancer_semaine(classement, joueurs)
        
    def simuler_tournois_semaine(self, joueur, joueurs, classement, preliminaire=False):
        tournois_semaine = self.obtenir_tournois_semaine()
        joueurs_disponibles = self.selectionner_joueurs_disponibles(joueur, joueurs)

        # Liste des tournois triés par ordre d'importance
        tournoi_tries = sorted(tournois_semaine, key=lambda t: t.importance_tournoi)

        for tournoi in tournoi_tries:
            participants = selectionner_joueurs_pour_tournoi(
                tournoi, joueurs_disponibles, classement
            )
            resultat = tournoi.simuler_tournoi(participants, classement, preliminaire=preliminaire)
            for player, points in resultat.items():
                self.current_atp_points.loc[f"{player.prenom} {player.nom}", self.current_week] = points

            joueurs_disponibles -= set(participants)

    @staticmethod
    def repos(joueur):
        joueur.se_reposer()
        if joueur.principal:
            accord = "e" if joueur.sexe.lower() == 'f' else ""
            print(f"\n{joueur.prenom} s'est reposé{accord} cette semaine.")
            print(f"Niveau de fatigue actuel {joueur.fatigue}")

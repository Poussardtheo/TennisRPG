import threading

import pandas as pd
import time

# Local import
from TennisRPG.Calendar import *
from TennisRPG.Personnage import *
from TennisRPG.Classement import Classement


def main():
	annee_debut = 2024
	calendar = Calendar(annee_debut)
	while True:
		sexe = input("Jouer avec un personnage Masculin ('M') ou Féminin ('F') ? ")
		if sexe.lower() not in ["m", "f"]:
			print("Sexe invalide, veuillez choisir Masculin ('M') ou Féminin ('F')")
			continue
		break

	# String for men and women
	joueurs_sexe = "joueur" if sexe.lower() == 'm' else "joueuse"
	tennis_sexe = "tennisman" if sexe.lower() == 'm' else "tenniswoman"

	# Creating the player POOL
	pool_joueurs = {}
	start = time.time()
	pool_thread = threading.Thread(target=generer_pnj_thread, args=(1000, sexe, pool_joueurs))
	pool_thread.start()

	# Create your player
	prenom = input(f"\nEntrez le prénom de votre {joueurs_sexe} : ")
	nom = input(f"\nEntrez le nom de votre {joueurs_sexe} : ")
	pays = input(f"\nEntrez le pays de votre {joueurs_sexe} : ")
	joueur_principal = Personnage(sexe, prenom, nom, pays, principal=True)

	# Wait for player POOL generation to complete
	pool_thread.join()
	print(f"Temps de Création du Pool de PNJ: {time.time() - start}")

	# Initialize ranking with the POOL of players
	classement = Classement(pool_joueurs, preliminaire=True)
	calendar.current_atp_points = pd.DataFrame(0, index=pool_joueurs.keys(), columns=[i for i in range(1, 53)])
	start = time.time()
	for _ in range(1, 53):  # 10 ans de simulation
		calendar.simuler_tournois_semaine(joueur_principal, pool_joueurs, classement, preliminaire=True)
		calendar.avancer_semaine(classement, pool_joueurs)
	print(f"Temps de simulation année préliminaire: {time.time() - start}")

	# End of the preliminary period.
	pool_joueurs[f"{prenom} {nom}"] = joueur_principal
	classement = Classement(pool_joueurs, preliminaire=False)
	classement.reinitialiser_atp_race()
	calendar.current_atp_points.loc[f"{prenom} {nom}"] = 0  # Ensure that the main character is stored in the df
	# Main game
	print(f"\n\nBienvenue dans votre carrière de {tennis_sexe}, {prenom} {nom} !")
	print(f"Votre aventure commence en {calendar.current_year}.\n")

	while True:
		action = input("\nAppuyer sur: "
					   "\nEntrée pour continuer"
					   "\n'q' pour quitter"
					   "\n'c' pour afficher le classement"
					   "\n'a' pour afficher les points à défendre cette semaine"
					   f"\n'i pour voir la carte d'identité de votre {joueurs_sexe}"
					   f"\n'e' pour affecter des points d'attributs à votre {joueurs_sexe}\n")

		if action.lower() == 'q':
			break
		elif action.lower() == 'c':
			print("")
			ranking_type = ["atp", "atp_race"]
			for i, type_tournoi in enumerate(["atp", "atp_race"], 1):
				print(f"{i}. {type_tournoi}")


			while True:
				choix = input("\nQuel classement souhaitez vous voir ?")
				if choix.isdigit() and 1 <= int(choix) <= len(ranking_type):
					type_tournoi = ranking_type[int(choix) - 1]
					break
				else:
					print("\nChoix invalide, veuillez réessayer")
			classement.afficher_classement(type=type_tournoi)
		elif action.lower() == 'i':
			joueur_principal.id_card(classement)
		elif action.lower() == 'a':
			print(calendar.current_atp_points.loc[:, calendar.current_week].sort_values(ascending=False))
		elif action.lower() == 'e':
			joueur_principal.attribuer_ap_points_manuellement()
		elif action == '':  # Si le joueur à appuyer sur entrée
			calendar.choisir_activite(joueur_principal, pool_joueurs, classement)

	print("\nMerci d'avoir joué ! Voici vos statistiques finales : ")
	joueur_principal.id_card(classement)

main()
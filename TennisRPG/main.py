import threading

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
	POOL_JOUEURS = {}
	pool_thread = threading.Thread(target=generer_pnj_thread, args=(130, sexe, POOL_JOUEURS))
	pool_thread.start()
	
	# Create your player
	prenom = input(f"\nEntrez le prénom de votre {joueurs_sexe} : ")
	nom = input(f"\nEntrez le nom de votre {joueurs_sexe} : ")
	pays = input(f"\nEntrez le pays de votre {joueurs_sexe} : ")
	joueur_principal = Personnage(sexe, prenom, nom, pays, principal=True)
	
	# Wait for player POOL generation to complete
	pool_thread.join()
	POOL_JOUEURS[f"{prenom} {nom}"] = joueur_principal

	# Initialize ranking with the player POOL
	classement = Classement(POOL_JOUEURS)

	# Main game
	print(f"\n\nBienvenue dans votre carrière de {tennis_sexe}, {prenom} {nom} !")
	print(f"Votre aventure commence en {annee_debut}.\n")

	while True:

		action = input("\nAppuyer sur: "
						"\nEntrée pour continuer"
						"\n'q' pour quitter"
						"\n'c' pour afficher le classement"
						f"\n'i pour voir la carte d'identité de votre {joueurs_sexe}"
						f"\n'e' pour affecter des points d'attributs à votre {joueurs_sexe}\n")

		if action.lower() == 'q':
			break
		elif action.lower() == 'c':
			print("\n")
			for i, type in enumerate(["atp", "atp_race"], 1):
				print(f"{i}. {type}")
			type = input("\nQuel classement souhaitez vous voir ?")
			classement.afficher_classement(type=type)
		elif action.lower() == 'i':
			joueur_principal.id_card(classement)
		elif action.lower() == 'e':
			joueur_principal.attribuer_ap_points_manuellement()
		elif action == '':  # Si le joueur à appuyer sur entrée
			calendar.choisir_activite(joueur_principal, POOL_JOUEURS, classement)

	print("\nMerci d'avoir joué ! Voici vos statistiques finales : ")
	joueur_principal.id_card(classement)


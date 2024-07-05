from Calendar import *
from Personnage import *
from Tournois import *
from Classement import Classement

POOL_JOUEURS = generer_pnj(130)

annee_debut = 2024
calendar = Calendar(annee_debut)
prenom = input("Entrez le prénom de votre joueur : ")
nom = input("\nEntrez le nom de votre joueur : ")
pays = input("\nEntrez le pays de votre joueur : ")
joueur_principal = Personnage(prenom, nom, pays)

POOL_JOUEURS[f"{prenom} {nom}"] = joueur_principal

# Initialiser le classement en fonction du POOL de Joueurs
classement = Classement(POOL_JOUEURS)

print(f"\n\nBienvenue dans votre carrière de tennisman, {prenom} {nom} !")
print(f"Votre aventure commence en {annee_debut}.\n")

while True:
	
	action = input("\nAppuyer sur: "
					"\nEntrée pour continuer"
					"\n'q' pour quitter :"
					"\n'c' pour afficher le classement"
					"\n'i pour avoir les informations sur notre joueur"
					"\n'e' pour affecter des points AP à votre joueur\n")
	
	if action.lower == 'q':
		break
	elif action.lower() == 'c':
		classement.afficher_classement()
	elif action.lower() == 'i':
		joueur_principal.id_card()
	elif action.lower() == 'e':
		joueur_principal.attribuer_ap_points_manuellement()
	elif action == '':  # Si le joueur à appuyer sur entrée
		calendar.choisir_activite(joueur_principal, POOL_JOUEURS, classement)

print("\nMerci d'avoir joué ! Voici vos statistiques finales : ")
joueur_principal.id_card()


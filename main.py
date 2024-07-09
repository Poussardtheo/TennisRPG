from Calendar import *
from Personnage import *
from Tournois import *
from Classement import Classement

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

# Create your player
prenom = input(f"Entrez le prénom de votre {joueurs_sexe} : ")
nom = input(f"\nEntrez le nom de votre {joueurs_sexe} : ")
pays = input(f"\nEntrez le pays de votre {joueurs_sexe} : ")
joueur_principal = Personnage(sexe, prenom, nom, pays)

# Creating the player POOL
POOL_JOUEURS = generer_pnj(130, sexe)
POOL_JOUEURS[f"{prenom} {nom}"] = joueur_principal

# Initialiser le classement en fonction du POOL de Joueurs
classement = Classement(POOL_JOUEURS)

# Main game
print(f"\n\nBienvenue dans votre carrière de {tennis_sexe}, {prenom} {nom} !")
print(f"Votre aventure commence en {annee_debut}.\n")

while True:
	
	action = input("\nAppuyer sur: "
					"\nEntrée pour continuer"
					"\n'q' pour quitter"
					"\n'c' pour afficher le classement"
					f"\n'i pour avoir les informations sur votre {joueurs_sexe}"
					f"\n'e' pour affecter des points AP à votre {joueurs_sexe}\n")
	
	if action.lower() == 'q':
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


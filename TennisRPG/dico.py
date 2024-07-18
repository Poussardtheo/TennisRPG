"""This file contains all the dictionnaries needed to run the game"""

# Le dico des blessures. Il sera potentiellement réorganisé par gravité pour être plus facilement accessible.
# Il faudra se renseigner sur les blessures proposé et
blessure_tennis = {
	"Entorse de la cheville": {"gravite": 4, "repos": 4},
	"Tendinite du coude": {"gravite": 3, "repos": 10},
	"Déchirure musculaire de la cuisse": {"gravite": 5, "repos": 7},
	"Élongation du mollet": {"gravite": 2, "repos": 2},
	"Rupture du tendon d'Achille": {"gravite": 7, "repos": 22},
	"Lombalgie": {"gravite": 3, "repos": 4},
	"Fracture de fatigue": {"gravite": 6, "repos": 7}, # Préciser un peu de quoi il s'agit
	"Déchirure des ligaments du genoux": {"gravite": 6, "repos": 20},
	"Tendinite de l'épaule": {"gravite": 4, "repos": 5},
	"Ampoule au pieds": {"gravite": 1, "repos": 1},
	"Crampes musculaire": {"gravite": 1, "repos": 1},
	"Syndrome du canal carpien": {"gravite": 2, "repos": 3},
	"Déchirure de la coiffe des rotateurs": {"gravite": 5, "repos": 12},
	"Épicondylite latérale": {"gravite": 3, "repos": 9},
	"Fracture de stress": {"gravite": 5, "repos": 7},
	"Entorse du poignet": {"gravite": 3, "repos": 3},
	"Luxation de l'épaule": {"gravite": 6, "repos": 16},
	"Syndrome de la bandelette ilio-tibiale": {"gravite": 2, "repos": 5},
	"Hernie discale": {"gravite": 7, "repos": 39},
	"Coup de chaleur": {"gravite": 1, "repos": 1}
}
import random


class Blessure:
	"""Cette classe gère tout ce qui est relatif aux blessures des personnages"""
	def __init__(self, nom, gravite, repos):
		self.nom = nom
		self.gravite = gravite
		self.repos = repos
		self.semaines_indisponibles = self.repos
		self.blessure_agravee_cette_semaine = False
		
	# Todo: Revoir la fonction
	def risque_aggravation_blessure(self, activite):
		risque_base = {
			"Tournoi": 30,
			"Entrainement": 20,
			"Exhibition": 15
		}
		
		risque_agravation = risque_base.get(activite, 0) + self.gravite * 10
		if random.randint(1, 100) < risque_agravation:
			self.aggraver_blessure()
		
	def aggraver_blessure(self):
		ancienne_gravite = self.gravite
		self.gravite = min(7, self.gravite + 1)
		augmentation_repos = random.randint(1, 3)
		self.semaines_indisponibles += augmentation_repos
		self.blessure_agravee_cette_semaine = True
		return ancienne_gravite, augmentation_repos
	
	def reduire_indisponibilite(self):
		if self.semaines_indisponibles > 0 and not self.blessure_agravee_cette_semaine:
			self.semaines_indisponibles -= 1
	
	def __str__(self):
		return f"Blessure: {self.nom}, Gravite: {self.gravite}, Repos initial: {self.repos}, Repos restant: {self.semaines_indisponibles}"


dico_blessures = {
	1: [
		{"nom": "Ampoule au pied", "gravite": 1, "repos": 1},
		{"nom": "Crampes musculaires", "gravite": 1, "repos": 1},
		{"nom": "Contracture musculaires", "gravite": 1, "repos": 1},
		{"nom": "Coup de chaleur", "gravite": 1, "repos": 1}
	],
	2: [
		{"nom": "Contracture musculaire", "gravite": 2, "repos": 2},
		{"nom": "Élongation du mollet", "gravite": 2, "repos": 2},
		{"nom": "Syndrome du canal carpien", "gravite": 2, "repos": 3},
		{"nom": "Entorse du poignet", "gravite": 2, "repos": 3},
	],
	3: [
		{"nom": "Lombalgie", "gravite": 3, "repos": 4},
		{"nom": "Syndrome de la bandelette ilio-tibiale", "gravite": 3, "repos": 5},
		{"nom": "Tendinite légère", "gravite": 3, "repos": 5}
	],
	4: [
		{"nom": "Entorse de la cheville", "gravite": 4, "repos": 4},
		{"nom": "Élongation musculaire", "gravite": 4, "repos": 4},
		{"nom": "Tendinite de l'épaule", "gravite": 4, "repos": 5},
		{"nom": "Déchirement partiel du ménisque", "gravite": 4, "repos": 6},
	],
	5: [
		{"nom": "Déchirure musculaire", "gravite": 5, "repos": 7},
		{"nom": "Fracture simple", "gravite": 5, "repos": 7},
		{"nom": "Épicondylite latérale", "gravite": 5, "repos": 9}
	],
	6: [
		{"nom": "Déchirure de la coiffe des rotateurs", "gravite": 6, "repos": 12},
		{"nom": "Fracture osseuse complexe", "gravite": 6, "repos": 13},
		{"nom": "Luxation de l'épaule", "gravite": 6, "repos": 16},
	],
	7: [
		{"nom": "Déchirure ligamentaire", "gravite": 6, "repos": 20},
		{"nom": "Rupture du tendon d'Achille", "gravite": 7, "repos": 22},
		{"nom": "Rupture du ligament croisé antérieur", "gravite": 7, "repos": 36}
	]
}



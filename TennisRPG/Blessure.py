import random


class Blessure:
	"""Cette classe gère tout ce qui est relatif aux blessures des personnages"""
	def __init__(self, nom, gravite, repos):
		self.nom = nom
		self.gravite = gravite
		self.repos = repos
		self.semaines_indisponibles = repos
		self.blessure_agravee_cette_semaine = False
		
	# TODO: Réfléchir aux valeurs et à la logique de risque
	def risque_agravation_blessure(self, activite):
		risque_base = {
			"Tournoi": 30,
			"Entrainement": 20,
			"Exhibition": 15
		}
		
		risque_agravation = risque_base.get(activite, 0) + self.gravite * 5
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


dico_blessures = {
	1: [
		Blessure("Ampoule au pied", 1, 1),
		Blessure("Crampes musculaires", 1, 1),
		Blessure("Coup de chaleur", 1, 1)
	],
	2: [
		Blessure("Élongation du mollet", 2, 2),
		Blessure("Syndrome du canal carpien", 2, 3),
		Blessure("Syndrome de la bandelette ilio-tibiale", 2, 5)
	],
	3: [
		Blessure("Tendinite du coude", 3, 10),
		Blessure("Lombalgie", 3, 4),
		Blessure("Épicondylite latérale", 3, 9),
		Blessure("Entorse du poignet", 3, 3)
	],
	4: [
		Blessure("Entorse de la cheville", 4, 4),
		Blessure("Tendinite de l'épaule", 4, 5)
	],
	5: [
		Blessure("Déchirure musculaire de la cuisse", 5, 7),
		Blessure("Déchirure de la coiffe des rotateurs", 5, 12),
		Blessure("Fracture de stress", 5, 7)
	],
	6: [
		Blessure("Fracture de fatigue", 6, 7),
		Blessure("Déchirure des ligaments du genou", 6, 20),
		Blessure("Luxation de l'épaule", 6, 16)
	],
	7: [
		Blessure("Rupture du tendon d'Achille", 7, 22),
		Blessure("Hernie discale", 7, 39)
	]
}

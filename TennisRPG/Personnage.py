import math
import random

import numpy as np

from faker import Faker
from transliterate import translit
from unidecode import unidecode
from scipy.stats import truncnorm

from TennisRPG.Blessure import dico_blessures, Blessure
from TennisRPG.Tournois import Tournoi

SURFACE_IMPACTS = {
	"Hard": {
		"Service": 1.2,
		"Coup droit": 1.1,
		"Revers": 1.1,
		"Volée": 1.0,
		"Puissance": 1.1,
		"Vitesse": 1.2,
		"Endurance": 1.0,
		"Réflexes": 1.1
	},
	"Clay": {
		"Service": 0.9,
		"Coup droit": 1.2,
		"Revers": 1.2,
		"Volée": 0.9,
		"Puissance": 1.0,
		"Vitesse": 0.9,
		"Endurance": 1.3,
		"Réflexes": 1.1
	},
	"Grass": {
		"Service": 1.3,
		"Coup droit": 1.1,
		"Revers": 1.0,
		"Volée": 1.2,
		"Puissance": 1.2,
		"Vitesse": 1.1,
		"Endurance": 0.9,
		"Réflexes": 1.2
	},
	"Indoor Hard": {
		"Service": 1.2,
		"Coup droit": 1.1,
		"Revers": 1.1,
		"Volée": 1.1,
		"Puissance": 1.2,
		"Vitesse": 1.1,
		"Endurance": 1.0,
		"Réflexes": 1.1
	},
	"Carpet": {
		"Service": 1.3,
		"Coup droit": 1.0,
		"Revers": 1.0,
		"Volée": 1.3,
		"Puissance": 1.1,
		"Vitesse": 1.2,
		"Endurance": 0.9,
		"Réflexes": 1.3
	}
}

ARCHETYPES = {
	"Service-Volley": {
		"primaire": ["Service", "Volée"],
		"secondaire": ["Réflexes", "Vitesse"],
		"tertiaire": ["Coup droit", "Revers", "Puissance", "Endurance"]
	},
	"Attaquant Fond de Court": {
		"primaire": ["Coup droit", "Revers", "Puissance"],
		"secondaire": ["Service", "Vitesse"],
		"tertiaire": ["Volée", "Réflexes", "Endurance"]
	},
	"Défenseur": {
		"primaire": ["Endurance", "Vitesse", "Réflexes"],
		"secondaire": ["Coup droit", "Revers"],
		"tertiaire": ["Service", "Volée", "Puissance"]
	},
	"Polyvalent": {
		"primaire": ["Coup droit", "Revers", "Service"],
		"secondaire": ["Endurance", "Puissance", "Vitesse"],
		"tertiaire": ["Volée", "Réflexes"]
	}
}


def generer_truncnorm(lower_bound, upper_bound):
	std_dev = 10  # écart-type de la distribution
	mean = (upper_bound + lower_bound) / 2  # moyenne de la distribution
	
	a = (lower_bound - mean) / std_dev
	b = (upper_bound - mean) / std_dev
	
	return int(truncnorm.rvs(a, b, loc=mean, scale=std_dev, size=1))


def niveau_proportionnel_age(age, age_min=16, age_max=37, lvl_min=1, lvl_max=30):
	"""Calcule le niveau proportionnel à l'âge avec une légère variation aléatoire et une chance rare pour des talents
	exceptionnels."""
	
	proportionnel = lvl_min + (lvl_max - lvl_min) * (age - age_min) / (age_max - age_min)
	variation = random.normalvariate(0, 1.4)  # Ajouter une petite variation normale
	niveau = proportionnel + variation
	
	# Chance rare pour un jeune joueur d'être une pépite
	if age < 20 and random.random() < 0.003:  # 0.3% de chance
		niveau = random.randint(2, 15)  # Niveau élevé pour une pépite
	
	# Assurer que le niveau est entre lvl_min et lvl_max
	return int(max(lvl_min, min(lvl_max, niveau)))


class Personnage:
	POINTS_BASE = 6
	LVL_MAX = 30
	POIDS_BASE = {
		"Coup droit": 1.5,
		"Revers": 1.5,
		"Service": 1.5,
		"Volée": 1,
		"Puissance": 1.2,
		"Vitesse": 1.2,
		"Endurance": 1.3,
		"Réflexes": 1.2,
	}

	TAILLE_IMPACTS = {
		"Service": 0.3,  # Impact positif important
		"Puissance": 0.2,  # Impact positif modéré
		"Vitesse": -0.1,  # Impact négatif léger
		"Endurance": -0.2,  # Impact négatif modéré
	}

	def __init__(self, sexe, prenom, nom, country, age = None, taille=None, lvl=1, archetype=None, principal=False):
		# Validation
		assert sexe.lower() in ["m", "f"], "le sexe doit être 'm' ou 'f'"
		assert lvl >= 1, "niveau minimum = 1"
		assert isinstance(prenom, str) and isinstance(nom, str) and isinstance(country, str)
		assert taille is None or 145 < taille < 220
		assert isinstance(principal, bool)
		assert archetype is None or archetype in ARCHETYPES.keys()
		assert age is None or isinstance(age, int)
		
		# Height logic
		if sexe.lower() == "m":
			taille = taille if taille else generer_truncnorm(160, 205)
		if sexe.lower() == "f":
			taille = taille if taille else generer_truncnorm(155, 185)
			
		self.sexe = sexe.lower()
		self.nom = nom
		self.prenom = prenom
		self.taille = taille
		self.main_dominante = "Gauche" if random.random() < 0.15 else "Droite"
		self.revers = "Une main" if random.random() < 0.11 else "Deux mains"
		self.country = country
		self.archetype = archetype or random.choice(list(ARCHETYPES.keys()))
		self.principal = principal  # Indique si le joueur est le personnage_principal ou un pnj
		self.age = age
		self.age_declin = generer_truncnorm(30, 37)  # Génération de l'âge de déclin du joueur
		
		# Niveau, XP et attributs
		self.lvl = lvl
		self.xp_points = 0
		self.ap_points = 6 * (lvl - 1)  # Permet pnj avec des stats

		# Classement
		self.atp_points = 0
		self.historique_atp_points = []
		self.atp_race_points = 0

		# Fatigue & Blessure
		self.fatigue = 0
		self.blessure = None

		# Stats et Elo
		self.stats = {attr: 30 for attr in list(self.POIDS_BASE.keys())}
		self.elo = self.calculer_elo(initial=True)
		self.generer_statistique()
		self.historique_elo = [self.elo]
	
	def check_retirement(self):
		if self.age > self.age_declin:
			elo_factor = max(0, 1 - (self.elo + 100) / 2000) # The higher the elo, the less probable the retirement
			retirement_chance = (self.age - self.age_declin) * 0.05 * elo_factor
			return random.random() < retirement_chance
		return False
	
	def calculer_elo(self, surface=None, initial=False):
		if surface:
			poids = {attr: self.POIDS_BASE[attr] * SURFACE_IMPACTS[surface].get(attr, 1.0) for attr in self.POIDS_BASE}
			
			score_pondere = sum(self.stats[attr] * poids[attr] for attr in poids)
			score_moyen = score_pondere / sum(poids.values())
			
			diff_age = self.age - self.age_declin
			age_factor = 1 - diff_age * (0.01 * diff_age / self.age_declin) if self.age > self.age_declin else 1
			elo_modif = (score_moyen * age_factor - 40) * 30

		# Convertir le score en ELO (sert à simuler l'issue d'un match)
		# if score_moyen * age_factor <= 40:
		# 	elo_modif = (score_moyen * age_factor - 40) * 30
		# 	# Convertir le score en ELO (sert à simuler l'issue d'un match)
			elo = 1500 - self.age + elo_modif if initial else self.elo - self.age + elo_modif
		else:
			# If score_moyen * age_factor > 40, we keep the current ELO
			elo = 1500 if initial else self.elo

		return max(0, round(elo))
	
	def calculer_k(self):
		"""Calcul k pour faire évoluer l'elo du joueur"""
		if self.elo < 2400:
			k = 20
		else:
			k = 10
			
		return k
	
	def generer_statistique(self):
		mean_height = 170 if self.sexe == "f" else 182.5
		taille_mod = (self.taille - mean_height) / 20  # -1 à 1 pour lower_height à higher_height
		for attr, impact in self.TAILLE_IMPACTS.items():
			ajustement = round(impact * taille_mod * 10)  # l'ajustement se fait de -3 à 3
			self.stats[attr] = min(70, self.stats[attr] + ajustement)

		if self.lvl > 1:
			self.attribuer_ap_points_automatiquement()

	def attribuer_ap_points_automatiquement(self):
		priorites = ARCHETYPES[self.archetype]
		points_categorie = {"primaire": round(self.ap_points * 0.5),
							"secondaire": round(self.ap_points * 0.3),
							"tertiaire": round(self.ap_points * 0.2)}

		for categorie, points in points_categorie.items():
			attrs = priorites[categorie]

			for _ in range(points):
				attr = random.choice(attrs)
				if self.stats[attr] < 70:
					self.stats[attr] += 1
				else:
					# Si attribut déjà à 70, on choisit un autre attribut de la même catégorie
					autres_attrs = [a for a in attrs if self.stats[a] < 70]
					if autres_attrs:
						self.stats[random.choice(autres_attrs)] += 1
					else:
						# Si tous les attributs de la catégorie sont à 70, on passe à la catégorie suivante
						break

			self.ap_points -= points
		self.elo = self.calculer_elo()
	
	def update_statistiques_declin(self, taux_declin=0.002):
		if self.age > self.age_declin:
			facteur = 1 - taux_declin * (self.age - self.age_declin)**2.25
			for key, stat in self.stats.items():
				self.stats[key] = int(stat * facteur)
		
			# Update the elo once the stats have changed
			self.elo = self.calculer_elo()
				
	def gagner_experience(self, earned_xp):
		facteur_niveau = max(1 - (self.lvl/30) * 0.6, 0.4)
		xp_ajuste = round(earned_xp * facteur_niveau)
		self.xp_points += xp_ajuste
		if self.principal:
			print(f"\n{self.prenom} a gagné {xp_ajuste} points d'expérience.")
		self.level_up()

	def calculer_experience_requise(self):
		return int(200 * self.lvl ** 1.2)

	def level_up(self):
		# Tant que l'on a assez d'xp pour passer au niveau suivant et qu'on n'est pas au niveau max
		while self.xp_points >= self.calculer_experience_requise() and self.lvl < self.LVL_MAX:
			self.xp_points -= self.calculer_experience_requise()
			self.lvl += 1
			self.ap_points += self.POINTS_BASE
			# Si le personnage est une femme, on accorde le message au féminin
			accord = "e" if self.sexe.lower() == 'f' else ""
			if self.principal:
				print(f"{self.prenom} est passé{accord} au niveau {self.lvl}!")
				print(f"{self.prenom} a gagné {self.POINTS_BASE} AP points.")
			else:
				self.attribuer_ap_points_automatiquement()

	def attribuer_ap_points_manuellement(self):
		if self.ap_points == 0:
			print("\n Pas de points AP à attribuer.")
		while self.ap_points > 0:
			print(f"\nAP Points disponible: {self.ap_points}")
			for i, attr in enumerate(list(self.POIDS_BASE.keys()), 1):
				print(f"{i}: {attr}")

			choix = input("Choisissez un attribut à améliorer (1-8) ou q pour quitter")
			if choix.lower() == "q":
				break

			try:
				index = int(choix) - 1
				attr = list(self.POIDS_BASE.keys())[index]

				points = int(
					input(f"\nCombien de points voulez vous attribuer à {attr} ? ")
				)
				if points > self.ap_points:
					print("vous n'avez pas assez de AP points")
					continue
				if self.stats[attr] + points > 100:
					print("L'attribut ne peut pas dépasser 100.")
					continue

				self.stats[attr] += points
				self.ap_points -= points
				print(f"\n{attr} augmenté à {self.stats[attr]}")

			except (ValueError, IndexError):
				print("Choix invalide, Veuillez réessayer.")
		
		# Update the elo of the player
		self.elo = self.calculer_elo()
	
	###############################################################
	#                           SECTION                           #
	#                      FATIGUE & BLESSURES                    #
	###############################################################
	
	def gerer_fatigue(self, activite: Tournoi | str, sets_joues: int = 0):
		fatigue_base = {
			"Entrainement": random.randint(1, 3),
			"Exhibition": random.randint(5, 15),
		}
		
		# fatigue en fonction de la qualité du tournoi et du nombre de sets joués
		tournoi_fatigue_mapping = {
			1: lambda: sets_joues * 1.7,  # Grand Chelem: 1.7 pt de fatigue par sets joués
			2: lambda: sets_joues * 1.4,  # Masters 1000 : 1.4 pt de fatigue par sets joués
			3: lambda: sets_joues * 1.2,  # ATP 500 : 1.2 pt de fatigue par sets joués
			4: lambda: sets_joues,  # ATP 250 : 1 pt de fatigue par sets joués
			5: lambda: sets_joues * 0.9,   # Challenger 175 : 0.9 pt de fatigue par sets joués
			6: lambda: sets_joues * 0.9,   # Challenger 125 : 0.9 pt de fatigue par sets joués
			7: lambda: sets_joues * 0.9,   # Challenger 100 : 0.9 pt de fatigue par sets joués
			8: lambda: sets_joues * 0.9,   # Challenger 75 : 0.9 pt de fatigue par sets joués
			9: lambda: sets_joues * 0.8    # Challenger 50 : 0.8 pt de fatigue par sets joués
		}
	
		if isinstance(activite, Tournoi):
			fatigue_ajoutee = tournoi_fatigue_mapping.get(activite.importance_tournoi, lambda: 0)()
		else:
			fatigue_ajoutee = fatigue_base.get(activite, 0)

		self.fatigue = min(100, self.fatigue + fatigue_ajoutee)

		if self.blessure:
			self.blessure.risque_aggravation_blessure(activite)
		
		self.verifier_blessure()

		if self.fatigue >= 80 and not self.blessure:
			accord = "la joueuse est très fatiguée" if self.sexe.lower() == 'f' else "Le joueur est très fatigué"
			if self.principal:
				print(f"Attention ! {accord} et risque de se blesser. ")

	def verifier_blessure(self, seuil=60):
		k = np.where(self.fatigue < seuil, 0.2, 0.12)
		risque = 100 / (1 + math.exp(-k * (self.fatigue - seuil)))
		if random.randint(1, 100) < risque:
			self.infliger_blessure()

	def infliger_blessure(self):
		gravite = self.gravite_blessure()
		blessures_possibles = dico_blessures[gravite]

		blessure_infos = random.choice(blessures_possibles)
		
		self.blessure = Blessure(blessure_infos["nom"], blessure_infos["gravite"], blessure_infos["repos"])
		
		accord = "e" if self.sexe.lower() == 'f' else ""
		accord2 = "s" if self.blessure.repos != 1 else ""

		if self.principal:
			print(f"{self.nom} s'est blessé{accord} : {self.blessure.nom} (Gravité: {self.blessure.gravite})"
			      f". Indisponible pour {self.blessure.repos} semaine{accord2}.")

	def reduire_temps_indisponibilite(self):
		if self.blessure:
			self.blessure.reduire_indisponibilite()
			
			if self.blessure.semaines_indisponibles == 0 or self.fatigue == 0:
				self.guerir()
				
			if self.principal and self.blessure:
				accord2 = "s" if self.blessure.semaines_indisponibles > 1 else ""
				print(f"{self.prenom} {self.nom} récupère de sa blessure. Encore indisponible {self.blessure.repos} semaine{accord2}")
				print(f"{self.prenom} {self.nom} s'est reposé.")
				print(f"Fatigue : {self.fatigue}, Blessure : {self.blessure}")

	def se_reposer(self):
		repos = random.randint(3, 5)
		self.fatigue = max(0, self.fatigue - repos)

		self.reduire_temps_indisponibilite()
	
	def gravite_blessure(self):
		# Paramètres de la fonction logistique
		k = 0.05  # Contrôle la pente des courbes
		x0 = {1: 15, 2: 25, 3: 40, 4: 75, 5: 100, 6: 125, 7: 150}  # Points centraux pour chaque gravité
		
		# Calcul de la valeur logistique pour chaque gravité
		logistic_values = [1 / (1 + np.exp(-k * (self.fatigue - x0[g]))) for g in range(1, 8)]
		
		# Normalisation pour s'assurer que la somme des probabilités est 1
		total = sum(logistic_values)
		normalized_values = [v / total for v in logistic_values]
		
		gravite = random.choices(range(1, 8), weights=normalized_values)[0]
		return gravite

	def guerir(self):
		self.blessure = None
		if self.principal:
			print(f"{self.prenom} {self.nom} est guéri")
		
	def peut_jouer(self):
		# Le joueur ne peut pas jouer s'il est blessé
		return self.blessure is None or self.blessure.gravite <= 2
	
	def should_participate(self, tournoi, classement):
		classement_limites = {
			1: lambda c: True,                 # Grand Chelem: Pas de limite supérieure
			2: lambda c: True,                 # Masters 1000: Top 1 à 150
			3: lambda c: True,                 # ATP 500: Top 1 à 250
			4: lambda c: True,                 # ATP 250: Top 1 à 300
			5: lambda c: c >= 30,              # Challenger 175: Top 30+
			6: lambda c: c >= 50,              # Challenger 125: Top 50+
			7: lambda c: c >= 60,              # Challenger 100: Top 60+
			8: lambda c: c >= 70,             # Challenger 75: Top 70+
			9: lambda c: c >= 130              # Challenger 50: Top 130+
		}
	
		classement_joueur = classement.obtenir_rang(self, 'atp')
		# Vérification du classement du joueur pour le type de tournoi
		if not classement_limites[tournoi.importance_tournoi](classement_joueur):
			return False
		
		def f(x, seuil):
			k = np.where(x < seuil, 0.3, 0.12)
			return 1 - (1 / (1 + np.exp(-k * (x - seuil))))
		
		participation_chance = f(self.fatigue, seuil=45)
		
		# Ajuste la participation en fonction de l'importance du tournoi et du classement du joueur:
		if tournoi.importance_tournoi <= 2:  # Grand Chelem, ATP Finals et Masters1000
			participation_chance += 0.2
		elif tournoi.importance_tournoi <= 4:  # ATP 500 et 250
			if classement_joueur > 50:  # Les moins bien classé seront plus enclin à participer
				participation_chance += 0.05
		else:  # Tournoi Challengers
			if classement_joueur < 40:
				participation_chance -= 0.4
			elif classement_joueur < 100:
				participation_chance -= 0.2
		
		return random.random() < participation_chance
		
	def id_card(self, classement):
		largeur = 46
		print("┌" + "─" * (largeur - 2) + "┐")
		print("│" + " ID CARD ".center(largeur - 2) + "│")
		print("├" + "─" * (largeur - 2) + "┤")
		print(f"│ Nom     : {self.nom:<32} │")
		print(f"│ Prénom  : {self.prenom:<32} │")
		print(f"│ Taille  : {self.taille} cm{' ' * 26} │")
		print(f"│ Nationalité  : {self.country:<27} │")
		print(f"│ Main    : {self.main_dominante:<32} │")
		print(f"│ Revers  : {self.revers:<32} │")
		print("├" + "─" * (largeur - 2) + "┤")
		print("│" + " SITUATION ".center(largeur - 2) + "│")
		print("├" + "─" * (largeur - 2) + "┤")
		print(f"│ Classement  ATP  : {classement.obtenir_rang(self,'atp'):<23} │")
		print(f"│ Points ATP  : {self.atp_points:<28} │")
		print(f"│ ELO     : {int(self.elo):<32} │")
		print(f"│ Niveau  : {self.lvl:<32} │")
		
		xp_requis = self.calculer_experience_requise()
		xp_actuel = self.xp_points
		max_barre = 20
		barre_xp = "▓" * int(xp_actuel * max_barre / xp_requis)
		espace_xp = "░" * (max_barre - len(barre_xp))
		xp_values = f"{xp_actuel}/{xp_requis}"
		xp_space = len(xp_values)
		left_space = largeur - 11 - max_barre - 2
		middle_space = max(0, left_space - xp_space)
		
		print(f"│ XP      : {barre_xp}{espace_xp}{' ' * (middle_space-1)}{xp_values} │")
		print(f"│ Fatigue : {self.fatigue:<32} │")
		print(f"│ Blessure: {self.blessure if self.blessure else False} │")
		print("├" + "─" * (largeur - 2) + "┤")
		print("│" + " STATISTIQUES ".center(largeur - 2) + "│")
		print("├" + "─" * (largeur - 2) + "┤")

		for attr, valeur in self.stats.items():
			barre = "▓" * int(valeur * max_barre / 100)
			espace = " " * (max_barre - len(barre))
			print(f"│ {attr:<10}: {barre}{espace} {valeur:>9} │")

		print("└" + "─" * (largeur - 2) + "┘")


pays_locales = {
	"France": ["fr_FR"],
	"United States": ["en_US"],
	"Ireland": ["en_IE"],
	"New_Zeland": ["en_NZ"],
	"Spain": ["es_ES"],
	"Mexico": ["es_MX"],
	"Germany": ["de_DE"],
	"Italy": ["it_IT"],
	"Russia": ["ru_RU"],
	"Ukraine": ["uk_UA"],
	"United Kingdom": ["en_GB"],
	"Australia": ["en_AU"],
	"Netherlands": ["nl_NL"],
	"Belgium": ["nl_BE", "fr_BE"],
	"Estonia": ["et_EE"],
	"Brazil": ["pt_BR"],
	"Argentina": ["es_AR"],
	"Canada": ["en_CA", "fr_CA"],
	"Switzerland": ["de_CH", "fr_CH", "it_CH"],
	"Poland": ["pl_PL"],
	"Croatia": ["hr_HR"],
	"Romania": ["ro_RO"],
	"Greece": ["el_GR"],
	"Chile": ["es_CL"],
	"Denmark": ["da_DK"],
	"Sweden": ["sv_SE"],
	"Bulgaria": ["bg_BG"],
	"Hungary": ["hu_HU"],
	"Lituania": ["lt_LT"],
	"Czech Republic": ["cs_CZ"],
	"Austria": ["de_AT"],
	"Portugal": ["pt_PT"],
	"Finland": ["fi_FI"],
	"India": ["en_IN"],
	"Colombia": ["es_CO"],
	"Slovakia": ["sk_SK"],
	"Slovenia": ["sl_SI"],
	"China": ["zh_CN"],
	"Turkey": ["tr_TR"],
	"Japan": ["ja_JP"],
	"Norway": ["no_NO"]
}


def generer_pnj(nombre, sexe, age_min=16, age_max=37):
	personnages_dico = {}
	for _ in range(nombre):
		country = random.choice(list(pays_locales.keys()))

		if len(pays_locales[country]) > 1:
			random_locale = random.choice(pays_locales[country])
		else:
			random_locale = pays_locales[country][0]

		fake = Faker(random_locale)
		
		prenom = fake.first_name_male() if sexe.lower() == 'm' else fake.first_name_female()
		
		nom = fake.last_name()
		age = random.randint(age_min, age_max)  # Plage d'âge entre 16 et 37 ans
		lvl = niveau_proportionnel_age(age)
		# Note : A voir ce que cela donne dans la simulation des années préliminaires
		
		if random_locale in ["ru_RU", "bg_BG", "uk_UA"]:
			prenom = translit(prenom, "ru", reversed=True)
			nom = translit(nom, "ru", reversed=True)
		elif random_locale in ["el_GR", "zh_CN", "ja_JP"]:
			prenom = unidecode(prenom)
			nom = unidecode(nom)

		personnage = Personnage(sexe, prenom, nom, country, age=age, lvl=lvl)
		personnage.generer_statistique()
		personnages_dico[f"{personnage.prenom} {personnage.nom}"] = personnage

	return personnages_dico


def generer_pnj_thread(nb_joueurs, sexe, pool):
	generated_pool = generer_pnj(nb_joueurs, sexe)
	pool.update(generated_pool)

import math
import random

import numpy as np

from faker import Faker
from transliterate import translit
from unidecode import unidecode
from scipy.stats import truncnorm

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


def generer_taille(lower_bound, upper_bound):
	std_dev = 10  # écart-type de la distribution
	mean = (upper_bound + lower_bound) / 2  # moyenne de la distribution

	a = (lower_bound - mean) / std_dev
	b = (upper_bound - mean) / std_dev

	return int(truncnorm.rvs(a, b, loc=mean, scale=std_dev, size=1))


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

	def __init__(self, sexe, prenom, nom, country, taille=None, lvl=1, archetype=None, principal=False):
		# Validation
		assert sexe.lower() in ["m", "f"], "le sexe doit être 'm' ou 'f'"
		assert lvl >= 1, "niveau minimum = 1"
		assert isinstance(prenom, str) and isinstance(nom, str) and isinstance(country, str)
		assert taille is None or 145 < taille < 220
		assert isinstance(principal, bool)
		assert archetype is None or archetype in ARCHETYPES.keys()

		# Height logic
		if sexe.lower() == "m":
			taille = taille if taille else generer_taille(160, 205)
		if sexe.lower() == "f":
			taille = taille if taille else generer_taille(155, 185)

		self.sexe = sexe.lower()
		self.nom = nom
		self.prenom = prenom
		self.taille = taille
		self.main_dominante = "Gauche" if random.random() < 0.15 else "Droite"
		self.revers = "Une main" if random.random() < 0.11 else "Deux mains"
		self.country = country
		self.archetype = archetype or random.choice(list(ARCHETYPES.keys()))
		self.principal = principal  # Indique si le joueur est le personnage_principal ou un pnj

		# Niveau, XP et attributs
		self.lvl = lvl
		self.xp_points = 0
		self.ap_points = 6 * (lvl - 1)  # Permet pnj avec des stats

		# Classement
		self.atp_points = 0
		self.atp_race_points = 0

		# Fatigue
		self.fatigue = 0

		# Stats et Elo
		self.stats = {attr: 30 for attr in list(self.POIDS_BASE.keys())}
		self.elo = self.calculer_elo(initial=True)
		self.generer_statistique()

	# Todo: Stocker directement dans le init les elo par surfaces plutôt que d'avoir à les recalculer à chaque fois
	def calculer_elo(self, surface=None, initial=False):
		if surface:
			poids = {attr: self.POIDS_BASE[attr] * SURFACE_IMPACTS[surface].get(attr, 1.0) for attr in self.POIDS_BASE}
		else:
			poids = self.POIDS_BASE

		score_pondere = sum(self.stats[attr] * poids[attr] for attr in poids)
		score_moyen = score_pondere / sum(poids.values())

		# Convertir le score en ELO (sert à simuler l'issue d'un match)
		elo_initial = 1500 + (score_moyen - 40) * 30 if initial else self.elo + (score_moyen - 40) * 30

		return round(elo_initial)

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

	def gagner_experience(self, earned_xp):
		facteur_niveau = max(1 - (self.lvl / 30) * 0.6, 0.4)
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

	def attribuer_atp_points(self, earned_atp_points):
		self.atp_points += earned_atp_points
		print(f"{self.prenom} {self.nom} a gagné {earned_atp_points} points ATP.")

	###############################################################
	#                           SECTION                           #
	#                      		FATIGUE                  		  #
	###############################################################
	# Todo: Reprendre cette partie là pour simplifier et améliorer le code
	def gerer_fatigue(self, activite: Tournoi | str, sets_joues: int = 0):
		fatigue_activite = {
			"Entrainement": random.randint(3, 7),
			"Exhibition": random.randint(5, 15),
		}

		# todo: Le coeff doit être proportionnel au tournoi
		# plus le tournoi est exigent et plus on accumule de la fatigue.
		coeff = 1

		if isinstance(activite, Tournoi):
			fatigue_ajoute = sets_joues*coeff
		else:
			fatigue_ajoute = fatigue_activite.get(activite, 0)

		self.fatigue = min(100, self.fatigue + fatigue_ajoute)

	def se_reposer(self):
		# Reprendre les valeurs
		repos = random.randint(3, 5)
		self.fatigue = max(0, self.fatigue - repos)

	# Todo: affiner la logique
	def should_participate(self):
		return self.fatigue < 50

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
		print(f"│ Classement  ATP  : {classement.obtenir_rang(self, 'atp'):<23} │")
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

		print(f"│ XP      : {barre_xp}{espace_xp}{' ' * (middle_space - 1)}{xp_values} │")
		print(f"│ Fatigue : {self.fatigue:<32} │")
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


def generer_pnj(nombre, sexe):
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
		lvl = random.randint(1, 25)

		if random_locale in ["ru_RU", "bg_BG", "uk_UA"]:
			prenom = translit(prenom, "ru", reversed=True)
			nom = translit(nom, "ru", reversed=True)
		elif random_locale in ["el_GR", "zh_CN", "ja_JP"]:
			prenom = unidecode(prenom)
			nom = unidecode(nom)

		personnage = Personnage(sexe, prenom, nom, country, lvl=lvl)
		personnage.generer_statistique()
		personnages_dico[f"{personnage.prenom} {personnage.nom}"] = personnage

	return personnages_dico


def generer_pnj_thread(nb_joueurs, sexe, pool):
	generated_pool = generer_pnj(nb_joueurs, sexe)
	pool.update(generated_pool)

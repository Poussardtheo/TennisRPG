"""
Entité Player - Joueur de tennis.
"""
import random

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

from ..utils.constants import (
	ARCHETYPES, PLAYER_CONSTANTS, STATS_WEIGHTS, HEIGHT_IMPACTS
)
from ..utils.helpers import (
	generate_height, calculate_weighted_elo, calculate_experience_required, get_random_hand,
	get_random_backhand, get_gender_agreement, calculate_fatigue_level, get_age_progression_factor,
	calculate_tournament_xp
)

from ..data.surface_data import SURFACE_IMPACTS


class Gender(Enum):
	MALE = "m"
	FEMALE = "f"


@dataclass
class PlayerStats:
	"""Statistiques du joueur"""
	coup_droit: int = PLAYER_CONSTANTS["BASE_STAT_VALUE"]
	revers: int = PLAYER_CONSTANTS["BASE_STAT_VALUE"]
	service: int = PLAYER_CONSTANTS["BASE_STAT_VALUE"]
	vollee: int = PLAYER_CONSTANTS["BASE_STAT_VALUE"]
	puissance: int = PLAYER_CONSTANTS["BASE_STAT_VALUE"]
	vitesse: int = PLAYER_CONSTANTS["BASE_STAT_VALUE"]
	endurance: int = PLAYER_CONSTANTS["BASE_STAT_VALUE"]
	reflexes: int = PLAYER_CONSTANTS["BASE_STAT_VALUE"]

	def to_dict(self) -> Dict[str, int]:
		return {
			"Coup droit": self.coup_droit,
			"Revers": self.revers,
			"Service": self.service,
			"Volée": self.vollee,
			"Puissance": self.puissance,
			"Vitesse": self.vitesse,
			"Endurance": self.endurance,
			"Réflexes": self.reflexes
		}

	def update_from_dict(self, stats_dict: Dict[str, int]):
		"""Met à jour les stats à partir d'un dictionnaire"""
		mapping = {
			"Coup droit": "coup_droit",
			"Revers": "revers",
			"Service": "service",
			"Volée": "vollee",
			"Puissance": "puissance",
			"Vitesse": "vitesse",
			"Endurance": "endurance",
			"Réflexes": "reflexes"
		}
		for french_name, english_attr in mapping.items():
			if french_name in stats_dict:
				setattr(self, english_attr, stats_dict[french_name])


@dataclass
class PlayerCareer:
	"""Données de carrière d'un joueur"""
	level: int = 1
	xp_points: int = 0
	ap_points: int = 0
	atp_points: int = 0
	atp_race_points: int = 0
	age: int = 20  # Âge du joueur (nouveau champ)
	# ELO stocké pour chaque surface pour éviter les recalculs
	elo_ratings: Optional[Dict[str, int]] = None


@dataclass
class PlayerPhysical:
	"""Données physiques d'un joueur"""
	height: int = 180  # Todo: modification possible
	dominant_hand: str = ""
	backhand_style: str = ""
	fatigue: int = 0

	def __post_init__(self):
		if not self.dominant_hand:
			self.dominant_hand = get_random_hand()
		if not self.backhand_style:
			self.backhand_style = get_random_backhand()

	def recover_fatigue(self, amount: int):
		"""Récupère une certaine quantité de fatigue"""
		self.fatigue = max(0, self.fatigue - amount)


class Player:
	"""Joueur de tennis"""

	def __init__(self, gender: Gender, first_name: str, last_name: str,
				 country: str, height: Optional[int] = None,
				 level: int = 1, archetype: Optional[str] = None,
				 is_main_player: bool = False, age: Optional[int] = None):

		# Validation des paramètres
		self._validate_init_params(gender, first_name, last_name, country, height, level)

		self.gender = gender
		self.first_name = first_name
		self.last_name = last_name
		self.country = country
		self.height = height
		self.archetype = archetype or random.choice(list(ARCHETYPES.keys()))
		self.is_main_player = is_main_player

		# Génération de l'âge si non spécifié
		if age is None:
			age = random.randint(PLAYER_CONSTANTS["STARTING_AGE_MIN"], PLAYER_CONSTANTS["STARTING_AGE_MAX"])

		# Initialisation des composants
		self.stats = PlayerStats()
		self.career = PlayerCareer(level=level, ap_points=PLAYER_CONSTANTS["BASE_POINTS"] * (level - 1), age=age)
		self.physical = PlayerPhysical()
		
		# Initialiser les ratings ELO pour toutes les surfaces
		self._initialize_elo_ratings()

		# Génération de la taille selon le genre
		if height is None:
			bounds = (160, 205) if gender == Gender.MALE else (155, 185)
			self.physical.height = generate_height(*bounds)
		else:
			self.physical.height = height

		# Initialisation des statistiques
		self._apply_height_modifiers()

		if self.career.level == 1:
			self._auto_assign_ap_points()

	def _validate_init_params(self, gender: Gender, first_name: str, last_name: str,
							  country: str, height: Optional[int], level: int):
		"""Valide les paramètres d'initialisation"""
		if not isinstance(gender, Gender):
			raise ValueError("Le genre doit être une instance de Gender")
		if not isinstance(first_name, str) or not isinstance(last_name, str):
			raise ValueError("Prénom et nom doivent être des strings")
		if not isinstance(country, str):
			raise ValueError("Le pays doit être une chaîne de caractères")
		if height is not None and not (145 < height < 220):
			raise ValueError("La taille doit être entre 145 et 220 cm")
		if level < 1:
			raise ValueError("Le niveau minimum est 1")

	@property
	def full_name(self) -> str:
		return f"{self.first_name} {self.last_name}"

	@property
	def elo(self) -> int:
		"""Retourne l'ELO général stocké du joueur"""
		return self.get_elo()

	def get_elo(self, surface: Optional[str] = None) -> int:
		"""Retourne l'ELO pour une surface donnée ou général"""
		if surface and surface in self.career.elo_ratings:
			return self.career.elo_ratings[surface]
		elif not surface and "General" in self.career.elo_ratings:
			return self.career.elo_ratings["General"]
		else:
			# Si l'ELO n'est pas encore calculé, le calculer et le stocker
			return self._calculate_and_store_elo(surface)

	def _calculate_and_store_elo(self, surface: Optional[str] = None) -> int:
		"""Calcule et stocke l'ELO pour une surface donnée ou général"""
		stats_dict = self.stats.to_dict()

		if surface and surface in SURFACE_IMPACTS:
			# Modificateurs de surface
			modified_stats = {
				stat: value * SURFACE_IMPACTS[surface].get(stat, 1.0)
				for stat, value in stats_dict.items()
			}
			weights = {
				stat: STATS_WEIGHTS[stat] * SURFACE_IMPACTS[surface].get(stat, 1.0)
				for stat in STATS_WEIGHTS
			}
			key = surface
		else:
			modified_stats = stats_dict
			weights = STATS_WEIGHTS
			key = "General"

		elo = calculate_weighted_elo(modified_stats, weights)
		self.career.elo_ratings[key] = elo
		return elo

	def _initialize_elo_ratings(self):
		"""Initialise les ratings ELO pour toutes les surfaces"""
		if self.career.elo_ratings is None:
			self.career.elo_ratings = {}

	def _recalculate_all_elo_ratings(self):
		"""Recalcule tous les ELO ratings stockés après un changement de stats/niveau"""
		if self.career.elo_ratings is None:
			self.career.elo_ratings = {}
		
		# Recalculer l'ELO général
		self._calculate_and_store_elo()
		
		# Recalculer l'ELO pour toutes les surfaces connues
		for surface in SURFACE_IMPACTS.keys():
			self._calculate_and_store_elo(surface)

	def _apply_height_modifiers(self):
		"""Modifie les statistiques du joueur en fonction de la taille"""
		mean_height = 182 if self.gender == Gender.MALE else 170
		heigh_mod = (self.physical.height - mean_height) / 20

		stats_dict = self.stats.to_dict()

		for stat, impact in HEIGHT_IMPACTS.items():
			if stat in stats_dict:
				adjustement = round(impact * heigh_mod * 10)
				new_value = min(70, stats_dict[stat] + adjustement)
				stats_dict[stat] = new_value

		self.stats.update_from_dict(stats_dict)

	def gain_experience(self, xp: int):
		"""Gagne de l'xp et gère la montée de niveau"""
		# Ancien facteur de niveau (réduit légèrement)
		level_factor = max(1 - ((self.career.level-1) / PLAYER_CONSTANTS["MAX_LEVEL"]) * 0.4, 0.5)

		# Nouveau: facteur d'âge pour plus de réalisme
		age_factor = get_age_progression_factor(self.career.age)

		# Combinaison des facteurs
		total_factor = level_factor * age_factor
		adjusted_xp = round(xp * total_factor)

		self.career.xp_points += adjusted_xp

		if self.is_main_player:
			print(f"\n{self.full_name} a gagné {adjusted_xp} pts d'xp.")

		self._check_level_up()

	def gain_tournament_experience(self, tournament_category: str, round_reached: str):
		"""Gagne de l'XP spécifique à une performance en tournoi"""
		tournament_xp = calculate_tournament_xp(tournament_category, round_reached)
		self.gain_experience(tournament_xp, source=f"tournoi ({round_reached})")

		if self.is_main_player and tournament_xp > 0:
			print(f"Bonus XP tournoi: {tournament_xp} pts pour {round_reached} en {tournament_category}")

	def _check_level_up(self):
		"""Vérifie et gère la montée de niveau"""
		level_changed = False
		while (self.career.xp_points >= calculate_experience_required(self.career.level) and
			   self.career.level < PLAYER_CONSTANTS["MAX_LEVEL"]):

			self.career.xp_points -= calculate_experience_required(self.career.level)
			self.career.level += 1
			self.career.ap_points += PLAYER_CONSTANTS["BASE_POINTS"]
			level_changed = True

			if self.is_main_player:
				gender_suffix = get_gender_agreement(self.gender.value)
				print(f"{self.first_name} est passé{gender_suffix} au niveau {self.career.level}!")
				print(f"{self.first_name} a gagné {PLAYER_CONSTANTS['BASE_POINTS']} AP points.")
			else:
				self._auto_assign_ap_points()
		
		# Recalculer les ELO si le niveau a changé
		if level_changed:
			self._recalculate_all_elo_ratings()

	def _auto_assign_ap_points(self):
		"""Assigne automatiquement les points AP selon l'archetype"""
		if self.career.ap_points == 0:
			return

		priorities = ARCHETYPES[self.archetype]
		category_points = {
			"primaire": round(self.career.ap_points * 0.5),
			"secondaire": round(self.career.ap_points * 0.3),
			"tertiaire": round(self.career.ap_points * 0.2)
		}

		stats_dict = self.stats.to_dict()

		for category, points in category_points.items():
			attrs = priorities[category]

			for _ in range(points):
				# Trouve un attribut à améliorer dans la catégorie
				available_attrs = [attr for attr in attrs if stats_dict[attr] < 70]
				if not available_attrs:
					break

				chosen_attr = random.choice(available_attrs)
				stats_dict[chosen_attr] += 1
				self.career.ap_points -= 1

		self.stats.update_from_dict(stats_dict)
		# Recalculer les ELO après changement de stats
		self._recalculate_all_elo_ratings()

	def assign_ap_points_manually(self):
		"""Interface pour l'attribution manuelle des points AP"""
		if self.career.ap_points == 0:
			print("\nPas de points AP à attribuer.")
			return

		stats_dict = self.stats.to_dict()
		stats_names = list(stats_dict.keys())

		while self.career.ap_points > 0:
			print(f"\nAP Points disponibles: {self.career.ap_points}")
			for i, stat in enumerate(stats_names, 1):
				print(f"{i}: {stat} (actuel: {stats_dict[stat]})")

			choice = input("Choisissez un attribut à améliorer (1-8) ou 'q' pour quitter: ")
			if choice.lower() == 'q':
				break

			try:
				index = int(choice) - 1
				if 0 <= index < len(stats_names):
					chosen_stat = stats_names[index]
					points = int(input(f"Combien de points pour {chosen_stat}? "))

					if points > self.career.ap_points:
						print("Pas assez de points AP disponibles.")
						continue

					if stats_dict[chosen_stat] + points > PLAYER_CONSTANTS["MAX_STAT_VALUE"]:
						print(f"L'attribut ne peut pas dépasser {PLAYER_CONSTANTS['MAX_STAT_VALUE']}.")
						continue

					stats_dict[chosen_stat] += points
					self.career.ap_points -= points
					print(f"\n{chosen_stat} augmenté à {stats_dict[chosen_stat]}")
				else:
					print("Choix invalide.")

			except (ValueError, IndexError):
				print("Choix invalide. Veuillez réessayer.")

		self.stats.update_from_dict(stats_dict)
		# Recalculer les ELO après changement de stats
		self._recalculate_all_elo_ratings()

	def add_atp_points(self, points: int):
		"""Ajoute des points ATP au joueur"""
		self.career.atp_points += points
		if self.is_main_player:
			print(f"{self.first_name} {self.last_name} a gagné {points} points ATP.")

	def manage_fatigue(self, activity: str, sets_played: int = 0, tournament_category: str = None,
					   display: bool = False) -> Optional[int]:
		"""Gère la fatigue du joueur selon l'activité"""
		fatigue_added = calculate_fatigue_level(activity, sets_played, tournament_category)
		self.physical.fatigue = min(PLAYER_CONSTANTS["MAX_FATIGUE"],
									self.physical.fatigue + fatigue_added)

		return fatigue_added if display else None

	def rest(self):
		"""Le joueur se repose"""
		rest_amount = calculate_fatigue_level("Repos")
		self.physical.fatigue = max(0, self.physical.fatigue - rest_amount)

	def recover_fatigue(self, recovery_amount: int):
		"""Récupère de la fatigue naturellement"""
		self.physical.fatigue = max(0, self.physical.fatigue - recovery_amount)

	def should_participate(self) -> bool:
		"""
		Détermine si le joueur devrait participer selon sa fatigue

		Returns:
			True si le joueur devrait participer
		"""
		return self.physical.fatigue < PLAYER_CONSTANTS["FATIGUE_PARTICIPATION_THRESHOLD"]

	def get_display_card(self, ranking_position: int = None) -> str:
		"""
		Génère la carte d'affichage du joueur

		Args:
			ranking_position: Position dans le classement (optionnel)

		Returns:
			Chaîne formatée pour l'affichage
		"""
		width = 46
		lines = []

		# En-tête
		lines.append("┌" + "─" * (width - 2) + "┐")
		lines.append("│" + " ID CARD ".center(width - 2) + "│")
		lines.append("├" + "─" * (width - 2) + "┤")

		# Informations personnelles
		lines.append(f"│ Nom     : {self.last_name:<32} │")
		lines.append(f"│ Prénom  : {self.first_name:<32} │")
		lines.append(f"│ Taille  : {self.physical.height} cm{' ' * 26} │")
		lines.append(f"│ Nationalité  : {self.country:<27} │")
		lines.append(f"│ Main    : {self.physical.dominant_hand:<32} │")
		lines.append(f"│ Revers  : {self.physical.backhand_style:<32} │")

		# Situation
		lines.append("├" + "─" * (width - 2) + "┤")
		lines.append("│" + " SITUATION ".center(width - 2) + "│")
		lines.append("├" + "─" * (width - 2) + "┤")

		lines.append(f"│ Âge     : {self.career.age} ans{' ' * 26} │")
		if ranking_position:
			lines.append(f"│ Classement ATP : {ranking_position:<23} │")
		lines.append(f"│ Points ATP : {self.career.atp_points:<28} │")
		lines.append(f"│ ELO     : {self.elo:<32} │")
		lines.append(f"│ Niveau  : {self.career.level:<32} │")

		# Barre d'expérience
		xp_required = calculate_experience_required(self.career.level)
		xp_current = self.career.xp_points
		max_bar = 20
		xp_bar = "▓" * int(xp_current * max_bar / xp_required)
		xp_empty = "░" * (max_bar - len(xp_bar))
		xp_text = f"{xp_current}/{xp_required}"

		lines.append(f"│ XP      : {xp_bar}{xp_empty} {xp_text:>8} │")
		lines.append(f"│ Fatigue : {self.physical.fatigue:<32} │")

		# Statistiques
		lines.append("├" + "─" * (width - 2) + "┤")
		lines.append("│" + " STATISTIQUES ".center(width - 2) + "│")
		lines.append("├" + "─" * (width - 2) + "┤")

		for stat, value in self.stats.to_dict().items():
			bar = "▓" * int(value * max_bar / 100)
			empty = " " * (max_bar - len(bar))
			lines.append(f"│ {stat:<10}: {bar}{empty} {value:>9} │")

		lines.append("└" + "─" * (width - 2) + "┘")

		return "\n".join(lines)

	def display_id_card(self, ranking_manager: Optional['RankingManager'] = None):
		"""
		Affiche la carte du joueur

		Args:
			ranking_position: Position dans le classement (optionnel)
		"""
		ranking_position = ranking_manager.atp_ranking.get_player_rank(self)
		print(self.get_display_card(ranking_position))

	def to_dict(self) -> Dict:
		"""Convertit le joueur en dictionnaire pour la sauvegarde"""
		from dataclasses import asdict

		career_dict = asdict(self.career)
		# S'assurer que elo_ratings est sérialisé correctement
		if self.career.elo_ratings is None:
			career_dict["elo_ratings"] = {}
		else:
			career_dict["elo_ratings"] = self.career.elo_ratings

		return {
			"gender": self.gender.value,
			"first_name": self.first_name,
			"last_name": self.last_name,
			"country": self.country,
			"archetype": self.archetype,
			"is_main_player": self.is_main_player,
			"stats": asdict(self.stats),
			"career": career_dict,
			"physical": asdict(self.physical)
		}

	@classmethod
	def from_dict(cls, data: Dict) -> 'Player':
		"""Crée un joueur depuis un dictionnaire"""

		# Récupère l'âge depuis les données sauvegardées ou utilise une valeur par défaut
		saved_age = data.get("career", {}).get("age", 20)

		player = cls(
			gender=Gender(data["gender"]),
			first_name=data["first_name"],
			last_name=data["last_name"],
			country=data["country"],
			is_main_player=data.get("is_main_player", False),
			age=saved_age
		)

		# Restaure les attributs principaux
		player.archetype = data["archetype"]

		# Restaure les statistiques
		stats_data = data["stats"]
		player.stats.coup_droit = stats_data["coup_droit"]
		player.stats.revers = stats_data["revers"]
		player.stats.service = stats_data["service"]
		player.stats.vollee = stats_data["vollee"]
		player.stats.puissance = stats_data["puissance"]
		player.stats.vitesse = stats_data["vitesse"]
		player.stats.endurance = stats_data["endurance"]
		player.stats.reflexes = stats_data["reflexes"]

		# Restaure la carrière
		career_data = data["career"]
		player.career.level = career_data["level"]
		player.career.xp_points = career_data["xp_points"]
		player.career.ap_points = career_data["ap_points"]
		player.career.atp_points = career_data["atp_points"]
		player.career.atp_race_points = career_data["atp_race_points"]
		# Support pour l'âge (rétrocompatibilité)
		player.career.age = career_data.get("age", 20)
		# Support pour les ELO ratings (rétrocompatibilité)
		player.career.elo_ratings = career_data.get("elo_ratings", {})

		# Todo : Ceci sera utilisé dans une version future
		#player.career.matches_played = career_data["matches_played"]
		#player.career.matches_won = career_data["matches_won"]
		#player.career.tournaments_won = career_data["tournaments_won"]

		# Restaure le physique
		physical_data = data["physical"]
		player.physical.height = physical_data["height"]
		player.physical.dominant_hand = physical_data["dominant_hand"]
		player.physical.backhand_style = physical_data["backhand_style"]
		player.physical.fatigue = physical_data["fatigue"]

		return player

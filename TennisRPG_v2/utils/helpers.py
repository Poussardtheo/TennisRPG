"""
Fonctions utilitaires pour le jeu
"""
import random
from typing import Dict
from scipy.stats import truncnorm

from .constants import STATS_WEIGHTS, AGE_PROGRESSION_FACTORS, RETIREMENT_CONSTANTS


def generate_height(lower_bound: int, upper_bound: int) -> int:
	"""
	Génère une taille selon une distribution normale tronquée

	Args:
		lower_bound: Limite inférieure
		upper_bound: Limite supérieure

	Returns:
		Taille générée en centimètres
	"""
	std_dev = 10  # écart-type de la distribution
	mean = (upper_bound + lower_bound) / 2  # moyenne de la distribution

	a = (lower_bound - mean) / std_dev
	b = (upper_bound - mean) / std_dev

	return int(truncnorm.rvs(a, b, loc=mean, scale=std_dev, size=1))


def calculate_weighted_elo(stats: Dict[str, int], weights: Dict[str, float] = None) -> int:
	"""
	Calcule l'ELO pondéré basé sur les statistiques

	Args:
		stats: Dictionnaire des statistiques
		weights: Poids pour chaque statistique (optionnel)

	Returns:
		ELO calculé
	"""
	if weights is None:
		weights = STATS_WEIGHTS

	weighted_score = sum(stats[stat] * weights[stat] for stat in weights)
	average_score = weighted_score / sum(weights.values())

	return round(1500 + (average_score - 40) * 30)


def calculate_experience_required(level: int) -> int:
	"""
	Calcule l'expérience requise pour atteindre le niveau suivant

	Args:
		level: Niveau actuel

	Returns:
		Expérience requise
	"""
	return int(150 * (level ** 1.2) + level * 25)


def get_gender_agreement(gender: str) -> str:
	"""
	Retourne l'accord grammatical selon le genre

	Args:
		gender: Genre ('m' ou 'f')

	Returns:
		Accord grammatical ('e' pour féminin, '' pour masculin)
	"""
	return "e" if gender.lower() == 'f' else ""


def get_random_hand() -> str:
	"""Retourne une main dominante aléatoire"""
	return "Gauche" if random.random() < 0.15 else "Droite"


def get_random_backhand() -> str:
	"""Retourne un style de revers aléatoire"""
	return "Une main" if random.random() < 0.11 else "Deux mains"


def calculate_fatigue_level(activity: str, sets_played: int = 0, tournament_category: str = None) -> int:
	"""
	Calcule le niveau de fatigue selon l'activité

	Args:
		activity: Type d'activité
		sets_played: Nombre de sets joués (pour les tournois)
		tournament_category: Catégorie du tournoi (pour appliquer le bon coefficient)

	Returns:
		Niveau de fatigue ajouté
	"""
	from .constants import FATIGUE_VALUES, TOURNAMENT_FATIGUE_MULTIPLIERS

	if activity in FATIGUE_VALUES:
		min_fatigue, max_fatigue = FATIGUE_VALUES[activity]
		return random.randint(min_fatigue, max_fatigue)
	elif activity == "Tournament":
		# Fatigue de base proportionnelle aux sets joués
		base_fatigue = sets_played * 2
		
		# Application du coefficient spécifique au tournoi
		if tournament_category and tournament_category in TOURNAMENT_FATIGUE_MULTIPLIERS:
			multiplier = TOURNAMENT_FATIGUE_MULTIPLIERS[tournament_category]
			return int(base_fatigue * multiplier)
		else:
			# Coefficient par défaut (ATP 250)
			return base_fatigue
	else:
		return 0


def get_participation_rate(tournament: 'Tournament') -> float:
	"""
	Retourne le taux de participation pour un type de tournoi

	Args:
		tournament: tournoi à prendre en compte

	Returns:
		Taux de participation
	"""
	if tournament.category in ["Grand Slam", "ATP Finals"]:
		participation_rate = 2 	# Huge participation rate for major tournaments
	elif tournament.category == "Masters 1000":
		participation_rate = 0.9
	elif tournament.category == "ATP 500":
		participation_rate = 0.8
	elif tournament.category == "ATP 250":
		participation_rate = 0.75
	else:
		participation_rate = 0.7
	return participation_rate


def get_age_progression_factor(age: int) -> float:
	"""
	Retourne le facteur de progression en fonction de l'âge
	
	Args:
		age: Âge du joueur
		
	Returns:
		Facteur multiplicateur pour la progression
	"""
	if age <= 19:
		return AGE_PROGRESSION_FACTORS["16-19"]
	elif age <= 22:
		return AGE_PROGRESSION_FACTORS["20-22"]
	elif age <= 26:
		return AGE_PROGRESSION_FACTORS["23-26"]
	elif age <= 30:
		return AGE_PROGRESSION_FACTORS["27-30"]
	elif age <= 33:
		return AGE_PROGRESSION_FACTORS["31-33"]
	else:
		return AGE_PROGRESSION_FACTORS["34+"]


def calculate_tournament_xp(tournament_category: str, round_reached: str, base_xp: int = None) -> int:
	"""
	Calcule l'XP gagnée pour une performance en tournoi
	
	Args:
		tournament_category: Catégorie du tournoi
		round_reached: Round atteint ("Champion", "Finale", etc.)
		base_xp: XP de base (optionnel, utilise les constantes par défaut)
		
	Returns:
		XP calculée
	"""
	from .constants import TOURNAMENT_XP_REWARDS, ROUND_XP_MULTIPLIERS
	
	if base_xp is None:
		base_xp = TOURNAMENT_XP_REWARDS.get(tournament_category, 20)  # Défaut si catégorie inconnue
	
	multiplier = ROUND_XP_MULTIPLIERS.get(round_reached, 0.1)  # Défaut = premier tour
	
	return int(base_xp * multiplier)


def calculate_retirement_probability(age: int, atp_ranking: int = None) -> float:
	"""
	Calcule la probabilité de retraite d'un joueur basée sur son âge et son classement
	
	Args:
		age: Âge du joueur
		atp_ranking: Classement ATP du joueur (optionnel, pour ajuster la probabilité)
		
	Returns:
		Probabilité de retraite (entre 0 et 1)
	"""
	# Âge minimum pour prendre sa retraite
	if age < RETIREMENT_CONSTANTS["MIN_RETIREMENT_AGE"]:
		return 0.0
	
	# Retraite forcée à l'âge maximum
	if age >= RETIREMENT_CONSTANTS["MAX_CAREER_AGE"]:
		return 1.0
	
	# Calcul de la probabilité de base selon l'âge
	years_past_min = age - RETIREMENT_CONSTANTS["MIN_RETIREMENT_AGE"]
	base_probability = RETIREMENT_CONSTANTS["BASE_RETIREMENT_PROBABILITY"]
	age_multiplier = RETIREMENT_CONSTANTS["AGE_RETIREMENT_MULTIPLIER"]
	
	# Probabilité exponentielle croissante avec l'âge
	probability = base_probability * (1 + age_multiplier) ** years_past_min
	
	# Ajustement selon le classement ATP (les joueurs mieux classés restent plus longtemps)
	if atp_ranking is not None:
		if atp_ranking <= 50:  # Top 50: réduction significative de la probabilité
			probability *= 0.3
		elif atp_ranking <= 100:  # Top 100: réduction modérée
			probability *= 0.5
		elif atp_ranking <= 200:  # Top 200: légère réduction
			probability *= 0.7
		elif atp_ranking > 500:  # Joueurs mal classés: augmentation
			probability *= 1.5
	
	# Assure que la probabilité reste dans les limites [0, 1]
	return min(1.0, max(0.0, probability))


def should_player_retire(player: 'Player', atp_ranking: int = None) -> bool:
	"""
	Détermine si un joueur devrait prendre sa retraite
	
	Args:
		player: Instance du joueur
		atp_ranking: Classement ATP du joueur (optionnel)
		
	Returns:
		True si le joueur devrait prendre sa retraite
	"""
	if not hasattr(player, 'career') or not hasattr(player.career, 'age'):
		return False
		
	probability = calculate_retirement_probability(player.career.age, atp_ranking)
	return random.random() < probability

def get_round_display_name(round_name: str) -> str:
	"""Convertit le nom interne du round en nom d'affichage"""
	display_names = {
		"finalist": "FINALE",
		"semifinalist": "DEMI-FINALES",
		"quarterfinalist": "QUARTS DE FINALE",
		"round_16": "8ème DE FINALE",
		"round_32": "16ème DE FINALE",
		"round_64": "32ème DE FINALE",
		"round_128": "64ème DE FINALE"
	}
	return display_names.get(round_name, f"TOUR {round_name.upper()}")

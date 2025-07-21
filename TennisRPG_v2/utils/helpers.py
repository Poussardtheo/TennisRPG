"""
Fonctions utilitaires pour le jeu
"""
import random
from typing import Dict
from scipy.stats import truncnorm

from .constants import STATS_WEIGHTS


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
	return int(200 * level ** 1.2)


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


def calculate_fatigue_level(activity: str, sets_played: int = 0) -> int:
	"""
	Calcule le niveau de fatigue selon l'activité

	Args:
		activity: Type d'activité
		sets_played: Nombre de sets joués (pour les tournois)

	Returns:
		Niveau de fatigue ajouté
	"""
	from .constants import FATIGUE_VALUES

	if activity in FATIGUE_VALUES:
		min_fatigue, max_fatigue = FATIGUE_VALUES[activity]
		return random.randint(min_fatigue, max_fatigue)
	elif activity == "Tournament":
		# Fatigue proportionnelle aux sets joués
		return sets_played * 2  # TODO: Coefficient à ajuster
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
		participation_rate = 1.5
	elif tournament.category == "Masters 1000":
		participation_rate = 0.9
	elif tournament.category == "ATP 500":
		participation_rate = 0.8
	elif tournament.category == "ATP 250":
		participation_rate = 0.75
	else:
		participation_rate = 0.7
	return participation_rate
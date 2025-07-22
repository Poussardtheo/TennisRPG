"""
Entité Tournament - Tournois de tennis
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import random

from ..data.tournaments_data import (
	TournamentCategory, ATP_POINTS_CONFIG, XP_POINTS_CONFIG,
	ELIGIBILITY_THRESHOLDS, SPECIAL_TOURNAMENT_CONFIG
)
from ..utils.constants import TOURNAMENT_CONSTANTS, TOURNAMENT_FORMATS, TOURNAMENT_SURFACES


class TournamentStatus(Enum):
	"""Statut d'un tournoi"""
	PREPARATION = "preparation"
	IN_PROGRESS = "in_progress"
	COMPLETED = "completed"
	CANCELLED = "cancelled"


@dataclass
class MatchResult:
	"""Résultat d'un match"""
	winner: 'Player'
	loser: 'Player'
	sets_won: int
	sets_lost: int
	fatigue_winner: int
	fatigue_loser: int


@dataclass
class TournamentResult:
	"""Résultat d'un tournoi"""
	tournament_name: str
	category: TournamentCategory
	winner: 'Player'
	finalist: 'Player'
	semifinalists: List['Player']
	quarterfinalists: List['Player']
	all_results: Dict['Player', str]  # joueur -> round éliminé
	match_results: List[MatchResult]


class Tournament(ABC):
	"""Classe de base pour tous les tournois"""

	def __init__(self, name: str, location: str, surface: str,
				 category: TournamentCategory, num_players: int,
				 sets_to_win: int = None):
		"""
		Initialise un tournoi

		Args:
			name: Nom du tournoi
			location: Lieu du tournoi
			surface: Surface de jeu
			category: Catégorie du tournoi
			num_players: Nombre de joueurs
			sets_to_win: Nombre de sets à gagner (optionnel)
		"""
		self.name = name
		self.location = location
		self.surface = self._validate_surface(surface)
		self.category = category
		self.num_players = num_players
		self.sets_to_win = sets_to_win or TOURNAMENT_CONSTANTS["DEFAULT_SETS_TO_WIN"]

		# État du tournoi
		self.status = TournamentStatus.PREPARATION
		self.participants: List['Player'] = []
		self.match_results: List[MatchResult] = []
		self.eliminated_players: Dict['Player', str] = {}

		# Configuration automatique
		self.eligibility_threshold = ELIGIBILITY_THRESHOLDS.get(category, 400)
		self.atp_points_config = ATP_POINTS_CONFIG.get(category, {})
		self.xp_points_config = XP_POINTS_CONFIG.get(category, {})

	def _validate_surface(self, surface: str) -> str:
		"""Valide la surface du tournoi"""
		if surface not in TOURNAMENT_SURFACES.values():
			raise ValueError(f"Surface inconnue: {surface}")
		return surface

	@property
	def is_grand_slam(self) -> bool:
		"""Vérifie si c'est un Grand Slam"""
		return self.category == TournamentCategory.GRAND_SLAM

	@property
	def tournament_importance(self) -> int:
		"""Retourne l'importance du tournoi (1-5)"""
		importance_map = {
			TournamentCategory.GRAND_SLAM: 5,
			TournamentCategory.ATP_FINALS: 5,
			TournamentCategory.MASTERS_1000: 4,
			TournamentCategory.ATP_500: 3,
			TournamentCategory.ATP_250: 2,
			TournamentCategory.CHALLENGER_175: 1,
			TournamentCategory.CHALLENGER_125: 1,
			TournamentCategory.CHALLENGER_100: 1,
			TournamentCategory.CHALLENGER_75: 1,
			TournamentCategory.CHALLENGER_50: 1,
			TournamentCategory.ITF_M25: 1,
			TournamentCategory.ITF_M15: 1
		}
		return importance_map.get(self.category, 1)

	def is_player_eligible(self, player: 'Player', ranking_manager=None) -> bool:
		"""
		Vérifie si un joueur est éligible pour ce tournoi

		Args:
			player: Joueur à vérifier
			ranking_manager: Optionnel, pour vérifier le classement ATP

		Returns:
			True si éligible
		"""
		# TODO: Utiliser le classement ATP si ranking_manager est fourni
		if ranking_manager:
			atp_rank = ranking_manager.atp_ranking.get_player_rank(player)
			return atp_rank and atp_rank <= self.eligibility_threshold
		return player.elo >= self.eligibility_threshold

	def add_participant(self, player: 'Player', ranking_manager=None) -> bool:
		"""
		Ajoute un participant au tournoi

		Args:
			player: Joueur à ajouter
			ranking_manager: Optionnel, pour vérifier le classement ATP

		Returns:
			True si ajouté avec succès
		"""
		if len(self.participants) >= self.num_players:
			return False

		if not self.is_player_eligible(player, ranking_manager):
			return False

		if player in self.participants:
			return False

		self.participants.append(player)
		return True

	def get_seeded_players(self, num_seeds: int) -> List['Player']:
		"""
		Obtient les joueurs têtes de série

		Args:
			num_seeds: Nombre de têtes de série

		Returns:
			Liste des têtes de série triée par force
		"""
		if not self.participants:
			return []

		# Trie par ELO décroissant
		sorted_players = sorted(
			self.participants,
			key=lambda p: p.elo,
			reverse=True
		)

		return sorted_players[:min(num_seeds, len(sorted_players))]

	def assign_atp_points(self, player: 'Player', round_reached: str, 
						  atp_points_manager=None, week: int = None) -> int:
		"""
		Attribue les points ATP selon le tour atteint

		Args:
			player: Joueur
			round_reached: Tour atteint
			atp_points_manager: Gestionnaire des points ATP pour le système glissant
			week: Semaine courante pour le système glissant

		Returns:
			Points ATP attribués
		"""
		# Détermine le nombre de tours pour les tournois avec configurations multiples
		round_key = self._get_round_key_for_tournament(round_reached)
		points = self.atp_points_config.get(round_key, 0)

		if points > 0:
			atp_points_manager.add_tournament_points(player, week, points)

			if hasattr(player, 'is_main_player') and player.is_main_player:
				print(f"   💰 +{points} points ATP pour {player.full_name}")

		return points

	def _get_round_key_for_tournament(self, round_reached: str) -> str:
		"""
		Détermine la clé de configuration ATP en fonction du tournoi et du tour
		
		Args:
			round_reached: Tour atteint (ex: "winner", "semifinalist")
			
		Returns:
			Clé pour la configuration ATP (ex: "winner_6", "semifinalist_5")
		"""
		# Pour les catégories qui n'ont pas de variations de tours
		if self.category not in [TournamentCategory.MASTERS_1000, TournamentCategory.ATP_500, TournamentCategory.ATP_250]:
			return round_reached
			
		# Calcule le nombre de tours basé sur le nombre de joueurs
		num_rounds = self._calculate_tournament_rounds()
		
		# Pour Masters 1000, ATP 500 et ATP 250 avec configurations multiples
		round_key = f"{round_reached}_{num_rounds}"
		
		# Vérifie si la clé existe, sinon utilise la clé de base
		if round_key in self.atp_points_config:
			return round_key
		else:
			return round_reached

	def _calculate_tournament_rounds(self) -> int:
		"""
		Calcule le nombre de tours du tournoi basé sur le nombre de joueurs
		
		Returns:
			Nombre de tours
		"""
		import math
		if self.num_players <= 0:
			return 5  # Valeur par défaut
		return int(math.ceil(math.log2(self.num_players)))

	def assign_xp_points(self, player: 'Player', round_reached: str) -> int:
		"""
		Attribue les points XP selon le tour atteint

		Args:
			player: Joueur
			round_reached: Tour atteint

		Returns:
			Points XP attribués
		"""
		xp = self.xp_points_config.get(round_reached, 0)

		if xp > 0:
			player.gain_experience(xp)

		return xp

	def simulate_match(self, player1: 'Player', player2: 'Player') -> MatchResult:
		"""
		Simule un match entre deux joueurs

		Args:
			player1: Premier joueur
			player2: Deuxième joueur

		Returns:
			Résultat du match
		"""
		# Calcul des ELO ajustés pour la surface
		elo1 = player1._calculate_elo(self.surface)
		elo2 = player2._calculate_elo(self.surface)

		# Probabilité de victoire basée sur l'ELO
		expected_score1 = 1 / (1 + 10 ** ((elo2 - elo1) / 400))

		# Facteur de fatigue
		fatigue_factor1 = max(0.7, 1 - (player1.physical.fatigue / 100) * 0.3)
		fatigue_factor2 = max(0.7, 1 - (player2.physical.fatigue / 100) * 0.3)

		adjusted_prob1 = expected_score1 * fatigue_factor1
		adjusted_prob2 = (1 - expected_score1) * fatigue_factor2

		# Normalisation
		total_prob = adjusted_prob1 + adjusted_prob2
		final_prob1 = adjusted_prob1 / total_prob

		# Détermine le vainqueur
		if random.random() < final_prob1:
			winner, loser = player1, player2
		else:
			winner, loser = player2, player1

		# Simule le nombre de sets
		sets_won = self.sets_to_win
		sets_lost = random.randint(0, self.sets_to_win - 1)

		# Calcul de la fatigue de base
		base_fatigue_winner = random.randint(8, 15) + (sets_won + sets_lost - 2) * 3
		base_fatigue_loser = random.randint(10, 18) + (sets_won + sets_lost - 2) * 4
		
		# Application du coefficient spécifique au tournoi
		from ..utils.constants import TOURNAMENT_FATIGUE_MULTIPLIERS
		multiplier = TOURNAMENT_FATIGUE_MULTIPLIERS.get(self.category.value, 1.0)
		
		fatigue_winner = int(base_fatigue_winner * multiplier)
		fatigue_loser = int(base_fatigue_loser * multiplier)

		# Applique la fatigue
		winner.physical.fatigue = min(100, winner.physical.fatigue + fatigue_winner)
		loser.physical.fatigue = min(100, loser.physical.fatigue + fatigue_loser)

		# Gain d'expérience pour le match
		winner.gain_experience(TOURNAMENT_CONSTANTS["MATCH_BASE_XP"])
		loser.gain_experience(TOURNAMENT_CONSTANTS["MATCH_BASE_XP"] // 2)

		return MatchResult(
			winner=winner,
			loser=loser,
			sets_won=sets_won,
			sets_lost=sets_lost,
			fatigue_winner=fatigue_winner,
			fatigue_loser=fatigue_loser
		)

	@property
	def has_main_player(self) -> bool:
		"""Vérifie si le joueur principal participe à ce tournoi"""
		return any(hasattr(p, 'is_main_player') and p.is_main_player for p in self.participants)

	@abstractmethod
	def play_tournament(self, verbose: bool = None, atp_points_manager=None, week: int = None) -> TournamentResult:
		"""
		Joue le tournoi (méthode abstraite)

		Args:
			verbose: Si True, affiche tous les détails. Si None, détermine automatiquement.
			atp_points_manager: Gestionnaire des points ATP pour le système glissant
			week: Semaine courante

		Returns:
			Résultat du tournoi
		"""
		pass

	def __str__(self) -> str:
		return f"{self.name} ({self.category.value}) - {self.location} - {self.surface}"

	def __repr__(self) -> str:
		return f"Tournament(name='{self.name}', category={self.category}, players={len(self.participants)})"


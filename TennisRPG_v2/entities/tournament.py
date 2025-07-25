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
	# Rajouter plus tard le score détaillé (nombre de jeu par sets) si nécessaire


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
		from ..data.tournaments_data import TournamentCategory
		
		# Cas spécial pour l'ATP Finals : utilise le classement race
		if self.category == TournamentCategory.ATP_FINALS and ranking_manager:
			race_rank = ranking_manager.atp_race_ranking.get_player_rank(player)
			if race_rank:  # Si le joueur a un classement race
				return race_rank <= self.eligibility_threshold
		
		# Pour tous les autres tournois : priorité au classement ATP si disponible (plus réaliste)
		if ranking_manager:
			atp_rank = ranking_manager.atp_ranking.get_player_rank(player)
			if atp_rank:  # Si le joueur a un classement ATP
				return atp_rank <= self.eligibility_threshold
		
		# Fallback sur ELO si pas de classement ATP
		# Utilise un seuil ELO équivalent basé sur une conversion approximative
		elo_threshold = self._convert_atp_rank_to_elo_threshold(self.eligibility_threshold)
		return player.elo >= elo_threshold

	def _convert_atp_rank_to_elo_threshold(self, atp_rank_threshold: int) -> int:
		"""
		Convertit un seuil de rang ATP en seuil ELO équivalent
		
		Args:
			atp_rank_threshold: Rang ATP maximum autorisé
			
		Returns:
			ELO minimum équivalent
		"""
		# Conversion approximative basée sur la corrélation ATP/ELO
		# Plus le rang ATP est élevé (mauvais), plus l'ELO requis est bas
		if atp_rank_threshold <= 10:      # Top 10
			return 1700
		elif atp_rank_threshold <= 50:    # Top 50
			return 1500
		elif atp_rank_threshold <= 100:   # Top 100
			return 1300
		elif atp_rank_threshold <= 200:   # Top 200
			return 1100
		elif atp_rank_threshold <= 500:   # Top 500
			return 900
		elif atp_rank_threshold <= 1000:  # Top 1000
			return 700
		else:                             # Au-delà
			return 500

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

		# Vérification robuste des doublons basée sur les attributs uniques
		player_already_in = any(
			p.first_name == player.first_name and 
			p.last_name == player.last_name and 
			p.country == player.country 
			for p in self.participants
		)
		
		if player_already_in:
			return False

		self.participants.append(player)
		return True

	def get_seeded_players(self, num_seeds: int, ranking_manager=None) -> List['Player']:
		"""
		Obtient les joueurs têtes de série basé sur le classement ATP

		Args:
			num_seeds: Nombre de têtes de série
			ranking_manager: Gestionnaire de classement pour obtenir les rangs ATP

		Returns:
			Liste des têtes de série triée par classement ATP
		"""
		if not self.participants:
			return []

		# Si on a un ranking_manager, trie par classement ATP
		if ranking_manager:
			def get_sort_key(player):
				atp_rank = ranking_manager.atp_ranking.get_player_rank(player)
				# Si pas de rang ATP, utilise un rang très élevé (mauvais)
				return atp_rank if atp_rank else 9999
			
			sorted_players = sorted(
				self.participants,
				key=get_sort_key
			)
		else:
			# Fallback sur ELO si pas de ranking_manager
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

		if points > 0 and atp_points_manager is not None:
			atp_points_manager.add_tournament_points(player, week, points)

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

	def calculate_xp_points(self, round_reached: str) -> int:
		"""
		Calcule les points XP selon le tour atteint sans les attribuer

		Args:
			round_reached: Tour atteint

		Returns:
			Points XP calculés
		"""
		# Détermine le nombre de tours pour les tournois avec configurations multiples
		round_key = self._get_round_key_for_tournament(round_reached)
		return self.xp_points_config.get(round_key, 0)

	def assign_xp_points(self, player: 'Player', round_reached: str) -> int:
		"""
		Attribue les points XP selon le tour atteint

		Args:
			player: Joueur
			round_reached: Tour atteint

		Returns:
			Points XP attribués
		"""
		xp = self.calculate_xp_points(round_reached)

		if xp > 0:
			player.gain_experience(xp)

		return xp

	def simulate_match(self, player1: 'Player', player2: 'Player', injury_manager=None) -> MatchResult:
		"""
		Simule un match entre deux joueurs

		Args:
			player1: Premier joueur
			player2: Deuxième joueur
			injury_manager: Gestionnaire des blessures (optionnel)

		Returns:
			Résultat du match
		"""
		# Calcul des ELO ajustés pour la surface
		elo1 = player1.get_elo(self.surface)
		elo2 = player2.get_elo(self.surface)

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

		# Gestion de la fatigue - utilisation des méthodes centralisées
		sets_played_total = sets_won + sets_lost
		winner.manage_fatigue("Tournament", sets_played_total, self.category.value)
		loser.manage_fatigue("Tournament", sets_played_total, self.category.value)

		# Vérification des blessures après le match
		if injury_manager:
			winner_injury = injury_manager.process_activity_injury(winner, "Tournoi", sets_played_total, self.category.value)
			loser_injury = injury_manager.process_activity_injury(loser, "Tournoi", sets_played_total, self.category.value)
			
			# Affichage des blessures si le joueur principal est concerné
			if hasattr(winner, 'is_main_player') and winner.is_main_player and winner_injury:
				print(f"\n🏥 {winner.full_name} s'est blessé pendant le match : {winner_injury.name}")
			elif hasattr(loser, 'is_main_player') and loser.is_main_player and loser_injury:
				print(f"\n🏥 {loser.full_name} s'est blessé pendant le match : {loser_injury.name}")

		# Note: L'XP de tournoi est attribuée seulement à la fin selon le tour atteint
		# Pas d'XP attribuée à chaque match pour éviter la double attribution

		return MatchResult(
			winner=winner,
			loser=loser,
			sets_won=sets_won,
			sets_lost=sets_lost
		)

	@property
	def has_main_player(self) -> bool:
		"""Vérifie si le joueur principal participe à ce tournoi"""
		return any(hasattr(p, 'is_main_player') and p.is_main_player for p in self.participants)

	@abstractmethod
	def play_tournament(self, verbose: bool = None, atp_points_manager=None, week: int = None, injury_manager=None) -> TournamentResult:
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


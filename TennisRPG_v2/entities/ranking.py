"""
Entité Ranking - Structure de données pour les classements de Tennis
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class RankingType(Enum):
	"""Types de classements disponibles"""
	ELO = "elo"
	ATP = "atp"
	ATP_RACE = "atp_race"


@dataclass
class RankingEntry:
	"""Entrée dans un classement"""
	player: 'Player'
	rank: int
	points: int

	@property
	def display_name(self) -> str:
		"""Nom d'affichage du joueur"""
		return f"{self.player.first_name} {self.player.last_name}"

	@property
	def country(self) -> str:
		"""Pays du joueur"""
		return self.player.country


class Ranking:
	"""Structure de données pour un classement - Entité pure sans logique métier"""

	def __init__(self, players: Dict[str, 'Player']):
		"""Initialise un classement vide"""
		self.players = players
		self.rankings: Dict[str, int] = {}  # player_name -> rank

	def update_rankings(self, ranked_players: List['Player']) -> None:
		"""Met à jour les rankings avec une liste ordonnée de joueurs"""
		self.rankings = {
			player.full_name: rank 
			for rank, player in enumerate(ranked_players, 1)
		}

	def get_player_rank(self, player: 'Player') -> int:
		"""Obtient le rang d'un joueur (0 si non classé)"""
		return self.rankings.get(player.full_name, 0)

	def get_ranked_players(self, top_n: Optional[int] = None) -> List['Player']:
		"""Retourne les joueurs classés par ordre de rang"""
		sorted_items = sorted(self.rankings.items(), key=lambda x: x[1])
		
		if top_n:
			sorted_items = sorted_items[:top_n]
			
		return [self.players[player_name] for player_name, _ in sorted_items]
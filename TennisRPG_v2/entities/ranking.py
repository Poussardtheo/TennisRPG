"""
Entité Ranking - Gestion des classement de Tennis
"""

from typing import Dict, List, Optional, Tuple
from collections import OrderedDict
from enum import Enum
from dataclasses import dataclass

from ..utils.constants import RANKING_CONSTANTS, RANKING_TYPES


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
	"""Gestionnaire des classements de Tennis"""

	def __init__(self, players: Dict[str, 'Player'], is_preliminary: bool = False):
		"""Initialise un classement"""
		self.players = players
		self.is_preliminary = is_preliminary

		# Classements stockés comme OrderedDict pour maintenir l'ordre
		self._rankings : Dict[RankingType, OrderedDict] = {
			RankingType.ELO: OrderedDict(),
			RankingType.ATP: OrderedDict(),
			RankingType.ATP_RACE: OrderedDict()
		}

		self._initialize_rankings()

	def _initialize_rankings(self):
		"""Initialise tous les classements"""
		if self.is_preliminary:
			# Classement initial basé sur l'ELO
			sorted_players = sorted(
				self.players.values(),
				key=lambda p: p.elo,
				reverse=True
			)
		else:
			# Classement basé sur les points ATP
			sorted_players = sorted(
				self.players.values(),
				key=lambda p: p.career.atp_points,
				reverse=True
			)

		# Initialise tous les classements avec le même ordre
		for ranking_type in RankingType:
			self._rankings[ranking_type] = OrderedDict(
				(player, rank) for rank, player in enumerate(sorted_players, 1)
			)

	def get_player_rank(self, player: 'Player', ranking_type: RankingType = RankingType.ATP) -> int:
		"""
		Obtient le rang d'un joueur dans un classement

		Args:
			player: Joueur à chercher
			ranking_type: Type de classement

		Returns:
			Rang du joueur (1 = premier)
		"""
		return self._rankings[ranking_type].get(player, 0)

	def update_ranking(self, ranking_type: RankingType = RankingType.ATP):
		"""
		Met à jour un classement spécifique

		Args:
			ranking_type: Type de classement à mettre à jour
		"""
		if ranking_type == RankingType.ELO:
			sorted_players = sorted(
				self.players.values(),
				key=lambda player: player.elo,
				reverse=True
			)
		elif ranking_type == RankingType.ATP:
			sorted_players = sorted(
				self.players.values(),
				key=lambda player: player.career.atp_points,
				reverse=True
			)
		elif ranking_type == RankingType.ATP_RACE:
			sorted_players = sorted(
				self.players.values(),
				key=lambda player: player.career.atp_race_points,
				reverse=True
			)

		# Met à jour le classement
		self._rankings[ranking_type] = OrderedDict(
			(player, rank) for rank, player in enumerate(sorted_players, 1)
		)

	def update_all_rankings(self):
		"""Met à jour tous les classements"""
		for ranking_type in RankingType:
			self.update_ranking(ranking_type)

	def get_ranking_entries(self, ranking_type: RankingType = RankingType.ATP,
							top_n: int = None) -> List[RankingEntry]:
		"""
		Obtient les entrées du classement

		Args:
			ranking_type: Type de classement
			top_n: Nombre maximum d'entrées (None = toutes)

		Returns:
			Liste des entrées du classement
		"""
		if top_n is None:
			top_n = RANKING_CONSTANTS["DEFAULT_DISPLAY_COUNT"]

		ranking = self._rankings[ranking_type]
		entries = []

		for player, rank in list(ranking.items())[:top_n]:
			if ranking_type == RankingType.ELO:
				points = player.elo
			elif ranking_type == RankingType.ATP:
				points = player.career.atp_points
			elif ranking_type == RankingType.ATP_RACE:
				points = player.career.atp_race_points

			entries.append(RankingEntry(player=player, rank=rank, points=points))

		return entries

	def display_ranking(self, ranking_type: RankingType = RankingType.ATP,
						top_n: int = None):
		"""
		Affiche le classement

		Args:
			ranking_type: Type de classement
			top_n: Nombre de joueurs à afficher
		"""
		if top_n is None:
			top_n = RANKING_CONSTANTS["DEFAULT_DISPLAY_COUNT"]

		# Titres des classements
		titles = {
			RankingType.ELO: "ELO",
			RankingType.ATP: "ATP",
			RankingType.ATP_RACE: "ATP Race"
		}

		print(f"\nClassement {titles[ranking_type]} :")

		entries = self.get_ranking_entries(ranking_type, top_n)

		for entry in entries:
			points_label = {
				RankingType.ELO: "ELO",
				RankingType.ATP: "ATP Points",
				RankingType.ATP_RACE: "ATP Race Points"
			}[ranking_type]

			print(f"{entry.rank}. {entry.display_name} - {points_label}: {entry.points} - Pays: {entry.country}")

	def reset_atp_race(self):
		"""Remet à zéro le classement ATP Race (début de saison)"""
		for player in self.players.values():
			player.career.atp_race_points = 0

		# Re-classe selon les points ATP normaux
		sorted_players = sorted(
			self.players.values(),
			key=lambda player: player.career.atp_points,
			reverse=True
		)

		self._rankings[RankingType.ATP_RACE] = OrderedDict(
			(player, rank) for rank, player in enumerate(sorted_players, 1)
		)

	def get_top_players(self, ranking_type: RankingType = RankingType.ATP,
						count: int = 10) -> List['Player']:
		"""
		Obtient les meilleurs joueurs selon un classement

		Args:
			ranking_type: Type de classement
			count: Nombre de joueurs à retourner

		Returns:
			Liste des meilleurs joueurs
		"""
		ranking = self._rankings[ranking_type]
		return list(ranking.keys())[:count]

	def get_ranking_stats(self, ranking_type: RankingType = RankingType.ATP) -> Dict[str, int]:
		"""
		Obtient les statistiques d'un classement

		Args:
			ranking_type: Type de classement

		Returns:
			Dictionnaire avec les statistiques
		"""
		entries = self.get_ranking_entries(ranking_type, None)

		if not entries:
			return {"total_players": 0, "min_points": 0, "max_points": 0, "average_points": 0}

		points_list = [entry.points for entry in entries]

		return {
			"total_players": len(entries),
			"min_points": min(points_list),
			"max_points": max(points_list),
			"average_points": sum(points_list) // len(points_list)
		}

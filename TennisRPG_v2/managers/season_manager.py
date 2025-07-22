"""
Gestionnaire spécialisé pour les saisons de tennis
"""
from ..utils.constants import TIME_CONSTANTS
from typing import Dict, Optional


class SeasonManager:
	"""Gestionnaire du calendrier des saisons de tennis"""

	def __init__(self, year: int):
		self.current_year = year
		self.current_week = 1

	def advance_week(self, ranking_manager: 'RankingManager', players: Dict[str, 'Player'], atp_points_manager):
		"""
		Avance d'une semaine et effectue les mises à jour nécessaires.

		Args:
            ranking_manager: Gestionnaire des classements
            players: Dictionnaire des joueurs
            atp_points_manager: Gestionnaire des points ATP
		"""
		if self.current_week == TIME_CONSTANTS["WEEKS_PER_YEAR"]:
			self._start_new_year(ranking_manager)
		else:
			self.current_week += 1

		self._apply_weekly_updates(players, atp_points_manager)

	def _start_new_year(self, ranking_manager: 'RankingManager'):
		"""Réinitialise l'année et les points ATP pour la nouvelle saison."""
		self.current_year += 1
		self.current_week = 0
		ranking_manager.reset_atp_race()

	def _apply_weekly_updates(self, players: Dict[str, 'Player'], atp_points_manager):
		"""Applique les mises à jour hebdomadaires aux joueurs."""
		for player_name, player in players.items():
			# récupération naturelle de la fatigue
			player.physical.fatigue = max(0, player.physical.fatigue - TIME_CONSTANTS["FATIGUE_NATURAL_RECOVERY"])

			# perte des points ATP de la même semaine l'année précédente (système glissant sur 52 semaines)
			if hasattr(atp_points_manager, 'current_atp_points'):
				try:
					# Retire les points de la même semaine l'année précédente
					points_to_remove = atp_points_manager.current_atp_points.loc[
						player.full_name, self.current_week
					]
					if points_to_remove > 0:
						player.career.atp_points -= points_to_remove
						# Remet à zéro les points de cette semaine pour la nouvelle année
						atp_points_manager.current_atp_points.loc[player.full_name, self.current_week] = 0
				except (KeyError, IndexError):
					# Le joueur n'existe pas dans le DataFrame ou la semaine est invalide
					continue

	@property
	def week_info(self) -> str:
		"""Retourne une chaîne d'information sur la semaine actuelle."""
		return f"Semaine {self.current_week} de l'année {self.current_year}"


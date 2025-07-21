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

	def advance_week(self, ranking: 'Ranking', players: Dict[str, 'Player'], atp_points_manager):
		"""
		Avance d'une semaine et effectue les mises à jour nécessaires.

		Args:
            ranking: Gestionnaire des classements
            players: Dictionnaire des joueurs
            atp_points_manager: Gestionnaire des points ATP
		"""
		if self.current_week == TIME_CONSTANTS["WEEKS_PER_YEAR"]:
			self._start_new_year(ranking)
		else:
			self.current_week += 1

		self._apply_weekly_updates(players, atp_points_manager)

	def _start_new_year(self, ranking: 'Ranking'):
		"""Réinitialise l'année et les points ATP pour la nouvelle saison."""
		self.current_year += 1
		self.current_week = 0
		ranking.reset_atp_race()

	def _apply_weekly_updates(self, players: Dict[str, 'Player'], atp_points_manager):
		"""Applique les mises à jour hebdomadaires aux joueurs."""
		for player_key, player in players.items():
			# récupération naturelle de la fatigue
			player.fatigue -= TIME_CONSTANTS["FATIGUE_NATURAL_RECOVERY"]

			# perte des points ATP de la semaine précédente (système glissant)
			if hasattr(atp_points_manager, 'current_atp_points'):
				points_to_remove = atp_points_manager.current_atp_points.loc[
					player_key, self.current_week
				]
				player.career.atp_points -= points_to_remove

	@property
	def week_info(self) -> str:
		"""Retourne une chaîne d'information sur la semaine actuelle."""
		return f"Semaine {self.current_week} de l'année {self.current_year}"

	# Possiblement inutile
	def _is_year_end(self) -> bool:
		"""Vérifie si c'est la fin de l'année."""
		return self.current_week == TIME_CONSTANTS["WEEKS_PER_YEAR"]

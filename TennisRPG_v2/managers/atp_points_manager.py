"""
Gestionnaire des points ATP avec système de points glissants.
"""
import pandas as pd
from typing import Dict, Optional


class ATPPointsManager:
	"""Gestionnaire des points ATP avec système glissant sur 52 semaines."""

	def __init__(self, players: Dict[str, 'Player']):
		"""
		Initialise le gestionnaire avec les joueurs.

		Args:
			players: Dictionnaire des joueurs
		"""
		self.players = players
		self.current_atp_points = pd.DataFrame(
			0,
			index=[p.full_names for p in players.values()],
			columns=range(1, 53), # 52 semaines par an
		)

	def add_tournament_points(self, player: 'Player', week: int, points: int):
		"""
		Ajoute des points ATP pour un joueur à une semaine spécifique.

		Args:
			player: Le joueur auquel les points sont attribués
			points: Points à ajouter
			week: Semaine de l'année (1-52)
		"""
		if week < 1 or week > 52:
			raise ValueError("La semaine doit être entre 1 et 52.")

		self.current_atp_points.loc[player.full_name, week] += points

		# Met à jour les points ATP totaux du joueur
		player.career.atp_points += points
		player.career.atp_race_points += points

	def remove_weekly_points(self, player: 'Player', week: int):
		"""
		Retire les points ATP de la semaine précédente pour tous les joueurs.

		Args:
			week: Semaine de l'année (1-52)
		"""
		if week < 1 or week > 52:
			raise ValueError("La semaine doit être entre 1 et 52.")

		points_to_remove = self.current_atp_points.loc[player.full_name, week]

		if points_to_remove > 0:
			player.career.atp_points -= points_to_remove
			self.current_atp_points.loc[player.full_name, week] = 0

	def get_player_points(self, player: 'Player', week: Optional[int] = None) -> int:
		"""
		Récupère les points ATP d'un joueur pour une semaine spécifique ou pour l'ensemble de la saison.

		Args:
			player: Le joueur dont on veut les points
			week: Semaine de l'année (1-52), si None, retourne les points totaux

		Returns:
			Points ATP du joueur
		"""
		if week is not None:
			if week < 1 or week > 52:
				raise ValueError("La semaine doit être entre 1 et 52.")
			return self.current_atp_points.loc[player.full_name, week]

		return player.career.atp_points

	def reset_atp_race_points(self):
		"""
		Réinitialise les points ATP de la course pour tous les joueurs.
		"""
		for player in self.players.values():
			player.career.atp_race_points = 0

	def process_tournament_results(self, results: Dict['Player', int], week: int):
		"""
		Traite les résultats d'un tournoi et met à jour les points

		Args:
			results: Dictionnaire {joueur: points_gagnés}
			week: Semaine du tournoi
		"""
		for player, points in results.items():
			if points > 0:
				self.add_tournament_points(player, week, points)
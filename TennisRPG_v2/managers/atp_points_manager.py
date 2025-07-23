"""
Gestionnaire des points ATP avec système de points glissants.
"""
from typing import Dict, Optional


class ATPPointsManager:
	"""Gestionnaire des points ATP - délègue au RankingManager pour éviter la duplication."""

	def __init__(self, players: Dict[str, 'Player'], ranking_manager: 'RankingManager'):
		"""
		Initialise le gestionnaire avec les joueurs.

		Args:
			players: Dictionnaire des joueurs
			ranking_manager: Gestionnaire des classements (requis)
		"""
		self.players = players
		if ranking_manager is None:
			raise ValueError("RankingManager is required")
		self.ranking_manager = ranking_manager

	def add_player(self, player: 'Player'):
		"""
		Ajoute un nouveau joueur au système de points ATP.

		Args:
			player: Le nouveau joueur à ajouter
		"""
		# Délègue au ranking manager
		self.ranking_manager.add_player(player)
		
		# S'assurer que le joueur est aussi dans le dictionnaire local
		if player.full_name not in self.players:
			self.players[player.full_name] = player

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

		# S'assurer que le joueur existe
		if player.full_name not in self.players:
			self.add_player(player)

		# Met à jour les points ATP totaux du joueur
		player.career.atp_points += points
		player.career.atp_race_points += points
		
		# Délègue la gestion de l'historique au ranking manager
		self.ranking_manager.add_atp_points(player.full_name, points, week)

	def remove_weekly_points(self, player: 'Player', week: int):
		"""
		Retire les points ATP de la même semaine l'année précédente (système glissant sur 52 semaines).

		Args:
			player: le joueur dont on veut retirer les points
			week: Semaine de l'année (1-52)
		"""
		if week < 1 or week > 52:
			raise ValueError("La semaine doit être entre 1 et 52.")

		# Délègue au ranking manager pour obtenir les points à retirer
		points_to_remove = self.ranking_manager.get_points_to_defend(player.full_name, week)

		if points_to_remove > 0:
			player.career.atp_points -= points_to_remove
			# Le ranking manager gère déjà la remise à zéro via advance_week()

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
			
			# Délègue au ranking manager
			week_col = f"week_{week}"
			if (player.full_name in self.ranking_manager.atp_points_history.index and 
				week_col in self.ranking_manager.atp_points_history.columns):
				return int(self.ranking_manager.atp_points_history.loc[player.full_name, week_col])
			return 0

		return player.career.atp_points

	def reset_atp_race_points(self):
		"""
		Réinitialise les points ATP de la course pour tous les joueurs.
		"""
		# Délègue au ranking manager
		self.ranking_manager.reset_atp_race()

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

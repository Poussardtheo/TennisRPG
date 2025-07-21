"""
Gestionaire des activité des joueurs
"""

import random
from typing import Dict, List, Set, Optional

from ..utils.helpers import get_gender_agreement
from ..utils.constants import ACTIVITIES

class ActivityManager:
	"""Gestionnaire des activités des joueurs"""

	def execute_training(self, player: 'Player'):
		"""
		Exécute l'entraînement pour le joueur.
		"""
		exp_gained = random.randint(10, 20)
		player.gain_experience(exp_gained)
		player.manage_fatigue("Entrainement")

		if player.is_main_player:
			gender_suffix = get_gender_agreement(player.gender)
			print(f"\n{player.full_name} s'est entraîné{gender_suffix} cette semaine.")

	def execute_rest(self, player: 'Player'):
		"""
		Exécute le repos pour le joueur.
		"""
		player.rest()

	def get_available_activities(self, player: 'Player', available_tournaments: List) -> List[str]:
		"""
		 Obtient la liste des activités disponibles pour un joueur

		Args:
			player: Le joueur pour lequel on récupère les activités
			available_tournaments: Liste des tournois disponibles

		Returns:
            Liste des activités possibles
		"""
		activities = [act for act in ACTIVITIES if act != "Tournoi"]

		if available_tournaments:
			activities = ACTIVITIES.copy()

		return activities


	@staticmethod
	def select_available_players(excluded_player: 'Player', all_players: Dict[str, 'Player']) -> Set['Player']:
		"""
		Sélectionne les joueurs disponibles pour participer à un tournoi, en excluant le joueur principal.

		Args:
			excluded_player: Le joueur principal qui ne doit pas être sélectionné.
			all_players: Dictionnaire des joueurs disponibles.

		Returns:
			Set de joueurs disponibles pour le tournoi.
		"""
		available_players = set(all_players.values())
		available_players.discard(excluded_player)

		return available_players
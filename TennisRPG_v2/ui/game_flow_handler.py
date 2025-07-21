from typing import Dict, List, Optional, Tuple

class GameFlowHandler:
	"""Gestionnaire du flux principal du jeu."""

	def __init__(self, season_manager: 'SeasonManager',
				 activity_manager: 'ActivityManager',
				 atp_points_manager: 'ATPPointsManager',
				 tournament_manager: 'TournamentManager'):
		self.season_manager = season_manager
		self.activity_manager = activity_manager
		self.tournament_manager = tournament_manager
		self.atp_points_manager = atp_points_manager

	def handle_weekly_turn(self, player: 'Player', players: Dict[str, 'Player'],
						   ranking: 'Ranking') -> bool:
		"""
		Gère un tour de jeu hedomadaire

		Args:
            player: Joueur principal
            players: Tous les joueurs
            ranking: Gestionnaire des classements

		 Returns:
            True si le jeu continue, False si le joueur veut quitter
        """
		print(f"\n{self.season_manager.week_info}")

		# Obtenir les tournois de la semaine
		weekly_tournaments  = self.tournament_manager.get_weekly_tournaments(
			self.season_manager.current_week, players
		)

		# Filtrer les tournois éligibles pour le joueur
		eligible_tournaments = self.tournament_manager.get_eligible_tournaments(
			player, weekly_tournaments, ranking
		)

		# Afficher les informations sur les tournois
		self._display_tournament_info(weekly_tournaments, eligible_tournaments)

		# Obtenir les activités disponibles
		available_activities = self.activity_manager.get_available_activities(
			player, eligible_tournaments
		)

		# Demander le choix de l'utilisateur
		chosen_activity = self._get_user_choice(available_activities)

		if chosen_activity.lower() == "q":
			return False

		# Exécuter l'activité choisie
		self._execute_chosen_activity(
			chosen_activity, player, players, ranking,
			eligible_tournaments, weekly_tournaments
		)

		return True


	def _display_tournament_info(self, all_tournaments: List['Tournament'],
								 eligible_tournaments: List['Tournament']):
		"""Affiche les informations sur les tournois de la semaine"""
		if eligible_tournaments and all_tournaments:
			print(f"\nTournois accessibles cette semaine:")
			for tournament in eligible_tournaments:
				print(f"  - {tournament.name} ({tournament.__class__.__name__})")
			print("")
		elif all_tournaments:
			print(f"\nTournois cette semaine:")
			for tournament in all_tournaments:
				print(f"  - {tournament.name} ({tournament.__class__.__name__})")
			print(f"\nAucun tournoi accessible cette semaine\n")
		else:
			print("Pas de tournois cette semaine\n")

	def _get_user_choice(self, available_activities: List[str]) -> str:
		"""Demande le choix de l'utilisateur"""
		for i, activity in enumerate(available_activities, 1):
			print(f"{i}. {activity}")

		while True:
			choice = input(
				f"\nChoisissez votre activité cette semaine (1-{len(available_activities)}) "
				f"ou q pour revenir au menu:\n"
			)

			if choice.lower() == "q":
				return "q"

			if choice.isdigit() and 1 <= int(choice) <= len(available_activities):
				return available_activities[int(choice) - 1]

			print("\nChoix invalide, veuillez réessayer")

	def _execute_chosen_activity(self, activity: str, player: 'Player',
								 players: Dict[str, 'Player'], ranking: 'Ranking',
								 eligible_tournaments: List['Tournament'],
								 all_tournaments: List['Tournament']):
		"""Exécute l'activité choisie par le joueur"""
		if activity == "Entrainement":
			self.activity_manager.execute_training(player)
			self._simulate_other_tournaments(player, players, ranking, all_tournaments)
		elif activity == "Tournoi":
			self._handle_tournament_participation(
				player, players, ranking, eligible_tournaments, all_tournaments
			)
		elif activity == "Repos":
			self.activity_manager.execute_rest(player)
			self._simulate_other_tournaments(player, players, ranking, all_tournaments)

		# Avancer d'une semaine
		self.season_manager.advance_week(ranking, players, self.atp_points_manager)

	def _handle_tournament_participation(self, player: 'Player',
										 players: Dict[str, 'Player'],
										 ranking: 'Ranking',
										 eligible_tournaments: List['Tournament'],
										 all_tournaments: List['Tournament']):
		"""Gère la participation à un tournoi"""
		# Choisir le tournoi si plusieurs options
		chosen_tournament = self._choose_tournament(eligible_tournaments)
		if not chosen_tournament:
			return

		gender_suffix = "e" if player.gender.lower() == 'f' else ""
		print(f"\n{player.first_name} a participé{gender_suffix} au tournoi: {chosen_tournament.name}.")

		# Participer au tournoi choisi et simuler les autres
		self.tournament_manager.participate_in_tournament(
			player, chosen_tournament, players, ranking,
			self.season_manager.current_week, self.atp_points_manager
		)

		# Simuler les autres tournois de la semaine
		other_tournaments = [t for t in all_tournaments if t != chosen_tournament]
		if other_tournaments:
			self._simulate_other_tournaments(player, players, ranking, other_tournaments)

		# Mettre à jour les classements
		ranking.update_all_rankings()

		# Avancer d'une semaine supplémentaire pour les Grand Slams et Masters 1000 à 7 tours
		if self._is_long_tournament(chosen_tournament):
			self.season_manager.advance_week(ranking, players, self.atp_points_manager)

	def _choose_tournament(self, eligible_tournaments: List['Tournament']) -> Optional['Tournament']:
		"""Permet au joueur de choisir son tournoi"""
		if len(eligible_tournaments) == 1:
			return eligible_tournaments[0]

		print("\nTournois disponibles cette semaine:\n")
		for i, tournament in enumerate(eligible_tournaments, 1):
			print(f"{i}. {tournament.name} ({tournament.__class__.__name__})")

		while True:
			choice = input(
				f"\nChoisissez votre tournoi cette semaine (1-{len(eligible_tournaments)}) "
				f"ou 'q' pour revenir au choix d'activité:"
			)

			if choice.lower() == "q":
				return None
			elif choice.isdigit() and 1 <= int(choice) <= len(eligible_tournaments):
				return eligible_tournaments[int(choice) - 1]
			else:
				print("\nChoix invalide, veuillez réessayer")

	def _simulate_other_tournaments(self, excluded_player: 'Player',
									players: Dict[str, 'Player'],
									ranking: 'Ranking',
									tournaments: List['Tournament']):
		"""Simule les tournois auxquels le joueur ne participe pas"""
		available_players = self.activity_manager.select_available_players(
			excluded_player, players
		)

		# Simuler chaque tournoi
		self.tournament_manager.simulate_tournaments_week(
			tournaments, available_players, ranking,
			self.season_manager.current_week, self.atp_points_manager
		)

		# Mettre à jour les classements
		ranking.update_all_rankings()

	@staticmethod
	def _is_long_tournament(tournament: 'Tournament') -> bool:
		"""Vérifie si le tournoi dure plus d'une semaine"""
		# Logique spécifique selon le type de tournoi
		from ..entities.tournament import GrandSlam, Masters1000

		if isinstance(tournament, GrandSlam):
			return True
		elif isinstance(tournament, Masters1000) and hasattr(tournament, 'nb_tours') and tournament.nb_tours == 7:
			return True

		return False


"""
Gestionnaire des activités hebdomadaires - Migration de Calendar.py v1
"""
import random
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

from ..data.tournaments_data import TournamentCategory
from ..entities.player import Player
from ..entities.tournament import Tournament
from ..managers.tournament_manager import TournamentManager
from ..managers.ranking_manager import RankingManager
from ..managers.injury_manager import InjuryManager
from ..utils.constants import ACTIVITIES, TIME_CONSTANTS, BASE_TRAINING_XP
from ..utils.helpers import get_round_display_name


# from ..utils.constants import FATIGUE_VALUES  # TODO: Supprimé - fatigue gérée dans Player


class ActivityResult:
    """Résultat d'une activité"""
    def __init__(self, activity_name: str, success: bool = True, message: str = ""):
        self.activity_name = activity_name
        self.success = success
        self.message = message
        self.fatigue_change = 0
        self.xp_gained = 0


class Activity(ABC):
    """Classe abstraite pour toutes les activités"""
    
    @abstractmethod
    def execute(self, player: Player, injury_manager: 'InjuryManager' = None) -> ActivityResult:
        """Exécute l'activité pour le joueur"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Retourne la description de l'activité"""
        pass


class TrainingActivity(Activity):
    """Activité d'entraînement"""
    
    def execute(self, player: Player, injury_manager: InjuryManager = None) -> ActivityResult:
        # Gain d'expérience (réduit pour équilibrer avec les nouvelles sources d'XP)
        xp_gained = random.randint(BASE_TRAINING_XP["min"], BASE_TRAINING_XP["max"])
        player.gain_experience(xp_gained)
        
        # Gestion de la fatigue - utilisation méthode centralisée
        fatigue_increase = player.manage_fatigue("Entrainement", display=True)
        fatigue_increase -= TIME_CONSTANTS["FATIGUE_NATURAL_RECOVERY"]  # Récupération naturelle de la fatigue

        # Vérification des blessures pendant l'entraînement
        injury = None
        if injury_manager:
            injury = injury_manager.process_activity_injury(player, "Entraînement")

        # Message personnalisé
        gender_suffix = "e" if player.gender.value == "f" else ""
        message = f"{player.full_name} s'est entraîné{gender_suffix} cette semaine."
        
        result = ActivityResult("Entraînement", True, message)
        result.xp_gained = xp_gained
        result.fatigue_change = fatigue_increase
        return result
    
    def get_description(self) -> str:
        return "🏃 Entraînement - Améliore vos compétences (+XP, +Fatigue)"


class RestActivity(Activity):
    """Activité de repos"""
    
    def execute(self, player: Player, injury_manager: InjuryManager = None) -> ActivityResult:
        # Récupération de fatigue - utilisation méthode centralisée
        fatigue_recovery = player.rest()
        
        # Guérison des blessures pendant le repos
        if injury_manager:
            healed_injuries = player.heal_injuries(weeks=1)
        
        # Message personnalisé
        gender_suffix = "e" if player.gender.value == "f" else ""
        current_fatigue = player.physical.fatigue if hasattr(player, 'physical') else 0
        message = f"{player.first_name} s'est reposé{gender_suffix} cette semaine.\n"
        message += f"Niveau de fatigue actuel: {current_fatigue}%"
        
        # Ajout info blessures si applicable
        if player.is_injured():
            message += f"\n{player.get_injury_status_display()}"
        
        result = ActivityResult("Repos", True, message)
        result.fatigue_change = -fatigue_recovery
        return result
    
    def get_description(self) -> str:
        return "😴 Repos - Récupère de la fatigue (-Fatigue)"


class TournamentActivity(Activity):
    """Activité de participation à un tournoi"""
    
    def __init__(self, tournament: Tournament):
        self.tournament = tournament
    
    def execute(self, player: Player, injury_manager: InjuryManager = None) -> ActivityResult:
        # La logique de tournoi sera gérée par le WeeklyActivityManager
        gender_suffix = "e" if player.gender.value == "f" else ""
        message = f"{player.first_name} a participé{gender_suffix} au tournoi: {self.tournament.name}"
        
        return ActivityResult("Tournoi", True, message)
    
    def get_description(self) -> str:
        return f"🎾 {self.tournament.name} ({self.tournament.category.value})"


class WeeklyActivityManager:
    """Gestionnaire des activités hebdomadaires"""
    
    def __init__(self, tournament_manager: TournamentManager, ranking_manager: RankingManager,
                 injury_manager: Optional[InjuryManager] = None, history_manager=None):
        self.tournament_manager = tournament_manager
        self.ranking_manager = ranking_manager
        self.injury_manager = injury_manager or InjuryManager()
        self.history_manager = history_manager
        
        # Activités de base (toujours disponibles)
        self.base_activities = [
            TrainingActivity(),
            RestActivity()
        ]
    
    def get_available_activities(self, player: Player, week: int) -> List[Activity]:
        """Retourne les activités disponibles pour un joueur cette semaine"""
        activities = list(self.base_activities)
        
        # Ajoute les tournois éligibles
        eligible_tournaments = self.tournament_manager.get_tournaments_for_player(
            week, player, self.ranking_manager
        )
        
        for tournament in eligible_tournaments:
            activities.append(TournamentActivity(tournament))
        
        return activities
    
    def display_weekly_activities(self, player: Player, week: int) -> None:
        """Affiche les activités disponibles pour la semaine"""
        print(f"\n📅 SEMAINE {week}")
        print("=" * 40)
        
        # Affiche les tournois de la semaine
        all_tournaments = self.tournament_manager.get_tournaments_for_week(week)
        eligible_tournaments = self.tournament_manager.get_tournaments_for_player(
            week, player, self.ranking_manager
        )
        
        if all_tournaments:
            print("🎾 TOURNOIS CETTE SEMAINE:")
            
            if eligible_tournaments:
                print("\n✅ Tournois accessibles:")
                for tournament in eligible_tournaments:
                    print(f"   • {tournament.name} ({tournament.category.value})")
                
                ineligible = [t for t in all_tournaments if t not in eligible_tournaments]
                if ineligible:
                    print("\n❌ Tournois non accessibles:")
                    for tournament in ineligible:
                        print(f"   • {tournament.name} ({tournament.category.value})")
            else:
                print("\n❌ Aucun tournoi accessible cette semaine")
                for tournament in all_tournaments:
                    print(f"   • {tournament.name} ({tournament.category.value})")
        else:
            print("📅 Aucun tournoi cette semaine")
        
        print("\n" + "=" * 40)
        
        # Affiche l'état de santé si pas de blessure grave
        if not player.is_injured():
            print(f"💚 STATUT MÉDICAL: {player.get_injury_status_display()}")
        else:
            print(f"\n🏥 STATUT MÉDICAL:")
            print(player.get_injury_status_display())
            print("\n⚠️  Repos obligatoire en raison de blessure(s)!")
    
    def choose_activity(self, player: Player, week: int) -> Optional[Activity]:
        """Interface de choix d'activité"""
        activities = self.get_available_activities(player, week)
        
        # Si le joueur est blessé, on arrête l'affichage ici car seul le repos est disponible
        if player.is_injured():
            print("\n🎯 ACTIVITÉ OBLIGATOIRE:")
            print("-" * 25)
            print("1: 😴 Repos - Récupère de la fatigue et guérit les blessures")
            # Trouve et retourne l'activité de repos
            for activity in activities:
                if isinstance(activity, RestActivity):
                    return activity
            # Si pas trouvée, crée une nouvelle activité de repos
            return RestActivity()
        
        print("\n🎯 ACTIVITÉS DISPONIBLES:")
        print("-" * 25)
        
        for i, activity in enumerate(activities, 1):
            print(f"{i}. {activity.get_description()}")
        
        while True:
            choice = input(f"\n🎮 Choisissez votre activité (1-{len(activities)}) ou 'q' pour revenir au menu: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            if choice.isdigit() and 1 <= int(choice) <= len(activities):
                return activities[int(choice) - 1]
            else:
                print("❌ Choix invalide, veuillez réessayer")
    
    def execute_activity(self, player: Player, activity: Activity, week: int, 
                        all_players: Dict[str, Player], current_year: int, atp_points_manager=None, injury_manager=None) -> ActivityResult:
        """Exécute une activité choisie"""
        
        # Utilise l'injury_manager passé en paramètre ou celui par défaut
        active_injury_manager = injury_manager or self.injury_manager
        
        if isinstance(activity, TournamentActivity):
            return self._execute_tournament_activity(player, activity, week, all_players, current_year, atp_points_manager, active_injury_manager)
        else:

            # Exécute l'activité de base
            result = activity.execute(player, active_injury_manager)

            # Simule les autres tournois de la semaine (sans le joueur principal)
            self._simulate_other_tournaments(player, week, all_players, current_year, atp_points_manager, active_injury_manager)

            return result
    
    def _execute_tournament_activity(self, player: Player, tournament_activity: TournamentActivity,
                                   week: int, all_players: Dict[str, Player], current_year: int, atp_points_manager=None, injury_manager=None) -> ActivityResult:
        """Exécute la participation à un tournoi"""
        tournament = tournament_activity.tournament
        
        # Sélectionne les autres participants
        available_players = {name: p for name, p in all_players.items() 
                           if p != player and p.gender == player.gender}
        
        participants = self.tournament_manager.select_players_for_tournament(
            tournament, available_players, self.ranking_manager
        )

        # Vérifie si le joueur principal est déjà dans les participants
        # Utilise une comparaison robuste basée sur les attributs uniques
        player_already_in = any(
            p.first_name == player.first_name and 
            p.last_name == player.last_name and 
            p.country == player.country 
            for p in participants
        )
        
        if player_already_in:
            # Le joueur est déjà qualifié automatiquement, pas besoin de l'ajouter
            pass
        else:
            # Si le tournoi n'est pas plein, ajoute simplement le joueur
            if len(participants) < tournament.num_players:
                participants.append(player)
            else:
                # Todo: améliorer la logique de remplacement
                # Le tournoi est plein, remplace le joueur avec le classement le plus proche
                main_player_rank = self.ranking_manager.get_player_rank(player) or 999999
                
                # Trouve le joueur le plus proche en classement pour un échange équitable
                closest_player = None
                closest_diff = float('inf')
                
                for participant in participants:
                    participant_rank = self.ranking_manager.get_player_rank(participant) or 999999
                    rank_diff = abs(main_player_rank - participant_rank)
                    if rank_diff < closest_diff:
                        closest_diff = rank_diff
                        closest_player = participant
                
                # Remplace le joueur le plus proche par le joueur principal
                if closest_player:
                    participants.remove(closest_player)
                    participants.append(player)
        
        # Nettoie le tournoi et ajoute les participants
        tournament.participants.clear()
        tournament.match_results.clear() 
        tournament.eliminated_players.clear()
        
        for participant in participants:
            tournament.add_participant(participant)
        
        # Joue le tournoi (verbose car joueur principal présent)
        tournament_result = tournament.play_tournament(verbose=True, atp_points_manager=atp_points_manager, week=week, injury_manager=injury_manager)
        
        # Enregistre dans l'historique si disponible
        if self.history_manager and tournament_result:
            self.history_manager.record_tournament_result(tournament_result, current_year, week)
        
        # Simule les autres tournois de la semaine
        other_tournaments = [t for t in self.tournament_manager.get_tournaments_for_week(week) 
                           if t != tournament]
        self._simulate_tournaments_list(other_tournaments, all_players, current_year, exclude_players=participants, atp_points_manager=atp_points_manager, week=week)
        
        # Met à jour les classements
        self.ranking_manager.update_weekly_rankings()
        
        # Crée le résultat d'activité
        result = tournament_activity.execute(player)
        
        # Ajoute des informations sur le résultat du tournoi
        if tournament_result.winner == player:
            result.message += f"\n🏆 FÉLICITATIONS! Vous avez remporté {tournament.name}!"
        else:
            elimination_round = tournament.eliminated_players.get(player, "Participation")
            formatted_round = get_round_display_name(elimination_round)
            result.message += f"\n📊 Éliminé: {formatted_round}"
        
        return result
    
    def _choose_specific_tournament(self, player: Player, week: int) -> Optional[Tournament]:
        """Permet de choisir un tournoi spécifique s'il y en a plusieurs"""
        eligible_tournaments = self.tournament_manager.get_tournaments_for_player(
            week, player, self.ranking_manager
        )
        
        if len(eligible_tournaments) <= 1:
            return eligible_tournaments[0] if eligible_tournaments else None
        
        print("\n🎾 CHOIX DU TOURNOI:")
        print("-" * 20)
        
        for i, tournament in enumerate(eligible_tournaments, 1):
            print(f"{i}. {tournament.name} ({tournament.category.value})")
        
        while True:
            choice = input(f"\nChoisissez votre tournoi (1-{len(eligible_tournaments)}) ou 'q' pour annuler: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            if choice.isdigit() and 1 <= int(choice) <= len(eligible_tournaments):
                return eligible_tournaments[int(choice) - 1]
            else:
                print("❌ Choix invalide, veuillez réessayer")
    
    def _simulate_other_tournaments(self, player: Player, week: int, all_players: Dict[str, Player], current_year: int, atp_points_manager=None, injury_manager=None) -> None:
        """Simule les autres tournois de la semaine (sans le joueur principal)"""
        tournaments = self.tournament_manager.get_tournaments_for_week(week)

        available_players = {name: p for name, p in all_players.items() 
                           if p != player and p.gender == player.gender}

        self._simulate_tournaments_list(tournaments, available_players, current_year, atp_points_manager=atp_points_manager, week=week, injury_manager=injury_manager)

        # Met à jour les classements
        self.ranking_manager.update_weekly_rankings()

    def _simulate_tournaments_list(self, tournaments: List[Tournament], 
                                 available_players: Dict[str, Player], current_year: int,
                                 exclude_players: List[Player] = None, atp_points_manager=None, week: int = None, injury_manager=None) -> None:
        """Simule une liste de tournois"""
        if exclude_players is None:
            exclude_players = []
        
        # Retire les joueurs exclus du pool disponible
        available_pool = {name: p for name, p in available_players.items() 
                         if p not in exclude_players}
        
        # Trie par ordre d'importance décroissant (plus prestigieux d'abord)
        sorted_tournaments = sorted(tournaments, 
                                  key=lambda t: t.tournament_importance, reverse=True)

        for tournament in sorted_tournaments:

            participants = self.tournament_manager.select_players_for_tournament(
                tournament, available_pool, self.ranking_manager
            )

            if len(participants) >= 4:  # Minimum pour un tournoi
                # Nettoie le tournoi
                tournament.participants.clear()
                tournament.match_results.clear()
                tournament.eliminated_players.clear()

                # Ajoute les participants
                for participant in participants:
                    tournament.add_participant(participant)


                # Joue le tournoi en mode silencieux
                result = tournament.play_tournament(verbose=False, atp_points_manager=atp_points_manager, week=week, injury_manager=injury_manager or self.injury_manager)
                
                # Enregistre dans l'historique si disponible
                if self.history_manager and result:
                    self.history_manager.record_tournament_result(result, current_year, week)

                # Retire les participants du pool disponible
                for participant in participants:
                    if participant.full_name in available_pool:
                        del available_pool[participant.full_name]
        
        # Gère les joueurs qui ne participent à aucun tournoi
        self._handle_non_participating_players(available_pool)
    
    def _handle_non_participating_players(self, non_participating_players: Dict[str, Player]) -> None:
        """
        Gère les joueurs qui ne participent à aucun tournoi cette semaine
        50% de chance de se reposer, 50% de chance de s'entraîner
        
        Args:
            non_participating_players: Dictionnaire des joueurs qui ne participent pas
        """
        for player in non_participating_players.values():
            # 50% de chance de se reposer, 50% de chance de s'entraîner
            if random.random() < 0.5:
                # Repos
                rest_activity = RestActivity()
                rest_activity.execute(player)
            else:
                # Entraînement
                training_activity = TrainingActivity()
                training_activity.execute(player)

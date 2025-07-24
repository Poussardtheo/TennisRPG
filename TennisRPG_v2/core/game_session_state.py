"""
Game Session State - Gestion de l'état du jeu
Extrait de GameSession pour une meilleure séparation des responsabilités
"""
import time
from typing import Dict, Optional
from ..entities.player import Player
from ..managers.player_generator import PlayerGenerator
from ..managers.tournament_manager import TournamentManager
from ..managers.ranking_manager import RankingManager
from ..managers.weekly_activity_manager import WeeklyActivityManager
from ..managers.atp_points_manager import ATPPointsManager
from ..managers.retirement_manager import RetirementManager
from ..managers.injury_manager import InjuryManager
from ..utils.constants import TIME_CONSTANTS
from .save_manager import SaveManager, GameState


class GameSessionState:
    """Gère l'état du jeu et ses modifications"""
    
    def __init__(self):
        # État principal du jeu
        self.main_player: Optional[Player] = None
        self.all_players: Dict[str, Player] = {}
        self.current_week: int = 1
        self.current_year: int = TIME_CONSTANTS["GAME_START_YEAR"]
        
        # Managers - initialisés progressivement
        self.tournament_manager = TournamentManager()
        self.ranking_manager: Optional[RankingManager] = None
        self.player_generator = PlayerGenerator()
        self.activity_manager: Optional[WeeklyActivityManager] = None
        self.atp_points_manager: Optional[ATPPointsManager] = None
        self.retirement_manager = RetirementManager(self.player_generator)
        self.injury_manager = InjuryManager()
        self.save_manager = SaveManager()
        
        # État de session
        self.session_start_time: Optional[float] = None
        self.is_preliminary_complete: bool = False
        self.game_running: bool = True
        
    def set_main_player(self, player: Player) -> None:
        """Définit le joueur principal"""
        self.main_player = player
        
    def add_player(self, player: Player) -> None:
        """Ajoute un joueur au pool"""
        self.all_players[player.full_name] = player
        
    def add_players(self, players: Dict[str, Player]) -> None:
        """Ajoute plusieurs joueurs au pool"""
        self.all_players.update(players)
        
    def remove_player(self, player_name: str) -> bool:
        """Retire un joueur du pool"""
        if player_name in self.all_players:
            del self.all_players[player_name]
            return True
        return False
        
    def get_player_count(self) -> int:
        """Retourne le nombre de joueurs"""
        return len(self.all_players)
        
    def start_session_timing(self) -> None:
        """Démarre le chronométrage de la session"""
        self.session_start_time = time.time()
        
    def get_session_duration(self) -> float:
        """Retourne la durée de la session en heures"""
        if self.session_start_time is None:
            return 0.0
        return (time.time() - self.session_start_time) / 3600
        
    def advance_week(self) -> bool:
        """Avance d'une semaine, retourne True si nouvelle année"""
        self.current_week += 1
        
        # Retire les points ATP expirés avant de passer à la semaine suivante
        if self.ranking_manager:
            # Synchronise avec la semaine qu'on vient d'avancer
            self.ranking_manager.current_week = self.current_week
            # Retire les points qui expirent cette semaine
            for player_name, player in self.ranking_manager.players.items():
                points_to_lose = self.ranking_manager.get_points_to_defend(player_name, self.current_week)
                player.career.atp_points = max(0,player.career.atp_points - points_to_lose)
            # Remet à zéro la colonne de la nouvelle semaine
            week_col = f"week_{self.current_week}"
            if week_col in self.ranking_manager.atp_points_history.columns:
                self.ranking_manager.atp_points_history[week_col] = 0
        
        if self.current_week > TIME_CONSTANTS["WEEKS_PER_YEAR"]:
            self.current_week = 1
            self.current_year += 1
            return True  # Nouvelle année
        return False
        
    def set_preliminary_complete(self) -> None:
        """Marque la simulation préliminaire comme terminée"""
        self.is_preliminary_complete = True
        
    def stop_game(self) -> None:
        """Arrête le jeu"""
        self.game_running = False
        
    def initialize_ranking_manager(self) -> None:
        """Initialise le ranking manager avec tous les joueurs"""
        if self.all_players:
            self.ranking_manager = RankingManager(list(self.all_players.values()))
            
    def initialize_atp_points_manager(self) -> None:
        """Initialise l'ATP points manager"""
        if self.ranking_manager:
            self.atp_points_manager = ATPPointsManager(self.all_players, self.ranking_manager)
            
    def initialize_activity_manager(self) -> None:
        """Initialise l'activity manager"""
        if self.ranking_manager:
            self.activity_manager = WeeklyActivityManager(
                self.tournament_manager, self.ranking_manager, self.injury_manager
            )
            
    def add_main_player_to_managers(self) -> None:
        """Ajoute le joueur principal aux managers après simulation préliminaire"""
        if self.main_player:
            # Ajoute au pool principal
            self.all_players[self.main_player.full_name] = self.main_player
            
            # Ajoute aux managers
            if self.atp_points_manager:
                self.atp_points_manager.add_player(self.main_player)
            if self.ranking_manager:
                self.ranking_manager.add_player(self.main_player)
                self.ranking_manager.reset_atp_race()
                
    def reset_time_to_start(self) -> None:
        """Remet le temps au début du jeu principal"""
        self.current_week = 1
        self.current_year = TIME_CONSTANTS["GAME_START_YEAR"]
        
    def age_main_player(self) -> None:
        """Vieillit le joueur principal d'un an"""
        if self.main_player and hasattr(self.main_player.career, 'age'):
            self.main_player.career.age += 1
            
    def apply_natural_fatigue_recovery(self) -> None:
        """Applique la récupération naturelle de fatigue au joueur principal"""
        if self.main_player:
            self.main_player.recover_fatigue(TIME_CONSTANTS["FATIGUE_NATURAL_RECOVERY"])
            
    def apply_natural_fatigue_recovery_all(self) -> None:
        """Applique la récupération naturelle de fatigue à tous les joueurs"""
        for player in self.all_players.values():
            player.recover_fatigue(TIME_CONSTANTS["FATIGUE_NATURAL_RECOVERY"])
            
    def create_game_state_for_save(self) -> GameState:
        """Crée un objet GameState pour la sauvegarde"""
        game_state = GameState()
        game_state.main_player = self.main_player
        game_state.all_players = self.all_players
        game_state.current_week = self.current_week
        game_state.current_year = self.current_year
        game_state.is_preliminary_complete = self.is_preliminary_complete
        game_state.retirement_log = self.retirement_manager.retirement_log if self.retirement_manager else []
        
        # Calcule le temps de jeu
        if self.session_start_time:
            game_state.playtime_hours = self.get_session_duration()
            
        return game_state
        
    def load_from_game_state(self, game_state: GameState) -> bool:
        """Charge l'état depuis un objet GameState"""
        try:
            self.main_player = game_state.main_player
            self.all_players = game_state.all_players
            self.current_week = game_state.current_week
            self.current_year = game_state.current_year
            self.is_preliminary_complete = game_state.is_preliminary_complete
            
            # Recrée les managers avec les données chargées
            if self.all_players:
                self.initialize_ranking_manager()
                self.initialize_atp_points_manager()
                self.initialize_activity_manager()
                
                # Restaure le retirement_log
                if hasattr(game_state, 'retirement_log'):
                    self.retirement_manager.retirement_log = game_state.retirement_log
                    
            # Remet à jour le temps de début de session
            self.session_start_time = time.time()
            
            return True
        except Exception as e:
            print(f"Erreur lors du chargement de l'état: {e}")
            return False
            
    def save_game(self, filename: str) -> bool:
        """Sauvegarde le jeu"""
        try:
            game_state = self.create_game_state_for_save()
            return self.save_manager.save_game(game_state, filename)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
            
    def load_game(self, filename: str) -> bool:
        """Charge une sauvegarde"""
        try:
            game_state = self.save_manager.load_game(filename)
            if game_state:
                return self.load_from_game_state(game_state)
            return False
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return False
            
    def get_save_files(self):
        """Retourne la liste des fichiers de sauvegarde"""
        return self.save_manager.list_saves()
        
    def get_save_by_index(self, index: int):
        """Retourne le nom de fichier à l'index donné"""
        return self.save_manager.get_save_by_index(index)
        
    def display_saves_menu(self):
        """Affiche le menu des sauvegardes"""
        self.save_manager.display_saves_menu()
        
    def reset_atp_race(self) -> None:
        """Remet à zéro l'ATP Race en début d'année"""
        if self.ranking_manager:
            self.ranking_manager.reset_atp_race()
            
    def update_weekly_rankings(self) -> None:
        """Met à jour les classements hebdomadaires"""
        if self.ranking_manager:
            self.ranking_manager.update_weekly_rankings()
            
    def get_players_by_age_threshold(self, min_age: int) -> list:
        """Retourne les joueurs au-dessus d'un âge donné"""
        return [p for p in self.all_players.values() 
                if hasattr(p.career, 'age') and p.career.age >= min_age]
        
    def process_retirements(self) -> tuple:
        """Traite les retraites et retourne (retraités, nouveaux)"""
        if not self.retirement_manager or not self.ranking_manager:
            return [], []
            
        retired_players, new_players = self.retirement_manager.process_end_of_season_retirements(
            self.all_players, self.ranking_manager, self.current_year - 1, 
            self.main_player.gender if self.main_player else None
        )
        
        # Met à jour les classements si de nouveaux joueurs ont été ajoutés
        if new_players:
            for new_player in new_players:
                self.ranking_manager.add_player(new_player)
                
        return retired_players, new_players
        
    def get_retirement_stats(self, year: int):
        """Retourne les statistiques de retraite pour une année"""
        if self.retirement_manager:
            return self.retirement_manager.get_retirement_stats(year)
        return None
        
    def is_managers_initialized(self) -> bool:
        """Vérifie si tous les managers nécessaires sont initialisés"""
        return (self.ranking_manager is not None and 
                self.activity_manager is not None and 
                self.atp_points_manager is not None)
                
    def get_state_summary(self) -> dict:
        """Retourne un résumé de l'état actuel"""
        return {
            'week': self.current_week,
            'year': self.current_year,
            'player_count': len(self.all_players),
            'main_player': self.main_player.full_name if self.main_player else None,
            'preliminary_complete': self.is_preliminary_complete,
            'game_running': self.game_running,
            'managers_initialized': self.is_managers_initialized(),
            'session_duration_hours': self.get_session_duration()
        }
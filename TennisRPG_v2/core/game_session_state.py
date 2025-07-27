"""
Game Session State - Gestion de l'état du jeu
Extrait de GameSession pour une meilleure séparation des responsabilités
"""
import time
from typing import Dict, Optional, Any
from ..entities.player import Player
from ..managers.history_manager import HistoryManager
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
        # Use enhanced save manager for better performance
        self.save_manager = SaveManager()
        
        # État de session
        self.session_start_time: Optional[float] = None
        self.is_preliminary_complete: bool = False
        self.game_running: bool = True
        
        # État de sauvegarde persistant pour l'historique
        self.game_state: Optional[GameState] = GameState()

    def reset_for_new_game(self):
        """Remet à zéro tous les états pour une nouvelle partie"""
        # Remet à zéro le générateur de joueurs
        self.player_generator.reset_generated_names()
        
        # Recrée un GameState propre
        self.game_state = GameState()
        
        # Remet à zéro les collections de joueurs
        self.all_players.clear()
        self.main_player = None
        
        # Remet à zéro les managers qui pourraient conserver des données
        self.ranking_manager = None
        self.activity_manager = None
        self.atp_points_manager = None
        
        # Recrée le retirement manager avec un générateur propre
        self.retirement_manager = RetirementManager(self.player_generator)
        
        # Remet les dates au début
        self.current_week = 1
        self.current_year = TIME_CONSTANTS["GAME_START_YEAR"]
        self.is_preliminary_complete = False
        
    def set_main_player(self, player: Player) -> None:
        """Définit le joueur principal"""
        self.main_player = player
        if self.game_state:
            self.game_state.main_player = player
        
    def add_player(self, player: Player) -> None:
        """Ajoute un joueur au pool"""
        self.all_players[player.full_name] = player
        if self.game_state:
            self.game_state.all_players[player.full_name] = player
        
    def add_players(self, players: Dict[str, Player]) -> None:
        """Ajoute plusieurs joueurs au pool"""
        self.all_players.update(players)
        if self.game_state:
            self.game_state.all_players.update(players)
        
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
        # Stocke la semaine précédente pour détecter le changement d'année
        previous_week = self.current_week
        
        # Avance d'abord la semaine dans ranking_manager (qui gère l'expiration des points ATP)
        if self.ranking_manager:
            # CORRECTION: Synchronise d'abord ranking_manager avec self.current_week
            self.ranking_manager.current_week = self.current_week
            self.ranking_manager.advance_week()
            # Puis synchronise la semaine courante
            self.current_week = self.ranking_manager.current_week
        else:
            self.current_week += 1
            if self.current_week > TIME_CONSTANTS["WEEKS_PER_YEAR"]:
                self.current_week = 1
        
        # Vérifie si on change d'année
        # Si on passe de la semaine 52 à la semaine 1, c'est une nouvelle année
        if previous_week == TIME_CONSTANTS["WEEKS_PER_YEAR"] and self.current_week == 1:
            self.current_year += 1
            new_year = True
        else:
            new_year = False
        
        # Synchronise avec game_state
        if self.game_state:
            self.game_state.current_week = self.current_week
            self.game_state.current_year = self.current_year
            
        return new_year
        
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
                self.tournament_manager, self.ranking_manager, self.injury_manager, self.game_state.history_manager
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
        
        # IMPORTANT: Synchronise aussi le ranking_manager pour éviter les désynchronisations
        if self.ranking_manager:
            self.ranking_manager.current_week = 1
        
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
            
            
    def save_game(self, filename: str, save_name: str = None) -> bool:
        """Sauvegarde le jeu avec le système optimisé"""
        try:
            if self._can_use_enhanced_save():
                save_filename = self.save_manager.save_game_enhanced(
                    main_player=self.main_player,
                    all_players=self.all_players,
                    history_manager=self.game_state.history_manager if self.game_state else HistoryManager(),
                    current_week=self.current_week,
                    current_year=self.current_year,
                    save_name=save_name,
                    playtime_hours=self.get_session_duration(),
                    is_preliminary_complete=self.is_preliminary_complete,
                    retirement_log=self.retirement_manager.retirement_log if self.retirement_manager else []
                )
                return True
            else:
                print("Erreur: Impossible de sauvegarder - joueur principal manquant")
                return False
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def _can_use_enhanced_save(self) -> bool:
        """Vérifie si le système de sauvegarde optimisé peut être utilisé"""
        return (self.main_player is not None and 
                self.all_players and 
                self.game_state is not None and
                self.game_state.history_manager is not None)
            
    def load_game(self, filename: str) -> bool:
        """Charge une sauvegarde (système optimisé ou classique)"""
        try:
            # Détermine s'il s'agit d'un nom de dossier (nouveau système) ou d'un fichier (ancien)
            # Chargement avec le système optimisé uniquement
            enhanced_data = self.save_manager.load_game_enhanced(filename)
            
            if enhanced_data:
                return self._load_from_enhanced_data(enhanced_data)
            else:
                print(f"❌ Impossible de charger la sauvegarde: {filename}")
                return False
                
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return False
    
    def _load_from_enhanced_data(self, enhanced_data: Dict) -> bool:
        """Charge l'état depuis les données du système optimisé"""
        try:
            self.main_player = enhanced_data['main_player']
            
            # Vérification et conversion des joueurs en objets Player si nécessaire
            self.all_players = {}
            for name, player in enhanced_data['all_players'].items():
                if isinstance(player, dict):
                    print(f"⚠️ Conversion du joueur {name} depuis dictionnaire")
                    self.all_players[name] = Player.from_dict(player)
                else:
                    self.all_players[name] = player
            
            # Reconstruit l'état du jeu
            self.game_state = GameState()
            self.game_state.main_player = self.main_player
            self.game_state.all_players = self.all_players
            self.game_state.history_manager = enhanced_data['history_manager']
            
            # Met à jour les métadonnées
            metadata = enhanced_data.get('metadata', {})
            self.current_week = metadata.get('current_week', 1)
            self.current_year = metadata.get('current_year', 2023)
            self.is_preliminary_complete = metadata.get('is_preliminary_complete', False)
            
            # Synchronise avec game_state
            self.game_state.current_week = self.current_week
            self.game_state.current_year = self.current_year
            self.game_state.is_preliminary_complete = self.is_preliminary_complete
            
            # Restaure les données de retraite si disponibles
            if 'retirement_log' in metadata:
                self.retirement_manager.retirement_log = metadata['retirement_log']
                self.game_state.retirement_log = metadata['retirement_log']
            
            # Recrée les managers avec les données chargées
            if self.all_players:
                self.initialize_ranking_manager()
                self.initialize_atp_points_manager()
                self.initialize_activity_manager()
            
            # Remet à jour le temps de début de session
            self.session_start_time = time.time()
            
            print(f"Chargement optimisé réussi!")
            return True
            
        except Exception as e:
            print(f"Erreur lors du chargement optimisé: {e}")
            return False
            
    def get_save_files(self):
        """Retourne la liste des fichiers de sauvegarde du système optimisé"""
        enhanced_saves = self.save_manager.list_enhanced_saves()
        
        # Marque toutes les sauvegardes comme enhanced
        for save in enhanced_saves:
            save['save_type'] = 'enhanced'
        
        # Trie par date de sauvegarde
        enhanced_saves.sort(key=lambda x: x.get("save_date", ""), reverse=True)
        return enhanced_saves
    
    def display_saves_menu(self) -> None:
        """Affiche le menu des sauvegardes disponibles"""
        saves = self.get_save_files()
        
        if not saves:
            print("\n📁 Aucune sauvegarde trouvée.")
            return
        
        print("\n📁 SAUVEGARDES DISPONIBLES")
        print("=" * 60)
        
        for i, save in enumerate(saves, 1):
            save_type = save.get('save_type', 'unknown')
            
            if save_type == 'enhanced':
                # Utilise le nom personnalisé pour les sauvegardes optimisées
                name = save.get('save_name', save.get('directory_name', 'Sans nom'))
                identifier = name
            else:
                # Utilise le nom de fichier pour les sauvegardes classiques
                identifier = save.get('filename', 'Sans nom')
                
            # Informations sur la sauvegarde
            week = save.get('current_week', '?')
            year = save.get('current_year', '?')
            playtime = save.get('playtime', 0.0)
            
            print(f"{i:2}. {identifier}")
            print(f"    Semaine {week}, {year} - {playtime:.1f}h de jeu")
        
        print("=" * 60)
    
    def get_save_by_index(self, index: int) -> Optional[str]:
        """Récupère le nom de sauvegarde par index (1-basé)"""
        saves = self.get_save_files()
        
        if 1 <= index <= len(saves):
            save = saves[index - 1]
            save_type = save.get('save_type', 'unknown')
            
            if save_type == 'enhanced':
                # Retourne le nom du dossier pour les sauvegardes optimisées
                return save.get('directory_name')
            else:
                # Retourne le nom de fichier pour les sauvegardes classiques
                return save.get('filename')
        
        return None
        
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
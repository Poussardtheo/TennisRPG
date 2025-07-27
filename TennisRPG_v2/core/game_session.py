"""
Session de jeu principale - Version refactorisée avec séparation des responsabilités
Maintient la compatibilité avec le reste du codebase tout en utilisant les nouveaux composants
"""
from typing import Dict, Optional

from .game_session_ui import GameSessionUI
from .game_session_state import GameSessionState
from .game_session_controller import GameSessionController


class GameSession:
    """
    Gestionnaire principal de session de jeu - Version refactorisée
    Délègue les responsabilités aux composants spécialisés tout en 
    maintenant la compatibilité avec l'interface existante
    """
    
    def __init__(self):
        # Composants spécialisés
        self.ui = GameSessionUI()
        self.state = GameSessionState()
        self.controller = GameSessionController(self.ui, self.state)
        
    # === Interface publique principale ===
    
    def start_new_game(self) -> None:
        """Démarre une nouvelle partie"""
        self.controller.start_new_game()
        
    def load_game_from_entry(self) -> bool:
        """Charge une partie depuis le menu d'entrée"""
        return self.controller.load_game_from_entry()
        
    def _main_game_loop(self) -> None:
        """Boucle principale du jeu - pour compatibilité avec le code existant"""
        self.controller._main_game_loop()
        
    # === Propriétés pour compatibilité avec le code existant ===
    
    @property
    def main_player(self):
        """Joueur principal"""
        return self.state.main_player
        
    @main_player.setter
    def main_player(self, value):
        """Définit le joueur principal"""
        self.state.main_player = value
        
    @property
    def all_players(self) -> Dict:
        """Tous les joueurs"""
        return self.state.all_players
        
    @all_players.setter
    def all_players(self, value: Dict):
        """Définit tous les joueurs"""
        self.state.all_players = value
        
    @property
    def current_week(self) -> int:
        """Semaine actuelle"""
        return self.state.current_week
        
    @current_week.setter
    def current_week(self, value: int):
        """Définit la semaine actuelle"""
        self.state.current_week = value
        
    @property
    def current_year(self) -> int:
        """Année actuelle"""
        return self.state.current_year
        
    @current_year.setter
    def current_year(self, value: int):
        """Définit l'année actuelle"""
        self.state.current_year = value
        
    @property
    def is_preliminary_complete(self) -> bool:
        """État de la simulation préliminaire"""
        return self.state.is_preliminary_complete
        
    @is_preliminary_complete.setter
    def is_preliminary_complete(self, value: bool):
        """Définit l'état de la simulation préliminaire"""
        self.state.is_preliminary_complete = value
        
    @property
    def game_running(self) -> bool:
        """État du jeu"""
        return self.state.game_running
        
    @game_running.setter
    def game_running(self, value: bool):
        """Définit l'état du jeu"""
        self.state.game_running = value
        
    @property
    def session_start_time(self):
        """Temps de début de session"""
        return self.state.session_start_time
        
    @session_start_time.setter
    def session_start_time(self, value):
        """Définit le temps de début de session"""
        self.state.session_start_time = value
        
    # === Accès aux managers pour compatibilité ===
    
    @property
    def tournament_manager(self):
        """Tournament manager"""
        return self.state.tournament_manager
        
    @property
    def ranking_manager(self):
        """Ranking manager"""
        return self.state.ranking_manager
        
    @property
    def player_generator(self):
        """Player generator"""
        return self.state.player_generator
        
    @property
    def activity_manager(self):
        """Activity manager"""
        return self.state.activity_manager
        
    @property
    def atp_points_manager(self):
        """ATP points manager"""
        return self.state.atp_points_manager
        
    @property
    def retirement_manager(self):
        """Retirement manager"""
        return self.state.retirement_manager
    
    @property
    def save_manager(self):
        """Save manager"""
        return self.state.save_manager
        
        
    # === Méthodes déléguées pour compatibilité ===
    
    def _load_game(self, filename: str) -> bool:
        """Charge une sauvegarde - pour compatibilité"""
        return self.controller._load_game(filename)
        
    def _save_game(self) -> None:
        """Sauvegarde le jeu - pour compatibilité"""
        self.controller._save_game()
        
    def _advance_week(self, weeks: int = 1) -> None:
        """Avance d'une ou plusieurs semaines - pour compatibilité"""
        self.controller._advance_week(weeks)
        
    def _display_weekly_header(self) -> None:
        """Affiche l'en-tête hebdomadaire - pour compatibilité"""
        self.ui.display_weekly_header(
            self.state.current_week,
            self.state.current_year,
            self.state.main_player,
            self.state.ranking_manager
        )
        
    def _display_main_menu(self) -> None:
        """Affiche le menu principal - pour compatibilité"""
        self.ui.display_main_menu()
        
    def _get_user_input(self) -> str:
        """Récupère l'input utilisateur - pour compatibilité"""
        return self.ui.get_user_input()
        
    def _handle_user_action(self, action: str) -> None:
        """Traite l'action utilisateur - pour compatibilité"""
        self.controller._handle_user_action(action)
        
    def _quit_game(self) -> None:
        """Quitte le jeu - pour compatibilité"""
        self.controller._quit_game()
        
    def _display_rankings(self) -> None:
        """Affiche les classements - pour compatibilité"""
        self.controller._display_rankings()
        
    def _display_atp_points_to_defend(self) -> None:
        """Affiche les points ATP à défendre - pour compatibilité"""
        self.controller._display_atp_points_to_defend()
        
    def _display_player_id_card(self) -> None:
        """Affiche la carte d'identité - pour compatibilité"""
        self.controller._display_player_id_card()
        
    def _assign_attribute_points(self) -> None:
        """Attribution des points d'attributs - pour compatibilité"""
        self.controller._assign_attribute_points()
        
    def _load_game_menu(self) -> None:
        """Menu de chargement - pour compatibilité"""
        self.controller._load_game_menu()
        
    def _display_recent_retirements(self) -> None:
        """Affiche les retraites récentes - pour compatibilité"""
        self.controller._display_recent_retirements()
        
    def _start_weekly_activities(self) -> None:
        """Démarre les activités hebdomadaires - pour compatibilité"""
        self.controller._start_weekly_activities()
        
    # === Méthodes utilitaires ===
    
    def get_state_summary(self) -> dict:
        """Retourne un résumé de l'état du jeu"""
        return self.state.get_state_summary()
        
    def is_managers_initialized(self) -> bool:
        """Vérifie si les managers sont initialisés"""
        return self.state.is_managers_initialized()


# === Fonctions globales pour compatibilité ===

def display_entry_menu():
    """Affiche le menu d'entrée du jeu"""
    print("="*60)
    print("🎾 BIENVENUE DANS TENNISRPG v2!")
    print("="*60)
    print("\n📋 QUE SOUHAITEZ-VOUS FAIRE ?")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🆕 [1] Commencer une nouvelle partie")
    print("📂 [2] Reprendre une partie existante") 
    print("❌ [3] Quitter")


def main():
    """Point d'entrée principal"""
    try:
        while True:
            display_entry_menu()
            
            choice = input("\n🎯 Votre choix (1-3) : ").strip()
            
            if choice == '1':
                # Nouvelle partie - Crée une instance complètement isolée
                game = GameSession()
                game.start_new_game()
                # Après une partie, retourne au menu principal
                # Ne pas break ici pour permettre de rejouer
                
            elif choice == '2':
                # Charger une partie - Crée une instance complètement isolée
                game = GameSession()
                if game.load_game_from_entry():
                    game._main_game_loop()
                else:
                    continue
                # Après une partie, retourne au menu principal
                # Ne pas break ici pour permettre de rejouer
                
            elif choice == '3':
                print("\n👋 À bientôt !")
                break
            else:
                print("❌ Choix invalide. Utilisez 1, 2 ou 3.")
                
    except KeyboardInterrupt:
        print("\n\n👋 Jeu interrompu par l'utilisateur. À bientôt!")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("🔧 Veuillez signaler ce problème.")


if __name__ == "__main__":
    main()
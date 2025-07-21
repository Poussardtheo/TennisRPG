"""
Session de jeu principale - Cœur du gameplay TennisRPG v2
"""
import time
import threading
from typing import Dict, List, Optional

from ..entities.player import Player, Gender
from ..entities.ranking import Ranking, RankingType  
from ..managers.player_generator import PlayerGenerator
from ..managers.tournament_manager import TournamentManager
from ..managers.ranking_manager import RankingManager
from ..managers.weekly_activity_manager import WeeklyActivityManager
from ..managers.atp_points_manager import ATPPointsManager
from ..utils.constants import TIME_CONSTANTS
from .save_manager import SaveManager, GameState


class GameSession:
    """Gestionnaire principal de session de jeu"""
    
    def __init__(self):
        self.main_player: Optional[Player] = None
        self.all_players: Dict[str, Player] = {}
        self.current_week: int = 1
        self.current_year: int = 2024
        
        # Managers
        self.tournament_manager = TournamentManager()
        self.ranking_manager: Optional[RankingManager] = None
        self.player_generator = PlayerGenerator()
        self.activity_manager: Optional[WeeklyActivityManager] = None
        self.atp_points_manager: Optional[ATPPointsManager] = None
        self.save_manager = SaveManager()
        
        # Timing pour playtime
        self.session_start_time: Optional[float] = None
        
        # Game state
        self.is_preliminary_complete: bool = False
        self.game_running: bool = True
        
    def start_new_game(self) -> None:
        """Démarre une nouvelle partie"""
        print("="*60)
        print("🎾 BIENVENUE DANS TENNISRPG v2!")
        print("="*60)
        
        # Démarre le chronométrage
        self.session_start_time = time.time()
        
        # 1. Création du joueur principal
        self._create_main_player()
        
        # 2. Génération du pool de PNJ
        self._generate_npc_pool()
        
        # 3. Simulation préliminaire (10 ans)
        self._run_preliminary_simulation()
        
        # 4. Initialisation du jeu principal
        self._initialize_main_game()
        
        # 5. Boucle de jeu principale
        self._main_game_loop()
        
    def _create_main_player(self) -> None:
        """Crée le joueur principal"""
        print("\n📝 CRÉATION DE VOTRE JOUEUR")
        print("-" * 30)
        
        # Sélection du genre
        while True:
            gender_input = input("Genre - Masculin ('M') ou Féminin ('F') ? ").strip().lower()
            if gender_input in ['m', 'f']:
                gender = Gender.MALE if gender_input == 'm' else Gender.FEMALE
                break
            print("❌ Entrée invalide. Utilisez 'M' pour masculin ou 'F' pour féminin.")
        
        # Informations du joueur
        first_name = input("\n👤 Prénom de votre joueur/joueuse : ").strip()
        last_name = input("👤 Nom de famille : ").strip()
        country = input("🌍 Pays : ").strip()
        
        # Création du joueur principal
        self.main_player = Player(
            gender=gender,
            first_name=first_name,
            last_name=last_name, 
            country=country,
            is_main_player=True
        )
        
        print(f"\n✅ Joueur créé: {self.main_player.full_name} ({country})")
        
    def _generate_npc_pool(self) -> None:
        """Génère le pool de PNJ en arrière-plan"""
        print("\n🤖 GÉNÉRATION DU CIRCUIT MONDIAL")
        print("-" * 35)
        print("⏳ Création de 1000 joueurs professionnels...")
        
        start_time = time.time()
        
        def generate_players():
            """Génère les joueurs en thread séparé"""
            for i in range(1000):
                # Alterne entre hommes et femmes selon le genre du joueur principal
                gender = self.main_player.gender
                player = self.player_generator.generate_player(gender)
                self.all_players[player.full_name] = player
                
                # Progress indication
                if (i + 1) % 200 == 0:
                    print(f"   📊 {i + 1}/1000 joueurs générés...")
        
        # Génération en thread pour montrer progression
        generate_thread = threading.Thread(target=generate_players)
        generate_thread.start()
        generate_thread.join()
        
        generation_time = time.time() - start_time
        print(f"✅ Pool généré en {generation_time:.1f} secondes")
        
    def _run_preliminary_simulation(self) -> None:
        """Simule 10 ans préliminaires pour établir un historique réaliste"""
        print("\n⚡ SIMULATION PRÉLIMINAIRE")
        print("-" * 25)
        print("📅 Simulation de 10 années pour créer un historique réaliste...")
        print("💡 Cela permet d'avoir des classements et des rivalités naturelles")
        
        # Initialise le ranking manager
        self.ranking_manager = RankingManager(list(self.all_players.values()))
        
        # Initialise l'ATP points manager
        self.atp_points_manager = ATPPointsManager(self.all_players)
        
        # Initialise l'activity manager
        self.activity_manager = WeeklyActivityManager(
            self.tournament_manager, self.ranking_manager
        )
        
        start_time = time.time()
        
        # Simule 520 semaines (10 ans)
        for year in range(1):
            print(f"   📈 Année {2014 + year}...")
            
            for week in range(1, 53):  # 52 semaines par an
                self._simulate_week_preliminarily(week)
                
                # Progress tous les 6 mois
                if week % 26 == 0:
                    print(f"      ⌛ Semestre {week//26} terminé")
        
        simulation_time = time.time() - start_time
        print(f"✅ Simulation préliminaire terminée en {simulation_time:.1f} secondes")
        self.is_preliminary_complete = True
        
    def _simulate_week_preliminarily(self, week: int) -> None:
        """Simule une semaine sans le joueur principal"""
        # Simule tous les tournois de la semaine
        self.tournament_manager.simulate_week_tournaments(
            week=week, 
            all_players=self.all_players,
            ranking_manager=self.ranking_manager,
            atp_points_manager=self.atp_points_manager
        )
        # Met à jour les classements
        self.ranking_manager.update_weekly_rankings()
        
        # Récupération naturelle de fatigue
        for player in self.all_players.values():
            if hasattr(player, 'physical'):
                player.physical.recover_fatigue(TIME_CONSTANTS["FATIGUE_NATURAL_RECOVERY"])
    
    def _initialize_main_game(self) -> None:
        """Initialise le jeu principal après la simulation préliminaire"""
        print("\n🎮 INITIALISATION DU JEU PRINCIPAL")
        print("-" * 35)
        
        # Ajoute le joueur principal au pool
        self.all_players[self.main_player.full_name] = self.main_player
        
        # Réinitialise les classements avec le joueur principal
        self.ranking_manager.add_player(self.main_player)
        self.ranking_manager.reset_atp_race()
        
        # Réinitialise le temps
        self.current_week = 1
        self.current_year = 2024
        
        gender_term = "tennisman" if self.main_player.gender == Gender.MALE else "tenniswoman"
        print(f"\n🌟 Bienvenue dans votre carrière de {gender_term},")
        print(f"🌟 {self.main_player.full_name}!")
        print(f"📅 Votre aventure commence en {self.current_year}")
        
    def _main_game_loop(self) -> None:
        """Boucle principale du jeu"""
        while self.game_running:
            self._display_weekly_header()
            self._display_main_menu()
            action = self._get_user_input()
            self._handle_user_action(action)
    
    def _display_weekly_header(self) -> None:
        """Affiche l'en-tête hebdomadaire"""
        print("\n" + "="*60)
        print(f"📅 SEMAINE {self.current_week} - ANNÉE {self.current_year}")
        print(f"👤 {self.main_player.full_name}")
        
        # Informations sur la fatigue
        if hasattr(self.main_player, 'physical'):
            fatigue = self.main_player.physical.fatigue
            fatigue_emoji = "💚" if fatigue < 30 else "⚠️" if fatigue < 70 else "🔴"
            print(f"{fatigue_emoji} Fatigue: {fatigue}%")
        
        # Classement actuel
        if self.ranking_manager:
            atp_rank = self.ranking_manager.get_player_rank(self.main_player, RankingType.ATP)
            race_rank = self.ranking_manager.get_player_rank(self.main_player, RankingType.ATP_RACE)
            print(f"🏆 Classement ATP: #{atp_rank} | Race: #{race_rank}")
        
        print("="*60)
    
    def _display_main_menu(self) -> None:
        """Affiche le menu principal"""
        print("\n📋 ACTIONS DISPONIBLES:")
        print("━━━━━━━━━━━━━━━━━━━━━━")
        print("⏭️  [ENTRÉE] Continuer vers les activités de la semaine")
        print("📊 [C] Voir les classements")  
        print("🏆 [A] Points ATP à défendre cette semaine")
        print("👤 [I] Carte d'identité de votre joueur")
        print("📈 [E] Attribuer des points d'attributs")
        print("💾 [S] Sauvegarder le jeu")
        print("📂 [L] Charger une sauvegarde")
        print("❌ [Q] Quitter le jeu")
    
    def _get_user_input(self) -> str:
        """Récupère la saisie utilisateur"""
        return input("\n🎯 Votre choix : ").strip().lower()
    
    def _handle_user_action(self, action: str) -> None:
        """Traite l'action de l'utilisateur"""
        if action == 'q':
            self._quit_game()
        elif action == 'c':
            self._display_rankings()
        elif action == 'a':
            self._display_atp_points_to_defend()
        elif action == 'i':
            self._display_player_id_card()
        elif action == 'e':
            self._assign_attribute_points()
        elif action == 's':
            self._save_game()
        elif action == 'l':
            self._load_game_menu()
        elif action == '' or action == 'continue':
            self._start_weekly_activities()
        else:
            print("❌ Action non reconnue. Utilisez les lettres indiquées ou ENTRÉE.")
    
    def _quit_game(self) -> None:
        """Quitte le jeu"""
        print("\n👋 MERCI D'AVOIR JOUÉ À TENNISRPG v2!")
        print("📊 Voici vos statistiques finales:")
        self._display_player_id_card()
        self.game_running = False
    
    def _display_rankings(self) -> None:
        """Affiche les classements"""
        if not self.ranking_manager:
            print("❌ Classements non disponibles")
            return
            
        print("\n📊 QUEL CLASSEMENT SOUHAITEZ-VOUS VOIR ?")
        print("1. Classement ATP (52 semaines glissantes)")
        print("2. ATP Race (année en cours)")
        
        while True:
            choice = input("\n🎯 Votre choix (1-2) : ").strip()
            if choice == '1':
                self.ranking_manager.display_ranking(RankingType.ATP)
                break
            elif choice == '2':
                self.ranking_manager.display_ranking(RankingType.ATP_RACE)  
                break
            else:
                print("❌ Choix invalide. Utilisez 1 ou 2.")
    
    def _display_atp_points_to_defend(self) -> None:
        """Affiche les points ATP à défendre"""
        # TODO: Implémenter la logique des points à défendre
        print("🏆 Points ATP à défendre cette semaine:")
        print("💡 Fonctionnalité en cours de développement...")
    
    def _display_player_id_card(self) -> None:
        """Affiche la carte d'identité du joueur"""
        if self.ranking_manager:
            self.main_player.display_id_card(self.ranking_manager)
        else:
            print("👤 Informations du joueur non disponibles")
    
    def _assign_attribute_points(self) -> None:
        """Permet d'attribuer des points d'attributs"""
        # TODO: Implémenter le système d'attribution
        print("📈 Attribution de points d'attributs:")
        print("💡 Fonctionnalité en cours de développement...")
    
    def _start_weekly_activities(self) -> None:
        """Démarre les activités hebdomadaires"""
        if not self.activity_manager:
            print("❌ Gestionnaire d'activités non initialisé")
            return
        
        # Affiche les activités de la semaine
        self.activity_manager.display_weekly_activities(self.main_player, self.current_week)
        
        # Choix de l'activité
        chosen_activity = self.activity_manager.choose_activity(self.main_player, self.current_week)
        
        if chosen_activity is None:
            print("🔙 Retour au menu principal")
            return
        
        # Exécute l'activité
        print("\n⚡ EXÉCUTION DE L'ACTIVITÉ...")
        print("-" * 30)
        
        result = self.activity_manager.execute_activity(
            self.main_player, chosen_activity, self.current_week, self.all_players, self.atp_points_manager
        )
        
        # Affiche le résultat
        if result.success:
            print(f"✅ {result.message}")
            if result.xp_gained > 0:
                print(f"📈 +{result.xp_gained} XP")
            if result.fatigue_change != 0:
                change_symbol = "+" if result.fatigue_change > 0 else ""
                print(f"💪 {change_symbol}{result.fatigue_change}% Fatigue")
        else:
            print(f"❌ {result.message}")
        
        # Avance à la semaine suivante
        self._advance_week()
    
    def _save_game(self) -> None:
        """Sauvegarde le jeu"""
        print("\n💾 SAUVEGARDE DU JEU")
        print("-" * 20)
        
        # Crée l'état du jeu
        game_state = GameState()
        game_state.main_player = self.main_player
        game_state.all_players = self.all_players
        game_state.current_week = self.current_week
        game_state.current_year = self.current_year
        game_state.is_preliminary_complete = self.is_preliminary_complete
        
        # Calcule le temps de jeu
        if self.session_start_time:
            session_time = (time.time() - self.session_start_time) / 3600  # en heures
            game_state.playtime_hours = session_time
        
        # Choix du nom de sauvegarde
        default_name = f"{self.main_player.first_name}_{self.main_player.last_name}_S{self.current_week}_{self.current_year}"
        
        print(f"💡 Nom par défaut: {default_name}")
        custom_name = input("📝 Nom de sauvegarde (ENTRÉE pour défaut) : ").strip()
        
        filename = custom_name if custom_name else default_name
        
        # Sauvegarde
        if self.save_manager.save_game(game_state, filename):
            print("✅ Jeu sauvegardé avec succès!")
        else:
            print("❌ Erreur lors de la sauvegarde")
    
    def _load_game_menu(self) -> None:
        """Menu de chargement de sauvegarde"""
        print("\n📂 CHARGER UNE SAUVEGARDE")
        print("-" * 25)
        
        self.save_manager.display_saves_menu()
        saves = self.save_manager.list_saves()
        
        if not saves:
            input("\n⏎ Appuyez sur ENTRÉE pour continuer...")
            return
        
        while True:
            choice = input(f"\n🎯 Choisir sauvegarde (1-{len(saves)}) ou 'q' pour annuler : ").strip()
            
            if choice.lower() == 'q':
                return
            
            if choice.isdigit() and 1 <= int(choice) <= len(saves):
                filename = self.save_manager.get_save_by_index(int(choice))
                if filename:
                    self._load_game(filename)
                    return
            else:
                print("❌ Choix invalide")
    
    def _load_game(self, filename: str) -> None:
        """Charge une sauvegarde"""
        game_state = self.save_manager.load_game(filename)
        
        if not game_state:
            print("❌ Impossible de charger la sauvegarde")
            return
        
        # Restaure l'état du jeu
        self.main_player = game_state.main_player
        self.all_players = game_state.all_players
        self.current_week = game_state.current_week
        self.current_year = game_state.current_year
        self.is_preliminary_complete = game_state.is_preliminary_complete
        
        # Recrée les managers avec les données chargées
        if self.all_players:
            self.ranking_manager = RankingManager(list(self.all_players.values()))
            self.atp_points_manager = ATPPointsManager(self.all_players)
            self.activity_manager = WeeklyActivityManager(
                self.tournament_manager, self.ranking_manager
            )
        
        # Remet à jour le temps de début de session
        self.session_start_time = time.time()
        
        print("✅ Sauvegarde chargée avec succès!")
        print(f"📅 Position: Semaine {self.current_week}, Année {self.current_year}")
        
        if game_state.playtime_hours > 0:
            print(f"⏱️  Temps de jeu: {game_state.playtime_hours:.1f} heures")
    
    def _advance_week(self) -> None:
        """Avance d'une semaine"""
        self.current_week += 1
        
        if self.current_week > TIME_CONSTANTS["WEEKS_PER_YEAR"]:
            self.current_week = 1
            self.current_year += 1
            print(f"\n🎊 NOUVELLE ANNÉE: {self.current_year}")
            
            if self.ranking_manager:
                self.ranking_manager.reset_atp_race()
        
        # Récupération naturelle de fatigue
        if hasattr(self.main_player, 'physical'):
            self.main_player.physical.recover_fatigue(TIME_CONSTANTS["FATIGUE_NATURAL_RECOVERY"])


def main():
    """Point d'entrée principal"""
    try:
        game = GameSession()
        game.start_new_game()
    except KeyboardInterrupt:
        print("\n\n👋 Jeu interrompu par l'utilisateur. À bientôt!")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("🔧 Veuillez signaler ce problème.")


if __name__ == "__main__":
    main()
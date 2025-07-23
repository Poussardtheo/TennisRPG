"""
Session de jeu principale - Cœur du gameplay TennisRPG v2
"""
import time
import threading
import random
from typing import Dict, List, Optional

from ..entities.player import Player, Gender
from ..entities.ranking import RankingType  
from ..managers.player_generator import PlayerGenerator
from ..managers.tournament_manager import TournamentManager
from ..managers.ranking_manager import RankingManager
from ..managers.weekly_activity_manager import WeeklyActivityManager
from ..managers.atp_points_manager import ATPPointsManager
from ..managers.retirement_manager import RetirementManager
from ..utils.constants import TIME_CONSTANTS, RETIREMENT_CONSTANTS
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
        self.retirement_manager = RetirementManager(self.player_generator)
        self.save_manager = SaveManager()
        
        # Timing pour playtime
        self.session_start_time: Optional[float] = None
        
        # Game state
        self.is_preliminary_complete: bool = False
        self.game_running: bool = True
        
    def start_new_game(self) -> None:
        """Démarre une nouvelle partie"""
        print("="*60)
        print("🎾 BIENVENUE DANS TENNISRPG !")
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
        
        # Initialise l'ATP points manager avec le ranking manager pour synchronisation
        self.atp_points_manager = ATPPointsManager(self.all_players, self.ranking_manager)
        
        # Initialise l'activity manager
        self.activity_manager = WeeklyActivityManager(
            self.tournament_manager, self.ranking_manager
        )
        
        start_time = time.time()
        
        # Simule 1 année préliminaire (réduit pour performance)
        for year in range(1):
            print(f"   📈 Année {2014 + year}...")
            
            for week in range(1, 53):  # 52 semaines par an
                self._simulate_week_preliminarily(week)
                
                # Progress tous les 6 mois
                if week % 26 == 0:
                    print(f"      ⌛ Semestre {week//26} terminé")
            
            # Vieillit les joueurs en fin d'année et traite quelques retraites préliminaires
            self.retirement_manager.force_aging_simulation(self.all_players, 1)
            
            # Applique quelques retraites préliminaires pour créer de la rotation
            if year == 0:  # Seulement lors de la dernière année de simulation
                # Force quelques retraites pour les plus vieux joueurs
                very_old_players = [p for p in self.all_players.values() 
                                  if hasattr(p.career, 'age') and p.career.age >= 35]
                if very_old_players:
                    # Retire 10% des joueurs les plus âgés
                    num_to_retire = max(1, len(very_old_players) // 10)
                    players_to_retire = random.sample(very_old_players, num_to_retire)
                    
                    for player in players_to_retire:
                        if player.full_name in self.all_players:
                            del self.all_players[player.full_name]

                    gender = players_to_retire[0].gender    # Gènère des remplacements du même genre

                    # Génère des remplacements
                    for _ in range(num_to_retire):
                        new_player = self.player_generator.generate_player(gender, level_range=(1, 10))
                        mini, maxi = RETIREMENT_CONSTANTS["YOUNG_PLAYER_MIN_AGE"], RETIREMENT_CONSTANTS["YOUNG_PLAYER_MAX_AGE"]
                        new_player.career.age = random.randint(mini, maxi)
                        self.all_players[new_player.full_name] = new_player
        
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
        
        # Récupération naturelle de fatigue - utilisation méthode centralisée
        for player in self.all_players.values():
            player.recover_fatigue(TIME_CONSTANTS["FATIGUE_NATURAL_RECOVERY"])
    
    def _initialize_main_game(self) -> None:
        """Initialise le jeu principal après la simulation préliminaire"""
        print("\n🎮 INITIALISATION DU JEU PRINCIPAL")
        print("-" * 35)
        
        # Ajoute le joueur principal au pool
        self.all_players[self.main_player.full_name] = self.main_player
        self.atp_points_manager.add_player(self.main_player)   # Ajoute les points ATP du joueur principal

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
        print("⏭️ [ENTRÉE] Continuer vers les activités de la semaine")
        print("📊 [C] Voir les classements")  
        print("🏆 [A] Points ATP à défendre cette semaine")
        print("👤 [I] Carte d'identité de votre joueur")
        print("📈 [E] Attribuer des points d'attributs")
        print("💾 [S] Sauvegarder le jeu")
        print("📂 [L] Charger une autre sauvegarde")
        print("🔄 [R] Voir les retraites récentes")
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
        elif action == 'r':
            self._display_recent_retirements()
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
        
        ranking_type = None
        while True:
            choice = input("\n🎯 Votre choix (1-2) : ").strip()
            if choice == '1':
                ranking_type = RankingType.ATP
                break
            elif choice == '2':
                ranking_type = RankingType.ATP_RACE
                break
            else:
                print("❌ Choix invalide. Utilisez 1 ou 2.")
        
        # Demander la plage d'affichage
        print("\n📍 PLAGE D'AFFICHAGE")
        try:
            start_rank = int(input("🎯 Rang de départ (par défaut 1) : ").strip() or "1")
            if start_rank < 1:
                start_rank = 1
                print("⚠️  Rang de départ ajusté à 1")
        except ValueError:
            start_rank = 1
            print("⚠️  Valeur invalide, rang de départ défini à 1")
            
        try:
            count = int(input("🎯 Nombre de joueurs à afficher (par défaut 50) : ").strip() or "50")
            if count < 1:
                count = 50
                print("⚠️  Nombre ajusté à 50")
        except ValueError:
            count = 50
            print("⚠️  Valeur invalide, nombre défini à 50")
        
        self.ranking_manager.display_ranking(ranking_type, count, start_rank)
    
    def _display_atp_points_to_defend(self) -> None:
        """Affiche les points ATP à défendre"""
        print("🏆 Points ATP à défendre cette semaine:")
        
        if not self.ranking_manager or not self.main_player:
            print("❌ Données non disponibles")
            return
            
        points_to_defend = self.ranking_manager.get_points_to_defend(self.main_player.full_name)
        
        if points_to_defend == 0:
            print("💚 Aucun point à défendre cette semaine !")
        else:
            print(f"⚠️  Vous devez défendre {points_to_defend} points ATP cette semaine")
            print(f"📊 Si vous ne participez à aucun tournoi, vous perdrez {points_to_defend} points")
            
        # Affiche aussi le classement actuel pour contexte
        current_rank = self.ranking_manager.get_player_rank(self.main_player)
        if current_rank:
            print(f"📈 Classement actuel: #{current_rank} ({self.main_player.career.atp_points} points)")
            potential_points = max(0, self.main_player.career.atp_points - points_to_defend)
            print(f"💭 Points potentiels si aucune participation: {potential_points}")
        
        # Affiche les semaines suivantes avec des points à défendre
        print("\n📅 Points à défendre dans les prochaines semaines:")
        future_points = []
        for i in range(1, 5):  # 4 semaines suivantes
            future_week = (self.ranking_manager.current_week + i - 1) % 52 + 1
            future_defend = self.ranking_manager.get_points_to_defend(
                self.main_player.full_name, future_week
            )
            if future_defend > 0:
                future_points.append((future_week, future_defend))
        
        if future_points:
            for week, points in future_points:
                print(f"   Semaine {week}: {points} points")
        else:
            print("   Aucun point à défendre dans les 4 prochaines semaines")
    
    def _display_player_id_card(self) -> None:
        """Affiche la carte d'identité du joueur"""
        if self.ranking_manager:
            self.main_player.display_id_card(self.ranking_manager)
        else:
            print("👤 Informations du joueur non disponibles")
    
    def _assign_attribute_points(self) -> None:
        """Permet d'attribuer des points d'attributs"""
        print("📈 Attribution de points d'attributs:")
        if not self.main_player:
            print("❌ Aucun joueur principal défini")
            return
        
        if self.main_player.career.ap_points == 0:
            print("💡 Aucun point AP disponible à attribuer")
            return
            
        print(f"🎯 Points AP disponibles: {self.main_player.career.ap_points}")
        print("\nChoix d'attribution:")
        print("1. Attribution manuelle")
        print("2. Attribution automatique basée sur l'archétype")
        print("3. Retour au menu")
        
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == "1":
            self.main_player.assign_ap_points_manually()
        elif choice == "2":
            points_before = self.main_player.career.ap_points
            self.main_player._auto_assign_ap_points()
            points_used = points_before - self.main_player.career.ap_points
            print(f"✅ {points_used} points attribués automatiquement selon votre archétype!")
        elif choice == "3":
            return
        else:
            print("❌ Choix invalide")
    
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
    
    def _load_game(self, filename: str) -> bool:
        """Charge une sauvegarde"""
        game_state = self.save_manager.load_game(filename)
        
        if not game_state:
            print("❌ Impossible de charger la sauvegarde")
            return False
        
        # Restaure l'état du jeu
        self.main_player = game_state.main_player
        self.all_players = game_state.all_players
        self.current_week = game_state.current_week
        self.current_year = game_state.current_year
        self.is_preliminary_complete = game_state.is_preliminary_complete
        
        # Recrée les managers avec les données chargées
        if self.all_players:
            self.ranking_manager = RankingManager(list(self.all_players.values()))
            self.atp_points_manager = ATPPointsManager(self.all_players, self.ranking_manager)
            self.activity_manager = WeeklyActivityManager(
                self.tournament_manager, self.ranking_manager
            )
        
        # Remet à jour le temps de début de session
        self.session_start_time = time.time()
        
        print("✅ Sauvegarde chargée avec succès!")
        print(f"📅 Position: Semaine {self.current_week}, Année {self.current_year}")
        
        if game_state.playtime_hours > 0:
            print(f"⏱️  Temps de jeu: {game_state.playtime_hours:.1f} heures")
            
        return True
    
    def load_game_from_entry(self) -> bool:
        """Charge une partie depuis le menu d'entrée"""
        print("\n📂 CHARGER UNE SAUVEGARDE")
        print("-" * 25)
        
        self.save_manager.display_saves_menu()
        saves = self.save_manager.list_saves()
        
        if not saves:
            input("\n⏎ Appuyez sur ENTRÉE pour retourner au menu principal...")
            return False
        
        while True:
            choice = input(f"\n🎯 Choisir sauvegarde (1-{len(saves)}) ou 'q' pour retourner au menu : ").strip()
            
            if choice.lower() == 'q':
                return False
            
            if choice.isdigit() and 1 <= int(choice) <= len(saves):
                filename = self.save_manager.get_save_by_index(int(choice))
                print("là ça marche j'ai le nom du fichier:", filename)
                if filename and self._load_game(filename):
                    return True
                else:
                    print("❌ Erreur lors du chargement. Réessayez.")
            else:
                print("❌ Choix invalide")
    
    def _advance_week(self) -> None:
        """Avance d'une semaine"""
        self.current_week += 1
        
        if self.current_week > TIME_CONSTANTS["WEEKS_PER_YEAR"]:
            self.current_week = 1
            self.current_year += 1
            print(f"\n🎊 NOUVELLE ANNÉE: {self.current_year}")
            
            # Remet à zéro l'ATP Race
            if self.ranking_manager:
                self.ranking_manager.reset_atp_race()
            
            # Traite les retraites et la rotation des joueurs en fin d'année
            self._process_end_of_year_retirements()
        
        # Récupération naturelle de fatigue - utilisation méthode centralisée
        self.main_player.recover_fatigue(TIME_CONSTANTS["FATIGUE_NATURAL_RECOVERY"])
    
    def _process_end_of_year_retirements(self) -> None:
        """Traite les retraites et la rotation des joueurs en fin d'année"""
        if not self.retirement_manager or not self.ranking_manager:
            return
        
        # Vieillit le joueur principal d'un an
        if self.main_player and hasattr(self.main_player.career, 'age'):
            self.main_player.career.age += 1
            print(f"🎂 {self.main_player.full_name} a maintenant {self.main_player.career.age} ans")
        
        # Traite les retraites et remplacements
        retired_players, new_players = self.retirement_manager.process_end_of_season_retirements(
            self.all_players, self.ranking_manager, self.current_year - 1
        )
        
        # Met à jour les classements si de nouveaux joueurs ont été ajoutés
        if new_players:
            for new_player in new_players:
                self.ranking_manager.add_player(new_player)
        
        # Affichage interactif des retraites
        if retired_players or new_players:
            print(f"\n🎭 CHANGEMENTS DU CIRCUIT PROFESSIONNEL - FIN {self.current_year - 1}")
            print("═" * 60)
            
            # Offre des options d'affichage
            while True:
                print(f"\n📋 OPTIONS D'AFFICHAGE:")
                print("1️⃣  Voir le résumé des retraites")
                print("2️⃣  Voir les statistiques détaillées")
                print("3️⃣  Comparer avec les années précédentes")
                print("4️⃣  Continuer vers la nouvelle saison")
                
                choice = input("\n🎯 Votre choix (1-4): ").strip()
                
                if choice == '1':
                    self._display_retirement_details(retired_players, new_players)
                elif choice == '2':
                    self._display_retirement_statistics(self.current_year - 1)
                elif choice == '3':
                    self._display_retirement_trends()
                elif choice == '4':
                    break
                else:
                    print("❌ Choix invalide. Utilisez 1, 2, 3 ou 4.")
            
            print("═" * 60)
        
        # Résumé final automatique
        retirement_stats = self.retirement_manager.get_retirement_stats(self.current_year - 1)
        if retirement_stats and retirement_stats.get("total_retirements", 0) > 0:
            print(f"\n📊 RÉSUMÉ RAPIDE - {retirement_stats['total_retirements']} retraites, âge moyen {retirement_stats['average_retirement_age']:.1f} ans")
            print(f"🎂 {self.main_player.full_name} commence l'année à {self.main_player.career.age} ans")
            
            # Pause pour que l'utilisateur puisse lire
            input("\n⏎ Appuyez sur ENTRÉE pour démarrer la nouvelle saison...")
    
    def _display_retirement_details(self, retired_players: list, new_players: list) -> None:
        """Affiche les détails des retraites de manière organisée"""
        if retired_players:
            print(f"\n👋 RETRAITÉS CETTE ANNÉE ({len(retired_players)}):")
            print("─" * 50)
            
            # Trie par classement (meilleurs d'abord)
            retired_sorted = sorted(retired_players, 
                                  key=lambda p: self.ranking_manager.get_player_rank(p) or 9999)
            
            for i, player in enumerate(retired_sorted[:15], 1):  # Limite à 15 pour l'affichage
                ranking = self.ranking_manager.get_player_rank(player) or "N/C"
                atp_points = player.career.atp_points or 0
                country_flag = "🇫🇷" if player.country == "France" else "🌍"
                print(f"{i:2}. #{ranking:<4} {player.full_name:<25} {country_flag} {player.career.age} ans ({atp_points} pts ATP)")
            
            if len(retired_players) > 15:
                print(f"   ... et {len(retired_players) - 15} autres retraites")
        
        if new_players:
            print(f"\n🌟 NOUVEAUX SUR LE CIRCUIT ({len(new_players)}):")
            print("─" * 50)
            
            # Échantillon aléatoire des nouveaux
            sample_new = random.sample(new_players, min(15, len(new_players)))
            for i, player in enumerate(sample_new, 1):
                country_flag = "🇫🇷" if player.country == "France" else "🌍"
                print(f"{i:2}. {player.full_name:<25} {country_flag} {player.career.age} ans (Débutant)")
    
    def _display_retirement_statistics(self, year: int) -> None:
        """Affiche des statistiques détaillées sur les retraites"""
        stats = self.retirement_manager.get_retirement_stats(year)
        
        if not stats or stats.get("total_retirements", 0) == 0:
            print(f"\n📊 Aucune retraite enregistrée pour {year}")
            return
        
        print(f"\n📈 STATISTIQUES DÉTAILLÉES - {year}")
        print("─" * 40)
        print(f"📊 Total des retraites: {stats['total_retirements']}")
        print(f"🎂 Âge moyen de retraite: {stats['average_retirement_age']:.1f} ans")
        print(f"👶 Plus jeune retraité: {stats['youngest_retiree']} ans")
        print(f"👴 Plus âgé: {stats['oldest_retiree']} ans")
        
        if 'countries' in stats and stats['countries']:
            print(f"🌍 Pays touchés: {len(stats['countries'])}")
            print(f"   Exemples: {', '.join(stats['countries'][:5])}")
        
        # Analyse comparative
        current_year_players = len(self.all_players)
        retirement_rate = (stats['total_retirements'] / current_year_players) * 100
        print(f"📉 Taux de retraite: {retirement_rate:.1f}% du circuit")
    
    def _display_retirement_trends(self) -> None:
        """Affiche les tendances des retraites sur plusieurs années"""
        print(f"\n📈 TENDANCES DES RETRAITES")
        print("─" * 35)
        
        # Récupère les stats des dernières années
        years_to_check = range(max(2024, self.current_year - 5), self.current_year)
        
        print("Année  | Retraites | Âge moyen")
        print("────── | ───────── | ─────────")
        
        total_retirements = 0
        for year in years_to_check:
            stats = self.retirement_manager.get_retirement_stats(year)
            if stats and stats.get("total_retirements", 0) > 0:
                retirements = stats["total_retirements"]
                avg_age = stats["average_retirement_age"]
                total_retirements += retirements
                print(f"{year}   | {retirements:9} | {avg_age:7.1f} ans")
            else:
                print(f"{year}   | {0:9} | {'N/A':>9}")
        
        if total_retirements > 0:
            avg_per_year = total_retirements / len(years_to_check)
            print("────── | ───────── | ─────────")
            print(f"Moy.   | {avg_per_year:9.1f} | -")
            
            # Prédiction pour l'année suivante
            current_players = len(self.all_players)
            older_players = len([p for p in self.all_players.values() 
                               if hasattr(p.career, 'age') and p.career.age >= 32])
            
            print(f"\n🔮 PRÉDICTIONS {self.current_year}:")
            print(f"   • Joueurs 32+ ans: {older_players}")
            print(f"   • Retraites estimées: {int(avg_per_year * 1.1)}-{int(avg_per_year * 1.3)}")
        else:
            print("\n💭 Pas assez de données historiques pour les tendances")
    
    def _display_recent_retirements(self) -> None:
        """Affiche les retraites récentes et les nouvelles arrivées"""
        print("\n🔄 MOUVEMENTS RÉCENTS SUR LE CIRCUIT")
        print("=" * 45)
        
        # Affiche les retraites de l'année actuelle et précédente
        years_to_check = [self.current_year - 1, self.current_year - 2] if self.current_year > 2024 else [2024]
        
        total_recent_retirements = 0
        for year in years_to_check:
            stats = self.retirement_manager.get_retirement_stats(year)
            if stats and stats.get("total_retirements", 0) > 0:
                total_recent_retirements += stats["total_retirements"]
                print(f"\n📅 ANNÉE {year}:")
                print(f"   • {stats['total_retirements']} retraites")
                print(f"   • Âge moyen: {stats['average_retirement_age']:.1f} ans")
                if stats.get('youngest_retiree') and stats.get('oldest_retiree'):
                    print(f"   • Tranche d'âge: {stats['youngest_retiree']}-{stats['oldest_retiree']} ans")
        
        if total_recent_retirements == 0:
            print("\n💭 Aucune retraite récente enregistrée")
            print("🔮 Le circuit professionnel est stable pour le moment")
        else:
            # Statistiques du circuit actuel
            current_players = len(self.all_players)
            older_players = len([p for p in self.all_players.values() 
                               if hasattr(p.career, 'age') and p.career.age >= 30])
            
            print(f"\n📊 ÉTAT ACTUEL DU CIRCUIT:")
            print(f"   • Total de joueurs: {current_players}")
            print(f"   • Joueurs 30+ ans: {older_players} ({(older_players/current_players*100):.1f}%)")
            
            # Prédiction des retraites à venir
            very_old = len([p for p in self.all_players.values() 
                          if hasattr(p.career, 'age') and p.career.age >= 35])
            if very_old > 0:
                print(f"   • Joueurs 35+ ans: {very_old} (retraites probables)")
        
        # Information sur le joueur principal
        if self.main_player:
            player_age = self.main_player.career.age
            peers = len([p for p in self.all_players.values() 
                        if hasattr(p.career, 'age') and 
                        abs(p.career.age - player_age) <= 2 and p != self.main_player])
            
            print(f"\n👤 VOTRE GÉNÉRATION:")
            print(f"   • Votre âge: {player_age} ans")
            print(f"   • Joueurs de votre âge (±2 ans): {peers}")
            
            if player_age >= 30:
                from ..utils.helpers import calculate_retirement_probability
                retirement_prob = calculate_retirement_probability(
                    player_age, 
                    self.ranking_manager.get_player_rank(self.main_player) if self.ranking_manager else None
                )
                print(f"   • Probabilité de retraite: {retirement_prob*100:.1f}%")
        
        print("\n" + "=" * 45)
        input("⏎ Appuyez sur ENTRÉE pour revenir au menu...")


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
                # Nouvelle partie
                game = GameSession()
                game.start_new_game()
                break
            elif choice == '2':
                # Charger une partie
                game = GameSession()
                if game.load_game_from_entry():
                    game._main_game_loop()
                else:
                    continue
                break
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
"""
Game Session Controller - Orchestration et logique de contrôle du jeu
Extrait de GameSession pour une meilleure séparation des responsabilités
"""
import time
import threading
import random
from typing import Dict, List, Optional

from ..entities.player import Player, Gender
from ..entities.ranking import RankingType
from ..utils.constants import TIME_CONSTANTS, GAME_CONSTANTS
from .game_session_ui import GameSessionUI
from .game_session_state import GameSessionState
from ..ui.history_menus import HistoryMenus


class GameSessionController:
    """Contrôle le flux du jeu et orchestre les composants"""
    
    def __init__(self, ui: GameSessionUI, state: GameSessionState):
        self.ui = ui
        self.state = state
        
    def start_new_game(self) -> None:
        """Démarre une nouvelle partie - orchestration complète"""
        self.ui.display_welcome()
        
        # IMPORTANT: Remet à zéro tous les états pour éviter la contamination entre parties
        self.state.reset_for_new_game()
        
        # Démarre le chronométrage
        self.state.start_session_timing()
        
        # 1. Création du joueur principal
        self._create_main_player()
        
        # 2. Génération du pool de PNJ
        self._generate_npc_pool()
        
        # 3. Simulation préliminaire (1-2 ans)
        self._run_preliminary_simulation()
        
        # 4. Initialisation du jeu principal
        self._initialize_main_game()
        
        # 5. Boucle de jeu principale
        self._main_game_loop()
        
    def _create_main_player(self) -> None:
        """Crée le joueur principal"""
        player_data = self.ui.get_player_creation_data()
        
        # Création du joueur principal
        main_player = Player(
            gender=player_data['gender'],
            first_name=player_data['first_name'],
            last_name=player_data['last_name'], 
            country=player_data['country'],
            is_main_player=True,
            talent_level=player_data['talent_level'],
            difficulty=player_data['difficulty']
        )
        
        self.state.set_main_player(main_player)
        self.ui.display_player_created(main_player, player_data['difficulty'])
        
    def _generate_npc_pool(self) -> None:
        """Génère le pool de PNJ en arrière-plan"""
        pool_size = GAME_CONSTANTS["NPC_POOL_SIZE"]
        self.ui.display_npc_generation_progress(pool_size)
        
        start_time = time.time()
        
        def generate_players():
            """Génère les joueurs en thread séparé"""
            for i in range(pool_size):
                # Alterne entre hommes et femmes selon le genre du joueur principal
                gender = self.state.main_player.gender
                player = self.state.player_generator.generate_player(gender)
                self.state.add_player(player)
                
                # Progress indication
                if (i + 1) % 200 == 0:
                    self.ui.display_npc_generation_progress_update(i + 1, pool_size)
        
        # Génération en thread pour montrer progression
        generate_thread = threading.Thread(target=generate_players)
        generate_thread.start()
        generate_thread.join()
        
        generation_time = time.time() - start_time
        self.ui.display_npc_generation_complete(generation_time)
        
    def _run_preliminary_simulation(self) -> None:
        """Simule 1-2 ans préliminaires pour établir un historique réaliste"""
        self.ui.display_preliminary_simulation_start()
        
        # Initialise les managers
        self.state.initialize_ranking_manager()
        self.state.initialize_atp_points_manager()
        self.state.initialize_activity_manager()
        
        start_time = time.time()
        
        # Simule 2 années préliminaires (réduit de 11 à 2 pour performance)
        preliminary_start_year = TIME_CONSTANTS["GAME_START_YEAR"] - 2
        for year in range(2):
            current_sim_year = preliminary_start_year + year
            self.ui.display_preliminary_simulation_year(current_sim_year)
            
            for week in range(1, TIME_CONSTANTS["WEEKS_PER_YEAR"] + 1):  # 52 semaines par an
                self._simulate_week_preliminarily(week, current_sim_year)
                
                # Progress tous les 6 mois
                if week % 26 == 0:
                    self.ui.display_preliminary_simulation_semester(week//26)
            
            # Traite les retraites en fin d'année avec le système complet
            self.state.process_retirements()
        
        simulation_time = time.time() - start_time
        self.ui.display_preliminary_simulation_complete(simulation_time)
        self.state.set_preliminary_complete()
        
    def _simulate_week_preliminarily(self, week: int, sim_year: int) -> None:
        """Simule une semaine sans le joueur principal"""
        # Met à jour la semaine courante dans le ranking manager pour synchroniser
        if self.state.ranking_manager:
            self.state.ranking_manager.current_week = week
            
        # DÉBUT DE SEMAINE : Retire les points qui expirent (système glissant 52 semaines)
        if self.state.ranking_manager:
            self.state.ranking_manager.expire_weekly_points()
            
        # Simule tous les tournois de la semaine
        self.state.tournament_manager.simulate_week_tournaments(
            week=week,
            all_players=self.state.all_players,
            current_year=sim_year,
            ranking_manager=self.state.ranking_manager,
            atp_points_manager=self.state.atp_points_manager,
            injury_manager=self.state.injury_manager,
            history_manager=self.state.game_state.history_manager
        )
        
        # Met à jour les classements
        self.state.update_weekly_rankings()
        
        # Récupération naturelle de fatigue - utilisation méthode centralisée
        self.state.apply_natural_fatigue_recovery_all()
    
    def _initialize_main_game(self) -> None:
        """Initialise le jeu principal après la simulation préliminaire"""
        self.ui.display_main_game_initialization()
        
        # Ajoute le joueur principal au pool et aux managers
        self.state.add_main_player_to_managers()
        
        # Réinitialise le temps UNIQUEMENT pour une nouvelle partie
        self.state.reset_time_to_start()
        
        self.ui.display_career_start(self.state.main_player, self.state.current_year)
        
    def _main_game_loop(self) -> None:
        """Boucle principale du jeu"""
        while self.state.game_running:
            self.ui.display_weekly_header(
                self.state.current_week, 
                self.state.current_year,
                self.state.main_player, 
                self.state.ranking_manager
            )
            self.ui.display_main_menu()
            action = self.ui.get_user_input()
            self._handle_user_action(action)
            
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
        elif action == 'h':
            self._display_tournament_history()
        elif action == 's':
            self._save_game()
        elif action == 'l':
            self._load_game_menu()
        elif action == 'r':
            self._display_recent_retirements()
        elif action == '' or action == 'continue':
            self._start_weekly_activities()
        else:
            self.ui.display_invalid_choice()
            
    def _quit_game(self) -> None:
        """Quitte le jeu"""
        self.ui.display_quit_message()
        self._display_player_id_card()
        self.state.stop_game()
        
    def _display_rankings(self) -> None:
        """Affiche les classements"""
        if not self.state.ranking_manager:
            self.ui.display_no_ranking_data()
            return
            
        ranking_type = self.ui.get_ranking_choice()
        if ranking_type is None:
            return
            
        # Demander la plage d'affichage
        start_rank, count = self.ui.get_ranking_display_range()
        
        self.state.ranking_manager.display_ranking(ranking_type, count, start_rank)
        
    def _display_atp_points_to_defend(self) -> None:
        """Affiche les points ATP à défendre"""
        if not self.state.ranking_manager or not self.state.main_player:
            self.ui.display_no_data_available()
            return
            
        points_to_defend = self.state.ranking_manager.get_points_to_defend(
            self.state.main_player.full_name
        )
        
        self.ui.display_atp_points_to_defend(
            self.state.main_player, 
            self.state.ranking_manager, 
            points_to_defend,
            self.state.current_week
        )
        
    def _display_player_id_card(self) -> None:
        """Affiche la carte d'identité du joueur"""
        if self.state.ranking_manager and self.state.main_player:
            self.state.main_player.display_id_card(self.state.ranking_manager)
        else:
            self.ui.display_no_data_available("Informations du joueur non disponibles")
            
    def _assign_attribute_points(self) -> None:
        """Permet d'attribuer des points d'attributs"""
        if not self.state.main_player:
            self.ui.display_no_main_player()
            return
        
        ap_points = self.state.main_player.career.ap_points
        choice = self.ui.get_attribute_assignment_choice(ap_points)
        
        if choice == "1":
            self.state.main_player.assign_ap_points_manually()
        elif choice == "2":
            points_before = self.state.main_player.career.ap_points
            self.state.main_player._auto_assign_ap_points()
            points_used = points_before - self.state.main_player.career.ap_points
            self.ui.display_auto_assignment_result(points_used)
        # choice == "3" ou None = retour
        
    def _save_game(self) -> None:
        """Sauvegarde le jeu"""
        filename = self.ui.get_save_filename(self.state.main_player)
        
        success = self.state.save_game(filename)
        self.ui.display_save_result(success)
        
    def _load_game_menu(self) -> None:
        """Menu de chargement de sauvegarde"""
        self.ui.display_load_menu_header()
        
        self.state.display_saves_menu()
        saves = self.state.get_save_files()
        
        choice = self.ui.get_save_file_choice(len(saves))
        if choice == 'q' or choice is None:
            return
            
        filename = self.state.get_save_by_index(int(choice))
        if filename:
            self._load_game(filename)
            
    def _display_tournament_history(self) -> None:
        """Affiche le menu d'historique des tournois"""
        history_menus = HistoryMenus(self.state.game_state.history_manager)
        history_menus.show_main_history_menu(self.state.main_player, self.state.all_players)
            
    def _load_game(self, filename: str) -> bool:
        """Charge une sauvegarde"""
        success = self.state.load_game(filename)
        
        if success:
            self.ui.display_load_result(
                True, 
                self.state.current_week, 
                self.state.current_year,
                self.state.get_session_duration()
            )
        else:
            self.ui.display_load_result(False)
            
        return success
        
    def load_game_from_entry(self) -> bool:
        """Charge une partie depuis le menu d'entrée"""
        # IMPORTANT: Remet à zéro tous les états avant de charger pour éviter la contamination
        self.state.reset_for_new_game()
        
        saves = self.state.get_save_files()
        self.state.display_saves_menu()
        
        choice = self.ui.get_load_from_entry_choice(len(saves))
        if choice == 'q' or choice is None:
            return False
            
        filename = self.state.get_save_by_index(int(choice))
        if filename and self._load_game(filename):
            return True
        else:
            print("❌ Erreur lors du chargement. Réessayez.")
            return False
            
    def _start_weekly_activities(self) -> None:
        """Démarre les activités hebdomadaires"""
        if not self.state.activity_manager:
            self.ui.display_no_activity_manager()
            return
        
        # DÉBUT DE SEMAINE : Retire les points qui expirent (système glissant 52 semaines)
        if self.state.ranking_manager:
            self.state.ranking_manager.expire_weekly_points()
        
        # Affiche les activités de la semaine
        self.state.activity_manager.display_weekly_activities(
            self.state.main_player, self.state.current_week
        )
        
        # Choix de l'activité
        chosen_activity = self.state.activity_manager.choose_activity(
            self.state.main_player, self.state.current_week
        )
        
        if chosen_activity is None:
            self.ui.display_return_to_menu()
            return
        
        # Exécute l'activité
        self.ui.display_activity_execution_header()
        
        result = self.state.activity_manager.execute_activity(
            self.state.main_player, chosen_activity, self.state.current_week, 
            self.state.all_players, self.state.current_year, self.state.atp_points_manager, self.state.injury_manager
        )
        
        # Affiche le résultat
        self.ui.display_activity_result(result)

        # Avance à la semaine suivante (2 semaines pour les tournois 7 tours, 
        # sauf si éliminé dans les 3 premiers tours)
        weeks_to_advance = self._determine_weeks_to_advance(chosen_activity, result)
        
        # Affiche un message informatif pour les tournois multi-semaines
        self._display_week_advance_message(chosen_activity, weeks_to_advance, result)
        
        self._advance_week(weeks_to_advance, chosen_activity)
        
    def _determine_weeks_to_advance(self, activity, result=None) -> int:
        """Détermine le nombre de semaines à avancer selon le type d'activité et le résultat"""
        from ..managers.weekly_activity_manager import TournamentActivity, ActivityResult
        
        # Si c'est une activité de tournoi, vérifie s'il s'agit d'un tournoi à 7 tours
        if isinstance(activity, TournamentActivity):
            tournament = activity.tournament
            # Calcule le nombre de tours basé sur le nombre de joueurs
            num_rounds = tournament._calculate_tournament_rounds()
            
            # Les tournois à 7 tours durent normalement 2 semaines
            if num_rounds == 7:
                # Si on a le résultat et que le joueur principal a été éliminé rapidement
                if result and isinstance(result, ActivityResult):
                    # Récupère le tour d'élimination depuis les données du tournoi
                    if self.state.main_player in tournament.eliminated_players:
                        elimination_round = tournament.eliminated_players[self.state.main_player]
                        # Si éliminé dans les 3 premiers tours (round_128, round_64, round_32), 1 semaine
                        if elimination_round in ["round_128", "round_64", "round_32"]:
                            return 1
                    # Si le joueur a gagné ou a été éliminé tard, 2 semaines
                    elif tournament.participants and any(
                        hasattr(p, 'is_main_player') and p.is_main_player 
                        for p in tournament.participants
                    ):
                        # Le joueur principal a participé, mais pas dans eliminated_players
                        # Cela signifie qu'il a probablement gagné le tournoi
                        return 2
                
                # Par défaut pour les tournois à 7 tours, 2 semaines
                return 2
        
        # Par défaut, toutes les autres activités durent 1 semaine
        return 1
        
    def _display_week_advance_message(self, activity, weeks_to_advance: int, result=None) -> None:
        """Affiche un message informatif sur l'avancement des semaines"""
        from ..managers.weekly_activity_manager import TournamentActivity
        
        if isinstance(activity, TournamentActivity) and weeks_to_advance > 1:
            tournament = activity.tournament
            num_rounds = tournament._calculate_tournament_rounds()
            
            if num_rounds == 7:
                if (self.state.main_player in tournament.eliminated_players and 
                    tournament.eliminated_players[self.state.main_player] in ["round_128", "round_64", "round_32"]):
                    # Éliminé tôt - 1 semaine seulement (ne devrait pas arriver ici car weeks_to_advance > 1)
                    pass
                else:
                    # Éliminé tard ou victoire - 2 semaines
                    print(f"\n⏰ Le {tournament.name} s'étend sur 2 semaines. Avancement de 2 semaines...")
        elif isinstance(activity, TournamentActivity) and weeks_to_advance == 1:
            tournament = activity.tournament  
            num_rounds = tournament._calculate_tournament_rounds()
            
            if num_rounds == 7 and self.state.main_player in tournament.eliminated_players:
                elimination_round = tournament.eliminated_players[self.state.main_player]
                if elimination_round in ["round_128", "round_64", "round_32"]:
                    print(f"\n⏰ Éliminé précocement du {tournament.name}. Vous pouvez participer à un autre tournoi la semaine prochaine.")
        
    def _advance_week(self, weeks: int = 1, last_activity=None) -> None:
        """Avance d'une ou plusieurs semaines"""
        is_new_year = False
        for _ in range(weeks):
            is_new_year = self.state.advance_week() or is_new_year
        
        if is_new_year:
            self.ui.display_new_year(self.state.current_year)
            
            # Remet à zéro l'ATP Race
            self.state.reset_atp_race()
            
            # Traite les retraites et la rotation des joueurs en fin d'année
            self._process_end_of_year_retirements()
        
        # Récupération naturelle de fatigue - éviter le double comptage avec le repos
        from ..managers.weekly_activity_manager import RestActivity
        if not (last_activity and isinstance(last_activity, RestActivity)):
            self.state.apply_natural_fatigue_recovery()
        
        # Traitement hebdomadaire des blessures pour tous les joueurs
        if self.state.injury_manager:
            all_players_list = list(self.state.all_players.values())
            weekly_injuries = self.state.injury_manager.process_weekly_injuries(all_players_list)
            
            # Affichage des nouvelles blessures si le joueur principal est concerné
            if self.state.main_player and self.state.main_player.is_injured():
                current_injuries = [inj.name for inj in self.state.main_player.injuries]
                print(f"\n🏥 Blessures actuelles : {', '.join(current_injuries)}")
        
    def _process_end_of_year_retirements(self) -> None:
        """Traite les retraites et la rotation des joueurs en fin d'année"""
        # Vieillit le joueur principal d'un an
        self.state.age_main_player()
        if self.state.main_player:
            self.ui.display_player_birthday(self.state.main_player)
        
        # Traite les retraites et remplacements
        retired_players, new_players = self.state.process_retirements()
        
        # Affichage interactif des retraites
        if retired_players or new_players:
            self._display_end_of_year_retirement_menu(retired_players, new_players)
        
        # Résumé final automatique
        retirement_stats = self.state.get_retirement_stats(self.state.current_year - 1)
        if retirement_stats and retirement_stats.get("total_retirements", 0) > 0:
            print(f"\n📊 RÉSUMÉ RAPIDE - {retirement_stats['total_retirements']} retraites, âge moyen {retirement_stats['average_retirement_age']:.1f} ans")
            print(f"🎂 {self.state.main_player.full_name} commence l'année à {self.state.main_player.career.age} ans")
            
            # Pause pour que l'utilisateur puisse lire
            input("\n⏎ Appuyez sur ENTRÉE pour démarrer la nouvelle saison...")
            
    def _display_end_of_year_retirement_menu(self, retired_players: list, new_players: list) -> None:
        """Affiche le menu interactif des retraites de fin d'année"""
        print(f"\n🎭 CHANGEMENTS DU CIRCUIT PROFESSIONNEL - FIN {self.state.current_year - 1}")
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
                self._display_retirement_statistics(self.state.current_year - 1)
            elif choice == '3':
                self._display_retirement_trends()
            elif choice == '4':
                break
            else:
                print("❌ Choix invalide. Utilisez 1, 2, 3 ou 4.")
        
        print("═" * 60)
        
    def _display_retirement_details(self, retired_players: list, new_players: list) -> None:
        """Affiche les détails des retraites de manière organisée"""
        if retired_players:
            print(f"\n👋 RETRAITÉS CETTE ANNÉE ({len(retired_players)}):")
            print("─" * 50)
            
            # Trie par classement (meilleurs d'abord)
            retired_sorted = sorted(retired_players, 
                                  key=lambda p: self.state.ranking_manager.get_player_rank(p) or 9999)
            
            for i, player in enumerate(retired_sorted[:15], 1):  # Limite à 15 pour l'affichage
                ranking = self.state.ranking_manager.get_player_rank(player) or "N/C"
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
        stats = self.state.get_retirement_stats(year)
        
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
        current_year_players = self.state.get_player_count()
        retirement_rate = (stats['total_retirements'] / current_year_players) * 100
        print(f"📉 Taux de retraite: {retirement_rate:.1f}% du circuit")
        
    def _display_retirement_trends(self) -> None:
        """Affiche les tendances des retraites sur plusieurs années"""
        print(f"\n📈 TENDANCES DES RETRAITES")
        print("─" * 35)
        
        # Récupère les stats des dernières années
        years_to_check = range(max(TIME_CONSTANTS["GAME_START_YEAR"], self.state.current_year - 5), self.state.current_year)
        
        print("Année  | Retraites | Âge moyen")
        print("────── | ───────── | ─────────")
        
        total_retirements = 0
        for year in years_to_check:
            stats = self.state.get_retirement_stats(year)
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
            current_players = self.state.get_player_count()
            older_players = len(self.state.get_players_by_age_threshold(32))
            
            print(f"\n🔮 PRÉDICTIONS {self.state.current_year}:")
            print(f"   • Joueurs 32+ ans: {older_players}")
            print(f"   • Retraites estimées: {int(avg_per_year * 1.1)}-{int(avg_per_year * 1.3)}")
        else:
            print("\n💭 Pas assez de données historiques pour les tendances")
            
    def _display_recent_retirements(self) -> None:
        """Affiche les retraites récentes et les nouvelles arrivées"""
        print("\n🔄 MOUVEMENTS RÉCENTS SUR LE CIRCUIT")
        print("=" * 45)
        
        # Affiche les retraites de l'année actuelle et précédente
        years_to_check = []
        if self.state.current_year > TIME_CONSTANTS["GAME_START_YEAR"]:
            years_to_check = [self.state.current_year - 1, self.state.current_year - 2]
        
        # Toujours inclure l'année de simulation préliminaire
        preliminary_year = TIME_CONSTANTS["GAME_START_YEAR"] - 1
        if preliminary_year not in years_to_check:
            years_to_check.append(preliminary_year)
        
        # Trier par ordre décroissant (plus récent en premier)
        years_to_check.sort(reverse=True)
        
        total_recent_retirements = 0
        for year in years_to_check:
            stats = self.state.get_retirement_stats(year)
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
            current_players = self.state.get_player_count()
            older_players = len(self.state.get_players_by_age_threshold(30))
            
            print(f"\n📊 ÉTAT ACTUEL DU CIRCUIT:")
            print(f"   • Total de joueurs: {current_players}")
            print(f"   • Joueurs 30+ ans: {older_players} ({(older_players/current_players*100):.1f}%)")
            
            # Prédiction des retraites à venir
            very_old = len(self.state.get_players_by_age_threshold(35))
            if very_old > 0:
                print(f"   • Joueurs 35+ ans: {very_old} (retraites probables)")
        
        # Information sur le joueur principal
        if self.state.main_player:
            player_age = self.state.main_player.career.age
            peers = len([p for p in self.state.all_players.values() 
                        if hasattr(p.career, 'age') and 
                        abs(p.career.age - player_age) <= 2 and p != self.state.main_player])
            
            print(f"\n👤 VOTRE GÉNÉRATION:")
            print(f"   • Votre âge: {player_age} ans")
            print(f"   • Joueurs de votre âge (±2 ans): {peers}")
            
            if player_age >= 30:
                from ..utils.helpers import calculate_retirement_probability
                retirement_prob = calculate_retirement_probability(
                    player_age, 
                    self.state.ranking_manager.get_player_rank(self.state.main_player) if self.state.ranking_manager else None
                )
                print(f"   • Probabilité de retraite: {retirement_prob*100:.1f}%")
        
        self.ui.display_back_to_menu_prompt()
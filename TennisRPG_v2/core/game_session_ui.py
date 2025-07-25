"""
Game Session UI - Gestion de toute l'interface utilisateur
Extrait de GameSession pour une meilleure séparation des responsabilités
"""
from typing import Dict, List, Optional, Tuple, Any
from ..entities.player import Player, Gender
from ..entities.ranking import RankingType
from ..utils.constants import DIFFICULTY_TO_TALENT
from .interfaces import IGameUI


class GameSessionUI(IGameUI):
    """Gère toute l'interface utilisateur du jeu"""
    
    def display_welcome(self) -> None:
        """Affiche le message de bienvenue"""
        print("="*60)
        print("🎾 BIENVENUE DANS TENNISRPG !")
        print("="*60)
        
    def get_player_creation_data(self) -> Dict:
        """Récupère toutes les données pour créer le joueur principal"""
        print("\n📝 CRÉATION DE VOTRE JOUEUR")
        print("-" * 30)
        
        # Sélection du genre
        while True:
            gender_input = input("Genre - Masculin ('M') ou Féminin ('F') ? ").strip().lower()
            if gender_input in ['m', 'f']:
                gender = Gender.MALE if gender_input == 'm' else Gender.FEMALE
                break
            print("❌ Entrée invalide. Utilisez 'M' pour masculin ou 'F' pour féminin.")

        # Sélection de la difficulté
        difficulty = self.select_difficulty()
        talent_level = DIFFICULTY_TO_TALENT[difficulty]

        # Informations du joueur
        first_name = input("\n👤 Prénom de votre joueur/joueuse : ").strip()
        last_name = input("👤 Nom de famille : ").strip()
        country = input("🌍 Pays : ").strip()
        
        return {
            'gender': gender,
            'difficulty': difficulty,
            'talent_level': talent_level,
            'first_name': first_name,
            'last_name': last_name,
            'country': country
        }
        
    def select_difficulty(self) -> str:
        """Interface de sélection de difficulté"""
        print("\n🎯 SÉLECTION DE LA DIFFICULTÉ")
        print("-" * 30)
        print("Choisissez votre niveau de difficulté :")
        print("1. Novice - Génie précoce (+30% stats)")
        print("2. Facile - Pépite (+20% stats)")
        print("3. Normal - Talent brut (+10% stats)")
        print("4. Difficile - Joueur prometteur (stats normales)")
        print("5. Expert - Espoir fragile (-10% stats)")
        
        difficulty_mapping = {
            "1": "Novice",
            "2": "Facile", 
            "3": "Normal",
            "4": "Difficile",
            "5": "Expert"
        }
        
        while True:
            choice = input("\nVotre choix (1-5) : ").strip()
            if choice in difficulty_mapping:
                selected_difficulty = difficulty_mapping[choice]
                
                # Affichage de confirmation
                talent = DIFFICULTY_TO_TALENT[selected_difficulty]
                print(f"\n✅ Difficulté sélectionnée : {selected_difficulty}")
                print(f"⭐ Votre talent : {talent.value}")
                
                return selected_difficulty
            else:
                print("❌ Choix invalide. Veuillez entrer un nombre entre 1 et 5.")
                
    def display_player_created(self, player: Player, difficulty: str) -> None:
        """Affiche la confirmation de création du joueur"""
        print(f"\n✅ Joueur créé: {player.full_name} ({player.country})")
        print(f"🎯 Difficulté: {difficulty}")
        print(f"⭐ Niveau de talent: {player.talent_level.value}")
        
    def display_npc_generation_progress(self, pool_size: int) -> None:
        """Affiche les messages de génération des NPCs"""
        print("\n🤖 GÉNÉRATION DU CIRCUIT MONDIAL")
        print("-" * 35)
        print(f"⏳ Création de {pool_size} joueurs professionnels...")
        
    def display_npc_generation_progress_update(self, current: int, total: int) -> None:
        """Affiche la progression de génération"""
        print(f"   📊 {current}/{total} joueurs générés...")
        
    def display_npc_generation_complete(self, generation_time: float) -> None:
        """Affiche la fin de génération des NPCs"""
        print(f"✅ Pool généré en {generation_time:.1f} secondes")
        
    def display_preliminary_simulation_start(self) -> None:
        """Affiche le début de la simulation préliminaire"""
        print("\n⚡ SIMULATION PRÉLIMINAIRE")
        print("-" * 25)
        print("📅 Simulation de 2 années pour créer un historique réaliste...")
        print("💡 Cela permet d'avoir des classements et des rivalités naturelles")
        
    def display_preliminary_simulation_year(self, year: int) -> None:
        """Affiche l'année en cours de simulation"""
        print(f"   📈 Année {year}...")
        
    def display_preliminary_simulation_semester(self, semester: int) -> None:
        """Affiche la fin d'un semestre"""
        print(f"      ⌛ Semestre {semester} terminé")
        
    def display_preliminary_simulation_complete(self, simulation_time: float) -> None:
        """Affiche la fin de la simulation préliminaire"""
        print(f"✅ Simulation préliminaire terminée en {simulation_time:.1f} secondes")
        
    def display_main_game_initialization(self) -> None:
        """Affiche l'initialisation du jeu principal"""
        print("\n🎮 INITIALISATION DU JEU PRINCIPAL")
        print("-" * 35)
        
    def display_career_start(self, player: Player, year: int) -> None:
        """Affiche le début de carrière"""
        gender_term = "tennisman" if player.gender == Gender.MALE else "tenniswoman"
        print(f"\n🌟 Bienvenue dans votre carrière de {gender_term},")
        print(f"🌟 {player.full_name}!")
        print(f"📅 Votre aventure commence en {year}")
        
    def display_weekly_header(self, current_week: int, current_year: int, 
                            main_player: Player, ranking_manager) -> None:
        """Affiche l'en-tête hebdomadaire"""
        print("\n" + "="*60)
        print(f"📅 SEMAINE {current_week} - ANNÉE {current_year}")
        print(f"👤 {main_player.full_name}")
        
        # Informations sur la fatigue
        if hasattr(main_player, 'physical'):
            fatigue = main_player.physical.fatigue
            fatigue_emoji = "💚" if fatigue < 30 else "⚠️" if fatigue < 70 else "🔴"
            print(f"{fatigue_emoji} Fatigue: {fatigue}%")
        
        # Classement actuel
        if ranking_manager:
            atp_rank = ranking_manager.get_player_rank(main_player, RankingType.ATP)
            race_rank = ranking_manager.get_player_rank(main_player, RankingType.ATP_RACE)
            print(f"🏆 Classement ATP: #{atp_rank} | Race: #{race_rank}")
        
        print("="*60)
        
    def display_main_menu(self) -> None:
        """Affiche le menu principal"""
        print("\n📋 ACTIONS DISPONIBLES:")
        print("━━━━━━━━━━━━━━━━━━━━━━")
        print("⏭️ [ENTRÉE] Continuer vers les activités de la semaine")
        print("📊 [C] Voir les classements")  
        print("🏆 [A] Points ATP à défendre cette semaine")
        print("👤 [I] Carte d'identité de votre joueur")
        print("📈 [E] Attribuer des points d'attributs")
        print("📚 [H] Historique des tournois")
        print("💾 [S] Sauvegarder le jeu")
        print("📂 [L] Charger une autre sauvegarde")
        print("🔄 [R] Voir les retraites récentes")
        print("❌ [Q] Quitter le jeu")
        
    def get_user_input(self) -> str:
        """Récupère la saisie utilisateur"""
        return input("\n🎯 Votre choix : ").strip().lower()
        
    def display_quit_message(self) -> None:
        """Affiche le message de fin"""
        print("\n👋 MERCI D'AVOIR JOUÉ À TENNISRPG v2!")
        print("📊 Voici vos statistiques finales:")
        
    def display_invalid_choice(self) -> None:
        """Affiche un message d'erreur pour choix invalide"""
        print("❌ Action non reconnue. Utilisez les lettres indiquées ou ENTRÉE.")
        
    def get_ranking_choice(self) -> Optional[RankingType]:
        """Interface de choix de classement"""
        print("\n📊 QUEL CLASSEMENT SOUHAITEZ-VOUS VOIR ?")
        print("1. Classement ATP (52 semaines glissantes)")
        print("2. ATP Race (année en cours)")
        
        while True:
            choice = input("\n🎯 Votre choix (1-2) : ").strip()
            if choice == '1':
                return RankingType.ATP
            elif choice == '2':
                return RankingType.ATP_RACE
            else:
                print("❌ Choix invalide. Utilisez 1 ou 2.")
                
    def get_ranking_display_range(self) -> Tuple[int, int]:
        """Interface pour choisir la plage d'affichage du classement"""
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
            
        return start_rank, count
        
    def display_atp_points_to_defend(self, main_player: Player, ranking_manager, 
                                   points_to_defend: int, current_week: int = None) -> None:
        """Affiche les points ATP à défendre"""
        print("🏆 Points ATP à défendre cette semaine:")
        
        if points_to_defend == 0:
            print("💚 Aucun point à défendre cette semaine !")
        else:
            print(f"⚠️  Vous devez défendre {points_to_defend} points ATP cette semaine")
            print(f"📊 Si vous ne participez à aucun tournoi, vous perdrez {points_to_defend} points")
            
        # Affiche aussi le classement actuel pour contexte
        current_rank = ranking_manager.get_player_rank(main_player)
        if current_rank:
            print(f"📈 Classement actuel: #{current_rank} ({main_player.career.atp_points} points)")
            potential_points = max(0, main_player.career.atp_points - points_to_defend)
            print(f"💭 Points potentiels si aucune participation: {potential_points}")
        
        # Affiche les semaines suivantes avec des points à défendre
        print("\n📅 Points à défendre dans les prochaines semaines:")
        future_points = []
        # Utilise la vraie semaine courante si fournie, sinon fallback vers ranking_manager
        week_to_use = current_week if current_week is not None else ranking_manager.current_week
        for i in range(1, 5):  # 4 semaines suivantes
            future_week = (week_to_use + i - 1) % 52 + 1
            future_defend = ranking_manager.get_points_to_defend(
                main_player.full_name, future_week
            )
            if future_defend > 0:
                future_points.append((future_week, future_defend))
        
        if future_points:
            for week, points in future_points:
                print(f"   Semaine {week}: {points} points")
        else:
            print("   Aucun point à défendre dans les 4 prochaines semaines")
            
    def display_no_data_available(self, message: str = "Données non disponibles") -> None:
        """Affiche un message générique de données non disponibles"""
        print(f"❌ {message}")
        
    def get_attribute_assignment_choice(self, ap_points: int) -> Optional[str]:
        """Interface d'attribution des points d'attributs"""
        print("📈 Attribution de points d'attributs:")
        
        if ap_points == 0:
            print("💡 Aucun point AP disponible à attribuer")
            return None
            
        print(f"🎯 Points AP disponibles: {ap_points}")
        print("\nChoix d'attribution:")
        print("1. Attribution manuelle")
        print("2. Attribution automatique basée sur l'archétype")
        print("3. Retour au menu")
        
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice in ["1", "2", "3"]:
            return choice
        else:
            print("❌ Choix invalide")
            return None
            
    def display_auto_assignment_result(self, points_used: int) -> None:
        """Affiche le résultat de l'attribution automatique"""
        print(f"✅ {points_used} points attribués automatiquement selon votre archétype!")
        
    def get_save_filename(self, main_player: Player, current_week: int, current_year: int) -> str:
        """Interface de choix du nom de sauvegarde"""
        print("\n💾 SAUVEGARDE DU JEU")
        print("-" * 20)
        
        default_name = f"{main_player.first_name}_{main_player.last_name}_S{current_week}_{current_year}"
        
        print(f"💡 Nom par défaut: {default_name}")
        custom_name = input("📝 Nom de sauvegarde (ENTRÉE pour défaut) : ").strip()
        
        return custom_name if custom_name else default_name
        
    def display_save_result(self, success: bool) -> None:
        """Affiche le résultat de la sauvegarde"""
        if success:
            print("✅ Jeu sauvegardé avec succès!")
        else:
            print("❌ Erreur lors de la sauvegarde")
            
    def display_load_menu_header(self) -> None:
        """Affiche l'en-tête du menu de chargement"""
        print("\n📂 CHARGER UNE SAUVEGARDE")
        print("-" * 25)
        
    def get_save_file_choice(self, save_count: int) -> Optional[str]:
        """Interface de choix de fichier de sauvegarde"""
        if save_count == 0:
            input("\n⏎ Appuyez sur ENTRÉE pour continuer...")
            return None
            
        while True:
            choice = input(f"\n🎯 Choisir sauvegarde (1-{save_count}) ou 'q' pour annuler : ").strip()
            
            if choice.lower() == 'q':
                return 'q'
            
            if choice.isdigit() and 1 <= int(choice) <= save_count:
                return choice
            else:
                print("❌ Choix invalide")
                
    def display_load_result(self, success: bool, current_week: int = 0, 
                          current_year: int = 0, playtime_hours: float = 0) -> None:
        """Affiche le résultat du chargement"""
        if success:
            print("✅ Sauvegarde chargée avec succès!")
            print(f"📅 Position: Semaine {current_week}, Année {current_year}")
            if playtime_hours > 0:
                print(f"⏱️  Temps de jeu: {playtime_hours:.1f} heures")
        else:
            print("❌ Impossible de charger la sauvegarde")
            
    def get_load_from_entry_choice(self, save_count: int) -> Optional[str]:
        """Interface de chargement depuis le menu d'entrée"""
        print("\n📂 CHARGER UNE SAUVEGARDE")
        print("-" * 25)
        
        if save_count == 0:
            input("\n⏎ Appuyez sur ENTRÉE pour retourner au menu principal...")
            return None
            
        while True:
            choice = input(f"\n🎯 Choisir sauvegarde (1-{save_count}) ou 'q' pour retourner au menu : ").strip()
            
            if choice.lower() == 'q':
                return 'q'
            
            if choice.isdigit() and 1 <= int(choice) <= save_count:
                return choice
            else:
                print("❌ Choix invalide")
                
    def display_activity_execution_header(self) -> None:
        """Affiche l'en-tête d'exécution d'activité"""
        print("\n⚡ EXÉCUTION DE L'ACTIVITÉ...")
        print("-" * 30)
        
    def display_activity_result(self, result) -> None:
        """Affiche le résultat d'une activité"""
        if result.success:
            print(f"✅ {result.message}")
            if result.xp_gained > 0:
                print(f"📈 +{result.xp_gained} XP")
            if result.fatigue_change != 0:
                change_symbol = "+" if result.fatigue_change > 0 else ""
                print(f"💪 {change_symbol}{result.fatigue_change}% Fatigue")
        else:
            print(f"❌ {result.message}")
            
    def display_new_year(self, year: int) -> None:
        """Affiche le message de nouvelle année"""
        print(f"\n🎊 NOUVELLE ANNÉE: {year}")
        
    def display_player_birthday(self, player: Player) -> None:
        """Affiche l'anniversaire du joueur"""
        print(f"🎂 {player.full_name} a maintenant {player.career.age} ans")
        
    def display_return_to_menu(self) -> None:
        """Affiche le retour au menu"""
        print("🔙 Retour au menu principal")
        
    def display_back_to_menu_prompt(self) -> None:
        """Affiche la demande de retour au menu"""
        print("\n" + "=" * 45)
        input("⏎ Appuyez sur ENTRÉE pour revenir au menu...")
        
    def display_no_ranking_data(self) -> None:
        """Affiche l'absence de données de classement"""
        print("❌ Classements non disponibles")
        
    def display_no_activity_manager(self) -> None:
        """Affiche l'absence de gestionnaire d'activités"""
        print("❌ Gestionnaire d'activités non initialisé")
        
    def display_no_main_player(self) -> None:
        """Affiche l'absence de joueur principal"""
        print("❌ Aucun joueur principal défini")
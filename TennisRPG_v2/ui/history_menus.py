"""
Menus d'interface utilisateur pour le système d'historique des tournois
"""
from typing import Optional

from ..managers.history_manager import HistoryManager
from ..entities.player import Player
from ..data.tournaments_data import TournamentCategory


class HistoryMenus:
    """Gestionnaire des menus d'historique"""
    
    def __init__(self, history_manager: HistoryManager):
        self.history_manager = history_manager
    
    def show_main_history_menu(self, main_player: Player, all_players: dict) -> None:
        """
        Affiche le menu principal d'historique
        
        Args:
            main_player: Joueur principal
            all_players: Dictionnaire de tous les joueurs
        """
        while True:
            print("\n" + "="*60)
            print("📚 MENU HISTORIQUE DES TOURNOIS")
            print("="*60)
            print("1. Historique par joueur")
            print("2. Historique par tournoi")
            print("3. Retour au menu principal")
            print("="*60)
            
            try:
                choice = input("\n➤ Votre choix (1-3): ").strip()
                
                if choice == "1":
                    self.show_player_history_menu(main_player, all_players)
                elif choice == "2":
                    self.show_tournament_history_menu()
                elif choice == "3":
                    break
                else:
                    print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")
                    
            except KeyboardInterrupt:
                print("\n👋 Retour au menu principal...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def show_player_history_menu(self, main_player: Player, all_players: dict) -> None:
        """
        Menu pour consulter l'historique d'un joueur
        
        Args:
            main_player: Joueur principal
            all_players: Dictionnaire de tous les joueurs
        """
        while True:
            print("\n" + "="*50)
            print("👤 HISTORIQUE PAR JOUEUR")
            print("="*50)
            print("1. Mon historique (joueur principal)")
            print("2. Historique d'un autre joueur")
            print("3. Retour")
            print("="*50)
            
            try:
                choice = input("\n➤ Votre choix (1-3): ").strip()
                
                if choice == "1":
                    self.show_player_year_selection(main_player)
                elif choice == "2":
                    self.show_other_player_selection(all_players)
                elif choice == "3":
                    break
                else:
                    print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")
                    
            except KeyboardInterrupt:
                print("\n👋 Retour au menu précédent...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def show_player_year_selection(self, player: Player) -> None:
        """
        Menu de sélection d'année pour un joueur
        
        Args:
            player: Joueur concerné
        """
        years = self.history_manager.get_years_with_data()
        
        if not years:
            print("\n📊 Aucune donnée d'historique disponible.")
            input("\nAppuyez sur Entrée pour continuer...")
            return
        
        while True:
            print(f"\n" + "="*50)
            print(f"📅 SÉLECTION D'ANNÉE - {player.full_name}")
            print("="*50)
            
            for i, year in enumerate(years, 1):
                print(f"{i}. {year}")
            
            print(f"{len(years) + 1}. Retour")
            print("="*50)
            
            try:
                choice = input(f"\n➤ Choisissez une année (1-{len(years) + 1}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(years):
                    selected_year = years[choice_num - 1]
                    self.history_manager.display_player_year_history(player, selected_year)
                    input("\nAppuyez sur Entrée pour continuer...")
                elif choice_num == len(years) + 1:
                    break
                else:
                    print(f"❌ Choix invalide. Veuillez entrer un nombre entre 1 et {len(years) + 1}.")
                    
            except ValueError:
                print("❌ Veuillez entrer un nombre valide.")
            except KeyboardInterrupt:
                print("\n👋 Retour au menu précédent...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def show_other_player_selection(self, all_players: dict) -> None:
        """
        Menu de sélection d'un autre joueur
        
        Args:
            all_players: Dictionnaire de tous les joueurs
        """
        # Filtre les joueurs principaux
        other_players = {name: player for name, player in all_players.items() 
                        if not (hasattr(player, 'is_main_player') and player.is_main_player)}
        
        if not other_players:
            print("\n👥 Aucun autre joueur disponible.")
            input("\nAppuyez sur Entrée pour continuer...")
            return
        
        # Trie les joueurs par classement ATP (du plus haut au plus bas)
        sorted_players = sorted(other_players.items(), key=lambda x: x[1].career.atp_points, reverse=True)
        
        # Affichage paginé si trop de joueurs
        page_size = 15
        total_pages = (len(sorted_players) + page_size - 1) // page_size
        current_page = 0
        
        while True:
            print("\n" + "="*60)
            print("👥 SÉLECTION D'UN JOUEUR")
            print("="*60)
            
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(sorted_players))
            
            for i, (name, player) in enumerate(sorted_players[start_idx:end_idx], start_idx + 1):
                print(f"{i}. {player.full_name} ({player.career.atp_points} pts ATP)")
            
            print(f"\n📄 Page {current_page + 1}/{total_pages}")
            if total_pages > 1:
                print("n. Page suivante | p. Page précédente")
            print("0. Retour")
            print("="*60)
            
            try:
                choice = input(f"\n➤ Votre choix: ").strip().lower()
                
                if choice == "0":
                    break
                elif choice == "n" and current_page < total_pages - 1:
                    current_page += 1
                    continue
                elif choice == "p" and current_page > 0:
                    current_page -= 1
                    continue
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(sorted_players):
                        selected_player = sorted_players[choice_num - 1][1]
                        self.show_player_year_selection(selected_player)
                    else:
                        print(f"❌ Choix invalide. Veuillez entrer un nombre entre 1 et {len(sorted_players)}.")
                except ValueError:
                    print("❌ Veuillez entrer un nombre valide ou 'n'/'p' pour naviguer.")
                    
            except KeyboardInterrupt:
                print("\n👋 Retour au menu précédent...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def show_tournament_history_menu(self) -> None:
        """Menu principal pour l'historique par tournoi"""
        while True:
            print("\n" + "="*50)
            print("🏆 HISTORIQUE PAR TOURNOI")
            print("="*50)
            print("1. Grand Chelem")
            print("2. ATP")
            print("3. Challenger")
            print("4. Retour")
            print("="*50)
            
            try:
                choice = input("\n➤ Votre choix (1-4): ").strip()
                
                if choice == "1":
                    self.show_grand_slam_menu()
                elif choice == "2":
                    self.show_atp_menu()
                elif choice == "3":
                    self.show_challenger_menu()
                elif choice == "4":
                    break
                else:
                    print("❌ Choix invalide. Veuillez entrer 1, 2, 3 ou 4.")
                    
            except KeyboardInterrupt:
                print("\n👋 Retour au menu précédent...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def show_grand_slam_menu(self) -> None:
        """Menu des tournois du Grand Chelem"""
        grand_slams = self.history_manager.get_grand_slam_tournaments()
        
        if not grand_slams:
            print("\n🎾 Aucun tournoi du Grand Chelem dans l'historique.")
            input("\nAppuyez sur Entrée pour continuer...")
            return
        
        self._show_tournament_selection_menu("Grand Chelem", list(grand_slams))
    
    def show_atp_menu(self) -> None:
        """Menu des tournois ATP par catégorie"""
        atp_tournaments = self.history_manager.get_atp_tournaments_by_level()
        
        if not any(atp_tournaments.values()):
            print("\n🎾 Aucun tournoi ATP dans l'historique.")
            input("\nAppuyez sur Entrée pour continuer...")
            return
        
        while True:
            print("\n" + "="*50)
            print("🏆 TOURNOIS ATP")
            print("="*50)
            
            menu_items = []
            for level, tournaments in atp_tournaments.items():
                if tournaments:  # Seulement si des tournois existent
                    menu_items.append((level, tournaments))
            
            if not menu_items:
                print("Aucun tournoi ATP disponible.")
                input("\nAppuyez sur Entrée pour continuer...")
                break
            
            for i, (level, _) in enumerate(menu_items, 1):
                print(f"{i}. {level}")
            
            print(f"{len(menu_items) + 1}. Retour")
            print("="*50)
            
            try:
                choice = input(f"\n➤ Votre choix (1-{len(menu_items) + 1}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(menu_items):
                    level, tournaments = menu_items[choice_num - 1]
                    self._show_tournament_selection_menu(level, list(tournaments))
                elif choice_num == len(menu_items) + 1:
                    break
                else:
                    print(f"❌ Choix invalide. Veuillez entrer un nombre entre 1 et {len(menu_items) + 1}.")
                    
            except ValueError:
                print("❌ Veuillez entrer un nombre valide.")
            except KeyboardInterrupt:
                print("\n👋 Retour au menu précédent...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def show_challenger_menu(self) -> None:
        """Menu des tournois Challenger par catégorie"""
        challenger_tournaments = self.history_manager.get_challenger_tournaments_by_level()
        
        if not any(challenger_tournaments.values()):
            print("\n🎾 Aucun tournoi Challenger dans l'historique.")
            input("\nAppuyez sur Entrée pour continuer...")
            return
        
        while True:
            print("\n" + "="*50)
            print("🏆 TOURNOIS CHALLENGER")
            print("="*50)
            
            menu_items = []
            for level, tournaments in challenger_tournaments.items():
                if tournaments:  # Seulement si des tournois existent
                    menu_items.append((level, tournaments))
            
            if not menu_items:
                print("Aucun tournoi Challenger disponible.")
                input("\nAppuyez sur Entrée pour continuer...")
                break
            
            for i, (level, _) in enumerate(menu_items, 1):
                print(f"{i}. {level}")
            
            print(f"{len(menu_items) + 1}. Retour")
            print("="*50)
            
            try:
                choice = input(f"\n➤ Votre choix (1-{len(menu_items) + 1}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(menu_items):
                    level, tournaments = menu_items[choice_num - 1]
                    self._show_tournament_selection_menu(level, list(tournaments))
                elif choice_num == len(menu_items) + 1:
                    break
                else:
                    print(f"❌ Choix invalide. Veuillez entrer un nombre entre 1 et {len(menu_items) + 1}.")
                    
            except ValueError:
                print("❌ Veuillez entrer un nombre valide.")
            except KeyboardInterrupt:
                print("\n👋 Retour au menu précédent...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def _show_tournament_selection_menu(self, category_name: str, tournaments: list) -> None:
        """
        Menu générique de sélection de tournoi
        
        Args:
            category_name: Nom de la catégorie
            tournaments: Liste des noms de tournois
        """
        tournaments.sort()  # Trie alphabétiquement
        
        while True:
            print(f"\n" + "="*60)
            print(f"🏆 TOURNOIS {category_name.upper()}")
            print("="*60)
            
            for i, tournament in enumerate(tournaments, 1):
                print(f"{i}. {tournament}")
            
            print(f"{len(tournaments) + 1}. Retour")
            print("="*60)
            
            try:
                choice = input(f"\n➤ Choisissez un tournoi (1-{len(tournaments) + 1}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(tournaments):
                    selected_tournament = tournaments[choice_num - 1]
                    self.history_manager.display_tournament_history(selected_tournament)
                    input("\nAppuyez sur Entrée pour continuer...")
                elif choice_num == len(tournaments) + 1:
                    break
                else:
                    print(f"❌ Choix invalide. Veuillez entrer un nombre entre 1 et {len(tournaments) + 1}.")
                    
            except ValueError:
                print("❌ Veuillez entrer un nombre valide.")
            except KeyboardInterrupt:
                print("\n👋 Retour au menu précédent...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
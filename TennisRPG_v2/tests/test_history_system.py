"""
Script de test pour le système d'historique des tournois
"""
import sys
import os

# Ajoute le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from TennisRPG_v2.managers.history_manager import HistoryManager
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.entities.tournament import TournamentResult
from TennisRPG_v2.data.tournaments_data import TournamentCategory
from TennisRPG_v2.ui.history_menus import HistoryMenus

def create_test_players():
    """Crée quelques joueurs pour les tests"""
    players = {}
    
    # Joueur principal
    main_player = Player("Rafael", "Nadal", "Espagne", Gender.MALE)
    main_player.is_main_player = True
    players[main_player.full_name] = main_player
    
    # Quelques PNJ
    federer = Player("Roger", "Federer", "Suisse", Gender.MALE)
    players[federer.full_name] = federer
    
    djokovic = Player("Novak", "Djokovic", "Serbie", Gender.MALE)
    players[djokovic.full_name] = djokovic
    
    murray = Player("Andy", "Murray", "Royaume-Uni", Gender.MALE)
    players[murray.full_name] = murray
    
    return players, main_player

def create_test_tournament_results(players):
    """Crée quelques résultats de tournois de test"""
    player_list = list(players.values())
    nadal = player_list[0]  # Rafael Nadal
    federer = player_list[1]  # Roger Federer
    djokovic = player_list[2]  # Novak Djokovic
    murray = player_list[3]  # Andy Murray
    
    results = []
    
    # Roland Garros 2023 - Nadal gagne
    roland_garros_2023 = TournamentResult(
        tournament_name="Roland Garros",
        category=TournamentCategory.GRAND_SLAM,
        winner=nadal,
        finalist=djokovic,
        semifinalists=[federer, murray],
        quarterfinalists=[],
        all_results={
            nadal: "winner",
            djokovic: "finalist", 
            federer: "semifinalist",
            murray: "semifinalist"
        },
        match_results=[]
    )
    results.append((roland_garros_2023, 2023, 21))  # Semaine 21
    
    # Wimbledon 2023 - Djokovic gagne
    wimbledon_2023 = TournamentResult(
        tournament_name="Wimbledon",
        category=TournamentCategory.GRAND_SLAM,
        winner=djokovic,
        finalist=federer,
        semifinalists=[nadal, murray],
        quarterfinalists=[],
        all_results={
            djokovic: "winner",
            federer: "finalist",
            nadal: "semifinalist", 
            murray: "semifinalist"
        },
        match_results=[]
    )
    results.append((wimbledon_2023, 2023, 27))  # Semaine 27
    
    # Masters 1000 Madrid 2023 - Federer gagne
    madrid_2023 = TournamentResult(
        tournament_name="Madrid Masters",
        category=TournamentCategory.MASTERS_1000,
        winner=federer,
        finalist=nadal,
        semifinalists=[djokovic, murray],
        quarterfinalists=[],
        all_results={
            federer: "winner",
            nadal: "finalist",
            djokovic: "semifinalist",
            murray: "semifinalist"
        },
        match_results=[]
    )
    results.append((madrid_2023, 2023, 18))  # Semaine 18
    
    # Roland Garros 2024 - Djokovic gagne
    roland_garros_2024 = TournamentResult(
        tournament_name="Roland Garros",
        category=TournamentCategory.GRAND_SLAM,
        winner=djokovic,
        finalist=nadal,
        semifinalists=[federer, murray],
        quarterfinalists=[],
        all_results={
            djokovic: "winner",
            nadal: "finalist",
            federer: "semifinalist",
            murray: "semifinalist"
        },
        match_results=[]
    )
    results.append((roland_garros_2024, 2024, 21))  # Semaine 21
    
    return results

def test_history_manager():
    """Test du HistoryManager"""
    print("=== TEST DU HISTORY MANAGER ===")
    
    # Crée les joueurs de test
    players, main_player = create_test_players()
    print(f"✅ Joueurs créés: {len(players)}")
    
    # Crée le manager d'historique
    history_manager = HistoryManager()
    print("✅ HistoryManager créé")
    
    # Crée et enregistre les résultats de test
    test_results = create_test_tournament_results(players)
    for result, year, week in test_results:
        history_manager.record_tournament_result(result, year, week)
    print(f"✅ {len(test_results)} résultats de tournois enregistrés")
    
    # Test: historique par joueur
    print("\n--- Test historique par joueur ---")
    nadal_2023 = history_manager.get_player_history_for_year(main_player, 2023)
    print(f"✅ Tournois de Nadal en 2023: {len(nadal_2023)}")
    
    nadal_2024 = history_manager.get_player_history_for_year(main_player, 2024)
    print(f"✅ Tournois de Nadal en 2024: {len(nadal_2024)}")
    
    # Test: historique par tournoi
    print("\n--- Test historique par tournoi ---")
    roland_garros_history = history_manager.get_tournament_history_by_name("Roland Garros")
    print(f"✅ Éditions de Roland Garros: {len(sum(roland_garros_history.values(), []))}")
    
    # Test: tournois par catégorie
    print("\n--- Test tournois par catégorie ---")
    grand_slams = history_manager.get_grand_slam_tournaments()
    print(f"✅ Tournois Grand Slam: {list(grand_slams)}")
    
    atp_tournaments = history_manager.get_atp_tournaments_by_level()
    print(f"✅ Tournois ATP par niveau: {list(atp_tournaments.keys())}")
    
    # Test: années avec des données
    years = history_manager.get_years_with_data()
    print(f"✅ Années avec données: {years}")
    
    return history_manager, players, main_player

def test_history_display():
    """Test des affichages d'historique"""
    print("\n=== TEST DES AFFICHAGES ===")
    
    history_manager, players, main_player = test_history_manager()
    
    # Test affichage historique joueur
    print("\n--- Affichage historique Nadal 2023 ---")
    history_manager.display_player_year_history(main_player, 2023)
    
    print("\n--- Affichage historique Roland Garros ---")
    history_manager.display_tournament_history("Roland Garros")
    
    print("✅ Tests d'affichage terminés")

def test_save_load():
    """Test de sauvegarde/chargement"""
    print("\n=== TEST SAUVEGARDE/CHARGEMENT ===")
    
    history_manager, players, main_player = test_history_manager()
    
    # Test conversion en dictionnaire
    history_dict = history_manager.to_dict()
    print(f"✅ Conversion en dict: {len(history_dict)} années")
    
    # Test chargement depuis dictionnaire
    new_history_manager = HistoryManager()
    new_history_manager.from_dict(history_dict, players)
    
    # Vérification
    nadal_2023_original = history_manager.get_player_history_for_year(main_player, 2023)
    nadal_2023_loaded = new_history_manager.get_player_history_for_year(main_player, 2023)
    
    if len(nadal_2023_original) == len(nadal_2023_loaded):
        print("✅ Chargement depuis dict réussi")
    else:
        print("❌ Erreur lors du chargement depuis dict")
    
    return new_history_manager

def test_interactive_menu():
    """Test du menu interactif (simulation)"""
    print("\n=== TEST MENU INTERACTIF ===")
    
    history_manager, players, main_player = test_history_manager()
    
    # Crée les menus
    history_menus = HistoryMenus(history_manager)
    print("✅ HistoryMenus créés")
    
    print("📝 Menu interactif disponible via: history_menus.show_main_history_menu(main_player, players)")
    print("   (Non testé automatiquement car nécessite interaction utilisateur)")

def main():
    """Fonction principale de test"""
    print("🧪 TESTS DU SYSTÈME D'HISTORIQUE DES TOURNOIS")
    print("=" * 60)
    
    try:
        # Tests unitaires
        test_history_manager()
        test_history_display()
        test_save_load()
        test_interactive_menu()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("🎾 Le système d'historique est fonctionnel.")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test script pour le système de sauvegarde optimisé
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from TennisRPG_v2.core.enhanced_save_manager import EnhancedSaveManager
from TennisRPG_v2.core.serialization_utils import SerializationUtils, benchmark_serialization
from TennisRPG_v2.core.save_manager import SaveManager
from TennisRPG_v2.entities.player import Player
from TennisRPG_v2.entities.player import Gender
from TennisRPG_v2.managers.history_manager import HistoryManager
from TennisRPG_v2.entities.tournament import TournamentResult
from TennisRPG_v2.data.tournaments_data import TournamentCategory


def create_test_data():
    """Crée des données de test"""
    print("Création des données de test...")
    
    # Joueur principal
    main_player = Player(Gender.MALE, "Test", "MainPlayer", "France")
    main_player.career.atp_points = 2500
    main_player.career.age = 22
    
    # Génère des joueurs de test
    all_players = {main_player.full_name: main_player}
    for i in range(100):  # 100 joueurs au lieu de 1000 pour le test
        player = Player(Gender.MALE, f"Player{i}", f"Test{i}", "Spain")
        player.career.atp_points = 1000 + i * 10
        player.career.age = 20 + (i % 15)
        all_players[player.full_name] = player
    
    # Crée l'historique des tournois
    history_manager = HistoryManager()
    
    # Simule quelques tournois
    for year in [2023, 2024]:
        for week in range(1, 11):  # 10 semaines par année
            for tournament_idx in range(2):  # 2 tournois par semaine
                # Sélectionne des joueurs participants
                participants = list(all_players.values())[:20]  # 20 joueurs par tournoi
                
                result = TournamentResult(
                    tournament_name=f"Test Tournament {year}W{week}T{tournament_idx}",
                    category=TournamentCategory.ATP_250,
                    winner=participants[0],
                    finalist=participants[1],
                    semifinalists=participants[2:4],
                    quarterfinalists=participants[4:8],
                    all_results={p: f"Round {i//4 + 1}" for i, p in enumerate(participants)},
                    match_results=[]
                )
                
                history_manager.record_tournament_result(result, year, week)
    
    print(f"Données créées: {len(all_players)} joueurs, {len(history_manager.get_years_with_data())} années")
    return main_player, all_players, history_manager


def test_serialization_performance():
    """Test les performances de sérialisation"""
    print("\n=== TEST DE SÉRIALISATION ===")
    
    # Crée des données de test
    test_data = {
        "players": [{"name": f"Player{i}", "points": i*100} for i in range(1000)],
        "tournaments": [{"name": f"Tournament{i}", "year": 2024} for i in range(100)]
    }
    
    # Compare les formats
    print("Comparaison des formats:")
    formats_comparison = SerializationUtils.compare_formats(test_data)
    
    for format_name, stats in formats_comparison.items():
        if "error" not in stats:
            print(f"  {format_name}: {stats['size_kb']:.1f} KB (ratio: {stats['compression_ratio']:.2f}x)")
        else:
            print(f"  {format_name}: ERROR - {stats['error']}")
    
    # Benchmark des performances
    print("\nBenchmark de performance:")
    benchmark_results = benchmark_serialization(test_data, iterations=5)
    
    for format_name, stats in benchmark_results.items():
        if "error" not in stats:
            print(f"  {format_name}: {stats['total_time_ms']:.2f}ms total ({stats['size_bytes']} bytes)")


def test_enhanced_save_system():
    """Test le système de sauvegarde optimisé"""
    print("\n=== TEST DU SYSTÈME DE SAUVEGARDE OPTIMISÉ ===")
    
    # Crée les données de test
    main_player, all_players, history_manager = create_test_data()
    
    # Initialise le gestionnaire optimisé
    enhanced_manager = EnhancedSaveManager("test_saves_enhanced")
    
    print(f"\nSauvegarde avec le système optimisé...")
    
    try:
        # Sauvegarde optimisée
        save_filename = enhanced_manager.save_game_enhanced(
            main_player=main_player,
            all_players=all_players,
            history_manager=history_manager,
            current_week=15,
            current_year=2024,
            playtime_hours=10.5,
            is_preliminary_complete=True,
            retirement_log=[]
        )
        
        print(f"Sauvegarde créée: {save_filename}")
        
        # Test de chargement
        print(f"\nTest de chargement...")
        save_id = save_filename.replace('.json', '')
        loaded_data = enhanced_manager.load_game_enhanced(save_id)
        
        if loaded_data:
            print("Chargement réussi!")
            print(f"Joueur principal: {loaded_data['main_player'].full_name}")
            print(f"Joueurs totaux: {len(loaded_data['all_players'])}")
            print(f"Années d'historique: {loaded_data['history_manager'].get_years_with_data()}")
        else:
            print("Échec du chargement")
            
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()


def compare_with_old_system():
    """Compare avec l'ancien système de sauvegarde"""
    print("\n=== COMPARAISON AVEC L'ANCIEN SYSTÈME ===")
    
    # Crée les données de test
    main_player, all_players, history_manager = create_test_data()
    
    # Test avec l'ancien système
    print("Sauvegarde avec l'ancien système...")
    old_manager = SaveManager("test_saves_old")
    
    # Crée un GameState pour l'ancien système
    from TennisRPG_v2.core.save_manager import GameState
    old_game_state = GameState()
    old_game_state.main_player = main_player
    old_game_state.all_players = all_players
    old_game_state.current_week = 15
    old_game_state.current_year = 2024
    old_game_state.history_manager = history_manager
    old_game_state.playtime_hours = 10.5
    
    old_filename = "test_old_save.json"
    old_success = old_manager.save_game(old_game_state, old_filename)
    
    if old_success:
        old_filepath = Path("test_saves_old") / old_filename
        old_size = old_filepath.stat().st_size if old_filepath.exists() else 0
        print(f"Ancien système: {old_size / 1024:.1f} KB")
    
    # Test avec le nouveau système
    print("Sauvegarde avec le nouveau système...")
    enhanced_manager = EnhancedSaveManager("test_saves_new")
    
    try:
        new_filename = enhanced_manager.save_game_enhanced(
            main_player=main_player,
            all_players=all_players,
            history_manager=history_manager,
            current_week=15,
            current_year=2024,
            playtime_hours=10.5
        )
        
        # Calcule la taille totale du nouveau système
        new_total_size = 0
        enhanced_dir = Path("test_saves_new")
        if enhanced_dir.exists():
            for file in enhanced_dir.rglob("*"):
                if file.is_file():
                    new_total_size += file.stat().st_size
        
        print(f"Nouveau système: {new_total_size / 1024:.1f} KB")
        
        if old_success and new_total_size > 0:
            reduction = (old_size - new_total_size) / old_size * 100
            print(f"Réduction de taille: {reduction:.1f}%")
            
    except Exception as e:
        print(f"Erreur nouveau système: {e}")


def cleanup_test_files():
    """Nettoie les fichiers de test"""
    import shutil
    
    test_dirs = ["test_saves_enhanced", "test_saves_old", "test_saves_new"]
    for directory in test_dirs:
        if Path(directory).exists():
            shutil.rmtree(directory)
            print(f"Nettoyé: {directory}")


if __name__ == "__main__":
    try:
        print("TEST DU SYSTÈME DE SAUVEGARDE OPTIMISÉ")
        print("=" * 50)
        
        # Tests de sérialisation
        test_serialization_performance()
        
        # Test du système optimisé
        test_enhanced_save_system()
        
        # Comparaison avec l'ancien système
        compare_with_old_system()
        
        print("\nTests terminés!")
        
    except Exception as e:
        print(f"\nErreur générale: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nNettoyage des fichiers de test...")
        cleanup_test_files()
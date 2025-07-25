#!/usr/bin/env python3
"""
Test de l'intégration du système de sauvegarde optimisé
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from TennisRPG_v2.core.game_session_state import GameSessionState
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.history_manager import HistoryManager
from TennisRPG_v2.entities.tournament import TournamentResult
from TennisRPG_v2.data.tournaments_data import TournamentCategory


def test_integration():
    """Test l'intégration du système optimisé"""
    print("Test d'intégration du système de sauvegarde optimisé")
    print("=" * 60)
    
    # Crée une session de jeu
    session = GameSessionState()
    
    # Crée un joueur principal
    main_player = Player(Gender.MALE, "Integration", "Test", "France")
    main_player.career.atp_points = 1500
    main_player.career.age = 20
    
    session.set_main_player(main_player)
    
    # Ajoute quelques joueurs adversaires
    for i in range(10):
        player = Player(Gender.MALE, f"Player{i}", f"Test{i}", "Spain")
        player.career.atp_points = 1000 + i * 50
        session.add_player(player)
    
    # Initialise les managers
    session.initialize_ranking_manager()
    session.initialize_atp_points_manager()
    session.initialize_activity_manager()
    
    # Ajoute quelques données d'historique
    if session.game_state and session.game_state.history_manager:
        participants = list(session.all_players.values())[:5]
        result = TournamentResult(
            tournament_name="Test Integration Tournament",
            category=TournamentCategory.ATP_250,
            winner=participants[0],
            finalist=participants[1],
            semifinalists=participants[2:4],
            quarterfinalists=participants[4:5],
            all_results={p: f"Round {i+1}" for i, p in enumerate(participants)},
            match_results=[]
        )
        session.game_state.history_manager.record_tournament_result(result, 2023, 10)
    
    # Avance quelques semaines pour tester la progression d'année
    print(f"État initial: Année {session.current_year}, Semaine {session.current_week}")
    
    for week in range(45):  # Avance 45 semaines pour changer d'année
        session.advance_week()
    
    print(f"Après progression: Année {session.current_year}, Semaine {session.current_week}")
    
    # Test de sauvegarde
    print("\nTest de sauvegarde...")
    save_success = session.save_game("test_integration")
    print(f"Sauvegarde réussie: {save_success}")
    
    if save_success:
        # Test d'affichage des sauvegardes
        print("\nAffichage des sauvegardes disponibles:")
        session.display_saves_menu()
        
        # Test de chargement
        print("\nTest de chargement...")
        # Modifie l'état pour tester le chargement
        original_week = session.current_week
        session.current_week = 999  # Valeur temporaire
        
        load_success = session.load_game("test_integration")
        print(f"Chargement réussi: {load_success}")
        
        if load_success:
            print(f"État après chargement: Année {session.current_year}, Semaine {session.current_week}")
            print(f"Joueur principal: {session.main_player.full_name if session.main_player else 'None'}")
            print(f"Nombre de joueurs: {len(session.all_players)}")
            
            if session.game_state and session.game_state.history_manager:
                years = session.game_state.history_manager.get_years_with_data()
                print(f"Années d'historique: {years}")
    
    print("\nTest terminé!")


def cleanup():
    """Nettoie les fichiers de test"""
    import shutil
    
    test_dirs = ["saves"]
    for directory in test_dirs:
        if Path(directory).exists():
            # Supprime seulement les fichiers de test
            for file in Path(directory).glob("*test_integration*"):
                try:
                    if file.is_file():
                        file.unlink()
                    elif file.is_dir():
                        shutil.rmtree(file)
                except:
                    pass


if __name__ == "__main__":
    try:
        test_integration()
    except Exception as e:
        print(f"\nErreur lors du test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nNettoyage des fichiers de test...")
        cleanup()
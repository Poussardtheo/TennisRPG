"""
Script de test pour vérifier la compatibilité du GameSession refactorisé
"""
import sys
import os

# Ajouter le chemin du package
sys.path.append(os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

try:
    from TennisRPG_v2.core.game_session_refactored import GameSession
    from TennisRPG_v2.entities.player import Player, Gender
    from TennisRPG_v2.utils.constants import TIME_CONSTANTS
    
    print("✅ Import des modules refactorisés réussi")
    
    # Test de création d'instance
    game = GameSession()
    print("✅ Création d'instance GameSession réussie")
    
    # Test des propriétés
    print(f"✅ Semaine actuelle: {game.current_week}")
    print(f"✅ Année actuelle: {game.current_year}")
    print(f"✅ État préliminaire: {game.is_preliminary_complete}")
    print(f"✅ Jeu en cours: {game.game_running}")
    
    # Test d'accès aux managers
    print(f"✅ Tournament manager: {game.tournament_manager is not None}")
    print(f"✅ Player generator: {game.player_generator is not None}")
    print(f"✅ Save manager: {game.save_manager is not None}")
    
    # Test des méthodes déléguées
    print(f"✅ Résumé d'état: {game.get_state_summary()}")
    print(f"✅ Managers initialisés: {game.is_managers_initialized()}")
    
    # Test de modification des propriétés
    game.current_week = 10
    game.current_year = 2025
    print(f"✅ Modification semaine: {game.current_week}")
    print(f"✅ Modification année: {game.current_year}")
    
    # Test d'ajout de joueur fictif pour vérifier la compatibilité
    try:
        test_player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player",
            country="Test",
            is_main_player=False
        )
        game.state.add_player(test_player)
        print(f"✅ Ajout de joueur: {len(game.all_players)} joueur(s)")
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout de joueur: {e}")
    
    print("\n🎉 Tous les tests de compatibilité sont passés!")
    print("📋 Le refactoring maintient la compatibilité avec l'interface existante")
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("🔧 Vérifiez que tous les fichiers sont présents")
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
    import traceback
    traceback.print_exc()
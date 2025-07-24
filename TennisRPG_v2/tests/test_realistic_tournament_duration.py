#!/usr/bin/env python3
"""
Test pour vérifier que les tournois à 7 tours avancent de 1 ou 2 semaines 
selon le tour d'élimination du joueur principal
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

from entities.player import Player, Gender
from entities.spectialized_tournaments import GrandSlam, Masters1000
from managers.weekly_activity_manager import TournamentActivity, ActivityResult
from core.game_session_controller import GameSessionController
from core.game_session_state import GameSessionState
from core.game_session_ui import GameSessionUI

def create_mock_main_player():
    """Crée un joueur principal factice"""
    return Player(
        gender=Gender.MALE,
        first_name="Test",
        last_name="Player",
        country="France",
        is_main_player=True
    )

def test_early_elimination_logic():
    """Test la logique d'élimination précoce (1 semaine)"""
    
    # Crée un contrôleur de jeu factice
    ui = GameSessionUI()
    state = GameSessionState()
    state.main_player = create_mock_main_player()
    controller = GameSessionController(ui, state)
    
    # Crée un Grand Slam
    grand_slam = GrandSlam("US Open", "New York", "Hard Court", 128)
    tournament_activity = TournamentActivity(grand_slam)
    
    # Crée un résultat factice
    result = ActivityResult("Tournoi", True, "Test message")
    
    # Test 1: Élimination au 1er tour (round_128) -> 1 semaine
    grand_slam.eliminated_players[state.main_player] = "round_128"
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity, result)
    assert weeks_to_advance == 1, f"Élimination round_128 devrait donner 1 semaine, obtenu {weeks_to_advance}"
    
    # Test 2: Élimination au 2ème tour (round_64) -> 1 semaine  
    grand_slam.eliminated_players[state.main_player] = "round_64"
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity, result)
    assert weeks_to_advance == 1, f"Élimination round_64 devrait donner 1 semaine, obtenu {weeks_to_advance}"
    
    # Test 3: Élimination au 3ème tour (round_32) -> 1 semaine
    grand_slam.eliminated_players[state.main_player] = "round_32"
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity, result)
    assert weeks_to_advance == 1, f"Élimination round_32 devrait donner 1 semaine, obtenu {weeks_to_advance}"
    
    print("✅ Test d'élimination précoce réussi!")

def test_late_elimination_logic():
    """Test la logique d'élimination tardive (2 semaines)"""
    
    # Crée un contrôleur de jeu factice
    ui = GameSessionUI()
    state = GameSessionState()
    state.main_player = create_mock_main_player()
    controller = GameSessionController(ui, state)
    
    # Crée un Grand Slam
    grand_slam = GrandSlam("Wimbledon", "London", "Grass", 128)
    tournament_activity = TournamentActivity(grand_slam)
    
    # Crée un résultat factice
    result = ActivityResult("Tournoi", True, "Test message")
    
    # Test 1: Élimination au 4ème tour (round_16) -> 2 semaines
    grand_slam.eliminated_players[state.main_player] = "round_16"
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity, result)
    assert weeks_to_advance == 2, f"Élimination round_16 devrait donner 2 semaines, obtenu {weeks_to_advance}"
    
    # Test 2: Élimination en quart de finale -> 2 semaines
    grand_slam.eliminated_players[state.main_player] = "quarterfinalist"
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity, result)
    assert weeks_to_advance == 2, f"Élimination quarterfinalist devrait donner 2 semaines, obtenu {weeks_to_advance}"
    
    # Test 3: Élimination en demi-finale -> 2 semaines
    grand_slam.eliminated_players[state.main_player] = "semifinalist"
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity, result)
    assert weeks_to_advance == 2, f"Élimination semifinalist devrait donner 2 semaines, obtenu {weeks_to_advance}"
    
    # Test 4: Finaliste -> 2 semaines
    grand_slam.eliminated_players[state.main_player] = "finalist"
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity, result)
    assert weeks_to_advance == 2, f"Finaliste devrait donner 2 semaines, obtenu {weeks_to_advance}"
    
    print("✅ Test d'élimination tardive réussi!")

def test_victory_logic():
    """Test la logique de victoire (2 semaines)"""
    
    # Crée un contrôleur de jeu factice
    ui = GameSessionUI()
    state = GameSessionState()
    state.main_player = create_mock_main_player()
    controller = GameSessionController(ui, state)
    
    # Crée un Grand Slam
    grand_slam = GrandSlam("Roland Garros", "Paris", "Clay", 128)
    tournament_activity = TournamentActivity(grand_slam)
    
    # Ajoute le joueur principal aux participants
    grand_slam.participants.append(state.main_player)
    
    # Crée un résultat factice
    result = ActivityResult("Tournoi", True, "Test message")
    
    # Test: Victoire (pas dans eliminated_players) -> 2 semaines
    # Le joueur principal participe mais n'est pas dans eliminated_players = victoire
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity, result)
    assert weeks_to_advance == 2, f"Victoire devrait donner 2 semaines, obtenu {weeks_to_advance}"
    
    print("✅ Test de logique de victoire réussi!")

def test_non_7_round_tournaments():
    """Test que les tournois non-7 tours donnent toujours 1 semaine"""
    
    # Crée un contrôleur de jeu factice
    ui = GameSessionUI()
    state = GameSessionState()
    state.main_player = create_mock_main_player()
    controller = GameSessionController(ui, state)
    
    # Test avec Masters 1000 à 64 joueurs (6 tours)
    masters_64 = Masters1000("Monte Carlo", "Monte Carlo", "Clay", 64)
    tournament_activity_64 = TournamentActivity(masters_64)
    result = ActivityResult("Tournoi", True, "Test message")
    
    # Même si éliminé tard, devrait rester 1 semaine pour un tournoi 6 tours
    masters_64.eliminated_players[state.main_player] = "finalist"
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity_64, result)
    assert weeks_to_advance == 1, f"Masters 1000 (64) devrait toujours donner 1 semaine, obtenu {weeks_to_advance}"
    
    print("✅ Test des tournois non-7 tours réussi!")

if __name__ == "__main__":
    print("🔍 Test de la durée réaliste des tournois...")
    
    try:
        test_early_elimination_logic()
        test_late_elimination_logic()
        test_victory_logic()
        test_non_7_round_tournaments()
        print("\n🎉 Tous les tests sont passés!")
        print("✨ Logique réaliste : Tournois 7 tours = 1 semaine si éliminé dans les 3 premiers tours, 2 semaines sinon")
    except Exception as e:
        print(f"\n❌ Test échoué: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
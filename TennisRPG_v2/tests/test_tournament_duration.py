#!/usr/bin/env python3
"""
Test pour vérifier que les tournois à 7 tours avancent bien de 2 semaines
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

from entities.tournament import Tournament
from entities.spectialized_tournaments import GrandSlam, Masters1000, ATP250
from data.tournaments_data import TournamentCategory
from managers.weekly_activity_manager import TournamentActivity
from core.game_session_controller import GameSessionController
from core.game_session_state import GameSessionState
from core.game_session_ui import GameSessionUI

def test_tournament_rounds_calculation():
    """Test la calculation du nombre de tours pour différents tournois"""
    
    # Grand Slam avec 128 joueurs (7 tours)
    grand_slam = GrandSlam("US Open", "New York", "Hard Court", 128)
    assert grand_slam._calculate_tournament_rounds() == 7, f"Grand Slam devrait avoir 7 tours, a {grand_slam._calculate_tournament_rounds()}"
    
    # Masters 1000 avec 128 joueurs (7 tours)  
    masters_128 = Masters1000("Indian Wells", "Indian Wells", "Hard Court", 128)
    assert masters_128._calculate_tournament_rounds() == 7, f"Masters 1000 (128) devrait avoir 7 tours, a {masters_128._calculate_tournament_rounds()}"
    
    # Masters 1000 avec 64 joueurs (6 tours)
    masters_64 = Masters1000("Monte Carlo", "Monte Carlo", "Clay", 64)
    assert masters_64._calculate_tournament_rounds() == 6, f"Masters 1000 (64) devrait avoir 6 tours, a {masters_64._calculate_tournament_rounds()}"
    
    # ATP 250 avec 32 joueurs (5 tours)
    atp250 = ATP250("Montpellier", "Montpellier", "Hard Court", 32)
    assert atp250._calculate_tournament_rounds() == 5, f"ATP 250 devrait avoir 5 tours, a {atp250._calculate_tournament_rounds()}"
    
    print("✅ Test de calcul du nombre de tours réussi!")

def test_weeks_advance_logic():
    """Test la logique d'avancement des semaines"""
    
    # Crée un contrôleur de jeu factice
    ui = GameSessionUI()
    state = GameSessionState()
    controller = GameSessionController(ui, state)
    
    # Test avec un Grand Slam (7 tours = 2 semaines)
    grand_slam = GrandSlam("Wimbledon", "London", "Grass", 128)
    tournament_activity = TournamentActivity(grand_slam)
    
    weeks_to_advance = controller._determine_weeks_to_advance(tournament_activity)
    assert weeks_to_advance == 2, f"Grand Slam devrait avancer de 2 semaines, retourne {weeks_to_advance}"
    
    # Test avec un Masters 1000 à 128 joueurs (7 tours = 2 semaines)
    masters_128 = Masters1000("Indian Wells", "Indian Wells", "Hard Court", 128)
    tournament_activity_128 = TournamentActivity(masters_128)
    
    weeks_to_advance_128 = controller._determine_weeks_to_advance(tournament_activity_128)
    assert weeks_to_advance_128 == 2, f"Masters 1000 (128) devrait avancer de 2 semaines, retourne {weeks_to_advance_128}"
    
    # Test avec un Masters 1000 à 64 joueurs (6 tours = 1 semaine)
    masters_64 = Masters1000("Monte Carlo", "Monte Carlo", "Clay", 64)
    tournament_activity_64 = TournamentActivity(masters_64)
    
    weeks_to_advance_64 = controller._determine_weeks_to_advance(tournament_activity_64)
    assert weeks_to_advance_64 == 1, f"Masters 1000 (64) devrait avancer de 1 semaine, retourne {weeks_to_advance_64}"
    
    # Test avec un ATP 250 (5 tours = 1 semaine)
    atp250 = ATP250("Montpellier", "Montpellier", "Hard Court", 32)
    tournament_activity_atp250 = TournamentActivity(atp250)
    
    weeks_to_advance_atp250 = controller._determine_weeks_to_advance(tournament_activity_atp250)
    assert weeks_to_advance_atp250 == 1, f"ATP 250 devrait avancer de 1 semaine, retourne {weeks_to_advance_atp250}"
    
    print("✅ Test de logique d'avancement des semaines réussi!")

if __name__ == "__main__":
    print("🔍 Test de la durée des tournois...")
    
    try:
        test_tournament_rounds_calculation()
        test_weeks_advance_logic()
        print("\n🎉 Tous les tests sont passés! Les tournois à 7 tours avanceront bien de 2 semaines.")
    except Exception as e:
        print(f"\n❌ Test échoué: {e}")
        sys.exit(1)
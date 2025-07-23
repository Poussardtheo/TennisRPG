#!/usr/bin/env python3
"""
Test simple de la logique de retraite préliminaire
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from TennisRPG_v2.managers.player_generator import PlayerGenerator
from TennisRPG_v2.managers.retirement_manager import RetirementManager
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.entities.player import Gender
from TennisRPG_v2.utils.constants import TIME_CONSTANTS

def test_retirement_logging():
    """Test simple que les retraites sont enregistrées"""
    print("=== Test Logique Retraite Simulation Preliminaire ===")
    
    # Créer des joueurs
    generator = PlayerGenerator()
    players = {}
    
    for i in range(30):
        player = generator.generate_player(Gender.MALE)
        players[player.full_name] = player
    
    # Stats initiales
    ages = [p.career.age for p in players.values()]
    older_players = [p for p in players.values() if p.career.age >= 30]
    
    print(f"Pool initial: {len(players)} joueurs")
    print(f"Ages: min={min(ages)}, max={max(ages)}")
    print(f"Joueurs 30+ ans: {len(older_players)}")
    
    # Managers
    ranking_manager = RankingManager(list(players.values()))
    retirement_manager = RetirementManager(generator)
    
    print(f"Retirement log initial: {len(retirement_manager.retirement_log)} entrees")
    
    # Simulation retraites
    current_sim_year = TIME_CONSTANTS["GAME_START_YEAR"] - 1
    print(f"Simulation pour annee {current_sim_year}...")
    
    retired_players, new_players = retirement_manager.process_end_of_season_retirements(
        players, ranking_manager, current_sim_year
    )
    
    print(f"Resultats:")
    print(f"  Retraites: {len(retired_players)}")
    print(f"  Nouveaux: {len(new_players)}")
    print(f"  Log entries: {len(retirement_manager.retirement_log)}")
    
    # Vérification
    if retirement_manager.retirement_log:
        print("SUCCESS: Retraites enregistrees!")
        for retirement in retirement_manager.retirement_log[:2]:
            print(f"  - {retirement['player_name']} ({retirement['age']} ans)")
        
        stats = retirement_manager.get_retirement_stats(current_sim_year)
        if stats:
            print(f"Stats: {stats['total_retirements']} retraites, age moyen {stats['average_retirement_age']:.1f}")
        return True
    else:
        print("PROBLEM: Aucune retraite enregistree")
        return False

if __name__ == "__main__":
    success = test_retirement_logging()
    print(f"Test {'REUSSI' if success else 'ECHOUE'}")
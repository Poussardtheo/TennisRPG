#!/usr/bin/env python3
"""
Test script pour vérifier les corrections du système de retraite
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from TennisRPG_v2.managers.player_generator import PlayerGenerator
from TennisRPG_v2.managers.retirement_manager import RetirementManager
from TennisRPG_v2.entities.player import Gender
from TennisRPG_v2.utils.constants import TIME_CONSTANTS

def test_retirement_fixes():
    """Test les corrections du système de retraite"""
    print("=== Test des corrections du système de retraite ===\n")
    
    # Test 1: Vérifier que GAME_START_YEAR est bien défini
    print(f"1. GAME_START_YEAR constant: {TIME_CONSTANTS['GAME_START_YEAR']}")
    
    # Test 2: Génération normale de joueurs (jeunes)
    generator = PlayerGenerator()
    young_players = generator.generate_player_pool(5, Gender.MALE)
    print(f"\n2. Joueurs jeunes générés:")
    for name, player in young_players.items():
        print(f"   - {name}: {player.career.age} ans")
    
    # Test 3: Génération de joueurs de tous âges pour simulation
    old_players = generator.generate_simulation_player_pool(10, Gender.MALE)
    print(f"\n3. Joueurs de tous âges pour simulation:")
    ages = []
    for name, player in old_players.items():
        ages.append(player.career.age)
        print(f"   - {name}: {player.career.age} ans")
    
    print(f"   Âges: min={min(ages)}, max={max(ages)}")
    print(f"   Joueurs 30+ ans: {len([a for a in ages if a >= 30])}")
    
    # Test 4: Vérifier que le RetirementManager a bien un retirement_log
    retirement_manager = RetirementManager(generator)
    print(f"\n4. RetirementManager retirement_log: {type(retirement_manager.retirement_log)} (vide: {len(retirement_manager.retirement_log) == 0})")
    
    # Test 5: Simuler un ajout dans le log
    test_retirement = {
        "player_name": "Test Player",
        "age": 35,
        "ranking": 150,
        "year": TIME_CONSTANTS["GAME_START_YEAR"],
        "country": "France"
    }
    retirement_manager.retirement_log.append(test_retirement)
    print(f"   Après ajout test: {len(retirement_manager.retirement_log)} entrée(s)")
    
    # Test 6: Test des stats de retraite
    stats = retirement_manager.get_retirement_stats(TIME_CONSTANTS["GAME_START_YEAR"])
    if stats:
        print(f"   Stats de retraite pour {TIME_CONSTANTS['GAME_START_YEAR']}: {stats['total_retirements']} retraites")
    else:
        print(f"   Pas de stats pour {TIME_CONSTANTS['GAME_START_YEAR']}")
    
    print("\n✅ Tests des corrections terminés avec succès!")

if __name__ == "__main__":
    test_retirement_fixes()
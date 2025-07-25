#!/usr/bin/env python3
"""
Test script to verify fatigue recovery calculation vs display
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

from TennisRPG_v2.entities.player import Player
from TennisRPG_v2.managers.weekly_activity_manager import RestActivity
from TennisRPG_v2.utils.helpers import calculate_fatigue_level
from TennisRPG_v2.utils.constants import FATIGUE_VALUES

def test_fatigue_recovery():
    """Test the actual vs displayed fatigue recovery"""
    
    # Create a test player
    player = Player("Test", "Player", "France", "m")
    
    # Set initial fatigue
    player.physical.fatigue = 50
    print(f"Initial fatigue: {player.physical.fatigue}%")
    
    # Test the calculate_fatigue_level function for rest
    actual_recovery = calculate_fatigue_level("Repos")
    print(f"Actual recovery calculated: {actual_recovery}")
    print(f"FATIGUE_VALUES['Repos']: {FATIGUE_VALUES['Repos']}")
    
    # Test the RestActivity
    rest_activity = RestActivity()
    result = rest_activity.execute(player)
    
    print(f"Final fatigue: {player.physical.fatigue}%")
    print(f"Displayed fatigue change: {result.fatigue_change}%")
    print(f"Actual fatigue change: {50 - player.physical.fatigue}%")
    
    # Test multiple times to see the range
    print("\n--- Testing multiple rest calculations ---")
    for i in range(10):
        recovery = calculate_fatigue_level("Repos")
        print(f"Recovery calculation {i+1}: {recovery}")

if __name__ == "__main__":
    test_fatigue_recovery()
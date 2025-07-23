#!/usr/bin/env python3
"""
Test script pour vérifier la génération de joueurs de tous âges
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from TennisRPG_v2.managers.player_generator import PlayerGenerator
from TennisRPG_v2.entities.player import Gender

def test_age_generation():
    """Test la génération de joueurs de tous âges"""
    generator = PlayerGenerator()
    
    print("=== Test de génération de joueurs de tous âges ===")
    
    # Générer un pool de joueurs avec tous les âges
    players = generator.generate_simulation_player_pool(20, Gender.MALE)
    
    print(f"Joueurs générés: {len(players)}")
    
    ages = []
    older_players = []
    
    for name, player in players.items():
        ages.append(player.career.age)
        if player.career.age >= 30:  # Joueurs pouvant partir à la retraite
            older_players.append((name, player.career.age))
    
    print(f"\nÂges générés: min={min(ages)}, max={max(ages)}")
    print(f"Répartition des âges: {sorted(ages)}")
    
    print(f"\nJoueurs de 30+ ans (peuvent partir à la retraite): {len(older_players)}")
    for name, age in older_players:
        print(f"  - {name}: {age} ans")
    
    # Test avec âge spécifique
    print("\n=== Test avec plage d'âge spécifique (35-42 ans) ===")
    older_players_only = generator.generate_player_pool(5, Gender.FEMALE, age_range=(35, 42))
    
    for name, player in older_players_only.items():
        print(f"  - {name}: {player.career.age} ans")

if __name__ == "__main__":
    test_age_generation()
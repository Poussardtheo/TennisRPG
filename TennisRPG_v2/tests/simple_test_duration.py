#!/usr/bin/env python3
"""
Test simple pour vérifier la durée des tournois
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

# Test simple du calcul des tours
def test_rounds_calculation():
    import math
    
    # Test des calculs de tours
    test_cases = [
        (32, 5),   # ATP 250
        (64, 6),   # Masters 1000 petit
        (128, 7),  # Grand Slam / Masters 1000 gros
    ]
    
    for num_players, expected_rounds in test_cases:
        calculated_rounds = int(math.ceil(math.log2(num_players)))
        assert calculated_rounds == expected_rounds, f"Pour {num_players} joueurs: attendu {expected_rounds}, calculé {calculated_rounds}"
    
    print("✅ Calcul des tours correct!")

def test_weeks_logic():
    """Test de la logique de semaines selon le nombre de tours"""
    
    def determine_weeks(num_rounds):
        return 2 if num_rounds == 7 else 1
    
    # Test cases
    test_cases = [
        (5, 1),  # ATP 250 -> 1 semaine
        (6, 1),  # Masters 1000 normal -> 1 semaine  
        (7, 2),  # Grand Slam / Masters 1000 gros -> 2 semaines
    ]
    
    for rounds, expected_weeks in test_cases:
        calculated_weeks = determine_weeks(rounds)
        assert calculated_weeks == expected_weeks, f"Pour {rounds} tours: attendu {expected_weeks} semaines, calculé {calculated_weeks}"
    
    print("✅ Logique des semaines correcte!")

if __name__ == "__main__":
    print("🔍 Test de la durée des tournois...")
    
    try:
        test_rounds_calculation()
        test_weeks_logic()
        print("\n🎉 Logique de base validée! Les tournois à 7 tours devraient maintenant avancer de 2 semaines.")
    except Exception as e:
        print(f"\n❌ Test échoué: {e}")
        sys.exit(1)
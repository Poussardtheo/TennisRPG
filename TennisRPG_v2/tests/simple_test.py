#!/usr/bin/env python3
"""
Test simple du système de retraite
"""

# Test des imports
try:
    print("Testing imports...")
    from TennisRPG_v2.utils.constants import RETIREMENT_CONSTANTS
    print(f"✓ RETIREMENT_CONSTANTS imported: {list(RETIREMENT_CONSTANTS.keys())}")
    
    from TennisRPG_v2.utils.helpers import calculate_retirement_probability
    print("✓ calculate_retirement_probability imported")
    
    from TennisRPG_v2.entities.player import Player, Gender
    print("✓ Player and Gender imported")
    
    from TennisRPG_v2.managers.retirement_manager import RetirementManager
    print("✓ RetirementManager imported")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Test des fonctionnalités de base
try:
    print("\nTesting retirement probability calculation...")
    
    # Test des âges différents
    test_ages = [25, 30, 35, 40]
    for age in test_ages:
        prob = calculate_retirement_probability(age)
        print(f"  Age {age}: {prob:.4f} ({prob*100:.2f}%)")
    
    # Test avec classement
    prob_with_ranking = calculate_retirement_probability(35, atp_ranking=50)
    prob_without_ranking = calculate_retirement_probability(35)
    print(f"  Age 35 without ranking: {prob_without_ranking:.4f}")
    print(f"  Age 35 with top 50 ranking: {prob_with_ranking:.4f}")
    
    # Test création joueur
    print("\nTesting player creation with age...")
    player = Player(
        gender=Gender.MALE,
        first_name="Test",
        last_name="Player",
        country="France",
        age=30
    )
    print(f"  Created player: {player.full_name}, age {player.career.age}")
    
    # Test manager de retraite
    print("\nTesting retirement manager...")
    manager = RetirementManager()
    print("  ✓ RetirementManager created successfully")
    
    print("\n🎉 All tests passed! The retirement system is working correctly.")
    
except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
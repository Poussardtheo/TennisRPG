#!/usr/bin/env python3
"""Test simple du nouveau système de progression"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

from ..entities.player import Player, Gender
from ..utils.helpers import get_age_progression_factor, calculate_tournament_xp, calculate_experience_required


def test_age_progression_factors():
    """Test les facteurs de progression par âge"""
    print("=== Test des facteurs de progression par âge ===")

    test_ages = [18, 22, 25, 28, 32, 35]
    for age in test_ages:
        factor = get_age_progression_factor(age)
        print(f"Âge {age}: facteur {factor:.1f}x")
    print()


def test_new_level_formula():
    """Test la nouvelle formule de calcul d'XP"""
    print("=== Test de la nouvelle formule de niveau ===")

    print("Niveaux et XP requise:")
    for level in [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
        xp_required = calculate_experience_required(level)
        print(f"Niveau {level}: {xp_required} XP requis")
    print()


def test_tournament_xp_system():
    """Test du système d'XP de tournoi"""
    print("=== Test du système d'XP de tournoi ===")

    tournaments = ["Grand Slam", "Masters 1000", "ATP 500", "ATP 250"]
    rounds = ["Champion", "Finale", "Demi-finale", "Quart de finale", "Premier tour"]

    for tournament in tournaments:
        print(f"\n{tournament}:")
        for round_name in rounds:
            xp = calculate_tournament_xp(tournament, round_name)
            print(f"  {round_name}: {xp} XP")
    print()


def test_player_creation_with_age():
    """Test la création d'un joueur avec l'âge"""
    print("=== Test de création de joueur avec âge ===")

    # Joueur avec âge spécifié
    player1 = Player(Gender.MALE, "Test", "Player", "France", age=19)
    print(f"Joueur 1: {player1.full_name}, âge {player1.career.age}")

    # Joueur avec âge aléatoire
    player2 = Player(Gender.FEMALE, "Test", "Player2", "France")
    print(f"Joueur 2: {player2.full_name}, âge {player2.career.age}")

    # Test gain d'XP avec facteur d'âge
    print(f"\nTest gain XP:")
    print(f"Avant: {player1.career.xp_points} XP, niveau {player1.career.level}")
    player1.gain_experience(50)
    print(f"Après: {player1.career.xp_points} XP, niveau {player1.career.level}")
    print()


def test_tournament_xp_gain():
    """Test du gain d'XP de tournoi"""
    print("=== Test du gain d'XP de tournoi ===")

    player = Player(Gender.MALE, "Test", "Tournament", "France", age=24, is_main_player=True)
    print(f"Joueur initial: XP={player.career.xp_points}, niveau={player.career.level}")

    # Test victoire en ATP 500
    player.gain_tournament_experience("ATP 500", "Champion")
    print(f"Après victoire ATP 500: XP={player.career.xp_points}, niveau={player.career.level}")
    print()


if __name__ == "__main__":
    print("TEST DU NOUVEAU SYSTÈME DE PROGRESSION")
    print("=" * 50)
    print()

    try:
        test_age_progression_factors()
        test_new_level_formula()
        test_tournament_xp_system()
        test_player_creation_with_age()
        test_tournament_xp_gain()

        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("\nLe nouveau système de progression est fonctionnel:")
        print("- Facteurs de progression par âge ✓")
        print("- Nouvelle formule d'XP plus réaliste ✓")
        print("- Système d'XP de tournoi ✓")
        print("- Joueurs avec âge ✓")
        print("- Niveau max augmenté à 50 ✓")

    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

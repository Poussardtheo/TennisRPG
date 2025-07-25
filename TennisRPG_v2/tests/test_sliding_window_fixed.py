#!/usr/bin/env python3
"""
Test simple pour confirmer le bon fonctionnement du système glissant corrigé
"""
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.managers.atp_points_manager import ATPPointsManager


def test_sliding_window_corrected():
    """Test du système glissant corrigé"""
    print("=== TEST DU SYSTÈME GLISSANT CORRIGÉ ===\n")
    
    # Crée un joueur de test
    player = Player(
        gender=Gender.MALE,
        first_name="Test",
        last_name="Sliding",
        country="France"
    )
    
    # Crée les managers
    ranking_manager = RankingManager([player])
    players_dict = {player.full_name: player}
    atp_manager = ATPPointsManager(players_dict, ranking_manager)
    
    print("Scénario : Attribution de points en semaine 1, puis cycle complet")
    
    # Attribution initiale en semaine 1
    ranking_manager.current_week = 1
    atp_manager.add_tournament_points(player, 1, 500)
    print(f"Semaine 1: {player.career.atp_points} points ATP")
    
    # Vérifie que les points sont stockés dans la bonne colonne
    week1_stored = ranking_manager.atp_points_history.loc[player.full_name, 'week_1']
    print(f"Points stockés en colonne week_1: {week1_stored}")
    
    # Avance de 51 semaines (pas de perte de points)
    for week in range(2, 52):
        ranking_manager.advance_week()
        if week % 10 == 0:  # Affichage périodique
            print(f"Semaine {ranking_manager.current_week}: {player.career.atp_points} points ATP")
    
    # Arrive en semaine 52
    ranking_manager.advance_week()
    print(f"Semaine 52: {player.career.atp_points} points ATP")
    
    # Passage à la semaine 1 de l'année suivante (perte des points de l'année précédente)
    print("\n--- Passage à la nouvelle année ---")
    ranking_manager.advance_week()
    print(f"Semaine 1 (année 2): {player.career.atp_points} points ATP")
    
    # Vérifie que la colonne week_1 a été remise à zéro
    week1_after_reset = ranking_manager.atp_points_history.loc[player.full_name, 'week_1']
    print(f"Points dans colonne week_1 après reset: {week1_after_reset}")
    
    # Test d'ajout de nouveaux points
    atp_manager.add_tournament_points(player, 1, 750)
    print(f"Après nouveau gain en semaine 1 (année 2): {player.career.atp_points} points ATP")
    
    # Vérifications
    points_lost_correctly = (player.career.atp_points == 750)  # 500 perdus, 750 gagnés
    column_reset_correctly = (week1_after_reset == 0)
    
    print(f"\nRésultats:")
    print(f"Points perdus correctement après 52 semaines: {'OK' if points_lost_correctly else 'FAIL'}")
    print(f"Colonne remise à zéro correctement: {'OK' if column_reset_correctly else 'FAIL'}")
    
    success = points_lost_correctly and column_reset_correctly
    print(f"Test global: {'SUCCESS' if success else 'FAIL'}")
    
    return success


def test_multiple_weeks_same_player():
    """Test avec gains sur plusieurs semaines pour le même joueur"""
    print("\n=== TEST GAINS MULTIPLES SEMAINES ===\n")
    
    player = Player(Gender.MALE, "Multi", "Week", "France")
    ranking_manager = RankingManager([player])
    atp_manager = ATPPointsManager({player.full_name: player}, ranking_manager)
    
    # Gains sur plusieurs semaines
    points_per_week = [100, 200, 150, 300, 250]
    total_expected = sum(points_per_week)
    
    for week, points in enumerate(points_per_week, 1):
        ranking_manager.current_week = week
        atp_manager.add_tournament_points(player, week, points)
        print(f"Semaine {week}: +{points} points, total = {player.career.atp_points}")
    
    # Avance de 47 semaines (pour arriver en semaine 52)
    for _ in range(47):
        ranking_manager.advance_week()
    
    print(f"Semaine 52: {player.career.atp_points} points ATP")
    
    # Cycle complet : perte des points de la semaine 1
    ranking_manager.advance_week()  # Semaine 1 année 2
    expected_after_loss = total_expected - points_per_week[0]  # Perte des 100 points de la semaine 1
    
    print(f"Semaine 1 (année 2): {player.career.atp_points} points ATP")
    print(f"Attendu: {expected_after_loss} points")
    
    success = (player.career.atp_points == expected_after_loss)
    print(f"Test gains multiples: {'SUCCESS' if success else 'FAIL'}")
    
    return success


if __name__ == "__main__":
    print("TESTS DU SYSTÈME GLISSANT CORRIGÉ")
    print("=" * 50)
    
    results = []
    results.append(test_sliding_window_corrected())
    results.append(test_multiple_weeks_same_player())
    
    print("\n" + "=" * 50)
    print("RÉSUMÉ")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passés: {passed}/{total}")
    
    if passed == total:
        print("Système glissant fonctionne correctement!")
    else:
        print("Problèmes détectés dans le système glissant")
    
    sys.exit(0 if passed == total else 1)
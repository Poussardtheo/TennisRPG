#!/usr/bin/env python3
"""
Test final du système glissant corrigé - simulation du flux réel du jeu
"""
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.managers.atp_points_manager import ATPPointsManager


def simulate_real_game_flow():
    """Simule le flux réel du jeu : tournois puis advance_week"""
    print("=== SIMULATION DU FLUX RÉEL DU JEU ===\n")
    
    # Crée un joueur de test
    player = Player(
        gender=Gender.MALE,
        first_name="Real",
        last_name="Flow",
        country="France"
    )
    
    # Crée les managers
    ranking_manager = RankingManager([player])
    players_dict = {player.full_name: player}
    atp_manager = ATPPointsManager(players_dict, ranking_manager)
    
    print("Simulation du flux : Tournoi en semaine 1, puis advance_week")
    
    # Semaine 1 : Tournoi puis advance_week
    ranking_manager.current_week = 1
    print(f"Semaine courante: {ranking_manager.current_week}")
    
    # 1. Tournoi ajoute des points
    atp_manager.add_tournament_points(player, 1, 500)
    print(f"Après tournoi: {player.career.atp_points} points ATP")
    
    # Vérifie le stockage dans l'historique
    week1_stored = ranking_manager.atp_points_history.loc[player.full_name, 'week_1']
    print(f"Points stockés en colonne week_1: {week1_stored}")
    
    # 2. Advance week (comme dans le vrai jeu)
    ranking_manager.advance_week()
    print(f"Après advance_week: semaine {ranking_manager.current_week}, points: {player.career.atp_points}")
    
    # Vérifie que les points sont toujours dans la colonne week_1
    week1_after_advance = ranking_manager.atp_points_history.loc[player.full_name, 'week_1']
    print(f"Points restants en colonne week_1: {week1_after_advance}")
    
    # Cycle complet : 51 semaines supplémentaires
    print("\n--- Cycle complet de 51 semaines ---")
    for week in range(3, 53):  # Semaines 3 à 52
        ranking_manager.advance_week()
        if week % 10 == 0:
            print(f"Semaine {ranking_manager.current_week}: {player.career.atp_points} points ATP")
    
    print(f"Arrivée en semaine 52: {player.career.atp_points} points ATP")
    
    # Retour en semaine 1 : les points de l'année précédente devraient être retirés
    print("\n--- Retour en semaine 1 (expiration) ---")
    ranking_manager.advance_week()
    print(f"Semaine {ranking_manager.current_week}: {player.career.atp_points} points ATP")
    
    # Vérifications
    week1_final = ranking_manager.atp_points_history.loc[player.full_name, 'week_1']
    print(f"Points en colonne week_1 après expiration: {week1_final}")
    
    # Résultats attendus
    points_preserved_during_year = (week1_after_advance == 500)
    points_expired_correctly = (player.career.atp_points == 0)
    column_reset_after_expiry = (week1_final == 0)
    
    print(f"\nRésultats:")
    print(f"Points préservés pendant l'année: {'OK' if points_preserved_during_year else 'FAIL'}")
    print(f"Points expirés après 52 semaines: {'OK' if points_expired_correctly else 'FAIL'}")
    print(f"Colonne prête pour nouveaux points: {'OK' if column_reset_after_expiry else 'FAIL'}")
    
    success = points_preserved_during_year and points_expired_correctly and column_reset_after_expiry
    return success


def test_no_immediate_removal():
    """Test qu'on ne retire pas immédiatement les points qu'on vient d'ajouter"""
    print("\n=== TEST ANTI-RETRAIT IMMÉDIAT ===\n")
    
    player = Player(Gender.MALE, "No", "Immediate", "France")
    ranking_manager = RankingManager([player])
    atp_manager = ATPPointsManager({player.full_name: player}, ranking_manager)
    
    # Semaine 5
    ranking_manager.current_week = 5
    
    # Ajoute des points
    atp_manager.add_tournament_points(player, 5, 1000)
    points_after_tournament = player.career.atp_points
    
    # Advance week
    ranking_manager.advance_week()
    points_after_advance = player.career.atp_points
    
    print(f"Points après tournoi: {points_after_tournament}")
    print(f"Points après advance_week: {points_after_advance}")
    
    # Les points ne doivent PAS être retirés immédiatement
    success = (points_after_advance == points_after_tournament)
    print(f"Pas de retrait immédiat: {'OK' if success else 'FAIL'}")
    
    return success


if __name__ == "__main__":
    print("TEST FINAL DU SYSTÈME GLISSANT")
    print("=" * 50)
    
    results = []
    results.append(simulate_real_game_flow())
    results.append(test_no_immediate_removal())
    
    print("\n" + "=" * 50)
    print("RÉSUMÉ FINAL")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passés: {passed}/{total}")
    
    if passed == total:
        print("Système glissant fonctionne PARFAITEMENT!")
        print("Les points sont conservés pendant 52 semaines puis expirés correctement.")
    else:
        print("Problèmes détectés - vérifier la logique du système glissant")
    
    sys.exit(0 if passed == total else 1)
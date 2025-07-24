#!/usr/bin/env python3
"""
Test script pour vérifier que les retraites sont enregistrées pendant la simulation préliminaire
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from TennisRPG_v2.managers.player_generator import PlayerGenerator
from TennisRPG_v2.managers.retirement_manager import RetirementManager
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.entities.player import Gender
from TennisRPG_v2.utils.constants import TIME_CONSTANTS

def test_preliminary_retirement_logic():
    """Teste que la logique de retraite fonctionne dans la simulation préliminaire"""
    print("=== Test de la logique de retraite dans la simulation préliminaire ===\n")
    
    # Créer un petit pool de joueurs avec des âges variés
    generator = PlayerGenerator()
    players = {}
    
    # Générer des joueurs de différents âges (incluant des joueurs âgés)
    for i in range(50):
        player = generator.generate_player(Gender.MALE)
        players[player.full_name] = player
    
    # Afficher la répartition d'âges initiale
    ages = [p.career.age for p in players.values()]
    older_players = [p for p in players.values() if p.career.age >= 30]
    
    print(f"👥 Pool initial: {len(players)} joueurs")
    print(f"📊 Âges: min={min(ages)}, max={max(ages)}, moyenne={sum(ages)/len(ages):.1f}")
    print(f"👴 Joueurs 30+ ans: {len(older_players)} ({len(older_players)/len(players)*100:.1f}%)")
    
    # Créer les managers nécessaires
    ranking_manager = RankingManager(list(players.values()))
    retirement_manager = RetirementManager(generator)
    
    print(f"\n🔄 État initial du retirement_log: {len(retirement_manager.retirement_log)} entrées")
    
    # Simuler une fin d'année avec retraites (comme dans la simulation préliminaire)
    current_sim_year = TIME_CONSTANTS["GAME_START_YEAR"] - 1
    print(f"\n⚙️  Simulation des retraites pour l'année {current_sim_year}...")
    
    retired_players, new_players = retirement_manager.process_end_of_season_retirements(
        players, ranking_manager, current_sim_year
    )
    
    # Vérifier les résultats
    print(f"\n📈 Résultats de la simulation:")
    print(f"   🏁 Joueurs retraités: {len(retired_players)}")
    print(f"   🆕 Nouveaux joueurs: {len(new_players)}")
    print(f"   📝 Entrées dans le retirement_log: {len(retirement_manager.retirement_log)}")
    
    # Vérifier que les retraites sont enregistrées
    if retirement_manager.retirement_log:
        print(f"\n✅ SUCCESS: Les retraites sont maintenant enregistrées!")
        print("   Exemples d'entrées dans le log:")
        for i, retirement in enumerate(retirement_manager.retirement_log[:3]):
            print(f"   {i+1}. {retirement['player_name']} ({retirement['age']} ans) - Année {retirement['year']}")
        
        # Test des statistiques
        stats = retirement_manager.get_retirement_stats(current_sim_year)
        if stats:
            print(f"\n📊 Statistiques pour {current_sim_year}:")
            print(f"   • Total retraites: {stats['total_retirements']}")
            print(f"   • Âge moyen: {stats['average_retirement_age']:.1f} ans")
    else:
        print(f"\n❌ PROBLEM: Aucune retraite enregistrée dans le log")
    
    # Vérifier l'équilibre du pool
    final_count = len(players)
    print(f"\n🔄 Pool final: {final_count} joueurs (devrait être identique au début: {final_count == 50})")
    
    return len(retirement_manager.retirement_log) > 0

if __name__ == "__main__":
    success = test_preliminary_retirement_logic()
    if success:
        print("\n🎉 Test réussi! Les retraites seront maintenant visibles avec [R] dans le jeu.")
    else:
        print("\n💥 Test échoué! Il reste un problème dans la logique.")
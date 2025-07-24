#!/usr/bin/env python3
"""Test pour vérifier le problème de classement ATP"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.entities.ranking import RankingType

def test_ranking_consistency():
    """Test pour vérifier la cohérence du classement"""
    
    # Créer des joueurs de test avec des points ATP spécifiques
    players = [
        Player(Gender.MALE, "Toivo", "Koskela", "Finland", 180, 1),
        Player(Gender.MALE, "Gael", "Cavalcanti", "Brazil", 175, 1),
        Player(Gender.MALE, "Leigh", "Brady", "United Kingdom", 178, 1)
    ]
    
    # Assigner des points ATP
    players[0].career.atp_points = 2088  # Toivo
    players[1].career.atp_points = 1560  # Gael
    players[2].career.atp_points = 2005  # Leigh
    
    # Créer le ranking manager
    ranking_manager = RankingManager(players)
    
    print("Points ATP des joueurs:")
    for player in players:
        print(f"{player.full_name}: {player.career.atp_points}")
    
    print("\nClassement attendu (par points décroissants):")
    sorted_players = sorted(players, key=lambda p: p.career.atp_points, reverse=True)
    for i, player in enumerate(sorted_players, 1):
        print(f"{i}. {player.full_name}: {player.career.atp_points}")
    
    print("\nClassement affiché par RankingManager:")
    try:
        ranking_manager.display_ranking(RankingType.ATP, count=3)
    except UnicodeEncodeError:
        # Affichage alternatif sans émojis
        print("CLASSEMENT ATP")
        print("=" * 60)
        ranking_obj = ranking_manager._get_ranking_by_type(RankingType.ATP)
        all_players = ranking_obj.get_ranked_players(3)
        
        for i, player in enumerate(all_players):
            rank = i + 1
            points = player.career.atp_points
            print(f"{rank}. {player.first_name} {player.last_name} - ATP Points: {points} - Pays: {player.country}")
    
    # Vérifier les rangs individuels
    print("\nRangs individuels:")
    for player in players:
        rank = ranking_manager.get_player_rank(player, RankingType.ATP)
        print(f"{player.full_name}: rang {rank}")
    
    # Test de cohérence
    toivo_rank = ranking_manager.get_player_rank(players[0], RankingType.ATP)
    gael_rank = ranking_manager.get_player_rank(players[1], RankingType.ATP) 
    leigh_rank = ranking_manager.get_player_rank(players[2], RankingType.ATP)
    
    print(f"\nVérification de cohérence:")
    print(f"Toivo (2088 pts) - rang {toivo_rank}")
    print(f"Leigh (2005 pts) - rang {leigh_rank}")
    print(f"Gael (1560 pts) - rang {gael_rank}")
    
    if toivo_rank < gael_rank and leigh_rank < gael_rank:
        print("✅ Classement cohérent")
    else:
        print("❌ Classement incohérent détecté!")
        
        # Analyser l'ordre dans rankings
        print("\nDétails du dictionnaire rankings:")
        for name, rank in ranking_manager.atp_ranking.rankings.items():
            player = ranking_manager.players[name]
            print(f"{name}: rang {rank}, points {player.career.atp_points}")

if __name__ == "__main__":
    test_ranking_consistency()
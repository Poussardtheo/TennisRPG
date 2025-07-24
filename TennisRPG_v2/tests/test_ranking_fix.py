#!/usr/bin/env python3
"""Test pour vérifier la correction du problème de classement ATP"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.managers.atp_points_manager import ATPPointsManager
from TennisRPG_v2.entities.ranking import RankingType

def test_ranking_consistency_after_points_update():
    """Test pour vérifier la cohérence du classement après ajout de points"""
    
    # Créer des joueurs de test
    players = [
        Player(Gender.MALE, "Toivo", "Koskela", "Finland", 180, 1),
        Player(Gender.MALE, "Gael", "Cavalcanti", "Brazil", 175, 1),
        Player(Gender.MALE, "Leigh", "Brady", "United Kingdom", 178, 1)
    ]
    
    # Points initiaux
    players[0].career.atp_points = 1500  # Toivo
    players[1].career.atp_points = 1600  # Gael (le plus élevé initialement)
    players[2].career.atp_points = 1550  # Leigh
    
    # Créer les managers
    ranking_manager = RankingManager(players)
    players_dict = {player.full_name: player for player in players}
    atp_manager = ATPPointsManager(players_dict, ranking_manager)
    
    print("=== AVANT AJOUT DE POINTS ===")
    print("Points ATP des joueurs:")
    for player in players:
        rank = ranking_manager.get_player_rank(player, RankingType.ATP)
        print(f"{player.full_name}: {player.career.atp_points} points - rang {rank}")
    
    # Ajouter des points à Toivo pour qu'il dépasse Gael
    print("\n=== AJOUT DE 600 POINTS À TOIVO ===")
    atp_manager.add_tournament_points(players[0], 1, 600)  # Toivo passe à 2100
    
    print("Points ATP après ajout:")
    for player in players:
        rank = ranking_manager.get_player_rank(player, RankingType.ATP)
        print(f"{player.full_name}: {player.career.atp_points} points - rang {rank}")
    
    print("\n=== CLASSEMENT FINAL ===")
    try:
        # Affichage avec gestion d'erreur pour les émojis
        ranking_obj = ranking_manager._get_ranking_by_type(RankingType.ATP)
        all_players = ranking_obj.get_ranked_players(3)
        
        for i, player in enumerate(all_players):
            rank = i + 1
            points = player.career.atp_points
            print(f"{rank}. {player.first_name} {player.last_name} - ATP Points: {points} - Pays: {player.country}")
    except Exception as e:
        print(f"Erreur d'affichage: {e}")
    
    # Vérification finale
    toivo_rank = ranking_manager.get_player_rank(players[0], RankingType.ATP)
    gael_rank = ranking_manager.get_player_rank(players[1], RankingType.ATP) 
    leigh_rank = ranking_manager.get_player_rank(players[2], RankingType.ATP)
    
    print(f"\nVérification finale:")
    print(f"Toivo (2100 pts) - rang {toivo_rank}")
    print(f"Gael (1600 pts) - rang {gael_rank}")
    print(f"Leigh (1550 pts) - rang {leigh_rank}")
    
    # Test de cohérence
    if toivo_rank == 1 and gael_rank == 2 and leigh_rank == 3:
        print("SUCCESS: Classement cohérent!")
        return True
    else:
        print("ERROR: Classement incohérent!")
        return False

if __name__ == "__main__":
    success = test_ranking_consistency_after_points_update()
    sys.exit(0 if success else 1)
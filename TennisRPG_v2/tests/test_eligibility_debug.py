#!/usr/bin/env python3
"""
Test de debug pour comprendre pourquoi l'éligibilité ne fonctionne pas comme attendu
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from TennisRPG_v2.managers.tournament_manager import TournamentManager
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.data.tournaments_data import TournamentCategory

def debug_eligibility():
    """Debug l'éligibilité en détail"""
    
    # Créer un joueur avec ELO très faible
    weak_player = Player(Gender.MALE, "Test", "Player", "FRA", 180, 1)
    weak_player.elo = 100
    weak_player.is_main_player = True
    
    # Créer les managers
    players = [weak_player]
    tournament_manager = TournamentManager()
    ranking_manager = RankingManager(players)
    
    print("=== Debug éligibilité ===")
    print(f"Joueur ELO: {weak_player.elo}")
    print(f"Joueur a classement ATP: {ranking_manager.atp_ranking.get_player_rank(weak_player)}")
    print()
    
    # Trouver Australian Open
    for week in range(1, 10):
        tournaments = tournament_manager.get_tournaments_for_week(week)
        for tournament in tournaments:
            if tournament.category == TournamentCategory.GRAND_SLAM:
                print(f"Tournoi: {tournament.name}")
                print(f"Catégorie: {tournament.category}")
                print(f"Seuil ATP: {tournament.eligibility_threshold}")
                
                # Test d'éligibilité détaillé
                elo_threshold = tournament._convert_atp_rank_to_elo_threshold(tournament.eligibility_threshold)
                print(f"Seuil ELO calculé: {elo_threshold}")
                print(f"Joueur ELO >= seuil ELO: {weak_player.elo} >= {elo_threshold} = {weak_player.elo >= elo_threshold}")
                
                # Test via is_player_eligible
                eligible = tournament.is_player_eligible(weak_player, ranking_manager)
                print(f"is_player_eligible résultat: {eligible}")
                
                # Test via tournament manager
                manager_tournaments = tournament_manager.get_tournaments_for_player(week, weak_player, ranking_manager)
                manager_eligible = tournament in manager_tournaments
                print(f"Via tournament manager: {manager_eligible}")
                
                return  # Stop après le premier Grand Slam trouvé

if __name__ == "__main__":
    debug_eligibility()
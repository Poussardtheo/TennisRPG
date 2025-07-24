#!/usr/bin/env python3
"""
Test pour vérifier que les PNJ participent maintenant à tous les tournois
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from TennisRPG_v2.managers.tournament_manager import TournamentManager
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager

def test_pnj_tournament_participation():
    """Test que les PNJ peuvent participer à tous les tournois"""
    
    # Créer un PNJ avec ELO très faible (normalement exclu des grands tournois)
    weak_pnj = Player(Gender.MALE, "PNJ", "Faible", "FRA", 180, 1)
    weak_pnj.elo = 500  # ELO très faible qui serait normalement exclu
    weak_pnj.is_main_player = False
    
    # Créer un joueur principal avec même ELO très faible
    main_player = Player(Gender.MALE, "Joueur", "Principal", "FRA", 180, 1)
    main_player.elo = 500
    main_player.is_main_player = True
    
    # Créer les managers
    players = [weak_pnj, main_player]  # RankingManager attend une liste, pas un dict
    tournament_manager = TournamentManager()
    ranking_manager = RankingManager(players)
    
    print("=== Test de participation aux tournois ===")
    print(f"PNJ ELO: {weak_pnj.elo}")
    print(f"Joueur principal ELO: {main_player.elo}")
    print()
    
    # Tester pour plusieurs semaines avec différents types de tournois
    test_weeks = [1, 10, 20, 30, 40, 50]  # Semaines avec différents tournois
    
    for week in test_weeks:
        tournaments = tournament_manager.get_tournaments_for_week(week)
        if not tournaments:
            continue
            
        print(f"--- Semaine {week} ---")
        
        # Tournois disponibles pour le PNJ
        pnj_tournaments = tournament_manager.get_tournaments_for_player(week, weak_pnj, ranking_manager)
        
        # Tournois disponibles pour le joueur principal
        main_tournaments = tournament_manager.get_tournaments_for_player(week, main_player, ranking_manager)
        
        print(f"Tournois de la semaine: {len(tournaments)}")
        print(f"Tournois accessibles au PNJ: {len(pnj_tournaments)}")
        print(f"Tournois accessibles au joueur principal: {len(main_tournaments)}")
        
        if tournaments:
            tournament = tournaments[0]
            print(f"Premier tournoi: {tournament.name} (seuil: {tournament.eligibility_threshold})")
        
        # Le PNJ devrait avoir accès à TOUS les tournois
        if len(pnj_tournaments) == len(tournaments):
            print("[OK] PNJ a accès à tous les tournois")
        else:
            print("[ERREUR] PNJ n'a pas accès à tous les tournois")
            
        # Le joueur principal devrait être limité par l'éligibilité
        if len(main_tournaments) <= len(pnj_tournaments):
            print("[OK] Joueur principal correctement limité par l'éligibilité")
        else:
            print("[ERREUR] Problème avec les limitations du joueur principal")
            
        print()

if __name__ == "__main__":
    test_pnj_tournament_participation()
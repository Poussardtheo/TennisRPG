#!/usr/bin/env python3
"""
Test spécifique pour les Grand Slams avec ELO très faible
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from TennisRPG_v2.managers.tournament_manager import TournamentManager
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.data.tournaments_data import TournamentCategory

def test_grand_slam_access():
    """Test l'accès aux Grand Slams avec très faible ELO"""
    
    # Créer un PNJ avec ELO de débutant
    beginner_pnj = Player(Gender.MALE, "PNJ", "Debutant", "FRA", 180, 1)
    beginner_pnj.elo = 100  # ELO extrêmement faible
    beginner_pnj.is_main_player = False
    
    # Créer un joueur principal avec même ELO de débutant
    beginner_main = Player(Gender.MALE, "Joueur", "Debutant", "FRA", 180, 1)
    beginner_main.elo = 100  # ELO extrêmement faible
    beginner_main.is_main_player = True
    
    # Créer les managers
    players = [beginner_pnj, beginner_main]
    tournament_manager = TournamentManager()
    ranking_manager = RankingManager(players)
    
    print("=== Test accès Grand Slams avec ELO très faible ===")
    print(f"ELO des deux joueurs: {beginner_pnj.elo}")
    print()
    
    # Tester toutes les semaines pour trouver des Grand Slams
    for week in range(1, 53):
        tournaments = tournament_manager.get_tournaments_for_week(week)
        if not tournaments:
            continue
        
        # Chercher des Grand Slams
        grand_slams = [t for t in tournaments if t.category == TournamentCategory.GRAND_SLAM]
        if not grand_slams:
            continue
            
        print(f"--- Semaine {week} ---")
        
        for gs in grand_slams:
            print(f"Grand Slam trouvé: {gs.name}")
            print(f"  Seuil ATP: {gs.eligibility_threshold}")
            print(f"  Seuil ELO équivalent: {gs._convert_atp_rank_to_elo_threshold(gs.eligibility_threshold)}")
            
            # Test d'éligibilité directe
            pnj_eligible_direct = gs.is_player_eligible(beginner_pnj, ranking_manager)
            main_eligible_direct = gs.is_player_eligible(beginner_main, ranking_manager)
            
            print(f"  PNJ éligible (test direct): {pnj_eligible_direct}")
            print(f"  Joueur principal éligible (test direct): {main_eligible_direct}")
            
        # Test via tournament_manager
        pnj_tournaments = tournament_manager.get_tournaments_for_player(week, beginner_pnj, ranking_manager)
        main_tournaments = tournament_manager.get_tournaments_for_player(week, beginner_main, ranking_manager)
        
        pnj_gs = [t for t in pnj_tournaments if t.category == TournamentCategory.GRAND_SLAM]
        main_gs = [t for t in main_tournaments if t.category == TournamentCategory.GRAND_SLAM]
        
        print(f"Grand Slams accessibles au PNJ via manager: {len(pnj_gs)}")
        print(f"Grand Slams accessibles au joueur principal via manager: {len(main_gs)}")
        
        # Validation
        if len(pnj_gs) == len(grand_slams) and len(main_gs) <= len(grand_slams):
            if len(main_gs) < len(grand_slams):
                print("[SUCCÈS] PNJ accède à tous les Grand Slams, joueur principal est correctement limité")
            else:
                print("[INFO] Joueur principal accède aussi aux Grand Slams malgré ELO faible")
        else:
            print("[PROBLÈME] Résultats inattendus")
            
        print()
        break  # Test seulement le premier Grand Slam trouvé

if __name__ == "__main__":
    test_grand_slam_access()
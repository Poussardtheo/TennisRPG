#!/usr/bin/env python3
"""
Test pour démontrer la différence entre PNJ et joueur principal pour l'éligibilité
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from TennisRPG_v2.managers.tournament_manager import TournamentManager
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager

def test_eligibility_difference():
    """Test qui démontre clairement la différence d'éligibilité"""
    
    # Créer un PNJ avec ELO très faible
    weak_pnj = Player(Gender.MALE, "PNJ", "TresFaible", "FRA", 180, 1)
    weak_pnj.elo = 300  # ELO extrêmement faible
    weak_pnj.is_main_player = False
    
    # Créer un joueur principal avec même ELO très faible
    weak_main = Player(Gender.MALE, "Joueur", "TresFaible", "FRA", 180, 1)
    weak_main.elo = 300  # ELO extrêmement faible
    weak_main.is_main_player = True
    
    # Créer les managers
    players = [weak_pnj, weak_main]
    tournament_manager = TournamentManager()
    ranking_manager = RankingManager(players)
    
    print("=== Test différence éligibilité PNJ vs Joueur Principal ===")
    print(f"ELO des deux joueurs: {weak_pnj.elo}")
    print()
    
    # Chercher une semaine avec tournois exigeants (comme Roland Garros)
    grand_slam_weeks = [21, 22, 23]  # Période autour de Roland Garros
    
    for week in grand_slam_weeks:
        tournaments = tournament_manager.get_tournaments_for_week(week)
        if not tournaments:
            continue
            
        print(f"--- Semaine {week} ---")
        
        pnj_eligible = tournament_manager.get_tournaments_for_player(week, weak_pnj, ranking_manager)
        main_eligible = tournament_manager.get_tournaments_for_player(week, weak_main, ranking_manager)
        
        print(f"Tournois disponibles: {len(tournaments)}")
        for t in tournaments:
            print(f"  - {t.name} (seuil ELO: {t._convert_atp_rank_to_elo_threshold(t.eligibility_threshold)})")
        
        print(f"Tournois accessibles au PNJ: {len(pnj_eligible)}")
        print(f"Tournois accessibles au joueur principal: {len(main_eligible)}")
        
        # Résultat attendu : PNJ accède à tout, joueur principal est limité
        if len(pnj_eligible) == len(tournaments) and len(main_eligible) < len(tournaments):
            print("[SUCCÈS] PNJ accède à tous les tournois, joueur principal est limité comme attendu")
        elif len(pnj_eligible) == len(tournaments) and len(main_eligible) == len(tournaments):
            print("[INFO] Même ELO faible permet au joueur principal d'accéder à tous les tournois")
        else:
            print(f"[PROBLÈME] Résultats inattendus - PNJ: {len(pnj_eligible)}, Principal: {len(main_eligible)}")
            
        print()
        break  # On teste juste la première semaine trouvée

if __name__ == "__main__":
    test_eligibility_difference()
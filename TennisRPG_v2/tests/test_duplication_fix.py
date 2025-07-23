#!/usr/bin/env python3
"""
Test pour vérifier que la correction de la duplication du joueur principal fonctionne correctement.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.entities.tournament import TournamentCategory
from TennisRPG_v2.entities.spectialized_tournaments import ATP250
from TennisRPG_v2.managers.tournament_manager import TournamentManager
from TennisRPG_v2.managers.weekly_activity_manager import WeeklyActivityManager
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.managers.weekly_activity_manager import TournamentActivity

def test_no_duplication():
    """Test que le joueur principal n'apparaît qu'une seule fois dans un tournoi"""
    
    print("Test de non-duplication du joueur principal...")
    
    # Crée un joueur principal bien classé
    main_player = Player(Gender.MALE, "Test", "Player", "France", is_main_player=True)
    main_player.elo = 2000  # Bon niveau
    
    # Crée quelques PNJ moins forts
    npc1 = Player(Gender.MALE, "NPC", "One", "Spain")
    npc1.elo = 1800
    npc2 = Player(Gender.MALE, "NPC", "Two", "Italy") 
    npc2.elo = 1700
    npc3 = Player(Gender.MALE, "NPC", "Three", "Germany")
    npc3.elo = 1600
    
    all_players = {
        main_player.full_name: main_player,
        npc1.full_name: npc1,
        npc2.full_name: npc2,
        npc3.full_name: npc3
    }
    
    # Crée un petit tournoi
    tournament = ATP250(
        name="Test Tournament",
        surface="Hard",
        num_players=4,
        location="Test City"
    )
    
    # Simule les managers
    tournament_manager = TournamentManager()
    ranking_manager = RankingManager(list(all_players.values()))
    weekly_manager = WeeklyActivityManager(tournament_manager, ranking_manager)
    
    # Crée l'activité tournoi
    tournament_activity = TournamentActivity(tournament)
    
    # Exécute l'activité (ceci devrait normalement causer la duplication)
    try:
        result = weekly_manager._execute_tournament_activity(
            main_player, tournament_activity, 1, all_players, None
        )
        
        # Vérifie qu'il n'y a pas de duplication
        participant_names = [p.full_name for p in tournament.participants]
        main_player_count = participant_names.count(main_player.full_name)
        
        print(f"Participants: {participant_names}")
        print(f"Nombre d'occurrences du joueur principal: {main_player_count}")
        
        if main_player_count == 1:
            print("SUCCESS: Le joueur principal n'apparait qu'une seule fois!")
            return True
        else:
            print(f"ERREUR: Le joueur principal apparait {main_player_count} fois!")
            return False
            
    except Exception as e:
        print(f"ERREUR lors du test: {e}")
        return False

if __name__ == "__main__":
    success = test_no_duplication()
    sys.exit(0 if success else 1)

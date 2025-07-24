#!/usr/bin/env python3
"""
Simple tournament test without Unicode characters
"""
import sys
import os
sys.path.append('../..')
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from TennisRPG_v2.managers.tournament_manager import TournamentManager
    from TennisRPG_v2.entities.player import Player, Gender
    from TennisRPG_v2.managers.player_generator import PlayerGenerator
    from TennisRPG_v2.managers.atp_points_manager import ATPPointsManager
    from TennisRPG_v2.managers.ranking_manager import RankingManager

    def test_simple_tournament():
        print("=== SIMPLE TOURNAMENT TEST ===")
        
        # Get tournament manager
        tournament_manager = TournamentManager()
        
        # Try to get Geneva Open from week 21
        print("Looking for Geneva Open in week 21...")
        tournament = tournament_manager.get_tournament_by_name("Gonet Geneva Open", week=21)
        
        if not tournament:
            print("ERROR: Could not find Gonet Geneva Open")
            # Let's see what tournaments are available in week 21
            print("Available tournaments in week 21:")
            week_21_tournaments = tournament_manager.get_tournaments_for_week(21)
            for i, t in enumerate(week_21_tournaments):
                print(f"  {i+1}. '{t.name}' - {t.location}")
            return
        
        print(f"Found tournament: {tournament.name}")
        
        # Create a simple player
        player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player",
            country="France",
            is_main_player=True
        )
        tournament.add_participant(player)
        
        # Add some basic AI players
        generator = PlayerGenerator()
        for i in range(tournament.num_players):
            ai_player = generator.generate_player(Gender.MALE)
            tournament.add_participant(ai_player)
        
        print(f"Tournament has {len(tournament.participants)} participants")
        
        # Try to play tournament
        players_dict = {p.full_name: p for p in tournament.participants}
        
        # Crée d'abord le ranking manager
        players_list = list(players_dict.values())
        ranking_manager = RankingManager(players_list)
        
        atp_points_manager = ATPPointsManager(players_dict, ranking_manager)
        
        print("Starting tournament...")
        result = tournament.play_tournament(atp_points_manager=atp_points_manager, week=21)
        
        print(f"Winner: {result.winner.full_name}")
        print("TEST COMPLETED SUCCESSFULLY")

    if __name__ == "__main__":
        test_simple_tournament()
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
#!/usr/bin/env python3
"""
Test script to verify year progression and ATP points rolling window
"""

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(__file__)
sys.path.insert(0, project_dir)

from TennisRPG_v2.core.game_session_state import GameSessionState
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.utils.constants import TIME_CONSTANTS

def test_year_progression():
    """Test that years progress correctly"""
    print("Testing year progression...")
    
    # Create a game session
    session = GameSessionState()
    
    # Create test players
    player1 = Player("Test", "Player1", "France", Gender.MALE)
    player2 = Player("Test", "Player2", "Spain", Gender.MALE)
    
    session.add_player(player1)
    session.add_player(player2)
    session.initialize_ranking_manager()
    session.initialize_atp_points_manager()
    
    print(f"Initial state: Year {session.current_year}, Week {session.current_week}")
    
    years_seen = set()
    years_seen.add(session.current_year)
    
    # Simulate 3 years (156 weeks)
    for week in range(156):
        # Add some ATP points occasionally
        if week % 10 == 0 and session.atp_points_manager:
            session.atp_points_manager.add_tournament_points(player1, session.current_week, 500)
            session.atp_points_manager.add_tournament_points(player2, session.current_week, 300)
        
        new_year = session.advance_week()
        if new_year:
            years_seen.add(session.current_year)
            print(f"NEW YEAR! Now in Year {session.current_year}, Week {session.current_week}")
            print(f"Player1 ATP Points: {player1.career.atp_points}")
            print(f"Player2 ATP Points: {player2.career.atp_points}")
    
    print(f"\nFinal state: Year {session.current_year}, Week {session.current_week}")
    print(f"Years seen: {sorted(years_seen)}")
    print(f"Player1 final ATP Points: {player1.career.atp_points}")
    print(f"Player2 final ATP Points: {player2.career.atp_points}")
    
    # Test history manager with different years
    if session.game_state and session.game_state.history_manager:
        from TennisRPG_v2.entities.tournament import TournamentResult
        from TennisRPG_v2.data.tournaments_data import TournamentCategory
        
        # Create test tournament results for different years
        for year in sorted(years_seen):
            result = TournamentResult(
                tournament_name=f"Test Tournament {year}",
                category=TournamentCategory.ATP_250,
                winner=player1,
                finalist=player2,
                semifinalists=[],
                quarterfinalists=[],
                all_results={player1: "Winner", player2: "Finalist"},
                match_results=[]
            )
            session.game_state.history_manager.record_tournament_result(result, year, 1)
        
        years_with_data = session.game_state.history_manager.get_years_with_data()
        print(f"Years with tournament data: {years_with_data}")
    
    # Validate results
    assert len(years_seen) == 4, f"Expected 4 years, got {len(years_seen)}"  # 2024, 2025, 2026, 2027
    assert session.current_year == 2027, f"Expected final year 2027, got {session.current_year}"
    assert session.current_week == 1, f"Expected final week 1, got {session.current_week}"
    
    # ATP points should not keep accumulating forever due to rolling window
    assert player1.career.atp_points < 10000, f"Player1 has too many ATP points: {player1.career.atp_points}"
    assert player2.career.atp_points < 10000, f"Player2 has too many ATP points: {player2.career.atp_points}"
    
    print("Year progression test passed!")

if __name__ == "__main__":
    test_year_progression()
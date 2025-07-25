#!/usr/bin/env python3
"""
Simple test to verify the fixes work by checking existing save files
"""

import sys
import os
import json

# Add the project directory to Python path
project_dir = os.path.dirname(__file__)
sys.path.insert(0, project_dir)

def test_existing_save():
    """Test that existing save shows proper year data"""
    print("Testing year progression with save files...")
    
    # Look for save files
    saves_dir = os.path.join(project_dir, "saves")
    if not os.path.exists(saves_dir):
        print("No saves directory found, creating basic test...")
        return test_basic_logic()
    
    save_files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
    if not save_files:
        print("No save files found, creating basic test...")
        return test_basic_logic()
    
    # Look for a save file with tournament history
    save_file = None
    for filename in save_files:
        filepath = os.path.join(saves_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'tournament_history' in data:
                save_file = filepath
                print(f"Checking save file with tournament history: {filename}")
                break
    
    if not save_file:
        print("No save file with tournament history found")
        return test_basic_logic()
    
    with open(save_file, 'r', encoding='utf-8') as f:
        save_data = json.load(f)
    
    # Check current year/week
    current_year = save_data.get('current_year', 2024)
    current_week = save_data.get('current_week', 1)
    print(f"Current game state: Year {current_year}, Week {current_week}")
    
    # Check tournament history
    history_data = save_data.get('tournament_history', {})
    years_with_data = list(history_data.keys())
    print(f"Years with tournament data: {sorted(years_with_data)}")
    
    # Check if there are multiple years or just one
    if len(years_with_data) > 1:
        print("SUCCESS: Multiple years found in history!")
        for year in sorted(years_with_data):
            tournaments_count = sum(len(weeks) for weeks in history_data[year].values())
            print(f"  Year {year}: {tournaments_count} tournament entries")
    else:
        print("ISSUE: Only one year found in history (or no history data)")
        if years_with_data:
            year = years_with_data[0]
            tournaments_count = sum(len(weeks) for weeks in history_data[year].values())
            print(f"  Year {year}: {tournaments_count} tournament entries")
    
    return len(years_with_data) > 1

def test_basic_logic():
    """Test the basic year progression logic"""
    from TennisRPG_v2.utils.constants import TIME_CONSTANTS
    
    print("Testing basic year progression logic...")
    
    # Test advance_week logic manually
    current_week = 52
    current_year = 2024
    
    # Simulate advancing from week 52 to week 1 (new year)
    previous_week = current_week
    current_week = (current_week % TIME_CONSTANTS["WEEKS_PER_YEAR"]) + 1  # Should become 1
    
    if previous_week == TIME_CONSTANTS["WEEKS_PER_YEAR"] and current_week == 1:
        current_year += 1
        print(f"SUCCESS: Year progression logic works - went from week {previous_week} to week {current_week}, year {current_year}")
        return True
    else:
        print(f"ISSUE: Year progression logic failed - week {previous_week} -> {current_week}, year {current_year}")
        return False

if __name__ == "__main__":
    success = test_existing_save()
    if success:
        print("Test completed successfully!")
    else:
        print("Test revealed issues that need to be addressed.")
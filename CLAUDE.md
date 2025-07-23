# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

Since Python may not be directly available as `python`, use the system's Python executable:

```bash
# Testing (requires pytest installation)
pytest TennisRPG_v2/tests/          # Run all tests
pytest TennisRPG_v2/tests/test_core_functionality.py  # Run specific test file
pytest -m "not slow"                # Skip slow tests
pytest -m integration               # Run only integration tests
pytest -m unit                      # Run only unit tests  
pytest -m regression                # Run only regression tests

# Running the game
python TennisRPG_v2/main.py         # Start the tennis RPG game
```

Note: The pytest configuration is in `pytest.ini` with coverage reporting enabled (70% minimum threshold).

## Python Path Notes

- Anaconda Python Path: `pouss/anaconda3/python.exe`

## Architecture Overview

TennisRPG is a text-based tennis RPG game written in Python. The codebase follows a modular architecture:

### Core Structure
- **`TennisRPG_v2/`**: Main package containing all game code
- **`core/`**: Game session management and save system
  - `game_session.py`: Main game loop and session management
  - `save_manager.py`: Save/load game state functionality
- **`entities/`**: Core game objects
  - `player.py`: Player class with stats, skills, and progression
  - `tournament.py`: Tournament system with different categories
  - `ranking.py`: ATP ranking system implementation
- **`managers/`**: Business logic controllers
  - `tournament_manager.py`: Tournament scheduling and management
  - `ranking_manager.py`: Player ranking calculations
  - `player_generator.py`: Procedural player generation
  - `weekly_activity_manager.py`: Week-by-week game progression
  - `atp_points_manager.py`: ATP points distribution system
- **`data/`**: Static game data
  - `tournaments_database.py`: Tournament calendar and data
  - `surface_data.py`: Court surface characteristics
  - `countries.py`: Country and nationality data
- **`utils/`**: Shared utilities and constants
  - `constants.py`: Game configuration and constants
  - `helpers.py`: Utility functions

### Game Flow
1. Player creates character through `GameSession.start_new_game()`
2. Weekly progression managed by `WeeklyActivityManager`
3. Player chooses between rest, training, or tournaments each week
4. Tournament participation handled by `TournamentManager`
5. Rankings updated through `RankingManager` and `ATPPointsManager`
6. Progress saved via `SaveManager`

### Key Features
- **Player Progression**: Stat-based RPG system with experience and skill points
- **Tournament System**: Real ATP calendar with different tournament categories (ATP250, ATP500, Masters 1000, Grand Slams)
- **Ranking System**: Realistic ATP ranking calculations
- **Surface Specialization**: Different court surfaces (clay, grass, hard court) affect gameplay
- **Career Mode**: Week-by-week progression through tennis seasons

### Testing Structure
Tests are organized by functionality:
- `test_core_functionality.py`: Core game mechanics
- `test_tournament.py`: Tournament system tests
- `test_performance.py`: Performance benchmarks
- `test_regression.py`: Regression testing
- Test markers: `slow`, `integration`, `unit`, `regression`

### Package Structure
The game is set up as an installable Python package with entry point `play = TennisRPG.main:main` defined in `setup.py`.
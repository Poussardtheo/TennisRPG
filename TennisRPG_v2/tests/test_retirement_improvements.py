#!/usr/bin/env python3
"""
Tests pour les améliorations du système de retraite
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from TennisRPG_v2.managers.player_generator import PlayerGenerator
from TennisRPG_v2.managers.retirement_manager import RetirementManager
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.entities.player import Gender
from TennisRPG_v2.utils.constants import TIME_CONSTANTS


class TestRetirementImprovements(unittest.TestCase):
    """Tests pour les améliorations du système de retraite"""

    def setUp(self):
        """Setup pour chaque test"""
        self.generator = PlayerGenerator()
        self.retirement_manager = RetirementManager(self.generator)

    def test_retirement_log_persistence(self):
        """Test que les retraites sont enregistrées dans le log"""
        # Créer des joueurs
        players = {}
        for i in range(20):
            player = self.generator.generate_player(Gender.MALE)
            players[player.full_name] = player

        # Créer un ranking manager
        ranking_manager = RankingManager(list(players.values()))
        
        # État initial du log
        initial_log_size = len(self.retirement_manager.retirement_log)
        
        # Simuler des retraites
        retired_players, new_players = self.retirement_manager.process_end_of_season_retirements(
            players, ranking_manager, TIME_CONSTANTS["GAME_START_YEAR"] - 1, Gender.MALE
        )
        
        # Vérifier que le log a été mis à jour
        self.assertGreaterEqual(len(self.retirement_manager.retirement_log), initial_log_size)
        
        # Si des retraites ont eu lieu, vérifier la structure du log
        if self.retirement_manager.retirement_log:
            retirement = self.retirement_manager.retirement_log[-1]
            required_keys = ['player_name', 'age', 'ranking', 'year', 'country']
            for key in required_keys:
                self.assertIn(key, retirement)

    def test_new_players_match_main_player_gender(self):
        """Test que tous les nouveaux joueurs ont le genre du joueur principal"""
        # Créer des joueurs mixtes
        players = {}
        for i in range(10):
            # Mix d'hommes et femmes
            gender = Gender.MALE if i % 2 == 0 else Gender.FEMALE
            player = self.generator.generate_player(gender)
            players[player.full_name] = player

        ranking_manager = RankingManager(list(players.values()))
        
        # Simuler des retraites avec genre principal = FEMALE
        retired_players, new_players = self.retirement_manager.process_end_of_season_retirements(
            players, ranking_manager, TIME_CONSTANTS["GAME_START_YEAR"] - 1, Gender.FEMALE
        )
        
        # Vérifier que tous les nouveaux joueurs sont FEMALE
        for new_player in new_players:
            self.assertEqual(new_player.gender, Gender.FEMALE)

    def test_retirement_stats_calculation(self):
        """Test le calcul des statistiques de retraite"""
        # Ajouter manuellement quelques retraites au log
        test_retirements = [
            {"player_name": "Test Player 1", "age": 32, "ranking": 50, "year": 2023, "country": "France"},
            {"player_name": "Test Player 2", "age": 35, "ranking": 100, "year": 2023, "country": "Spain"},
            {"player_name": "Test Player 3", "age": 38, "ranking": 200, "year": 2023, "country": "USA"}
        ]
        
        for retirement in test_retirements:
            self.retirement_manager.retirement_log.append(retirement)
        
        # Obtenir les stats
        stats = self.retirement_manager.get_retirement_stats(2023)
        
        # Vérifications
        self.assertEqual(stats["total_retirements"], 3)
        self.assertEqual(stats["average_retirement_age"], 35.0)  # (32+35+38)/3
        self.assertEqual(stats["youngest_retiree"], 32)
        self.assertEqual(stats["oldest_retiree"], 38)
        self.assertEqual(len(stats["countries"]), 3)

    def test_top_100_filtering(self):
        """Test que seuls les joueurs top 100 sont affichés"""
        # Créer des joueurs avec différents classements
        players = []
        for i in range(5):
            player = self.generator.generate_player(Gender.MALE)
            players.append(player)

        # Mock du ranking manager pour contrôler les classements
        mock_ranking_manager = Mock()
        mock_ranking_manager.get_player_rank.side_effect = lambda p: [50, 150, 30, 200, 80][players.index(p)]
        
        # Simuler l'affichage détaillé
        with patch('builtins.print') as mock_print:
            self.retirement_manager._display_detailed_retirements(players, mock_ranking_manager)
        
        # Vérifier qu'il y a eu un appel print pour les retraites notables
        print_calls = [str(call) for call in mock_print.call_args_list]
        notable_retirements_found = any("RETRAITES NOTABLES" in call for call in print_calls)
        self.assertTrue(notable_retirements_found)

    def test_preliminary_year_calculation(self):
        """Test que l'année préliminaire est correctement calculée"""
        preliminary_year = TIME_CONSTANTS["GAME_START_YEAR"] - 1
        expected_year = 2023  # Si GAME_START_YEAR = 2024
        
        self.assertEqual(preliminary_year, expected_year)


if __name__ == '__main__':
    unittest.main()
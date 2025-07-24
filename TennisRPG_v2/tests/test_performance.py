"""
Tests de performance pour TennisRPG v2
"""
import time
import pytest
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.atp_points_manager import ATPPointsManager
from TennisRPG_v2.managers.player_generator import PlayerGenerator
from TennisRPG_v2.managers.tournament_manager import TournamentManager
from TennisRPG_v2.managers.ranking_manager import RankingManager


class TestPerformance:
    """Tests de performance"""
    
    @pytest.mark.slow
    def test_player_generation_performance(self):
        """Test performance génération de joueurs"""
        generator = PlayerGenerator()
        
        start_time = time.time()
        players = []
        
        for _ in range(1000):
            player = generator.generate_player(Gender.MALE)
            players.append(player)
            
        end_time = time.time()
        generation_time = end_time - start_time
        
        assert len(players) == 1000
        assert generation_time < 5.0  # Moins de 5 secondes
        
        # Vérifie l'unicité
        names = [p.full_name for p in players]
        unique_names = set(names)
        assert len(unique_names) > 950  # Au moins 95% d'unicité
        
    @pytest.mark.slow
    def test_tournament_simulation_performance(self):
        """Test performance simulation tournoi"""
        from TennisRPG_v2.data.tournaments_database import tournois

        week = 10
        # Prend un tournoi ATP 250
        week_tournaments = tournois.get(week, [])
        if not week_tournaments:
            pytest.skip(f"No tournaments found for week {week}")
            
        tournament = week_tournaments[0]
        
        # Génère des joueurs
        generator = PlayerGenerator()
        players = {generator.generate_player(Gender.MALE).full_name: generator.generate_player(Gender.MALE)
                   for _ in range(tournament.num_players)}
        
        # Nettoie le tournoi
        tournament.participants.clear()
        tournament.match_results.clear()
        tournament.eliminated_players.clear()
        
        # Ajoute les participants
        for player in players.values():
            tournament.add_participant(player)

        # Crée d'abord le ranking manager  
        players_list = list(players.values())
        ranking_manager = RankingManager(players_list)
        
        # Génère le gestionnaire de points ATP
        atp_points_manager = ATPPointsManager(players, ranking_manager)

        start_time = time.time()
        result = tournament.play_tournament(verbose=False, atp_points_manager=atp_points_manager, week=week)
        end_time = time.time()
        
        simulation_time = end_time - start_time
        
        assert result is not None
        assert simulation_time < 2.0  # Moins de 2 secondes
        
    def test_elo_calculation_performance(self):
        """Test performance calcul ELO"""
        players = []
        generator = PlayerGenerator()
        
        # Crée 100 joueurs
        for _ in range(100):
            player = generator.generate_player(Gender.MALE)
            players.append(player)
            
        start_time = time.time()
        
        # Met à jour tous les ELOs
        for player in players:
            player._recalculate_all_elo_ratings()
            
        end_time = time.time()
        calculation_time = end_time - start_time
        
        assert calculation_time < 0.1  # Moins de 100ms
        
    @pytest.mark.slow
    def test_ranking_system_performance(self):
        """Test performance système de classement"""
        from TennisRPG_v2.managers.ranking_manager import RankingManager
        
        generator = PlayerGenerator()
        players = [generator.generate_player(Gender.MALE) for _ in range(500)]
        
        start_time = time.time()
        ranking_manager = RankingManager(players)
        end_time = time.time()
        
        initialization_time = end_time - start_time
        
        start_time = time.time()
        atp_ranking = ranking_manager.atp_ranking
        elo_ranking = ranking_manager.elo_ranking
        end_time = time.time()

        ranking_time = end_time - start_time
        
        assert initialization_time < 1.0  # Moins d'1 seconde
        assert ranking_time < 0.5  # Moins de 500ms
        assert len(atp_ranking.rankings) == 500
        assert len(elo_ranking.rankings) == 500

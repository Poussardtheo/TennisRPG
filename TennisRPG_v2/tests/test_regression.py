"""
Tests de régression pour TennisRPG v2
"""
import pytest
from TennisRPG.entities.player import Player, Gender
from TennisRPG.managers.player_generator import PlayerGenerator


class TestRegression:
    """Tests de régression pour vérifier la compatibilité"""
    
    def test_player_stats_consistency(self):
        """Test cohérence des stats joueur"""
        player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player",
            country="Test"
        )
        
        # Vérifie les valeurs par défaut
        assert player.stats.coup_droit >= 20
        assert player.stats.service >= 20
        assert player.stats.mental >= 20
        assert player.stats.physique >= 20
        
        # Vérifie que l'ELO est cohérent
        initial_elo = player.elo
        assert initial_elo > 0
        
        player.update_elo()
        assert player.elo == initial_elo  # Sans changement de stats
        
    def test_tournament_eligibility_regression(self):
        """Test régression éligibilité tournois"""
        from TennisRPG.managers.tournament_manager import TournamentManager
        
        manager = TournamentManager()
        
        # Joueur avec stats moyennes
        player = Player(
            gender=Gender.MALE,
            first_name="Average",
            last_name="Player",
            country="USA"
        )
        player.stats.coup_droit = 60
        player.stats.service = 60
        player.update_elo()
        
        # Doit être éligible à au moins quelques tournois
        eligible_tournaments = manager.get_tournaments_for_player(1, player)
        assert len(eligible_tournaments) > 0
        
    def test_save_load_consistency(self):
        """Test régression save/load"""
        player = Player(
            gender=Gender.FEMALE,
            first_name="Save",
            last_name="Test",
            country="Canada",
            is_main_player=True
        )
        
        # Modifie quelques stats
        player.stats.coup_droit = 85
        player.stats.service = 78
        player.update_elo()
        
        # Sauvegarde et charge
        player_data = player.to_dict()
        loaded_player = Player.from_dict(player_data)
        
        # Vérifie l'intégrité
        assert loaded_player.first_name == player.first_name
        assert loaded_player.stats.coup_droit == player.stats.coup_droit
        assert loaded_player.elo == player.elo
        assert loaded_player.is_main_player == player.is_main_player
        
    @pytest.mark.benchmark
    def test_player_generation_benchmark(self, benchmark):
        """Benchmark génération de joueur"""
        generator = PlayerGenerator()
        
        def generate_player():
            return generator.generate_player(Gender.MALE)
            
        player = benchmark(generate_player)
        assert player is not None
        assert player.gender == Gender.MALE
        
    def test_tournament_database_integrity(self):
        """Test intégrité base de données tournois"""
        from TennisRPG.data.tournaments_database import tournois
        
        # Vérifie que les semaines clés existent
        assert 1 in tournois  # Début d'année
        assert 22 in tournois  # Roland Garros
        assert 28 in tournois  # Wimbledon
        assert 35 in tournois  # US Open
        
        # Vérifie qu'il y a des tournois chaque semaine
        total_tournaments = 0
        for week in range(1, 53):
            week_tournaments = tournois.get(week, [])
            total_tournaments += len(week_tournaments)
            
        assert total_tournaments > 100  # Au moins 100 tournois dans l'année
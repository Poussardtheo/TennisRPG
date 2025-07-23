"""
Tests de fonctionnalité core pour TennisRPG v2
"""
import pytest
import sys
import os

from TennisRPG_v2.managers.atp_points_manager import ATPPointsManager

# Ajoute le chemin du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.tournament_manager import TournamentManager
from TennisRPG_v2.managers.player_generator import PlayerGenerator


class TestPlayerCreation:
    """Tests de création de joueurs"""
    
    def test_player_creation_basic(self):
        """Test création joueur de base"""
        player = Player(
            gender=Gender.MALE,
            first_name="Rafael",
            last_name="Testdal",
            country="Spain"
        )
        
        assert player.first_name == "Rafael"
        assert player.last_name == "Testdal"
        assert player.country == "Spain"
        assert player.gender == Gender.MALE
        assert player.full_name == "Rafael Testdal"
        
    def test_player_stats_initialization(self):
        """Test initialisation des stats"""
        player = Player(
            gender=Gender.FEMALE,
            first_name="Serena",
            last_name="Test",
            country="USA"
        )
        
        # Vérifie que toutes les stats sont initialisées
        assert hasattr(player, 'stats')
        assert player.stats.coup_droit >= 20
        assert player.stats.service >= 20
        assert player.elo > 0
        
    def test_player_serialization(self):
        """Test sérialisation/désérialisation"""
        player = Player(
            gender=Gender.MALE,
            first_name="Novak",
            last_name="Test",
            country="Serbia",
            is_main_player=True
        )
        
        # Sérialise
        player_dict = player.to_dict()
        
        # Désérialise
        restored_player = Player.from_dict(player_dict)
        
        assert restored_player.first_name == player.first_name
        assert restored_player.last_name == player.last_name
        assert restored_player.country == player.country
        assert restored_player.is_main_player == player.is_main_player


class TestPlayerGenerator:
    """Tests du générateur de joueurs"""
    
    def test_generate_male_players(self):
        """Test génération joueurs masculins"""
        generator = PlayerGenerator()
        
        players = []
        for _ in range(10):
            player = generator.generate_player(Gender.MALE)
            players.append(player)
            
        assert len(players) == 10
        assert all(p.gender == Gender.MALE for p in players)
        
        # Vérifie l'unicité des noms
        names = [p.full_name for p in players]
        assert len(set(names)) == len(names)  # Tous uniques
        
    def test_generate_female_players(self):
        """Test génération joueurs féminins"""
        generator = PlayerGenerator()
        
        players = []
        for _ in range(5):
            player = generator.generate_player(Gender.FEMALE)
            players.append(player)
            
        assert len(players) == 5
        assert all(p.gender == Gender.FEMALE for p in players)


class TestTournamentSystem:
    """Tests du système de tournois"""
    
    def test_tournament_manager_initialization(self):
        """Test initialisation gestionnaire tournois"""
        manager = TournamentManager()
        assert manager.tournament_database is not None
        
    def test_get_tournaments_for_week(self):
        """Test récupération tournois par semaine"""
        manager = TournamentManager()
        
        # Teste quelques semaines connues
        tournaments_week_1 = manager.get_tournaments_for_week(1)
        tournaments_week_22 = manager.get_tournaments_for_week(22)  # Roland Garros
        
        assert len(tournaments_week_1) > 0
        assert len(tournaments_week_22) > 0
        
        # Roland Garros doit être en semaine 22
        rg_found = any("Roland-Garros" in t.name for t in tournaments_week_22)
        assert rg_found, "Roland Garros should be in week 22"
        
    def test_tournament_eligibility(self):
        """Test éligibilité aux tournois"""
        manager = TournamentManager()
        
        # Crée un joueur fort
        strong_player = Player(
            gender=Gender.MALE,
            first_name="Strong",
            last_name="Player",
            country="USA"
        )
        strong_player.stats.coup_droit = 90
        strong_player.stats.service = 88
        strong_player._recalculate_all_elo_ratings()
        
        # Crée un joueur faible
        weak_player = Player(
            gender=Gender.MALE,
            first_name="Weak",
            last_name="Player",
            country="USA"
        )
        weak_player.stats.coup_droit = 30
        weak_player.stats.service = 25
        weak_player._recalculate_all_elo_ratings()
        
        # Test éligibilité semaine 1
        strong_eligible = manager.get_tournaments_for_player(1, strong_player)
        weak_eligible = manager.get_tournaments_for_player(1, weak_player)
        
        # Le joueur fort doit être éligible à plus de tournois
        assert len(strong_eligible) >= len(weak_eligible)


class TestGameFlow:
    """Tests du flux de jeu"""
    
    def test_game_session_creation(self):
        """Test création session de jeu"""
        from ..core.game_session import GameSession
        
        session = GameSession()
        assert session is not None
        assert session.game_running == True
        assert session.current_week == 1
        assert session.current_year == 2024
        
    def test_save_manager_creation(self):
        """Test création gestionnaire sauvegarde"""
        from ..core.save_manager import SaveManager
        
        save_manager = SaveManager()
        assert save_manager is not None
        assert save_manager.save_directory is not None


class TestIntegration:
    """Tests d'intégration"""
    
    @pytest.mark.slow
    def test_tournament_simulation_basic(self):
        """Test simulation tournoi basique"""
        from ..data.tournaments_database import tournois
        
        # Prend un tournoi ATP 250
        week_21_tournaments = tournois.get(21, [])
        geneva_open = None
        
        for t in week_21_tournaments:
            if "Geneva" in t.name:
                geneva_open = t
                break
                
        if geneva_open is None:
            pytest.skip("Geneva Open not found in week 21")
            
        # Génère des joueurs de test
        generator = PlayerGenerator()
        players = {generator.generate_player(Gender.MALE).full_name: generator.generate_player(Gender.MALE) for _ in
                   range(8)}

        # Nettoie le tournoi
        geneva_open.participants.clear()
        geneva_open.match_results.clear()
        geneva_open.eliminated_players.clear()
        
        # Ajoute les participants
        for player in players.values():
            geneva_open.add_participant(player)

        # Génère le gestionnaire de points ATP
        atp_points_manager = ATPPointsManager(players)

        # Simule le tournoi
        result = geneva_open.play_tournament(verbose=False, atp_points_manager=atp_points_manager, week=21)
        
        assert result is not None
        assert result.winner in players.values()
        assert result.tournament_name == geneva_open.name
        
    def test_activity_system_basic(self):
        """Test système d'activités basique"""
        from ..managers.weekly_activity_manager import (
            WeeklyActivityManager, TrainingActivity, RestActivity
        )
        from ..managers.tournament_manager import TournamentManager
        from ..managers.ranking_manager import RankingManager
        
        # Crée les managers
        tournament_manager = TournamentManager()
        
        # Crée quelques joueurs pour le ranking
        generator = PlayerGenerator()
        players = [generator.generate_player(Gender.MALE) for _ in range(10)]
        ranking_manager = RankingManager(players)
        
        activity_manager = WeeklyActivityManager(tournament_manager, ranking_manager)
        
        # Crée un joueur de test
        test_player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player",
            country="Test"
        )
        
        # Test activité entraînement
        training = TrainingActivity()
        result = training.execute(test_player)
        
        assert result.success
        assert result.xp_gained > 0
        
        # Test activité repos
        rest = RestActivity()
        result = rest.execute(test_player)
        
        assert result.success
        assert result.fatigue_change < 0  # Récupération
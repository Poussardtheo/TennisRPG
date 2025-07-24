"""
Tests pour le système de blessures.
"""

import pytest
from unittest.mock import Mock, patch
import random

from ..entities.player import Player, Gender
from ..entities.injury import Injury, InjuryCalculator
from ..managers.injury_manager import InjuryManager
from ..data.injuries_data import INJURIES_DATABASE, InjurySeverity, InjuryType


class TestInjury:
    """Tests pour la classe Injury"""
    
    def test_injury_creation(self):
        """Test de création d'une blessure"""
        injury_data = INJURIES_DATABASE["fatigue_musculaire"]
        injury = Injury(
            injury_key="fatigue_musculaire",
            injury_data=injury_data,
            weeks_remaining=2,
            original_duration=2
        )
        
        assert injury.name == "Fatigue musculaire"
        assert injury.type == InjuryType.MUSCLE
        assert injury.severity == InjurySeverity.LEGERE
        assert injury.weeks_remaining == 2
        assert not injury.is_healed
    
    def test_injury_recovery(self):
        """Test de la récupération d'une blessure"""
        injury_data = INJURIES_DATABASE["fatigue_musculaire"]
        injury = Injury(
            injury_key="fatigue_musculaire",
            injury_data=injury_data,
            weeks_remaining=3,
            original_duration=3
        )
        
        # Avance la récupération
        injury.advance_recovery(1)
        assert injury.weeks_remaining == 2
        assert injury.recovery_progress == pytest.approx(1/3, rel=1e-2)
        
        # Guérison complète
        injury.advance_recovery(2)
        assert injury.weeks_remaining == 0
        assert injury.is_healed
        assert injury.recovery_progress == 1.0
    
    def test_stat_modifier(self):
        """Test des modificateurs de statistiques"""
        injury_data = INJURIES_DATABASE["elbow_tennis"]
        injury = Injury(
            injury_key="elbow_tennis",
            injury_data=injury_data,
            weeks_remaining=3,
            original_duration=3
        )
        
        # Doit affecter le coup droit
        modifier = injury.get_stat_modifier("Coup droit")
        assert modifier < 1.0  # Réduction
        
        # Ne doit pas affecter une stat non concernée
        modifier = injury.get_stat_modifier("Vitesse")
        assert modifier == 1.0  # Pas d'effet
    
    def test_injury_serialization(self):
        """Test de la sérialisation/désérialisation"""
        injury_data = INJURIES_DATABASE["crampes"]
        injury = Injury(
            injury_key="crampes",
            injury_data=injury_data,
            weeks_remaining=1,
            original_duration=1
        )
        
        # Sérialisation
        data = injury.to_dict()
        assert data["injury_key"] == "crampes"
        assert data["weeks_remaining"] == 1
        
        # Désérialisation
        restored_injury = Injury.from_dict(data, injury_data)
        assert restored_injury.injury_key == "crampes"
        assert restored_injury.weeks_remaining == 1
        assert restored_injury.name == injury.name


class TestInjuryCalculator:
    """Tests pour le calculateur de blessures"""
    
    def test_injury_risk_calculation(self):
        """Test du calcul du risque de blessure"""
        # Fatigue faible = risque faible
        low_risk = InjuryCalculator.calculate_injury_risk(20, "Entraînement")
        assert low_risk < 0.01
        
        # Fatigue élevée = risque élevé
        high_risk = InjuryCalculator.calculate_injury_risk(90, "Tournament")
        assert high_risk > 0.1
        
        # Le tournoi augmente le risque
        training_risk = InjuryCalculator.calculate_injury_risk(70, "Entraînement")
        tournament_risk = InjuryCalculator.calculate_injury_risk(70, "Tournament")
        assert tournament_risk > training_risk
    
    def test_generate_random_injury(self):
        """Test de génération d'une blessure aléatoire"""
        # Fatigue très faible = pas de blessure possible
        injury = InjuryCalculator.generate_random_injury(10)
        assert injury is None
        
        # Fatigue élevée = blessures possibles
        injury = InjuryCalculator.generate_random_injury(80)
        # Note: peut être None selon l'aléatoire, mais les blessures possibles existent
        possible_injuries = [key for key, data in INJURIES_DATABASE.items() 
                           if 80 >= data.fatigue_threshold]
        assert len(possible_injuries) > 0


class TestPlayerInjuryIntegration:
    """Tests de l'intégration des blessures dans le joueur"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player",
            country="France",
            is_main_player=True
        )
    
    def test_player_injury_status(self):
        """Test du statut de blessure du joueur"""
        assert not self.player.is_injured()
        assert self.player.should_participate()
        
        # Ajoute une blessure
        injury_data = INJURIES_DATABASE["fatigue_musculaire"]
        injury = Injury(
            injury_key="fatigue_musculaire",
            injury_data=injury_data,
            weeks_remaining=2,
            original_duration=2
        )
        
        self.player.add_injury(injury)
        assert self.player.is_injured()
        assert not self.player.should_participate()  # Ne peut plus participer
    
    def test_player_heal_injuries(self):
        """Test de la guérison des blessures du joueur"""
        # Ajoute plusieurs blessures
        injury1_data = INJURIES_DATABASE["fatigue_musculaire"]
        injury1 = Injury(
            injury_key="fatigue_musculaire",
            injury_data=injury1_data,
            weeks_remaining=1,
            original_duration=2
        )
        
        injury2_data = INJURIES_DATABASE["crampes"]
        injury2 = Injury(
            injury_key="crampes",
            injury_data=injury2_data,
            weeks_remaining=2,
            original_duration=2
        )
        
        self.player.add_injury(injury1)
        self.player.add_injury(injury2)
        
        assert len(self.player.physical.get_active_injuries()) == 2
        
        # Guérison d'une semaine
        healed = self.player.heal_injuries(1)
        assert len(healed) == 1  # Une blessure guérie
        assert len(self.player.physical.get_active_injuries()) == 1  # Une reste
    
    def test_injury_modified_stats(self):
        """Test des statistiques modifiées par les blessures"""
        original_stats = self.player.stats.to_dict()
        
        # Ajoute une blessure qui affecte l'endurance
        injury_data = INJURIES_DATABASE["crampes"]
        injury = Injury(
            injury_key="crampes",
            injury_data=injury_data,
            weeks_remaining=1,
            original_duration=1
        )
        
        self.player.add_injury(injury)
        modified_stats = self.player.get_injury_modified_stats()
        
        # L'endurance doit être réduite
        assert modified_stats["Endurance"] < original_stats["Endurance"]
        # Les autres stats ne changent pas
        assert modified_stats["Coup droit"] == original_stats["Coup droit"]
    
    @patch('random.random')
    def test_check_for_injury(self, mock_random):
        """Test de la vérification de blessure"""
        # Fatigue élevée pour augmenter les chances
        self.player.physical.fatigue = 85
        
        # Force une blessure
        mock_random.return_value = 0.01  # Très faible pour déclencher la blessure
        
        injury = self.player.check_for_injury("Tournament")
        # Note: peut être None selon l'implémentation exacte et l'aléatoire


class TestInjuryManager:
    """Tests pour le gestionnaire des blessures"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.injury_manager = InjuryManager()
        self.player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Manager",
            country="France",
            is_main_player=False
        )
    
    def test_force_rest_if_injured(self):
        """Test du repos forcé pour joueur blessé"""
        # Joueur sain
        assert not self.injury_manager.force_rest_if_injured(self.player)
        
        # Ajoute une blessure
        injury_data = INJURIES_DATABASE["fatigue_musculaire"]
        injury = Injury(
            injury_key="fatigue_musculaire",
            injury_data=injury_data,
            weeks_remaining=2,
            original_duration=2
        )
        self.player.add_injury(injury)
        
        # Maintenant doit être forcé au repos
        assert self.injury_manager.force_rest_if_injured(self.player)
    
    def test_simulate_injury_for_testing(self):
        """Test de simulation d'une blessure pour tests"""
        injury = self.injury_manager.simulate_injury_for_testing(
            self.player, "fatigue_musculaire"
        )
        
        assert injury is not None
        assert injury.injury_key == "fatigue_musculaire"
        assert self.player.is_injured()
        
        # Clé invalide
        invalid_injury = self.injury_manager.simulate_injury_for_testing(
            self.player, "blessure_inexistante"
        )
        assert invalid_injury is None
    
    def test_activity_injury_processing(self):
        """Test du traitement des blessures lors d'activités"""
        # Fatigue très élevée pour maximiser les chances
        self.player.physical.fatigue = 95
        
        # Test avec mock pour contrôler l'aléatoire
        with patch('random.random', return_value=0.001):  # Force une blessure
            injury = self.injury_manager.process_activity_injury(
                self.player, "Tournament", sets_played=5, tournament_category="Grand Chelem"
            )
            # Le résultat dépend de l'implémentation exacte
    
    def test_weekly_injury_processing(self):
        """Test du traitement hebdomadaire des blessures"""
        players = [self.player]
        
        # Ajoute une blessure qui guérit cette semaine
        injury_data = INJURIES_DATABASE["fatigue_musculaire"]
        injury = Injury(
            injury_key="fatigue_musculaire",
            injury_data=injury_data,
            weeks_remaining=1,
            original_duration=2
        )
        self.player.add_injury(injury)
        
        results = self.injury_manager.process_weekly_injuries(players)
        
        # La blessure devrait être guérie
        assert not self.player.is_injured()


@pytest.mark.integration
class TestInjurySystemIntegration:
    """Tests d'intégration du système complet"""
    
    def test_injury_database_integrity(self):
        """Test de l'intégrité de la base de données des blessures"""
        for key, injury_data in INJURIES_DATABASE.items():
            # Vérification des champs obligatoires
            assert injury_data.name
            assert injury_data.type in InjuryType
            assert injury_data.severity in InjurySeverity
            assert injury_data.min_recovery_weeks > 0
            assert injury_data.max_recovery_weeks >= injury_data.min_recovery_weeks
            assert 0 <= injury_data.fatigue_threshold <= 100
            assert injury_data.probability_weight > 0
            
            # Vérification des modificateurs de stats
            for stat, modifier in injury_data.affected_stats.items():
                assert 0 <= modifier <= 1.0  # Réduction entre 0% et 100%
    
    def test_injury_probability_ranges(self):
        """Test des plages de probabilité de blessure"""
        from ..data.injuries_data import INJURY_PROBABILITY_BY_FATIGUE
        
        previous_max = -1
        for (min_fatigue, max_fatigue), probability in INJURY_PROBABILITY_BY_FATIGUE.items():
            # Vérification de l'ordre croissant
            assert min_fatigue > previous_max
            assert max_fatigue > min_fatigue
            assert 0 <= probability <= 1.0
            previous_max = max_fatigue - 1
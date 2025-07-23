"""
Tests pour le système de talents
"""
import pytest
from unittest.mock import patch

from ..entities.player import Player, Gender
from ..utils.constants import TalentLevel, TALENT_STAT_MULTIPLIERS, DIFFICULTY_TO_TALENT
from ..managers.player_generator import PlayerGenerator


class TestTalentSystem:
    """Tests pour le système de talents des joueurs"""

    def test_talent_level_enum(self):
        """Test que l'enum TalentLevel contient tous les niveaux attendus"""
        expected_talents = [
            "Génie précoce",
            "Pépite", 
            "Talent brut",
            "Joueur prometteur",
            "Espoir fragile"
        ]
        
        actual_talents = [talent.value for talent in TalentLevel]
        assert len(actual_talents) == 5
        for talent in expected_talents:
            assert talent in actual_talents

    def test_talent_stat_multipliers(self):
        """Test que tous les niveaux de talent ont des multiplicateurs définis"""
        for talent_level in TalentLevel:
            assert talent_level in TALENT_STAT_MULTIPLIERS
            multiplier = TALENT_STAT_MULTIPLIERS[talent_level]
            assert isinstance(multiplier, float)
            assert 0.5 <= multiplier <= 2.0  # Bornes raisonnables

    def test_difficulty_to_talent_mapping(self):
        """Test que toutes les difficultés ont un talent associé"""
        expected_difficulties = [
            "Novice",
            "Facile",
            "Normal", 
            "Difficile",
            "Expert"
        ]
        
        for difficulty in expected_difficulties:
            assert difficulty in DIFFICULTY_TO_TALENT
            assert isinstance(DIFFICULTY_TO_TALENT[difficulty], TalentLevel)

    def test_player_talent_initialization(self):
        """Test que le talent est correctement initialisé lors de la création d'un joueur"""
        player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player",
            country="France",
            talent_level=TalentLevel.GENIE_PRECOCE
        )
        
        assert player.talent_level == TalentLevel.GENIE_PRECOCE

    def test_player_default_talent(self):
        """Test que le talent par défaut est JOUEUR_PROMETTEUR"""
        player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player",
            country="France"
        )
        
        assert player.talent_level == TalentLevel.JOUEUR_PROMETTEUR

    def test_talent_stat_modification(self):
        """Test que les modificateurs de talent affectent correctement les stats"""
        # Joueur avec génie précoce (multiplicateur 1.30)
        genius_player = Player(
            gender=Gender.MALE,
            first_name="Genius",
            last_name="Player",
            country="France",
            talent_level=TalentLevel.GENIE_PRECOCE
        )
        
        # Joueur avec espoir fragile (multiplicateur 0.90)
        weak_player = Player(
            gender=Gender.MALE,
            first_name="Weak",
            last_name="Player",
            country="France",
            talent_level=TalentLevel.ESPOIR_FRAGILE
        )
        
        # Le génie doit avoir des stats supérieures à l'espoir fragile
        genius_stats = genius_player.stats.to_dict()
        weak_stats = weak_player.stats.to_dict()
        
        for stat_name in genius_stats:
            assert genius_stats[stat_name] >= weak_stats[stat_name]

    def test_talent_stat_bounds(self):
        """Test que les stats modifiées respectent les bornes (10-70)"""
        for talent_level in TalentLevel:
            player = Player(
                gender=Gender.MALE,
                first_name="Test",
                last_name="Player",
                country="France",
                talent_level=talent_level
            )
            
            stats = player.stats.to_dict()
            for stat_name, stat_value in stats.items():
                assert 10 <= stat_value <= 70, f"Stat {stat_name} = {stat_value} pour talent {talent_level.value}"

    def test_player_generator_with_talent(self):
        """Test que le générateur de joueurs peut créer des joueurs avec un talent spécifique"""
        generator = PlayerGenerator()
        
        player = generator.generate_player(
            gender=Gender.MALE,
            talent_level=TalentLevel.PEPITE
        )
        
        assert player.talent_level == TalentLevel.PEPITE

    def test_player_generator_random_talent(self):
        """Test que le générateur assigne un talent aléatoire si non spécifié"""
        generator = PlayerGenerator()
        
        player = generator.generate_player(gender=Gender.MALE)
        
        assert isinstance(player.talent_level, TalentLevel)

    def test_player_serialization_with_talent(self):
        """Test que le talent est correctement sérialisé/désérialisé"""
        original_player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player",
            country="France",
            talent_level=TalentLevel.PEPITE
        )
        
        # Sérialisation
        player_dict = original_player.to_dict()
        assert "talent_level" in player_dict
        assert player_dict["talent_level"] == TalentLevel.PEPITE.value
        
        # Désérialisation
        restored_player = Player.from_dict(player_dict)
        assert restored_player.talent_level == TalentLevel.PEPITE

    def test_player_card_display_with_talent(self):
        """Test que le talent apparaît dans la carte d'affichage du joueur"""
        player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player",
            country="France",
            talent_level=TalentLevel.GENIE_PRECOCE
        )
        
        card = player.get_display_card()
        assert "Génie précoce" in card

    @pytest.mark.parametrize("talent_level,expected_multiplier", [
        (TalentLevel.GENIE_PRECOCE, 1.30),
        (TalentLevel.PEPITE, 1.20),
        (TalentLevel.TALENT_BRUT, 1.10),
        (TalentLevel.JOUEUR_PROMETTEUR, 1.00),
        (TalentLevel.ESPOIR_FRAGILE, 0.90)
    ])
    def test_specific_talent_multipliers(self, talent_level, expected_multiplier):
        """Test que chaque niveau de talent a le bon multiplicateur"""
        assert TALENT_STAT_MULTIPLIERS[talent_level] == expected_multiplier

    def test_backward_compatibility_talent_loading(self):
        """Test de rétrocompatibilité pour les sauvegardes sans talent"""
        # Simule une ancienne sauvegarde sans champ talent_level
        old_save_data = {
            "gender": "m",
            "first_name": "Old",
            "last_name": "Player",
            "country": "France",
            "archetype": "Polyvalent",
            "is_main_player": False,
            "stats": {
                "coup_droit": 30,
                "revers": 30,
                "service": 30,
                "vollee": 30,
                "puissance": 30,
                "vitesse": 30,
                "endurance": 30,
                "reflexes": 30
            },
            "career": {
                "level": 1,
                "xp_points": 0,
                "ap_points": 0,
                "atp_points": 0,
                "atp_race_points": 0,
                "age": 20,
                "elo_ratings": {}
            },
            "physical": {
                "height": 180,
                "dominant_hand": "Droitier",
                "backhand_style": "Une main",
                "fatigue": 0
            }
        }
        
        player = Player.from_dict(old_save_data)
        assert player.talent_level == TalentLevel.JOUEUR_PROMETTEUR
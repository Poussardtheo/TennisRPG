from unittest import mock
from TennisRPG.Personnage import Personnage

import pytest


class TestGenererStatistique:

    # Adjust stats based on height correctly
    def test_adjust_stats_based_on_height_correctly(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=180, lvl=1)
        personnage.stats = {'force': 50}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        personnage.generer_statistique()
        assert personnage.stats['force'] == 50

    # Apply positive impacts for taller characters
    def test_apply_positive_impacts_for_taller_characters(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=200, lvl=1)
        personnage.stats = {'force': 50}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        personnage.generer_statistique()
        assert personnage.stats['force'] == 53

    # Apply negative impacts for shorter characters
    def test_apply_negative_impacts_for_shorter_characters(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=160, lvl=1)
        personnage.stats = {'force': 50}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        personnage.generer_statistique()
        assert personnage.stats['force'] == 47

    # Call attribuer_ap_points_automatiquement if level > 1
    def test_call_attribuer_ap_points_automatiquement_if_level_greater_than_1(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=180, lvl=2)
        personnage.stats = {'force': 50}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        with mock.patch.object(personnage, 'attribuer_ap_points_automatiquement') as mock_method:
            personnage.generer_statistique()
            mock_method.assert_called_once()

    # Calculate taille_mod correctly for given height
    def test_calculate_taille_mod_correctly_for_given_height(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=190, lvl=1)
        personnage.stats = {'force': 50}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        taille_mod = (personnage.taille - 180) / 20
        assert taille_mod == 0.5

    # Ensure stats do not exceed 70 after adjustment
    def test_ensure_stats_do_not_exceed_70_after_adjustment(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=200, lvl=1)
        personnage.stats = {'force': 68}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        personnage.generer_statistique()
        assert personnage.stats['force'] == 70

    # Handle minimum height (160 for male, 155 for female)
    def test_handle_minimum_height(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=160, lvl=1)
        personnage.stats = {'force': 50}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        personnage.generer_statistique()
        assert personnage.stats['force'] == 47

    # Handle maximum height (200 for male, 185 for female)
    def test_handle_maximum_height(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=200, lvl=1)
        personnage.stats = {'force': 50}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        personnage.generer_statistique()
        assert personnage.stats['force'] == 53

    # Handle edge case where all stats are already at 70
    def test_handle_edge_case_where_all_stats_are_already_at_70(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=180, lvl=1)
        personnage.stats = {'force': 70}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        personnage.generer_statistique()
        assert personnage.stats['force'] == 70

    # Handle level 1 character without calling attribuer_ap_points_automatiquement
    def test_handle_level_1_character_without_calling_attribuer_ap_points_automatiquement(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA',  taille=180, lvl=1)
        personnage.stats = {'force': 50}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        with mock.patch.object(personnage, 'attribuer_ap_points_automatiquement') as mock_method:
            personnage.generer_statistique()
            mock_method.assert_not_called()

    # Handle negative impacts correctly for very short characters
    def test_handle_negative_impacts_correctly_for_very_short_characters(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=150, lvl=1)
        personnage.stats = {'force': 50}
        personnage.TAILLE_IMPACTS = {'force': 0.3}
        personnage.generer_statistique()
        assert personnage.stats['force'] == 46

    # Verify correct adjustment for each attribute in TAILLE_IMPACTS
    def test_verify_correct_adjustment_for_each_attribute_in_TAILLE_IMPACTS(self):
        personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=190, lvl=1)
        personnage.stats = {'force': 50, 'agility': 60}
        personnage.TAILLE_IMPACTS = {'force': 0.3, 'agility': -0.5}
        personnage.generer_statistique()
        assert personnage.stats['force'] == 52 and personnage.stats['agility'] == 58
    
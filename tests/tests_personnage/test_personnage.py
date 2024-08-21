import random

import pytest
import sys

sys.path.append("../..")
from unittest import mock

from TennisRPG.Personnage import Personnage


# Creating a character with default parameters initializes correctly
class Test__Init__:
	def test_default_init(self):
		personnage = Personnage(sexe='m', prenom='John', nom='Doe', country='USA')
		assert personnage.sexe == 'm'
		assert personnage.prenom == 'John'
		assert personnage.nom == 'Doe'
		assert personnage.country == 'USA'
		assert 160 <= personnage.taille <= 200
		assert personnage.lvl == 1
		assert personnage.xp_points == 0
		assert personnage.ap_points == 0
		assert personnage.atp_points == 0
		assert personnage.atp_race_points == 0
		assert personnage.fatigue == 0
		assert personnage.blessure is None
		
	def test_specific_init(self):
		personnage = Personnage(sexe='f', prenom='Jane', nom="Doe", country='USA', taille=180, lvl=15,
		                        archetype="Défenseur", principal=True)
		assert personnage.sexe == 'f'
		assert personnage.prenom == 'Jane'
		assert personnage.nom == 'Doe'
		assert personnage.country == 'USA'
		assert personnage.taille == 180
		assert personnage.lvl == 15
		assert personnage.archetype == "Défenseur"
		assert personnage.principal is True
		assert sum([stat for stat in personnage.stats.values()]) == 324  # 8 * 30 + 6 * 14

	# Correctly calculate initial elo using calculer_elo method
	def test_initial_elo_calculation(self):
		obj = Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=180)
		assert obj.elo == 1200
	
	# Initialize with invalid sexe value
	def test_initialize_with_invalid_sexe(self):
		with pytest.raises(AssertionError):
			Personnage(sexe='x', prenom='John', nom='Doe', country='USA')
	
	# Initialize with lvl value less than 1
	def test_initialize_with_lvl_less_than_one(self):
		with pytest.raises(AssertionError):
			Personnage(sexe='m', prenom='John', nom='Doe', country='USA', lvl=0)
	
	# Initialize with taille value outside the expected range
	def test_initialize_with_taille_outside_range(self):
		with pytest.raises(AssertionError):
			Personnage(sexe='m', prenom='John', nom='Doe', country='USA', taille=300)
	
	# Initialize with an archetype not present in ARCHETYPES
	def test_initialize_with_invalid_archetype(self):
		with pytest.raises(AssertionError):
			Personnage(sexe='m', prenom='John', nom='Doe', country='USA', archetype='InvalidArchetype')
	
	# Initialize with non-string values for prenom, nom, or country
	def test_initialize_with_non_string_values(self):
		with pytest.raises(AssertionError):
			Personnage(sexe='m', prenom=123, nom='Doe', country='USA')
		with pytest.raises(AssertionError):
			Personnage(sexe='m', prenom='John', nom=456, country='USA')
		with pytest.raises(AssertionError):
			Personnage(sexe='m', prenom='John', nom='Doe', country=789)
	
	# Ensure random values for main_dominante and revers are within expected probabilities
	def test_random_values_for_main_dominante_and_revers(self):
		with mock.patch('random.random', return_value=0.1):
			obj = Personnage(sexe='m', prenom='John', nom='Doe', country='USA')
			assert obj.main_dominante == "Gauche"
			assert obj.revers == "Une main"
		
		with mock.patch('random.random', return_value=0.2):
			obj = Personnage(sexe='m', prenom='John', nom='Doe', country='USA')
			assert obj.main_dominante == "Droite"
			assert obj.revers == "Deux mains"

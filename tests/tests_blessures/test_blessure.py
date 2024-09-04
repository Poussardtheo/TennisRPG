import random
import pytest
import sys

sys.path.append("../..")

from TennisRPG.Blessure import Blessure, dico_blessures
from TennisRPG.Personnage import Personnage


def test_personnage_injured_properly():
	obj = Personnage(sexe='m', prenom='John', nom='Doe', country='USA')
	obj.blessure = dico_blessures[2][1]
	assert isinstance(obj.blessure, Blessure)
	
	
def test_repos_sans_blessure():
	obj = Personnage(sexe='m', prenom='John', nom='Doe', country='USA')
	obj.fatigue = 50
	
	obj.se_reposer()
	
	assert obj.fatigue < 50, "La fatigue doit diminuer après le repos"
	

def test_repos_avec_blessure():
	obj = Personnage(sexe='m', prenom='John', nom='Doe', country='USA')
	obj.blessure = dico_blessures[4][0]
	
	obj.se_reposer()
	
	assert obj.fatigue < 50, "La fatigue doit diminuer après le repos"
	assert obj.blessure is not None
	assert isinstance(obj.blessure.repos, int)

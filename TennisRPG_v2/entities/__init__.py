"""
Module des entités du jeu
"""

from .player import Player, Gender, PlayerStats, PlayerCareer, PlayerPhysical
from .ranking import Ranking, RankingType, RankingEntry

# Alias pour la compatibilité avec l'ancien code
Personnage = Player
Classement = Ranking


__all__ = [
    'Player', 'Gender', 'PlayerStats', 'PlayerCareer', 'PlayerPhysical',
    'Ranking', 'RankingType', 'RankingEntry',
    'Personnage', 'Classement'  # Alias de compatibilité
]

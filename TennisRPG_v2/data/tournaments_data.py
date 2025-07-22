"""
Données de configuration pour tous les types de tournois
"""
from enum import Enum
from typing import Dict, List, Tuple

import numpy as np


class TournamentCategory(Enum):
    """Catégories de tournois"""
    GRAND_SLAM = "Grand Slam"
    ATP_FINALS = "ATP Finals"
    MASTERS_1000 = "Masters 1000"
    ATP_500 = "ATP 500"
    ATP_250 = "ATP 250"
    CHALLENGER_175 = "Challenger 175"
    CHALLENGER_125 = "Challenger 125"
    CHALLENGER_100 = "Challenger 100"
    CHALLENGER_75 = "Challenger 75"
    CHALLENGER_50 = "Challenger 50"
    ITF_M25 = "ITF M25"
    ITF_M15 = "ITF M15"


# Configuration des points ATP par catégorie et tour
# Format: {catégorie: {tour: points}}
ATP_POINTS_CONFIG = {
    TournamentCategory.GRAND_SLAM: {
        "winner": 2000, "finalist": 1200, "semifinalist": 720,
        "quarterfinalist": 360, "round_16": 180, "round_32": 90,
        "round_64": 45, "round_128": 10
    },
    TournamentCategory.ATP_FINALS: {
        "winner": 1500, "finalist": 1200, "semifinalist": 800,
        "round_robin_win": 200, "participation": 0
    },
    TournamentCategory.MASTERS_1000: {
        # Configuration pour 6 tours
        "winner_6": 1000, "finalist_6": 600, "semifinalist_6": 360,
        "quarterfinalist_6": 180, "round_16_6": 90, "round_32_6": 45,
        "round_64_6": 25,
        # Configuration pour 7 tours
        "winner_7": 1000, "finalist_7": 600, "semifinalist_7": 360,
        "quarterfinalist_7": 180, "round_16_7": 90, "round_32_7": 45,
        "round_64_7": 25, "round_128_7": 10
    },
    TournamentCategory.ATP_500: {
        # Configuration pour 5 tours
        "winner_5": 500, "finalist_5": 300, "semifinalist_5": 180,
        "quarterfinalist_5": 90, "round_16_5": 45, "round_32_5": 20,
        # Configuration pour 6 tours
        "winner_6": 500, "finalist_6": 300, "semifinalist_6": 180,
        "quarterfinalist_6": 90, "round_16_6": 45, "round_32_6": 20,
        "round_64_6": 10
    },
    TournamentCategory.ATP_250: {
        # Configuration pour 5 tours
        "winner_5": 250, "finalist_5": 150, "semifinalist_5": 90,
        "quarterfinalist_5": 45, "round_16_5": 20, "round_32_5": 10,
        # Configuration pour 6 tours
        "winner_6": 250, "finalist_6": 150, "semifinalist_6": 90,
        "quarterfinalist_6": 45, "round_16_6": 20, "round_32_6": 10,
        "round_64_6": 5
    },
    TournamentCategory.CHALLENGER_175: {
        "winner": 175, "finalist": 100, "semifinalist": 60,
        "quarterfinalist": 32, "round_16": 15, "round_32": 0,
    },
    TournamentCategory.CHALLENGER_125: {
        "winner": 125, "finalist": 64, "semifinalist": 35,
        "quarterfinalist": 16, "round_16": 8, "round_32": 0,
    },
    TournamentCategory.CHALLENGER_100: {
        "winner": 100, "finalist": 50, "semifinalist": 25,
        "quarterfinalist": 14, "round_16": 7, "round_32": 0,
    },
    TournamentCategory.CHALLENGER_75: {
        "winner": 75, "finalist": 44, "semifinalist": 22,
        "quarterfinalist": 12, "round_16": 6, "round_32": 0,
    },
    TournamentCategory.CHALLENGER_50: {
        "winner": 50, "finalist": 25, "semifinalist": 14,
        "quarterfinalist": 8, "round_16": 4, "round_32": 0,
    },
    TournamentCategory.ITF_M25: {
        "winner": 25, "finalist": 15, "semifinalist": 9,
        "quarterfinalist": 4, "round_16": 2, "round_32": 1,
        "round_64": 1, "round_128": 1
    },
    TournamentCategory.ITF_M15: {
        "winner": 15, "finalist": 9, "semifinalist": 5,
        "quarterfinalist": 2, "round_16": 1, "round_32": 1,
        "round_64": 1, "round_128": 1
    }
}

# Configuration de l'XP par catégorie et tour
XP_POINTS_CONFIG = {
    TournamentCategory.GRAND_SLAM: {
        "winner": 500, "finalist": 350, "semifinalist": 250,
        "quarterfinalist": 180, "round_16": 130, "round_32": 90,
        "round_64": 60, "round_128": 40
    },
    TournamentCategory.ATP_FINALS: {
        "winner": 400, "finalist": 300, "semifinalist": 200,
        "round_robin_win": 50, "participation": 0
    },
    TournamentCategory.MASTERS_1000: {
        # Configuration pour 6 tours
        "winner_6": 350, "finalist_6": 250, "semifinalist_6": 180,
        "quarterfinalist_6": 130, "round_16_6": 90, "round_32_6": 60,
        "round_64_6": 40,
        # Configuration pour 7 tours
        "winner_7": 350, "finalist_7": 250, "semifinalist_7": 180,
        "quarterfinalist_7": 130, "round_16_7": 90, "round_32_7": 60,
        "round_64_7": 40, "round_128_7": 30
    },
    TournamentCategory.ATP_500: {
        # Configuration pour 5 tours
        "winner_5": 300, "finalist_5": 200, "semifinalist_5": 140,
        "quarterfinalist_5": 100, "round_16_5": 70, "round_32_5": 50,
        # Configuration pour 6 tours
        "winner_6": 300, "finalist_6": 200, "semifinalist_6": 140,
        "quarterfinalist_6": 100, "round_16_6": 70, "round_32_6": 50,
        "round_64_6": 35
    },
    TournamentCategory.ATP_250: {
        # Configuration pour 5 tours
        "winner_5": 250, "finalist_5": 170, "semifinalist_5": 120,
        "quarterfinalist_5": 85, "round_16_5": 60, "round_32_5": 40,
        # Configuration pour 6 tours
        "winner_6": 250, "finalist_6": 170, "semifinalist_6": 120,
        "quarterfinalist_6": 85, "round_16_6": 60, "round_32_6": 40,
        "round_64_6": 30
    },
    TournamentCategory.CHALLENGER_175: {
        "winner": 200, "finalist": 140, "semifinalist": 100,
        "quarterfinalist": 70, "round_16": 50, "round_32": 35,
        "round_64": 25, "round_128": 15
    },
    TournamentCategory.CHALLENGER_125: {
        "winner": 175, "finalist": 120, "semifinalist": 85,
        "quarterfinalist": 60, "round_16": 42, "round_32": 30,
        "round_64": 20, "round_128": 12
    },
    TournamentCategory.CHALLENGER_100: {
        "winner": 150, "finalist": 105, "semifinalist": 75,
        "quarterfinalist": 52, "round_16": 37, "round_32": 26,
        "round_64": 18, "round_128": 10
    },
    TournamentCategory.CHALLENGER_75: {
        "winner": 125, "finalist": 87, "semifinalist": 62,
        "quarterfinalist": 43, "round_16": 31, "round_32": 22,
        "round_64": 15, "round_128": 8
    },
    TournamentCategory.CHALLENGER_50: {
        "winner": 100, "finalist": 70, "semifinalist": 50,
        "quarterfinalist": 35, "round_16": 25, "round_32": 18,
        "round_64": 12, "round_128": 6
    },
    TournamentCategory.ITF_M25: {
        "winner": 75, "finalist": 52, "semifinalist": 37,
        "quarterfinalist": 26, "round_16": 18, "round_32": 13,
        "round_64": 9, "round_128": 5
    },
    TournamentCategory.ITF_M15: {
        "winner": 50, "finalist": 35, "semifinalist": 25,
        "quarterfinalist": 17, "round_16": 12, "round_32": 9,
        "round_64": 6, "round_128": 3
    }
}

# Seuils d'éligibilité par catégorie (rang ATP maximum autorisé)
# Si pas de classement ATP, conversion automatique vers seuil ELO équivalent
ELIGIBILITY_THRESHOLDS = {
    TournamentCategory.GRAND_SLAM: 150,        # Directement qualifiés + invitations
    TournamentCategory.ATP_FINALS: 12,          # Top 8 seulement
    TournamentCategory.MASTERS_1000: 150,      # Top 100 + qualifiés + invitations
    TournamentCategory.ATP_500: 200,           # Plus ouvert que Masters
    TournamentCategory.ATP_250: 250,           # Accessible aux Top 200
    TournamentCategory.CHALLENGER_175: 500,    # Semi-pro niveau élevé
    TournamentCategory.CHALLENGER_125: 600,    # Semi-pro standard
    TournamentCategory.CHALLENGER_100: 800,    # Semi-pro accessible
    TournamentCategory.CHALLENGER_75: np.inf,     # Développement
    TournamentCategory.CHALLENGER_50: np.inf,    # Jeunes pro
    TournamentCategory.ITF_M25: np.inf,          # Futures haut niveau
    TournamentCategory.ITF_M15: np.inf         # Ouvert à tous (pas de limite)
}

# Configurations spéciales
SPECIAL_TOURNAMENT_CONFIG = {
    "ATP_FINALS": {
        "qualified_players": 8,
        "groups": 2,
        "players_per_group": 4,
        "qualified_per_group": 2,
        "format": "mixed"  # Poules + élimination
    }
}
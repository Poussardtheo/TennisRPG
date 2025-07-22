"""
Constantes utilisées dans le jeu
"""

# Archétypes de joueurs
ARCHETYPES = {
    "Service-Volley": {
        "primaire": ["Service", "Volée"],
        "secondaire": ["Réflexes", "Vitesse"],
        "tertiaire": ["Coup droit", "Revers", "Puissance", "Endurance"]
    },
    "Attaquant Fond de Court": {
        "primaire": ["Coup droit", "Revers", "Puissance"],
        "secondaire": ["Service", "Vitesse"],
        "tertiaire": ["Volée", "Réflexes", "Endurance"]
    },
    "Défenseur": {
        "primaire": ["Endurance", "Vitesse", "Réflexes"],
        "secondaire": ["Coup droit", "Revers"],
        "tertiaire": ["Service", "Volée", "Puissance"]
    },
    "Polyvalent": {
        "primaire": ["Coup droit", "Revers", "Service"],
        "secondaire": ["Endurance", "Puissance", "Vitesse"],
        "tertiaire": ["Volée", "Réflexes"]
    }
}

# Constantes pour les joueurs
PLAYER_CONSTANTS = {
    "BASE_POINTS": 6,
    "MAX_LEVEL": 30,
    "BASE_STAT_VALUE": 30,
    "MAX_STAT_VALUE": 100,
    "MAX_FATIGUE": 100,
    "FATIGUE_PARTICIPATION_THRESHOLD": 90
}

# Poids des statistiques pour le calcul ELO
STATS_WEIGHTS = {
    "Coup droit": 1.5,
    "Revers": 1.5,
    "Service": 1.5,
    "Volée": 1.0,
    "Puissance": 1.2,
    "Vitesse": 1.2,
    "Endurance": 1.3,
    "Réflexes": 1.2,
}

# Impact de la taille sur les statistiques
HEIGHT_IMPACTS = {
    "Service": 0.3,      # Impact positif important
    "Puissance": 0.2,    # Impact positif modéré
    "Vitesse": -0.1,     # Impact négatif léger
    "Endurance": -0.2,   # Impact négatif modéré
}

# Valeurs de fatigue par activité
# TODO: Cette constante peut être supprimée dans une prochaine version - gestion centralisée dans Player
FATIGUE_VALUES = {
    "Entrainement": (3, 7),
    "Exhibition": (5, 15),
    "Repos": (3, 5)  # Valeur de récupération
}

# Coefficients de fatigue par catégorie de tournoi
TOURNAMENT_FATIGUE_MULTIPLIERS = {
    "Grand Slam": 2.5,          # Bo5, plus exigeant physiquement
    "ATP Finals": 2.2,          # Elite level, haute intensité
    "Masters 1000": 1.8,        # Tournois de prestige, plus exigeants
    "ATP 500": 1.3,             # Niveau intermédiaire
    "ATP 250": 1.0,             # Coefficient de base
    "Challenger 175": 0.9,      # Moins exigeant que l'ATP
    "Challenger 125": 0.8,
    "Challenger 100": 0.7,
    "Challenger 75": 0.6,
    "Challenger 50": 0.5,
    "ITF M25": 0.4,             # Niveau amateur/développement
    "ITF M15": 0.3
}

# Constantes pour les classements
RANKING_CONSTANTS = {
    "DEFAULT_DISPLAY_COUNT": 100,
    "MAX_DISPLAY_COUNT": 500,
}

# Types de classements disponibles
RANKING_TYPES = {
    "ELO": "elo",
    "ATP": "atp",
    "ATP_RACE": "atp_race"
}

# Constantes pour les tournois
TOURNAMENT_CONSTANTS = {
    "MIN_PLAYERS": 4,
    "MAX_PLAYERS": 128,
    "DEFAULT_SETS_TO_WIN": 2,
    "GRAND_SLAM_SETS_TO_WIN": 3,
    "DEFAULT_FATIGUE_MULTIPLIER": 1.0,
    "MATCH_BASE_XP": 50,
    "TOURNAMENT_COMPLETION_BONUS": 100
}

# Formats de tournois
TOURNAMENT_FORMATS = {
    "ELIMINATION": "elimination",
    "ROUND_ROBIN": "round_robin",
    "MIXED": "mixed"  # Pour ATP Finals (poules + élimination)
}

# Surfaces de tournois
TOURNAMENT_SURFACES = {
    "HARD": "Hard",
    "CLAY": "Clay",
    "GRASS": "Grass",
    "INDOOR_HARD": "Indoor Hard",
    "CARPET": "Carpet"
}

# Activités disponibles
ACTIVITIES = ["Entrainement", "Tournoi", "Repos", "Exhibition"]

# Constantes pour la gestion du temps
TIME_CONSTANTS = {
    "WEEKS_PER_YEAR": 52,
    "FATIGUE_NATURAL_RECOVERY": 3
}


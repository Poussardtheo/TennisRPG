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
    "MAX_LEVEL": 50,  # Augmenté pour une carrière plus réaliste
    "BASE_STAT_VALUE": 30,
    "MAX_STAT_VALUE": 100,
    "MAX_FATIGUE": 100,
    "FATIGUE_PARTICIPATION_THRESHOLD": 90,
    "STARTING_AGE_MIN": 16,  # Âge minimum de début de carrière
    "STARTING_AGE_MAX": 19,  # Âge maximum de début de carrière
    "PEAK_AGE_START": 23,    # Début de l'âge de pic
    "PEAK_AGE_END": 26,      # Fin de l'âge de pic
    "DECLINE_AGE_START": 31  # Début du déclin
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

# XP rewards par catégorie de tournoi (victoire finale)
TOURNAMENT_XP_REWARDS = {
    "Grand Slam": 120,
    "ATP Finals": 100,
    "Masters 1000": 80,
    "ATP 500": 60,
    "ATP 250": 40,
    "Challenger 175": 30,
    "Challenger 125": 25,
    "Challenger 100": 20,
    "Challenger 75": 15,
    "Challenger 50": 12,
    "ITF M25": 8,
    "ITF M15": 5
}

# Multiplicateurs XP selon le round atteint (relatif à la récompense finale)
ROUND_XP_MULTIPLIERS = {
    "Champion": 1.0,
    "Finale": 0.7,
    "Demi-finale": 0.5,
    "Quart de finale": 0.35,
    "Huitième de finale": 0.25,
    "Deuxième tour": 0.15,
    "Premier tour": 0.1
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

# XP de base pour les activités
BASE_TRAINING_XP = {"min": 6, "max": 10}  # Réduit par rapport à l'ancien système

# Constantes pour la gestion du temps
TIME_CONSTANTS = {
    "WEEKS_PER_YEAR": 52,
    "FATIGUE_NATURAL_RECOVERY": 3
}

# Facteurs de progression par âge
AGE_PROGRESSION_FACTORS = {
    "16-19": 1.4,  # Progression très rapide (jeune talent)
    "20-22": 1.2,  # Progression rapide (développement)
    "23-26": 1.0,  # Progression normale (pic de carrière)
    "27-30": 0.8,  # Progression ralentie (expérience)
    "31-33": 0.6,  # Progression lente (vétéran)
    "34+": 0.4     # Progression très lente (fin de carrière)
}

# Constantes pour le système de retraite
RETIREMENT_CONSTANTS = {
    "MIN_RETIREMENT_AGE": 30,      # Âge minimum pour prendre sa retraite
    "MAX_CAREER_AGE": 45,          # Âge maximum (retraite forcée)
    "BASE_RETIREMENT_PROBABILITY": 0.02,  # Probabilité de base à 30 ans (2%)
    "AGE_RETIREMENT_MULTIPLIER": 0.5,     # Multiplicateur par année après 30 ans
    "EARLY_RETIREMENT_BONUS": 0.1,        # Bonus pour blessures/mauvaise forme
    "YOUNG_PLAYER_MIN_AGE": 16,           # Âge minimum des nouveaux joueurs
    "YOUNG_PLAYER_MAX_AGE": 20,           # Âge maximum des nouveaux joueurs
}


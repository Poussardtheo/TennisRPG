"""
Base de données des blessures possibles dans le tennis.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional


class InjuryType(Enum):
    """Types de blessures possibles"""
    MUSCLE = "musculaire"
    ARTICULATION = "articulaire" 
    OS = "osseuse"
    TENDON = "tendineuse"


class InjurySeverity(Enum):
    """Gravité des blessures"""
    LEGERE = "légère"
    MODEREE = "modérée"
    GRAVE = "grave"
    SEVERE = "sévère"


@dataclass
class InjuryData:
    """Données d'une blessure"""
    name: str
    type: InjuryType
    severity: InjurySeverity
    min_recovery_weeks: int
    max_recovery_weeks: int
    fatigue_threshold: int  # Seuil de fatigue minimum pour cette blessure
    probability_weight: float  # Poids dans le calcul de probabilité
    description: str
    affected_stats: Dict[str, float] = None  # Stats affectées et leur réduction (0.0-1.0)
    
    def __post_init__(self):
        if self.affected_stats is None:
            self.affected_stats = {}


# Base de données des blessures
INJURIES_DATABASE = {
    # Blessures légères (1-2 semaines)
    "fatigue_musculaire": InjuryData(
        name="Fatigue musculaire",
        type=InjuryType.MUSCLE,
        severity=InjurySeverity.LEGERE,
        min_recovery_weeks=1,
        max_recovery_weeks=2,
        fatigue_threshold=60,
        probability_weight=3.0,
        description="Fatigue générale des muscles due à un surentraînement",
        affected_stats={"Endurance": 0.15, "Puissance": 0.10}
    ),
    
    "crampes": InjuryData(
        name="Crampes récurrentes",
        type=InjuryType.MUSCLE,
        severity=InjurySeverity.LEGERE,
        min_recovery_weeks=1,
        max_recovery_weeks=1,
        fatigue_threshold=70,
        probability_weight=2.5,
        description="Crampes musculaires dues à la déshydratation et fatigue",
        affected_stats={"Endurance": 0.20}
    ),
    
    "entorse_cheville_legere": InjuryData(
        name="Entorse légère de la cheville",
        type=InjuryType.ARTICULATION,
        severity=InjurySeverity.LEGERE,
        min_recovery_weeks=1,
        max_recovery_weeks=2,
        fatigue_threshold=50,
        probability_weight=2.0,
        description="Légère entorse de la cheville lors d'un mouvement brusque",
        affected_stats={"Vitesse": 0.15, "Réflexes": 0.10}
    ),
    
    # Blessures modérées (2-4 semaines)
    "elbow_tennis": InjuryData(
        name="Tennis elbow",
        type=InjuryType.TENDON,
        severity=InjurySeverity.MODEREE,
        min_recovery_weeks=3,
        max_recovery_weeks=6,
        fatigue_threshold=45,
        probability_weight=1.8,
        description="Épicondylite latérale, inflammation du tendon du coude",
        affected_stats={"Coup droit": 0.25, "Revers": 0.20, "Service": 0.15}
    ),
    
    "tendinite_epaule": InjuryData(
        name="Tendinite de l'épaule",
        type=InjuryType.TENDON,
        severity=InjurySeverity.MODEREE,
        min_recovery_weeks=2,
        max_recovery_weeks=4,
        fatigue_threshold=55,
        probability_weight=1.5,
        description="Inflammation des tendons de l'épaule",
        affected_stats={"Service": 0.30, "Volée": 0.20, "Coup droit": 0.15}
    ),
    
    "elongation_ischio": InjuryData(
        name="Élongation des ischio-jambiers",
        type=InjuryType.MUSCLE,
        severity=InjurySeverity.MODEREE,
        min_recovery_weeks=2,
        max_recovery_weeks=3,
        fatigue_threshold=65,
        probability_weight=1.7,
        description="Élongation des muscles arrière de la cuisse",
        affected_stats={"Vitesse": 0.25, "Endurance": 0.15}
    ),
    
    "entorse_cheville_moderee": InjuryData(
        name="Entorse modérée de la cheville",
        type=InjuryType.ARTICULATION,
        severity=InjurySeverity.MODEREE,
        min_recovery_weeks=3,
        max_recovery_weeks=5,
        fatigue_threshold=40,
        probability_weight=1.2,
        description="Entorse modérée avec ligaments étirés",
        affected_stats={"Vitesse": 0.30, "Réflexes": 0.20, "Endurance": 0.15}
    ),
    
    # Blessures graves (4-8 semaines)
    "dechirure_musculaire": InjuryData(
        name="Déchirure musculaire",
        type=InjuryType.MUSCLE,
        severity=InjurySeverity.GRAVE,
        min_recovery_weeks=4,
        max_recovery_weeks=8,
        fatigue_threshold=75,
        probability_weight=0.8,
        description="Déchirure partielle d'un muscle majeur",
        affected_stats={"Puissance": 0.35, "Vitesse": 0.25, "Endurance": 0.20}
    ),
    
    "hernie_discale": InjuryData(
        name="Hernie discale",
        type=InjuryType.OS,
        severity=InjurySeverity.GRAVE,
        min_recovery_weeks=6,
        max_recovery_weeks=12,
        fatigue_threshold=35,
        probability_weight=0.5,
        description="Hernie discale lombaire",
        affected_stats={"Service": 0.40, "Endurance": 0.30, "Puissance": 0.25}
    ),
    
    "fracture_fatigue": InjuryData(
        name="Fracture de fatigue",
        type=InjuryType.OS,
        severity=InjurySeverity.GRAVE,
        min_recovery_weeks=8,
        max_recovery_weeks=12,
        fatigue_threshold=80,
        probability_weight=0.3,
        description="Fracture de stress due à la répétition",
        affected_stats={"Vitesse": 0.40, "Endurance": 0.35, "Réflexes": 0.20}
    ),
    
    # Blessures sévères (8+ semaines)
    "rupture_tendon": InjuryData(
        name="Rupture du tendon d'Achille",
        type=InjuryType.TENDON,
        severity=InjurySeverity.SEVERE,
        min_recovery_weeks=12,
        max_recovery_weeks=20,
        fatigue_threshold=85,
        probability_weight=0.1,
        description="Rupture complète du tendon d'Achille",
        affected_stats={"Vitesse": 0.50, "Endurance": 0.40, "Réflexes": 0.30, "Puissance": 0.25}
    ),
    
    "ligament_croise": InjuryData(
        name="Rupture ligament croisé",
        type=InjuryType.ARTICULATION,
        severity=InjurySeverity.SEVERE,
        min_recovery_weeks=16,
        max_recovery_weeks=24,
        fatigue_threshold=30,
        probability_weight=0.05,
        description="Rupture du ligament croisé antérieur du genou",
        affected_stats={"Vitesse": 0.60, "Réflexes": 0.40, "Endurance": 0.35, "Volée": 0.25}
    )
}


# Probabilités de blessure selon le niveau de fatigue
INJURY_PROBABILITY_BY_FATIGUE = {
    (0, 30): 0.001,    # Très faible risque
    (30, 50): 0.005,   # Faible risque
    (50, 70): 0.015,   # Risque modéré
    (70, 85): 0.035,   # Risque élevé
    (85, 100): 0.15    # Risque très élevé
}


# Multiplicateurs selon l'activité
ACTIVITY_INJURY_MULTIPLIERS = {
    "Entraînement": 0.8,
    "Tournament": 1.5,
    "Repos": 0.0
}


def get_injuries_by_severity(severity: InjurySeverity) -> List[str]:
    """Retourne la liste des clés de blessures d'une gravité donnée"""
    return [key for key, injury in INJURIES_DATABASE.items() 
            if injury.severity == severity]


def get_injuries_by_type(injury_type: InjuryType) -> List[str]:
    """Retourne la liste des clés de blessures d'un type donné"""
    return [key for key, injury in INJURIES_DATABASE.items() 
            if injury.type == injury_type]


def get_possible_injuries_for_fatigue(fatigue_level: int) -> List[str]:
    """Retourne les blessures possibles selon le niveau de fatigue"""
    return [key for key, injury in INJURIES_DATABASE.items() 
            if fatigue_level >= injury.fatigue_threshold]
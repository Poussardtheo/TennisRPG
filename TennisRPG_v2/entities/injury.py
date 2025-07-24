"""
Entité Injury - Gestion des blessures des joueurs.
"""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from ..data.injuries_data import InjuryData, InjuryType, InjurySeverity


@dataclass
class Injury:
    """Représente une blessure d'un joueur"""
    injury_key: str
    injury_data: InjuryData
    weeks_remaining: int
    original_duration: int
    injury_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.injury_date is None:
            self.injury_date = datetime.now()
    
    @property
    def name(self) -> str:
        """Nom de la blessure"""
        return self.injury_data.name
    
    @property
    def type(self) -> InjuryType:
        """Type de blessure"""
        return self.injury_data.type
    
    @property
    def severity(self) -> InjurySeverity:
        """Gravité de la blessure"""
        return self.injury_data.severity
    
    @property
    def description(self) -> str:
        """Description de la blessure"""
        return self.injury_data.description
    
    @property
    def affected_stats(self) -> Dict[str, float]:
        """Statistiques affectées par la blessure"""
        return self.injury_data.affected_stats
    
    @property
    def is_healed(self) -> bool:
        """Vérifie si la blessure est guérie"""
        return self.weeks_remaining <= 0
    
    @property
    def recovery_progress(self) -> float:
        """Pourcentage de récupération (0.0 à 1.0)"""
        if self.original_duration == 0:
            return 1.0
        return max(0.0, 1.0 - (self.weeks_remaining / self.original_duration))
    
    def advance_recovery(self, weeks: int = 1):
        """Avance la récupération de la blessure"""
        self.weeks_remaining = max(0, self.weeks_remaining - weeks)
    
    def get_stat_modifier(self, stat_name: str) -> float:
        """
        Retourne le modificateur pour une statistique donnée
        
        Args:
            stat_name: Nom de la statistique
            
        Returns:
            Multiplicateur à appliquer (1.0 = pas d'effet, 0.8 = -20%)
        """
        if stat_name in self.affected_stats:
            # La réduction diminue avec la récupération
            base_reduction = self.affected_stats[stat_name]
            current_reduction = base_reduction * (1.0 - self.recovery_progress)
            return 1.0 - current_reduction
        return 1.0
    
    def get_display_info(self) -> str:
        """Retourne les informations d'affichage de la blessure"""
        severity_icon = {
            InjurySeverity.LEGERE: "🟢",
            InjurySeverity.MODEREE: "🟡", 
            InjurySeverity.GRAVE: "🟠",
            InjurySeverity.SEVERE: "🔴"
        }
        
        progress_bar = self._get_progress_bar()
        
        return (f"{severity_icon[self.severity]} {self.name}\n"
                f"   Récupération: {progress_bar} ({self.weeks_remaining} sem. restantes)\n"
                f"   Type: {self.type.value} | Gravité: {self.severity.value}")
    
    def _get_progress_bar(self, length: int = 20) -> str:
        """Génère une barre de progression pour la récupération"""
        progress = self.recovery_progress
        filled = int(progress * length)
        bar = "▓" * filled + "░" * (length - filled)
        percentage = int(progress * 100)
        return f"{bar} {percentage}%"
    
    def to_dict(self) -> Dict:
        """Convertit la blessure en dictionnaire pour la sauvegarde"""
        return {
            "injury_key": self.injury_key,
            "weeks_remaining": self.weeks_remaining,
            "original_duration": self.original_duration,
            "injury_date": self.injury_date.isoformat() if self.injury_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict, injury_data: InjuryData) -> 'Injury':
        """Crée une blessure depuis un dictionnaire"""
        injury_date = None
        if data.get("injury_date"):
            injury_date = datetime.fromisoformat(data["injury_date"])
        
        return cls(
            injury_key=data["injury_key"],
            injury_data=injury_data,
            weeks_remaining=data["weeks_remaining"],
            original_duration=data["original_duration"],
            injury_date=injury_date
        )


class InjuryCalculator:
    """Classe utilitaire pour calculer les risques de blessure"""
    
    @staticmethod
    def calculate_injury_risk(fatigue_level: int, activity: str = "Entraînement") -> float:
        """
        Calcule le risque de blessure selon la fatigue et l'activité
        
        Args:
            fatigue_level: Niveau de fatigue (0-100)
            activity: Type d'activité
            
        Returns:
            Probabilité de blessure (0.0 à 1.0)
        """
        from ..data.injuries_data import INJURY_PROBABILITY_BY_FATIGUE, ACTIVITY_INJURY_MULTIPLIERS
        from ..utils.constants import INJURY_CONSTANTS
        
        # Trouve la tranche de fatigue correspondante
        base_probability = 0.0
        for (min_fatigue, max_fatigue), probability in INJURY_PROBABILITY_BY_FATIGUE.items():
            if min_fatigue <= fatigue_level < max_fatigue:
                base_probability = probability
                break
        
        # Applique le multiplicateur d'activité
        activity_multiplier = ACTIVITY_INJURY_MULTIPLIERS.get(activity, 1.0)
        
        # Calcul de base
        injury_risk = base_probability * activity_multiplier
        
        # Augmentation drastique du risque pour fatigue très élevée
        if fatigue_level >= 95:
            # Risque critique: 25% minimum de blessure
            injury_risk = max(injury_risk, INJURY_CONSTANTS["CRITICAL_FATIGUE_INJURY_PROBABILITY"])
        elif fatigue_level >= INJURY_CONSTANTS["VERY_HIGH_FATIGUE_THRESHOLD"]:
            # Fatigue très élevée (90-94%): multiplicateur x3.5
            injury_risk *= INJURY_CONSTANTS["VERY_HIGH_FATIGUE_INJURY_MULTIPLIER"]
        elif fatigue_level >= INJURY_CONSTANTS["HIGH_FATIGUE_THRESHOLD"]:
            # Fatigue élevée (80-89%): multiplicateur x2.0
            injury_risk *= INJURY_CONSTANTS["HIGH_FATIGUE_INJURY_MULTIPLIER"]
        
        # Limite la probabilité à 100%
        return min(injury_risk, 1.0)
    
    @staticmethod
    def generate_random_injury(fatigue_level: int) -> Optional[Injury]:
        """
        Génère une blessure aléatoire selon le niveau de fatigue
        
        Args:
            fatigue_level: Niveau de fatigue du joueur
            
        Returns:
            Injury ou None si pas de blessure
        """
        from ..data.injuries_data import INJURIES_DATABASE, get_possible_injuries_for_fatigue
        
        possible_injuries = get_possible_injuries_for_fatigue(fatigue_level)
        if not possible_injuries:
            return None
        
        # Sélection pondérée selon la probabilité de chaque blessure
        weights = []
        injuries = []
        
        for injury_key in possible_injuries:
            injury_data = INJURIES_DATABASE[injury_key]
            injuries.append((injury_key, injury_data))
            weights.append(injury_data.probability_weight)
        
        # Sélection aléatoire pondérée
        selected_injury_key, selected_injury_data = random.choices(injuries, weights=weights)[0]
        
        # Durée aléatoire dans la fourchette
        duration = random.randint(
            selected_injury_data.min_recovery_weeks,
            selected_injury_data.max_recovery_weeks
        )
        
        return Injury(
            injury_key=selected_injury_key,
            injury_data=selected_injury_data,
            weeks_remaining=duration,
            original_duration=duration
        )
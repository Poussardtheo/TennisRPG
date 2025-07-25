"""
Gestionnaire des blessures - Coordonne la logique des blessures dans le jeu.
"""

import random
from typing import List, Dict, Optional, Tuple

from ..entities.player import Player
from ..entities.injury import Injury, InjuryCalculator
from ..data.injuries_data import INJURIES_DATABASE, InjurySeverity


class InjuryManager:
    """Gestionnaire central des blessures du jeu"""
    
    def __init__(self):
        self.injury_statistics = {
            "total_injuries": 0,
            "injuries_by_type": {},
            "injuries_by_severity": {},
            "players_affected": set()
        }
    
    def process_weekly_injuries(self, players: List[Player]) -> Dict[str, List[Injury]]:
        """
        Traite les blessures pour tous les joueurs à la fin d'une semaine
        
        Args:
            players: Liste des joueurs à traiter
            
        Returns:
            Dictionnaire {player_id: [nouvelles_blessures]}
        """
        weekly_injuries = {}
        
        for player in players:
            # Guérison des blessures existantes
            healed = player.heal_injuries(weeks=1)
            
            # Vérification de nouvelles blessures (seulement si pas déjà blessé)
            if not player.is_injured():
                new_injury = self._check_player_injury_risk(player)
                if new_injury:
                    weekly_injuries[player.full_name] = [new_injury]
                    self._update_statistics(new_injury, player)
        
        return weekly_injuries
    
    def process_activity_injury(self, player: Player, activity: str, 
                              sets_played: int = 0, tournament_category: str = None) -> Optional[Injury]:
        """
        Vérifie si un joueur se blesse pendant une activité spécifique
        
        Args:
            player: Joueur concerné
            activity: Type d'activité
            sets_played: Nombre de sets joués (pour les tournois)
            tournament_category: Catégorie du tournoi
            
        Returns:
            Injury si blessure survenue, None sinon
        """
        if player.is_injured():
            return None
        
        # Calcul du risque basé sur l'activité
        if activity == "Tournament":
            # Risque plus élevé en tournoi, surtout avec plus de sets
            base_risk = InjuryCalculator.calculate_injury_risk(player.physical.fatigue, "Tournament")
            # Augmente le risque avec le nombre de sets
            sets_multiplier = 1.0 + (sets_played * 0.1)
            # Modificateur selon la catégorie du tournoi
            category_multiplier = self._get_tournament_injury_multiplier(tournament_category)
            
            final_risk = base_risk * sets_multiplier * category_multiplier
        else:
            final_risk = InjuryCalculator.calculate_injury_risk(player.physical.fatigue, activity)
        
        # Test de blessure
        if random.random() < final_risk:
            injury = InjuryCalculator.generate_random_injury(player.physical.fatigue)
            if injury:
                player.add_injury(injury)
                self._update_statistics(injury, player)
                
                # Log spécial pour les blessures en tournoi
                if activity == "Tournament" and player.is_main_player:
                    print(f"💔 Blessure en tournoi! {player.full_name} doit abandonner.")
                
                return injury
        
        return None
    
    def force_rest_if_injured(self, player: Player) -> bool:
        """
        Force un joueur blessé à se reposer
        
        Args:
            player: Joueur à vérifier
            
        Returns:
            True si le joueur a été forcé au repos, False sinon
        """
        if player.is_injured():
            if player.is_main_player:
                active_injuries = player.physical.get_active_injuries()
                print(f"\n🚑 {player.full_name} est blessé(e) et doit se reposer:")
                for injury in active_injuries:
                    print(f"  • {injury.name} ({injury.weeks_remaining} semaines restantes)")
            return True
        return False
    
    def get_injury_report(self, player: Player) -> str:
        """
        Génère un rapport détaillé des blessures d'un joueur
        
        Args:
            player: Joueur concerné
            
        Returns:
            Rapport formaté
        """
        if not player.is_injured():
            return f"📋 Rapport médical de {player.full_name}: Aucune blessure active"
        
        report_lines = [f"📋 Rapport médical de {player.full_name}:"]
        report_lines.append("=" * 50)
        
        active_injuries = player.physical.get_active_injuries()
        
        for i, injury in enumerate(active_injuries, 1):
            report_lines.append(f"\n{i}. {injury.name}")
            report_lines.append(f"   Type: {injury.type.value} | Gravité: {injury.severity.value}")
            report_lines.append(f"   Description: {injury.description}")
            report_lines.append(f"   Récupération: {injury.weeks_remaining} semaines restantes")
            report_lines.append(f"   Progression: {injury._get_progress_bar()}")
            
            # Affiche les stats affectées
            if injury.affected_stats:
                report_lines.append("   Stats affectées:")
                for stat, reduction in injury.affected_stats.items():
                    current_modifier = injury.get_stat_modifier(stat)
                    current_reduction = (1.0 - current_modifier) * 100
                    report_lines.append(f"     • {stat}: -{current_reduction:.1f}%")
        
        return "\n".join(report_lines)
    
    def get_global_injury_statistics(self) -> str:
        """Retourne les statistiques globales des blessures"""
        if self.injury_statistics["total_injuries"] == 0:
            return "📊 Aucune blessure enregistrée dans cette partie."
        
        stats_lines = ["📊 Statistiques des blessures:"]
        stats_lines.append(f"Total de blessures: {self.injury_statistics['total_injuries']}")
        stats_lines.append(f"Joueurs affectés: {len(self.injury_statistics['players_affected'])}")
        
        if self.injury_statistics["injuries_by_severity"]:
            stats_lines.append("\nPar gravité:")
            for severity, count in self.injury_statistics["injuries_by_severity"].items():
                stats_lines.append(f"  • {severity}: {count}")
        
        if self.injury_statistics["injuries_by_type"]:
            stats_lines.append("\nPar type:")
            for injury_type, count in self.injury_statistics["injuries_by_type"].items():
                stats_lines.append(f"  • {injury_type}: {count}")
        
        return "\n".join(stats_lines)
    
    def _check_player_injury_risk(self, player: Player) -> Optional[Injury]:
        """Vérifie le risque de blessure d'un joueur selon sa fatigue"""
        # Les blessures hebdomadaires ne devraient pas arriver pour le joueur principal
        # car elles sont gérées au niveau des activités
        if hasattr(player, 'is_main_player') and player.is_main_player:
            return None
        return player.check_for_injury("Repos")  # Activité par défaut lors des vérifications hebdomadaires pour les NPCs
    
    def _get_tournament_injury_multiplier(self, tournament_category: str) -> float:
        """Retourne le multiplicateur de risque selon la catégorie de tournoi"""
        multipliers = {
            "Grand Chelem": 1.8,
            "ATP Masters 1000": 1.5,
            "ATP 500": 1.3,
            "ATP 250": 1.1,
            "Challenger": 1.0,
            "ITF": 0.9
        }
        return multipliers.get(tournament_category, 1.2)
    
    def _update_statistics(self, injury: Injury, player: Player):
        """Met à jour les statistiques des blessures"""
        self.injury_statistics["total_injuries"] += 1
        self.injury_statistics["players_affected"].add(player.full_name)
        
        # Par type
        injury_type = injury.type.value
        if injury_type not in self.injury_statistics["injuries_by_type"]:
            self.injury_statistics["injuries_by_type"][injury_type] = 0
        self.injury_statistics["injuries_by_type"][injury_type] += 1
        
        # Par gravité
        severity = injury.severity.value
        if severity not in self.injury_statistics["injuries_by_severity"]:
            self.injury_statistics["injuries_by_severity"][severity] = 0
        self.injury_statistics["injuries_by_severity"][severity] += 1
    
    def simulate_injury_for_testing(self, player: Player, injury_key: str) -> Optional[Injury]:
        """
        Force une blessure spécifique pour les tests
        
        Args:
            player: Joueur à blesser
            injury_key: Clé de la blessure dans INJURIES_DATABASE
            
        Returns:
            Injury créée ou None si clé invalide
        """
        if injury_key not in INJURIES_DATABASE:
            return None
        
        injury_data = INJURIES_DATABASE[injury_key]
        duration = random.randint(injury_data.min_recovery_weeks, injury_data.max_recovery_weeks)
        
        injury = Injury(
            injury_key=injury_key,
            injury_data=injury_data,
            weeks_remaining=duration,
            original_duration=duration
        )
        
        player.add_injury(injury)
        self._update_statistics(injury, player)
        
        return injury
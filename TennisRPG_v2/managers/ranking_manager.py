"""
Gestionnaire des classements ATP, Race et ELO
"""
from typing import Dict, List, Optional
import pandas as pd

from ..entities.player import Player
from ..entities.ranking import Ranking, RankingType
from ..utils.constants import TIME_CONSTANTS


class RankingManager:
    """Gestionnaire centralisé des classements"""
    
    def __init__(self, players: List[Player]):
        """
        Initialise le gestionnaire des classements
        
        Args:
            players: Liste initiale des joueurs
        """
        self.players = {player.full_name: player for player in players}
        
        # Crée les classements
        self.atp_ranking = Ranking(self.players, is_preliminary=False)
        self.atp_race_ranking = Ranking(self.players, is_preliminary=False)
        self.elo_ranking = Ranking(self.players, is_preliminary=False)
        
        # DataFrame pour tracker les points ATP par semaine (52 semaines glissantes)
        self.atp_points_history = pd.DataFrame(
            0, 
            index=list(self.players.keys()),
            columns=[f"week_{i}" for i in range(1, TIME_CONSTANTS["WEEKS_PER_YEAR"] + 1)]
        )
        
        self.current_week = 1
        
    def add_player(self, player: Player) -> None:
        """Ajoute un nouveau joueur aux classements"""
        if player.full_name not in self.players:
            self.players[player.full_name] = player
            
            # Ajoute aux classements
            self.atp_ranking.add_player(player)
            self.atp_race_ranking.add_player(player)  
            self.elo_ranking.add_player(player)
            
            # Ajoute à l'historique ATP
            new_row = pd.Series(0, index=self.atp_points_history.columns, name=player.full_name)
            self.atp_points_history = pd.concat([self.atp_points_history, new_row.to_frame().T])
    
    def remove_player(self, player: Player) -> None:
        """Retire un joueur des classements"""
        if player.full_name in self.players:
            del self.players[player.full_name]
            
            # Retire des classements
            self.atp_ranking.remove_player(player)
            self.atp_race_ranking.remove_player(player)
            self.elo_ranking.remove_player(player)
            
            # Retire de l'historique
            self.atp_points_history = self.atp_points_history.drop(player.full_name, errors='ignore')
    
    def get_player_rank(self, player: Player, ranking_type: RankingType = RankingType.ATP) -> Optional[int]:
        """
        Retourne le classement d'un joueur
        
        Args:
            player: Le joueur
            ranking_type: Type de classement
            
        Returns:
            Position dans le classement ou None si non classé
        """
        if ranking_type == RankingType.ATP:
            return self.atp_ranking.get_player_rank(player)
        elif ranking_type == RankingType.ATP_RACE:
            return self.atp_race_ranking.get_player_rank(player) 
        elif ranking_type == RankingType.ELO:
            return self.elo_ranking.get_player_rank(player)
        else:
            return None
    
    def update_weekly_rankings(self) -> None:
        """Met à jour tous les classements à la fin d'une semaine"""
        # Met à jour les classements
        self.atp_ranking.update_ranking()
        self.atp_race_ranking.update_ranking()
        self.elo_ranking.update_ranking()
    
    def reset_atp_race(self) -> None:
        """Remet à zéro la race ATP (début d'année)"""
        for player in self.players.values():
            if hasattr(player, 'career'):
                player.career.atp_race_points = 0
        
        # Met à jour le classement race
        self.atp_race_ranking.update_ranking()
    
    def display_ranking(self, ranking_type: RankingType = RankingType.ATP, 
                       count: int = 50) -> None:
        """
        Affiche un classement
        
        Args:
            ranking_type: Type de classement à afficher
            count: Nombre de joueurs à afficher
        """
        print(f"\n🏆 CLASSEMENT {ranking_type.value.upper()}")
        print("=" * 60)
        
        if ranking_type == RankingType.ATP:
            self.atp_ranking.display_ranking(count)
        elif ranking_type == RankingType.ATP_RACE:
            self.atp_race_ranking.display_ranking(count)
        elif ranking_type == RankingType.ELO:
            self.elo_ranking.display_ranking(count)
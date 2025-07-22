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
        self.atp_ranking = Ranking(self.players)
        self.atp_race_ranking = Ranking(self.players)
        self.elo_ranking = Ranking(self.players)
        
        # Initialise les classements
        self._initialize_all_rankings()
        
        # DataFrame pour tracker les points ATP par semaine (52 semaines glissantes)
        self.atp_points_history = pd.DataFrame(
            0, 
            index=list(self.players.keys()),
            columns=[f"week_{i}" for i in range(1, TIME_CONSTANTS["WEEKS_PER_YEAR"] + 1)]
        )
        
        self.current_week = 1
        
    def _initialize_all_rankings(self) -> None:
        """Initialise tous les classements avec les données actuelles des joueurs"""
        # Classement ATP
        atp_players = sorted(
            self.players.values(),
            key=lambda p: p.career.atp_points,
            reverse=True
        )
        self.atp_ranking.update_rankings(atp_players)
        
        # Classement ATP Race
        race_players = sorted(
            self.players.values(),
            key=lambda p: p.career.atp_race_points,
            reverse=True
        )
        self.atp_race_ranking.update_rankings(race_players)
        
        # Classement ELO
        elo_players = sorted(
            self.players.values(),
            key=lambda p: p.elo,
            reverse=True
        )
        self.elo_ranking.update_rankings(elo_players)
        
    def _get_ranking_by_type(self, ranking_type: RankingType) -> Ranking:
        """Retourne l'objet ranking correspondant au type"""
        if ranking_type == RankingType.ATP:
            return self.atp_ranking
        elif ranking_type == RankingType.ATP_RACE:
            return self.atp_race_ranking
        elif ranking_type == RankingType.ELO:
            return self.elo_ranking
        else:
            raise ValueError(f"Type de classement inconnu: {ranking_type}")
        
    def add_player(self, player: Player) -> None:
        """Ajoute un nouveau joueur aux classements"""
        if player.full_name not in self.players:
            self.players[player.full_name] = player
            
            # Ajoute à l'historique ATP
            new_row = pd.Series(0, index=self.atp_points_history.columns, name=player.full_name)
            self.atp_points_history = pd.concat([self.atp_points_history, new_row.to_frame().T])
            
            # Met à jour tous les classements
            self._initialize_all_rankings()
    
    def remove_player(self, player: Player) -> None:
        """Retire un joueur des classements"""
        if player.full_name in self.players:
            del self.players[player.full_name]
            
            # Retire de l'historique
            self.atp_points_history = self.atp_points_history.drop(player.full_name, errors='ignore')
            
            # Met à jour tous les classements
            self._initialize_all_rankings()
    
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
        self._initialize_all_rankings()
    
    def reset_atp_race(self) -> None:
        """Remet à zéro la race ATP (début d'année)"""
        # Remet à zéro les points de race de tous les joueurs
        for player in self.players.values():
            player.career.atp_race_points = 0
        
        # Met à jour le classement ATP Race
        race_players = sorted(
            self.players.values(),
            key=lambda p: p.career.atp_race_points,
            reverse=True
        )
        self.atp_race_ranking.update_rankings(race_players)
    
    def display_ranking(self, ranking_type: RankingType = RankingType.ATP, 
                       count: Optional[int] = 50) -> None:
        """
        Affiche un classement
        
        Args:
            ranking_type: Type de classement à afficher
            count: Nombre de joueurs à afficher
        """
        print(f"\n🏆 CLASSEMENT {ranking_type.value.upper()}")
        print("=" * 60)
        
        ranking_obj = self._get_ranking_by_type(ranking_type)
        players = ranking_obj.get_ranked_players(count)
        
        for rank, player in enumerate(players, 1):
            if ranking_type == RankingType.ATP:
                points = player.career.atp_points
                points_label = "ATP Points"
            elif ranking_type == RankingType.ATP_RACE:
                points = player.career.atp_race_points
                points_label = "ATP Race Points"
            elif ranking_type == RankingType.ELO:
                points = player.elo
                points_label = "ELO"
            
            print(f"{rank}. {player.first_name} {player.last_name} - {points_label}: {points} - Pays: {player.country}")

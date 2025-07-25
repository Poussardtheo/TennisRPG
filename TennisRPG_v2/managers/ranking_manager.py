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
        self._rankings_need_update = False  # Flag pour savoir si les classements doivent être mis à jour
        
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
        
        # Marque les classements comme à jour
        self._rankings_need_update = False
        
    def mark_rankings_for_update(self) -> None:
        """Marque les classements comme nécessitant une mise à jour"""
        self._rankings_need_update = True
        
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
        # Met à jour les classements seulement si nécessaire
        if self._rankings_need_update:
            self._initialize_all_rankings()
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
    
    def add_atp_points(self, player_name: str, points: int, week: Optional[int] = None) -> None:
        """
        Ajoute des points ATP à un joueur pour une semaine donnée
        
        Args:
            player_name: Nom du joueur
            points: Points à ajouter
            week: Semaine (par défaut semaine courante)
        """
        if week is None:
            week = self.current_week
            
        week_col = f"week_{week}"
        if player_name in self.atp_points_history.index and week_col in self.atp_points_history.columns:
            self.atp_points_history.loc[player_name, week_col] += points
    
    def get_points_to_defend(self, player_name: str, week: Optional[int] = None) -> int:
        """
        Calcule les points que le joueur doit défendre cette semaine
        (points gagnés en semaine équivalente il y a 52 semaines - stockés dans la même colonne)
        
        Args:
            player_name: Nom du joueur
            week: Semaine à vérifier (par défaut semaine courante)
            
        Returns:
            Nombre de points à défendre
        """
        if week is None:
            week = self.current_week
            
        # Pour un système glissant sur 52 semaines, on retire les points
        # de la même semaine stockés dans notre historique (qui datent de 52 semaines)
        week_col = f"week_{week}"
        
        if player_name in self.atp_points_history.index and week_col in self.atp_points_history.columns:
            return int(self.atp_points_history.loc[player_name, week_col])
        return 0
    
    def advance_week(self) -> None:
        """
        Avance d'une semaine seulement. 
        Les points ATP ne sont PAS gérés ici - ils doivent être retirés 
        au DÉBUT de chaque semaine, pas à la fin.
        """
        # Avance la semaine
        self.current_week = (self.current_week % TIME_CONSTANTS["WEEKS_PER_YEAR"]) + 1
        
        # Marque les classements pour mise à jour
        self.mark_rankings_for_update()
    
    def expire_weekly_points(self) -> None:
        """
        Retire les points qui expirent au début de cette semaine (système glissant sur 52 semaines).
        
        Cette méthode doit être appelée au DÉBUT de chaque semaine, avant les tournois.
        Elle retire les points gagnés dans cette même semaine il y a 52 semaines.
        """
        week_col = f"week_{self.current_week}"
        
        if week_col in self.atp_points_history.columns:
            for player_name, player in self.players.items():
                if player_name in self.atp_points_history.index:
                    # Points à retirer (datent de 52 semaines, stockés dans cette colonne)
                    points_to_lose = int(self.atp_points_history.loc[player_name, week_col])
                    if points_to_lose > 0:
                        player.career.atp_points = max(0, player.career.atp_points - points_to_lose)
            
            # Remet à zéro la colonne pour accueillir les nouveaux points de cette semaine
            self.atp_points_history[week_col] = 0
        
        # Marque les classements pour mise à jour après modification des points
        self.mark_rankings_for_update()
    
    def display_ranking(self, ranking_type: RankingType = RankingType.ATP, 
                       count: Optional[int] = 50, 
                       start_rank: int = 1) -> None:
        """
        Affiche un classement
        
        Args:
            ranking_type: Type de classement à afficher
            count: Nombre de joueurs à afficher
            start_rank: Rang de départ pour l'affichage (1-based)
        """
        # Met à jour les classements seulement si nécessaire
        if self._rankings_need_update:
            self._initialize_all_rankings()
        print(f"\n🏆 CLASSEMENT {ranking_type.value.upper()}")
        if start_rank > 1:
            print(f"📍 Affichage du rang {start_rank} à {start_rank + count - 1}")
        print("=" * 60)
        
        ranking_obj = self._get_ranking_by_type(ranking_type)
        # Récupérer plus de joueurs pour permettre l'affichage à partir du rang souhaité
        total_players_needed = start_rank + count - 1
        all_players = ranking_obj.get_ranked_players(total_players_needed)
        
        # Sélectionner seulement les joueurs dans la plage demandée
        if start_rank > len(all_players):
            print("❌ Rang de départ trop élevé - pas assez de joueurs dans le classement")
            return
            
        end_index = min(start_rank + count - 1, len(all_players))
        players_to_display = all_players[start_rank - 1:end_index]
        
        for i, player in enumerate(players_to_display):
            rank = start_rank + i
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

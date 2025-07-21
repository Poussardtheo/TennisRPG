"""
Gestionnaire de tournois - utilise la base de données existante
"""
from typing import List, Dict
import random

from ..data.tournaments_database import tournois
from ..entities.tournament import Tournament
from ..utils.helpers import get_participation_rate


class TournamentManager:
    """Gestionnaire pour les tournois du calendrier"""
    
    def __init__(self):
        self.tournament_database = tournois
    
    def get_tournaments_for_week(self, week: int) -> List[Tournament]:
        """
        Retourne les tournois disponibles pour une semaine donnée
        
        Args:
            week: Numéro de la semaine (1-52)
            
        Returns:
            Liste des tournois disponibles
        """
        if week not in self.tournament_database:
            return []
        
        return list(self.tournament_database[week])
    
    def get_tournaments_for_player(self, week: int, player, ranking_manager=None) -> List[Tournament]:
        """
        Retourne les tournois où le joueur peut participer selon son niveau
        
        Args:
            week: Numéro de la semaine
            player: Le joueur
            ranking_manager: Gestionnaire de classement (optionnel)
            
        Returns:
            Liste des tournois éligibles pour le joueur
        """
        available_tournaments = self.get_tournaments_for_week(week)
        eligible_tournaments = []
        
        for tournament in available_tournaments:
            if tournament.is_player_eligible(player, ranking_manager):
                eligible_tournaments.append(tournament)
        
        return eligible_tournaments
    
    def select_players_for_tournament(self, tournament: Tournament, 
                                    all_players: Dict[str, 'Player'], 
                                    ranking_manager=None) -> List['Player']:
        """
        Sélectionne les joueurs qui participeront au tournoi
        
        Args:
            tournament: Le tournoi
            all_players: Dictionnaire de tous les joueurs
            ranking_manager: Gestionnaire de classement

            
        Returns:
            Liste des participants sélectionnés
        """
        # Trouve tous les joueurs éligibles
        eligible_players = []
        for player in all_players.values():
            if tournament.is_player_eligible(player, ranking_manager):

                # Simule une décision de participation basée sur fatigue et probabilité
                participation_rate = get_participation_rate(tournament)
                should_participate = self._should_player_participate(player, tournament, participation_rate)

                if should_participate:
                    eligible_players.append(player)
        
        # Trie par force (ELO ou classement ATP)
        if ranking_manager:
            eligible_players.sort(key=lambda p: ranking_manager.get_player_rank(p) or 999999)
        else:
            eligible_players.sort(key=lambda p: p.elo, reverse=True)
        
        # Prend les premiers selon la capacité du tournoi
        selected = eligible_players[:tournament.num_players]
        
        # Si pas assez de joueurs, complète avec des joueurs moins forts
        while len(selected) < tournament.num_players and len(eligible_players) > len(selected):
            remaining = [p for p in eligible_players if p not in selected]
            if remaining:
                selected.extend(remaining[:tournament.num_players - len(selected)])
            else:
                break
        
        return selected
    
    def _should_player_participate(self, player, tournament: Tournament, base_rate: float) -> bool:
        """
        Détermine si un joueur devrait participer à un tournoi
        
        Args:
            player: Le joueur
            tournament: Le tournoi
            base_rate: Taux de base de participation
            
        Returns:
            True si le joueur devrait participer
        """
        # Facteurs influençant la participation
        fatigue_factor = 1.0
        if hasattr(player, 'physical') and hasattr(player.physical, 'fatigue'):
            fatigue_factor = max(0.2, 1.0 - (player.physical.fatigue / 100) * 0.6)
        
        # Les joueurs principaux participent toujours (si éligibles)
        if hasattr(player, 'is_main_player') and player.is_main_player:
            return fatigue_factor > 0.1  # Seulement si pas trop fatigué
        
        # Calcule la probabilité finale
        final_probability = base_rate * fatigue_factor
        
        return random.random() < final_probability
    
    def simulate_week_tournaments(self, week: int, all_players: Dict[str, 'Player'], 
                                ranking_manager=None, main_player=None) -> Dict[Tournament, 'TournamentResult']:
        """
        Simule tous les tournois d'une semaine
        
        Args:
            week: Numéro de la semaine
            all_players: Tous les joueurs disponibles
            ranking_manager: Gestionnaire de classement
            main_player: Joueur principal (optionnel)
            
        Returns:
            Dictionnaire des résultats par tournoi
        """
        tournaments = self.get_tournaments_for_week(week)
        results = {}
        for tournament in tournaments:
            # Sélectionne les participants
            participants = self.select_players_for_tournament(
                tournament, all_players, ranking_manager
            )

            # Ajoute les participants au tournoi
            for participant in participants:
                tournament.add_participant(participant)
            
            # Joue le tournoi (verbose seulement si joueur principal présent)
            if len(tournament.participants) >= 4:  # Minimum pour un tournoi
                result = tournament.play_tournament()
                results[tournament] = result
            
            # Nettoie pour le prochain tournoi potentiel
            tournament.participants.clear()
            tournament.match_results.clear()
            tournament.eliminated_players.clear()
        
        return results
    
    def get_tournament_by_name(self, name: str, week: int = None) -> Tournament:
        """
        Trouve un tournoi par son nom
        
        Args:
            name: Nom du tournoi
            week: Semaine spécifique (optionnel)
            
        Returns:
            Le tournoi trouvé ou None
        """
        if week:
            tournaments = self.get_tournaments_for_week(week)
            for tournament in tournaments:
                if tournament.name == name:
                    return tournament
        else:
            # Cherche dans toutes les semaines
            for week_tournaments in self.tournament_database.values():
                for tournament in week_tournaments:
                    if tournament.name == name:
                        return tournament
        
        return None
    
    def get_tournament_calendar_summary(self) -> Dict[str, List[str]]:
        """
        Retourne un résumé du calendrier des tournois
        
        Returns:
            Dictionnaire semaine -> liste des noms de tournois
        """
        calendar = {}
        for week, tournaments in self.tournament_database.items():
            calendar[f"Semaine {week}"] = [t.name for t in tournaments]
        
        return calendar

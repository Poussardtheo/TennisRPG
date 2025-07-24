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
            # Seul le joueur principal est soumis aux restrictions d'éligibilité
            # Les PNJ peuvent participer à tous les tournois
            if hasattr(player, 'is_main_player') and player.is_main_player:
                if tournament.is_player_eligible(player, ranking_manager):
                    eligible_tournaments.append(tournament)
            else:
                # PNJ : tous les tournois sont disponibles
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
        from ..data.tournaments_data import TournamentCategory
        
        # Cas spécial pour l'ATP Finals - logique garantie
        if tournament.category == TournamentCategory.ATP_FINALS:
            return self._select_atp_finals_participants(tournament, all_players, ranking_manager)
        
        # Trouve tous les joueurs éligibles (sans probabilité d'abord)
        all_eligible = []
        for player in all_players.values():
            if player.is_main_player:
                continue    # Ignore les joueurs principaux pour cette sélection
            # Les PNJ ne sont pas soumis aux restrictions d'éligibilité
            # Seul le joueur principal doit respecter les seuils de classement
            all_eligible.append(player)
        
        # Trie par force décroissante (meilleurs en premier, plus faibles en dernier)
        if ranking_manager:
            # Pour ATP: rang plus bas = meilleur, donc tri croissant
            all_eligible.sort(key=lambda p: ranking_manager.get_player_rank(p) or 999999)
        else:
            # Pour ELO: valeur plus haute = meilleur, donc tri décroissant  
            all_eligible.sort(key=lambda p: p.elo, reverse=True)
        
        # Phase 1: Sélection avec probabilité parmi les meilleurs joueurs
        willing_participants = []
        
        for player in all_eligible:
            # Taux de participation personnalisé selon le classement du joueur
            participation_rate = get_participation_rate(tournament, player, ranking_manager)
            should_participate = self._should_player_participate(player, participation_rate, tournament)
            if should_participate:
                willing_participants.append(player)
        
        # Phase 2: Si pas assez de volontaires, force la participation des meilleurs
        selected = willing_participants[:tournament.num_players]
        
        if len(selected) < tournament.num_players:
            # Prend les meilleurs joueurs restants pour compléter
            remaining_needed = tournament.num_players - len(selected)
            remaining_players = [p for p in all_eligible if p not in selected]
            selected.extend(remaining_players[:remaining_needed])
        
        return selected
    
    def _select_atp_finals_participants(self, tournament: Tournament, 
                                      all_players: Dict[str, 'Player'], 
                                      ranking_manager=None) -> List['Player']:
        """
        Sélection spéciale pour l'ATP Finals - garantit exactement 8 participants
        basés sur le classement race ATP
        
        Args:
            tournament: Le tournoi ATP Finals
            all_players: Dictionnaire de tous les joueurs
            ranking_manager: Gestionnaire de classement
            
        Returns:
            Liste des 8 participants pour l'ATP Finals
        """
        if not ranking_manager:
            # Fallback sur ELO si pas de ranking manager
            # Les PNJ ne sont pas soumis aux restrictions d'éligibilité pour l'ATP Finals
            eligible = [p for p in all_players.values() 
                       if not p.is_main_player]
            eligible.sort(key=lambda p: p.elo, reverse=True)
            return eligible[:8]

        # Trie par classement race (meilleur rang = plus petit nombre)
        from ..entities.ranking import RankingType
        all_eligible = [p for p in all_players.values()
                        if not p.is_main_player]
        all_eligible.sort(key=lambda p: ranking_manager.get_player_rank(p, RankingType.ATP_RACE) or 999999)

        # Prend les 8 meilleurs, mais vérifie qu'ils peuvent participer
        selected = []
        for player in all_eligible:
            # Pour l'ATP Finals, seule la fatigue extrême peut empêcher la participation
            fatigue_level = 0
            if hasattr(player, 'physical') and hasattr(player.physical, 'fatigue'):
                fatigue_level = player.physical.fatigue
            # Participation quasi-garantie sauf si fatigue critique (> 95%)
            if fatigue_level <= 95:
                selected.append(player)
            # Arrête dès qu'on a 8 joueurs
            if len(selected) >= 8:
                return selected[:8]

        return selected  # Garantit exactement 8 joueurs
    
    def _should_player_participate(self, player, base_rate: float, tournament) -> bool:
        """
        Détermine si un joueur devrait participer à un tournoi
        
        Args:
            player: Le joueur
            base_rate: Taux de base de participation
            tournament: Le tournoi concerné
            
        Returns:
            True si le joueur devrait participer
        """
        from ..data.tournaments_data import TournamentCategory
        
        # Facteurs influençant la participation
        fatigue_factor = 1.0
        fatigue_level = 0
        if hasattr(player, 'physical') and hasattr(player.physical, 'fatigue'):
            fatigue_level = player.physical.fatigue
            fatigue_factor = max(0.2, 1.0 - (fatigue_level / 100)) #Todo: Look at that value * 0.6)
        
        # Bonus de motivation pour les tournois prestigieux
        motivation_bonus = 1.0
        is_prestigious = tournament.category in [TournamentCategory.GRAND_SLAM, TournamentCategory.ATP_FINALS]
        
        if is_prestigious:
            motivation_bonus = 3  # 50% de bonus de motivation
            
            # Logique spéciale pour fatigue élevée dans les tournois prestigieux
            # TODO: Quand le système de blessure sera implémenté, prendre en compte les blessures ici
            if fatigue_level > 90:
                return False  # Ne participe pas si trop fatigué, même pour Grand Chelem/ATP Finals
        
        # Les joueurs principaux participent toujours (si éligibles)
        if hasattr(player, 'is_main_player') and player.is_main_player:
            # Pour les tournois prestigieux, accepte un peu plus de fatigue
            fatigue_threshold = 0.05 if is_prestigious else 0.1
            return fatigue_factor > fatigue_threshold
        
        # Calcule la probabilité finale avec bonus de motivation
        final_probability = base_rate * fatigue_factor * motivation_bonus
        
        return random.random() < final_probability
    
    def simulate_week_tournaments(self, week: int, all_players: Dict[str, 'Player'], 
                                ranking_manager=None, atp_points_manager=None, injury_manager=None) -> Dict[Tournament, 'TournamentResult']:
        """
        Simule tous les tournois d'une semaine
        
        Args:
            week: Numéro de la semaine
            all_players: Tous les joueurs disponibles
            ranking_manager: Gestionnaire de classement
            atp_points_manager: Gestionnaire des points ATP
            injury_manager: Gestionnaire des blessures
            
        Returns:
            Dictionnaire des résultats par tournoi
        """
        tournaments = self.get_tournaments_for_week(week)
        results = {}
        
        # CRUCIAL: Trie les tournois par prestige décroissant
        # Les meilleurs joueurs vont d'abord aux tournois les plus prestigieux
        sorted_tournaments = sorted(tournaments, key=lambda t: t.tournament_importance, reverse=True)
        
        # Pool de joueurs disponibles (copie pour éviter de modifier l'original)
        available_players = dict(all_players)
        
        for tournament in sorted_tournaments:
            # Sélectionne les participants parmi les joueurs encore disponibles
            participants = self.select_players_for_tournament(
                tournament, available_players, ranking_manager
            )

            # Ajoute les participants au tournoi
            for participant in participants:
                tournament.add_participant(participant)
            
            # Joue le tournoi (verbose seulement si joueur principal présent)
            if len(tournament.participants) >= 4:  # Minimum pour un tournoi
                result = tournament.play_tournament(atp_points_manager=atp_points_manager, week=week, injury_manager=injury_manager)
                results[tournament] = result
            
            # CRUCIAL: Retire les participants du pool disponible
            for participant in participants:
                if participant.full_name in available_players:
                    del available_players[participant.full_name]
            
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

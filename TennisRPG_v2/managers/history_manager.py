"""
Gestionnaire d'historique des tournois
"""
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict

from ..entities.tournament import TournamentResult
from ..entities.player import Player
from ..data.tournaments_data import TournamentCategory


class HistoryManager:
    """Gestionnaire pour l'historique des tournois"""
    
    def __init__(self):
        # Structure: {année: {semaine: [TournamentResult]}}
        self.tournament_history: Dict[int, Dict[int, List[TournamentResult]]] = defaultdict(lambda: defaultdict(list))
    
    def record_tournament_result(self, result: TournamentResult, year: int, week: int) -> None:
        """
        Enregistre le résultat d'un tournoi dans l'historique
        
        Args:
            result: Résultat du tournoi
            year: Année du tournoi
            week: Semaine du tournoi
        """
        self.tournament_history[year][week].append(result)
    
    def get_player_history_for_year(self, player: Player, year: int) -> List[Tuple[int, TournamentResult]]:
        """
        Récupère l'historique d'un joueur pour une année donnée
        
        Args:
            player: Joueur concerné
            year: Année à consulter
            
        Returns:
            Liste de (semaine, résultat) où le joueur a participé
        """
        player_tournaments = []
        
        if year not in self.tournament_history:
            return player_tournaments
            
        for week, results in self.tournament_history[year].items():
            for result in results:
                # Vérifie si le joueur a participé à ce tournoi
                # Comparaison par nom complet pour éviter les problèmes d'identité d'objet
                player_participated = any(p.full_name == player.full_name for p in result.all_results.keys())
                if player_participated:
                    player_tournaments.append((week, result))
        
        # Trie par semaine
        player_tournaments.sort(key=lambda x: x[0])
        return player_tournaments
    
    def get_tournament_history_by_name(self, tournament_name: str) -> Dict[int, List[Tuple[int, TournamentResult]]]:
        """
        Récupère l'historique d'un tournoi par son nom
        
        Args:
            tournament_name: Nom du tournoi
            
        Returns:
            Dictionnaire {année: [(semaine, résultat)]}
        """
        tournament_history = defaultdict(list)
        
        for year, weeks in self.tournament_history.items():
            for week, results in weeks.items():
                for result in results:
                    if result.tournament_name == tournament_name:
                        tournament_history[year].append((week, result))
        
        # Trie chaque année par semaine
        for year_results in tournament_history.values():
            year_results.sort(key=lambda x: x[0])
            
        return dict(tournament_history)
    
    def get_tournaments_by_category(self, category: TournamentCategory) -> Set[str]:
        """
        Récupère tous les noms de tournois d'une catégorie donnée
        
        Args:
            category: Catégorie de tournoi
            
        Returns:
            Ensemble des noms de tournois de cette catégorie
        """
        tournament_names = set()
        
        for year_data in self.tournament_history.values():
            for week_results in year_data.values():
                for result in week_results:
                    if result.category == category:
                        tournament_names.add(result.tournament_name)
        
        return tournament_names
    
    def get_grand_slam_tournaments(self) -> Set[str]:
        """Récupère tous les tournois du Grand Chelem"""
        return self.get_tournaments_by_category(TournamentCategory.GRAND_SLAM)
    
    def get_atp_tournaments_by_level(self) -> Dict[str, Set[str]]:
        """
        Récupère tous les tournois ATP organisés par niveau
        
        Returns:
            Dictionnaire {niveau: {noms_tournois}}
        """
        atp_levels = {
            "ATP Finals": TournamentCategory.ATP_FINALS,
            "Masters 1000": TournamentCategory.MASTERS_1000,
            "ATP 500": TournamentCategory.ATP_500,
            "ATP 250": TournamentCategory.ATP_250
        }
        
        tournaments_by_level = {}
        for level_name, category in atp_levels.items():
            tournaments_by_level[level_name] = self.get_tournaments_by_category(category)
        
        return tournaments_by_level
    
    def get_challenger_tournaments_by_level(self) -> Dict[str, Set[str]]:
        """
        Récupère tous les tournois Challenger organisés par niveau
        
        Returns:
            Dictionnaire {niveau: {noms_tournois}}
        """
        challenger_levels = {
            "Challenger 175": TournamentCategory.CHALLENGER_175,
            "Challenger 125": TournamentCategory.CHALLENGER_125,
            "Challenger 100": TournamentCategory.CHALLENGER_100,
            "Challenger 75": TournamentCategory.CHALLENGER_75,
            "Challenger 50": TournamentCategory.CHALLENGER_50
        }
        
        tournaments_by_level = {}
        for level_name, category in challenger_levels.items():
            tournaments_by_level[level_name] = self.get_tournaments_by_category(category)
        
        return tournaments_by_level
    
    def get_years_with_data(self) -> List[int]:
        """
        Récupère toutes les années pour lesquelles il y a des données
        
        Returns:
            Liste des années triées par ordre croissant (plus anciennes en premier)
        """
        years = list(self.tournament_history.keys())
        years.sort()  # Tri croissant: plus anciennes en premier
        return years
    
    def get_player_tournament_result(self, player: Player, result: TournamentResult) -> str:
        """
        Récupère le résultat spécifique d'un joueur dans un tournoi
        
        Args:
            player: Joueur concerné
            result: Résultat du tournoi
            
        Returns:
            String décrivant le tour atteint par le joueur
        """
        # Recherche par nom complet pour éviter les problèmes d'identité d'objet
        for p, round_reached in result.all_results.items():
            if p.full_name == player.full_name:
                return round_reached
        return "Non participé"
    
    def display_player_year_history(self, player: Player, year: int) -> None:
        """
        Affiche l'historique d'un joueur pour une année
        
        Args:
            player: Joueur concerné
            year: Année à afficher
        """
        player_history = self.get_player_history_for_year(player, year)
        
        if not player_history:
            print(f"\n📈 Aucun tournoi disputé par {player.full_name} en {year}")
            return
        
        print(f"\n📈 HISTORIQUE DE {player.full_name.upper()} - {year}")
        print("=" * 80)
        print(f"{'Semaine':<8} {'Tournoi':<35} {'Catégorie':<15} {'Résultat':<15}")
        print("-" * 80)
        
        for week, result in player_history:
            player_result = self.get_player_tournament_result(player, result)
            category_str = result.category.value
            
            print(f"{week:<8} {result.tournament_name:<35} {category_str:<15} {player_result:<15}")
        
        print("=" * 80)
        print(f"Total de tournois disputés: {len(player_history)}")
    
    def display_tournament_history(self, tournament_name: str) -> None:
        """
        Affiche l'historique complet d'un tournoi
        
        Args:
            tournament_name: Nom du tournoi
        """
        tournament_history = self.get_tournament_history_by_name(tournament_name)
        
        if not tournament_history:
            print(f"\n🏆 Aucune donnée pour le tournoi: {tournament_name}")
            return
        
        print(f"\n🏆 HISTORIQUE DU TOURNOI: {tournament_name.upper()}")
        print("=" * 90)
        print(f"{'Année':<6} {'Semaine':<8} {'Vainqueur':<25} {'Finaliste':<25} {'Catégorie':<15}")
        print("-" * 90)
        
        # Trie par année décroissante
        for year in sorted(tournament_history.keys(), reverse=True):
            for week, result in tournament_history[year]:
                winner_name = result.winner.full_name if result.winner else "N/A"
                finalist_name = result.finalist.full_name if result.finalist else "N/A"
                category_str = result.category.value
                
                print(f"{year:<6} {week:<8} {winner_name:<25} {finalist_name:<25} {category_str:<15}")
        
        print("=" * 90)
        total_editions = sum(len(year_data) for year_data in tournament_history.values())
        print(f"Total d'éditions: {total_editions}")
    
    def to_dict(self) -> Dict:
        """
        Convertit l'historique en dictionnaire pour la sauvegarde
        
        Returns:
            Dictionnaire représentant l'historique
        """
        history_dict = {}
        
        for year, weeks in self.tournament_history.items():
            history_dict[str(year)] = {}
            for week, results in weeks.items():
                history_dict[str(year)][str(week)] = []
                for result in results:
                    # Convertit TournamentResult en dictionnaire
                    result_dict = {
                        "tournament_name": result.tournament_name,
                        "category": result.category.value,
                        "winner": result.winner.to_dict() if result.winner else None,
                        "finalist": result.finalist.to_dict() if result.finalist else None,
                        "semifinalists": [p.to_dict() for p in result.semifinalists],
                        "quarterfinalists": [p.to_dict() for p in result.quarterfinalists],
                        "all_results": {p.full_name: round_reached for p, round_reached in result.all_results.items()},
                        "match_results": []  # Pour l'instant, on ne sauvegarde pas les détails des matchs
                    }
                    history_dict[str(year)][str(week)].append(result_dict)
        
        return history_dict
    
    def from_dict(self, data: Dict, all_players: Dict[str, Player]) -> None:
        """
        Charge l'historique depuis un dictionnaire
        
        Args:
            data: Dictionnaire contenant l'historique
            all_players: Dictionnaire de tous les joueurs {nom_complet: Player}
        """
        self.tournament_history.clear()
        
        for year_str, weeks in data.items():
            year = int(year_str)
            for week_str, results in weeks.items():
                week = int(week_str)
                for result_dict in results:
                    # Reconstruit TournamentResult depuis le dictionnaire
                    from ..data.tournaments_data import TournamentCategory
                    
                    # Trouve la catégorie
                    category = None
                    for cat in TournamentCategory:
                        if cat.value == result_dict["category"]:
                            category = cat
                            break
                    
                    if not category:
                        continue  # Skip si catégorie inconnue
                    
                    # Reconstruit les joueurs
                    winner = None
                    finalist = None
                    if result_dict["winner"]:
                        winner = Player.from_dict(result_dict["winner"])
                    if result_dict["finalist"]:
                        finalist = Player.from_dict(result_dict["finalist"])
                    
                    semifinalists = [Player.from_dict(p) for p in result_dict["semifinalists"]]
                    quarterfinalists = [Player.from_dict(p) for p in result_dict["quarterfinalists"]]
                    
                    # Reconstruit all_results
                    all_results = {}
                    for player_name, round_reached in result_dict["all_results"].items():
                        if player_name in all_players:
                            all_results[all_players[player_name]] = round_reached
                    
                    # Crée TournamentResult
                    result = TournamentResult(
                        tournament_name=result_dict["tournament_name"],
                        category=category,
                        winner=winner,
                        finalist=finalist,
                        semifinalists=semifinalists,
                        quarterfinalists=quarterfinalists,
                        all_results=all_results,
                        match_results=[]  # Vide pour l'instant
                    )
                    
                    self.tournament_history[year][week].append(result)
"""
Gestionnaire des retraites et rotation des joueurs
"""
import random
from typing import Dict, List, Tuple
from ..entities.player import Player, Gender
from ..managers.player_generator import PlayerGenerator
from ..utils.helpers import should_player_retire
from ..utils.constants import RETIREMENT_CONSTANTS


class RetirementManager:
    """Gestionnaire des retraites et de la rotation du pool de joueurs"""
    
    def __init__(self, player_generator: PlayerGenerator = None):
        self.player_generator = player_generator or PlayerGenerator()
        self.retirement_log: List[Dict] = []  # Historique des retraites
        
    def process_end_of_season_retirements(self, all_players: Dict[str, Player], 
                                        ranking_manager=None, year: int = None, main_player_gender: Gender = None) -> Tuple[List[Player], List[Player]]:
        """
        Traite les retraites en fin de saison et génère les remplaçants
        
        Args:
            all_players: Dictionnaire de tous les joueurs
            ranking_manager: Gestionnaire de classements (optionnel, pour obtenir les classements ATP)
            year: Année actuelle (pour les logs)
            main_player_gender: Genre du joueur principal (tous nouveaux joueurs auront ce genre)
            
        Returns:
            Tuple (liste des retraités, liste des nouveaux joueurs)
        """
        retired_players = []
        new_players = []
        
        print(f"\n🔄 ROTATION DU POOL DE JOUEURS - FIN {year or 'DE SAISON'}")
        print("=" * 50)
        
        # Sépare les joueurs par genre pour maintenir l'équilibre
        male_players = {name: player for name, player in all_players.items() 
                       if player.gender == Gender.MALE and not player.is_main_player}
        female_players = {name: player for name, player in all_players.items() 
                         if player.gender == Gender.FEMALE and not player.is_main_player}
        
        # Détermine le genre pour les nouveaux joueurs (celui du joueur principal si spécifié)
        replacement_gender = main_player_gender or Gender.MALE
        
        # Traite chaque genre séparément pour les retraites, mais utilise le genre principal pour les remplacements
        for gender_pool, gender in [(male_players, Gender.MALE), (female_players, Gender.FEMALE)]:
            gender_retired, gender_new = self._process_gender_retirements(
                gender_pool, gender, ranking_manager, year, replacement_gender
            )
            retired_players.extend(gender_retired)
            new_players.extend(gender_new)
        
        # Met à jour le pool de joueurs
        self._update_player_pool(all_players, retired_players, new_players)
        
        # Affiche le résumé
        self._display_retirement_summary(retired_players, new_players, year, ranking_manager)
        
        return retired_players, new_players
    
    def _process_gender_retirements(self, gender_pool: Dict[str, Player], gender: Gender, 
                                  ranking_manager=None, year: int = None, replacement_gender: Gender = None) -> Tuple[List[Player], List[Player]]:
        """Traite les retraites pour un genre spécifique"""
        retired_players = []
        new_players = []
        
        # Vieillit tous les joueurs d'un an
        self._age_players(gender_pool.values())
        
        # Détermine qui prend sa retraite
        for player_name, player in gender_pool.items():
            ranking_position = None
            if ranking_manager:
                ranking_position = ranking_manager.get_player_rank(player)
            
            if should_player_retire(player, ranking_position):
                retired_players.append(player)
                self._log_retirement(player, ranking_position, year)
        
        # Génère de nouveaux joueurs pour remplacer les retraités
        if retired_players:
            new_count = len(retired_players)
            final_gender = replacement_gender or gender
            print(f"   👴 {new_count} joueur{'s' if new_count > 1 else ''} {gender.value} prennent leur retraite")
            print(f"   🌱 Génération de {new_count} nouveau{'x' if new_count > 1 else ''} joueur{'s' if new_count > 1 else ''} {final_gender.value}")
            
            for _ in range(new_count):
                # Génère un jeune joueur avec un âge approprié
                young_age = random.randint(
                    RETIREMENT_CONSTANTS["YOUNG_PLAYER_MIN_AGE"],
                    RETIREMENT_CONSTANTS["YOUNG_PLAYER_MAX_AGE"]
                )
                new_player = self.player_generator.generate_player(final_gender, level_range=(1, 5))
                new_player.career.age = young_age
                new_players.append(new_player)
        
        return retired_players, new_players
    
    def _age_players(self, players: List[Player]) -> None:
        """Vieillit tous les joueurs d'un an"""
        for player in players:
            if hasattr(player, 'career') and hasattr(player.career, 'age'):
                player.career.age += 1
    
    def _log_retirement(self, player: Player, ranking_position: int = None, year: int = None) -> None:
        """Enregistre une retraite dans l'historique"""
        retirement_entry = {
            "player_name": player.full_name,
            "age": player.career.age,
            "ranking": ranking_position or "N/A",
            "year": year or "Unknown",
            "country": player.country
        }
        self.retirement_log.append(retirement_entry)
    
    def _update_player_pool(self, all_players: Dict[str, Player], 
                           retired_players: List[Player], new_players: List[Player]) -> None:
        """Met à jour le pool de joueurs en retirant les retraités et ajoutant les nouveaux"""
        # Retire les joueurs retraités
        for retired_player in retired_players:
            if retired_player.full_name in all_players:
                del all_players[retired_player.full_name]
        
        # Ajoute les nouveaux joueurs
        for new_player in new_players:
            # Assure que le nom est unique
            original_name = new_player.full_name
            counter = 1
            while new_player.full_name in all_players:
                new_player.first_name = f"{original_name} {counter}"
                counter += 1
            
            all_players[new_player.full_name] = new_player
    
    def _display_retirement_summary(self, retired_players: List[Player], 
                                   new_players: List[Player], year: int = None, 
                                   ranking_manager=None) -> None:
        """Affiche un résumé détaillé des retraites et nouveaux joueurs"""
        total_retired = len(retired_players)
        total_new = len(new_players)
        
        print(f"\n📊 RÉSUMÉ DE LA ROTATION:")
        print(f"   🏁 {total_retired} retraite{'s' if total_retired > 1 else ''}")
        print(f"   🆕 {total_new} nouveau{'x' if total_new > 1 else ''} joueur{'s' if total_new > 1 else ''}")
        
        if retired_players:
            self._display_detailed_retirements(retired_players, ranking_manager)
        
        if new_players:
            self._display_new_talents(new_players)
        
        print("=" * 50)
    
    def _display_detailed_retirements(self, retired_players: List[Player], ranking_manager=None) -> None:
        """Affiche les retraites en détail avec classements (uniquement top 100)"""
        
        # Filtre pour ne garder que les top 100
        top_100_retirees = []
        if ranking_manager:
            for player in retired_players:
                ranking = ranking_manager.get_player_rank(player)
                if ranking and ranking <= 100:
                    top_100_retirees.append(player)
        
        if not top_100_retirees:
            print(f"\n👋 RETRAITES NOTABLES: Aucun membre du top 100 n'a pris sa retraite")
            return
            
        print(f"\n👋 RETRAITES NOTABLES - TOP 100 ({len(top_100_retirees)}/{len(retired_players)}):")
        print("─" * 45)
        
        # Sépare par genre et trie par classement
        male_retirees = [p for p in top_100_retirees if p.gender == Gender.MALE]
        female_retirees = [p for p in top_100_retirees if p.gender == Gender.FEMALE]
        
        # Affiche les hommes
        if male_retirees:
            print("🚹 HOMMES:")
            male_retirees.sort(key=lambda p: ranking_manager.get_player_rank(p) or 999)
            for player in male_retirees:
                ranking = ranking_manager.get_player_rank(player)
                atp_points = player.career.atp_points or 0
                print(f"   #{ranking:<4} {player.full_name:<25} ({player.country}) - {player.career.age} ans - {atp_points} pts")
        
        # Affiche les femmes
        if female_retirees:
            print("\n🚺 FEMMES:")
            female_retirees.sort(key=lambda p: ranking_manager.get_player_rank(p) or 999)
            for player in female_retirees:
                ranking = ranking_manager.get_player_rank(player)
                atp_points = player.career.atp_points or 0
                print(f"   #{ranking:<4} {player.full_name:<25} ({player.country}) - {player.career.age} ans - {atp_points} pts")
        
        # Statistiques des retraites
        if retired_players:
            ages = [p.career.age for p in retired_players]
            avg_age = sum(ages) / len(ages)
            print(f"\n📈 STATISTIQUES DES RETRAITES:")
            print(f"   • Âge moyen: {avg_age:.1f} ans")
            print(f"   • Plus jeune: {min(ages)} ans")
            print(f"   • Plus âgé: {max(ages)} ans")
            
            # Top retraités par classement
            top_retirees = [p for p in retired_players if ranking_manager and ranking_manager.get_player_rank(p) and ranking_manager.get_player_rank(p) <= 100]
            if top_retirees:
                print(f"   • Retraités du Top 100: {len(top_retirees)}")
    
    def _display_new_talents(self, new_players: List[Player]) -> None:
        """Affiche les nouveaux talents en détail (échantillon limité)"""
        print(f"\n🌟 NOUVEAUX TALENTS ({len(new_players)}):")
        print("─" * 45)
        
        if new_players:
            # Affiche seulement un échantillon de 5 nouveaux joueurs max
            sample_size = min(5, len(new_players))
            sample_players = random.sample(new_players, sample_size)
            
            for player in sample_players:
                print(f"   🆕 {player.full_name:<25} ({player.country}) - {player.career.age} ans")
            
            if len(new_players) > 5:
                print(f"   ... et {len(new_players) - 5} autres nouveaux joueurs")
        
        # Statistiques des nouveaux joueurs
        if new_players:
            ages = [p.career.age for p in new_players]
            countries = list(set(p.country for p in new_players))
            print(f"\n📈 STATISTIQUES DES NOUVEAUX:")
            print(f"   • Âge moyen: {sum(ages) / len(ages):.1f} ans")
            print(f"   • Pays représentés: {len(countries)}")
    
    def get_retirement_stats(self, year: int = None) -> Dict:
        """Retourne des statistiques sur les retraites"""
        if year:
            year_retirements = [r for r in self.retirement_log if r["year"] == year]
        else:
            year_retirements = self.retirement_log
        
        if not year_retirements:
            return {}
        
        ages = [r["age"] for r in year_retirements]
        
        return {
            "total_retirements": len(year_retirements),
            "average_retirement_age": sum(ages) / len(ages),
            "youngest_retiree": min(ages),
            "oldest_retiree": max(ages),
            "countries": list(set(r["country"] for r in year_retirements))
        }
    
    def force_aging_simulation(self, all_players: Dict[str, Player], years: int = 1) -> None:
        """Force le vieillissement des joueurs (utile pour les simulations préliminaires)"""
        for player in all_players.values():
            if hasattr(player, 'career') and hasattr(player.career, 'age'):
                player.career.age += years
"""
Enhanced Save Manager - Multi-file, optimized save system
Sépare les données en plusieurs fichiers pour une meilleure organisation et performance
"""
import json
import pickle
import gzip
import os
from typing import Dict, Optional, Any, List, Set
from datetime import datetime
from pathlib import Path

from ..entities.player import Player, Gender
from ..entities.tournament import TournamentResult
from ..managers.history_manager import HistoryManager
from ..data.tournaments_data import TournamentCategory
from .serialization_utils import SerializationUtils, SerializationFormat, PlayerDataOptimizer


class EnhancedGameState:
    """État de jeu optimisé avec références au lieu de données complètes"""
    
    def __init__(self):
        self.main_player: Optional[Player] = None
        self.current_week: int = 1
        self.current_year: int = 2023
        self.is_preliminary_complete: bool = False
        self.save_date: str = ""
        self.game_version: str = "2.1"
        self.playtime_hours: float = 0.0
        self.retirement_log: List[Dict] = []
        
        # Références aux données externes
        self.active_player_refs: Set[str] = set()  # Joueurs qui ont interagi avec le joueur principal
        self.interacted_players: Dict[str, Player] = {}  # Cache des joueurs actifs


class EnhancedSaveManager:
    """Gestionnaire de sauvegarde optimisé avec système multi-fichiers"""
    
    def __init__(self, save_directory: str = "saves"):
        self.base_save_directory = Path(save_directory)
        self.base_save_directory.mkdir(parents=True, exist_ok=True)
        
        # Ces variables seront définies lors de la sauvegarde/chargement
        self.current_save_dir: Optional[Path] = None
        self.player_data_dir: Optional[Path] = None
        self.tournament_dir: Optional[Path] = None
        self.world_state_dir: Optional[Path] = None
        
        # Cache pour les données fréquemment utilisées
        self._player_cache: Dict[str, Player] = {}
        self._tournament_cache: Dict[str, Any] = {}
    
    def _setup_save_directories(self, save_name: str) -> None:
        """Crée la structure de répertoires pour une sauvegarde spécifique"""
        self.current_save_dir = self.base_save_directory / save_name
        self.player_data_dir = self.current_save_dir / "player_data"
        self.tournament_dir = self.current_save_dir / "tournaments"
        self.world_state_dir = self.current_save_dir / "world_state"
        
        for directory in [self.current_save_dir, self.player_data_dir, 
                         self.tournament_dir, self.world_state_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_game_enhanced(self, main_player: Player, all_players: Dict[str, Player],
                          history_manager: HistoryManager, current_week: int, 
                          current_year: int, save_name: str = None, **kwargs) -> str:
        """
        Sauvegarde optimisée avec séparation des données
        
        Args:
            save_name: Nom personnalisé pour la sauvegarde (optionnel)
        
        Returns:
            Le nom du dossier de sauvegarde
        """
        try:
            # Détermine le nom de la sauvegarde
            if save_name:
                # Nettoie le nom personnalisé (supprime caractères interdits)
                clean_save_name = "".join(c for c in save_name if c.isalnum() or c in (' ', '_', '-')).strip()
                clean_save_name = clean_save_name.replace(' ', '_')
            else:
                # Nom par défaut basé sur le joueur
                clean_save_name = f"{main_player.first_name}_{main_player.last_name}"
            
            # Ajoute timestamp si le dossier existe déjà
            base_save_name = clean_save_name
            counter = 1
            while (self.base_save_directory / clean_save_name).exists():
                clean_save_name = f"{base_save_name}_{counter}"
                counter += 1
            
            print(f"Sauvegarde optimisée: {clean_save_name}")
            
            # Configure les répertoires pour cette sauvegarde
            self._setup_save_directories(clean_save_name)
            
            # Génère l'ID interne pour les fichiers
            save_id = f"{main_player.first_name}_{main_player.last_name}_S{current_week}_{current_year}"
            
            # 1. Sauvegarde du joueur principal
            self._save_main_player(main_player, save_id)
            
            # 2. Détermine les joueurs actifs/interactifs
            active_players = self._determine_active_players(main_player, all_players, history_manager)
            self._save_active_players(active_players, save_id)
            
            # 3. Sauvegarde l'historique des tournois (optimisé)
            self._save_tournament_history_optimized(history_manager, save_id)
            
            # 4. Sauvegarde les données globales (état du monde)
            self._save_world_state(all_players, save_id, exclude_active=active_players.keys())
            
            # 5. Sauvegarde le fichier principal de métadonnées
            main_file = self._save_main_metadata(save_id, current_week, current_year, 
                                               active_players.keys(), clean_save_name, **kwargs)
            
            # 6. Statistiques de sauvegarde
            self._print_save_statistics(clean_save_name)
            
            return clean_save_name
            
        except Exception as e:
            print(f"Erreur sauvegarde optimisée: {e}")
            raise
    
    def _save_main_player(self, player: Player, save_id: str) -> None:
        """Sauvegarde uniquement le joueur principal"""
        filepath = self.player_data_dir / f"{save_id}_main_player.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(player.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _determine_active_players(self, main_player: Player, all_players: Dict[str, Player],
                                 history_manager: HistoryManager) -> Dict[str, Player]:
        """Détermine quels joueurs sont 'actifs' (ont interagi avec le joueur principal)"""
        active_players = {}
        
        # Ajoute tous les joueurs qui ont participé aux mêmes tournois
        for year_data in history_manager.tournament_history.values():
            for week_results in year_data.values():
                for result in week_results:
                    # Si le joueur principal a participé à ce tournoi
                    if any(p.full_name == main_player.full_name for p in result.all_results.keys()):
                        # Ajoute tous les autres participants
                        for player in result.all_results.keys():
                            if player.full_name != main_player.full_name:
                                active_players[player.full_name] = player
        
        print(f"Joueurs actifs identifiés: {len(active_players)}")
        return active_players
    
    def _save_active_players(self, active_players: Dict[str, Player], save_id: str) -> None:
        """Sauvegarde les joueurs actifs (format compressé)"""
        if not active_players:
            return
        
        filepath = self.player_data_dir / f"{save_id}_active_players"
        
        # Optimise les données des joueurs actifs
        optimized_data = {}
        for name, player in active_players.items():
            optimized_data[name] = PlayerDataOptimizer.optimize_player_data(
                player.to_dict(), "standard"
            )
        
        # Utilise la sérialisation optimisée
        SerializationUtils.save_to_file(optimized_data, filepath, SerializationFormat.MSGPACK_COMPRESSED)
    
    def _save_tournament_history_optimized(self, history_manager: HistoryManager, save_id: str) -> None:
        """Sauvegarde l'historique des tournois avec références optimisées"""
        history_data = {}
        
        for year, weeks_data in history_manager.tournament_history.items():
            history_data[str(year)] = {}
            for week, results in weeks_data.items():
                history_data[str(year)][str(week)] = []
                
                for result in results:
                    # Utilise des références au lieu des objets complets
                    optimized_result = {
                        "tournament_name": result.tournament_name,
                        "category": result.category.value,
                        "winner_ref": result.winner.full_name if result.winner else None,
                        "finalist_ref": result.finalist.full_name if result.finalist else None,
                        "semifinalists_refs": [p.full_name for p in result.semifinalists],
                        "quarterfinalists_refs": [p.full_name for p in result.quarterfinalists],
                        "results": {p.full_name: round_reached for p, round_reached in result.all_results.items()},
                        # Convertit match_results en références aussi
                        "match_results": [
                            {
                                "winner_ref": match.winner.full_name if match.winner else None,
                                "loser_ref": match.loser.full_name if match.loser else None,
                                "sets_won": match.sets_won,
                                "sets_lost": match.sets_lost
                            }
                            for match in result.match_results
                        ] if result.match_results else []
                    }
                    history_data[str(year)][str(week)].append(optimized_result)
        
        # Sauvegarde par année pour faciliter le chargement
        for year, year_data in history_data.items():
            filepath = self.tournament_dir / f"{save_id}_tournaments_{year}"
            SerializationUtils.save_to_file(year_data, filepath, SerializationFormat.MSGPACK_COMPRESSED)
    
    def _save_world_state(self, all_players: Dict[str, Player], save_id: str, 
                         exclude_active: Set[str]) -> None:
        """Sauvegarde l'état global des joueurs (données minimales)"""
        world_players = {}
        
        for name, player in all_players.items():
            if name not in exclude_active:
                # Données minimales pour les joueurs non-actifs
                world_players[name] = {
                    "first_name": player.first_name,
                    "last_name": player.last_name,
                    "country": player.country,
                    "gender": player.gender.value,
                    "elo": player.elo,
                    "atp_points": getattr(player.career, 'atp_points', 0),
                    "age": getattr(player.career, 'age', 25)
                }
        
        filepath = self.world_state_dir / f"{save_id}_world_players"
        
        # Utilise la sérialisation optimisée pour une compression maximale
        SerializationUtils.save_to_file(world_players, filepath, SerializationFormat.MSGPACK_COMPRESSED)
        
        print(f"Joueurs mondiaux sauvegardés: {len(world_players)}")
    
    def _save_main_metadata(self, save_id: str, current_week: int, current_year: int,
                           active_player_refs: Set[str], save_name: str, **kwargs) -> str:
        """Sauvegarde le fichier principal avec métadonnées et références"""
        filename = f"{save_id}.json"
        filepath = self.current_save_dir / filename
        
        metadata = {
            "save_id": save_id,
            "save_name": save_name,
            "save_date": datetime.now().isoformat(),
            "current_week": current_week,
            "current_year": current_year,
            "game_version": "2.1",
            "save_format": "enhanced_multi_file_v2",
            "playtime_hours": kwargs.get('playtime_hours', 0.0),
            "is_preliminary_complete": kwargs.get('is_preliminary_complete', False),
            "retirement_log": kwargs.get('retirement_log', []),
            
            # Références aux fichiers de données
            "data_files": {
                "main_player": f"{save_id}_main_player.json",
                "active_players": f"{save_id}_active_players.json.gz",
                "tournament_years": list(self._get_tournament_years(save_id)),
                "world_state": f"{save_id}_world_players.pkl.gz"
            },
            
            # Statistiques
            "stats": {
                "active_players_count": len(active_player_refs),
                "tournament_years": len(self._get_tournament_years(save_id))
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def _get_tournament_years(self, save_id: str) -> Set[str]:
        """Récupère les années pour lesquelles il y a des données de tournois"""
        years = set()
        for file in self.tournament_dir.glob(f"{save_id}_tournaments_*"):
            # Extrait l'année du nom de fichier (avant l'extension)
            filename_without_ext = file.name.split('.')[0]  # Retire toutes les extensions
            parts = filename_without_ext.split('_')
            if len(parts) >= 3:
                year = parts[-1]
                years.add(year)
        return years
    
    def _print_save_statistics(self, save_name: str) -> None:
        """Affiche les statistiques de la sauvegarde"""
        total_size = 0
        file_stats = {}
        
        # Calcule la taille de tous les fichiers de cette sauvegarde
        for directory in [self.current_save_dir, self.player_data_dir, 
                         self.tournament_dir, self.world_state_dir]:
            if directory and directory.exists():
                for file in directory.rglob("*"):
                    if file.is_file():
                        size = file.stat().st_size
                        total_size += size
                        # Utilise le chemin relatif depuis current_save_dir
                        relative_path = file.relative_to(self.current_save_dir)
                        file_stats[str(relative_path)] = size
        
        print(f"\nSTATISTIQUES DE SAUVEGARDE - {save_name}")
        print("=" * 60)
        print(f"Taille totale: {total_size / 1024:.1f} KB ({total_size:,} bytes)")
        print("\nDétail par fichier:")
        for filename, size in file_stats.items():
            print(f"  {filename}: {size / 1024:.1f} KB")
        print("=" * 60)
    
    def load_game_enhanced(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        Charge une sauvegarde optimisée
        
        Args:
            save_name: Nom du dossier de sauvegarde
        
        Returns:
            Dictionnaire avec toutes les données chargées
        """
        try:
            # Configure les répertoires pour cette sauvegarde
            self._setup_save_directories(save_name)
            
            # Trouve le fichier de métadonnées (il peut y en avoir plusieurs dans le dossier)
            metadata_files = list(self.current_save_dir.glob("*.json"))
            if not metadata_files:
                print(f"❌ Aucun fichier de métadonnées trouvé dans: {save_name}")
                return None
            
            # Prend le premier fichier .json trouvé (normalement il n'y en a qu'un)
            metadata_file = metadata_files[0]
            save_id = metadata_file.stem  # Nom du fichier sans extension
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            print(f"Chargement optimisé: {save_name}")
            
            # 2. Charge le joueur principal
            main_player = self._load_main_player(save_id)
            if not main_player:
                return None
            
            # 3. Charge les joueurs actifs
            active_players = self._load_active_players(save_id)
            
            # 4. Charge l'historique des tournois
            history_manager = self._load_tournament_history(save_id, metadata)
            
            # 5. Charge l'état du monde (lazy loading)
            world_players = self._load_world_state_lazy(save_id)
            
            # Combine toutes les données
            all_players = {**active_players, **world_players}
            all_players[main_player.full_name] = main_player
            
            return {
                "main_player": main_player,
                "all_players": all_players,
                "history_manager": history_manager,
                "metadata": metadata,
                "active_players": active_players
            }
            
        except Exception as e:
            print(f"Erreur chargement optimisé: {e}")
            return None
    
    def _load_main_player(self, save_id: str) -> Optional[Player]:
        """Charge le joueur principal"""
        filepath = self.player_data_dir / f"{save_id}_main_player.json"
        if not filepath.exists():
            print(f"Fichier joueur principal non trouvé")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Player.from_dict(data)
    
    def _load_active_players(self, save_id: str) -> Dict[str, Player]:
        """Charge les joueurs actifs"""
        # Cherche le fichier avec différentes extensions possibles
        for pattern in [f"{save_id}_active_players.*"]:
            files = list(self.player_data_dir.glob(pattern))
            if files:
                filepath = files[0]
                break
        else:
            return {}
        
        data = SerializationUtils.load_from_file(filepath)
        
        active_players = {}
        for name, player_data in data.items():
            # Reconstruit le joueur depuis les données optimisées
            player = self._reconstruct_player_from_optimized(player_data)
            active_players[name] = player
        
        print(f"Joueurs actifs chargés: {len(active_players)}")
        return active_players
    
    def _load_tournament_history(self, save_id: str, metadata: Dict) -> HistoryManager:
        """Charge l'historique des tournois"""
        history_manager = HistoryManager()
        
        tournament_years = metadata.get("data_files", {}).get("tournament_years", [])
        
        for year in tournament_years:
            # Cherche le fichier de tournois pour cette année
            pattern = f"{save_id}_tournaments_{year}.*"
            files = list(self.tournament_dir.glob(pattern))
            if files:
                filepath = files[0]
                year_data = SerializationUtils.load_from_file(filepath)
                
                # Reconstruit les objets TournamentResult avec références
                self._reconstruct_tournament_history(history_manager, int(year), year_data)
        
        return history_manager
    
    def _load_world_state_lazy(self, save_id: str) -> Dict[str, Player]:
        """Charge l'état du monde de manière paresseuse"""
        # Cherche le fichier d'état du monde
        pattern = f"{save_id}_world_players.*"
        files = list(self.world_state_dir.glob(pattern))
        if not files:
            return {}
        
        filepath = files[0]
        world_data = SerializationUtils.load_from_file(filepath)
        
        # Crée des objets Player minimalistes
        world_players = {}
        for name, data in world_data.items():
            player = self._create_minimal_player(data)
            world_players[name] = player
        
        print(f"État du monde chargé: {len(world_players)} joueurs")
        return world_players
    
    def _reconstruct_player_from_optimized(self, data: Dict) -> Player:
        """Reconstruit un joueur depuis des données optimisées"""
        # Utilise la méthode from_dict existante de Player si les données sont complètes
        if "career" in data and "physical" in data:
            return Player.from_dict(data)
        
        # Sinon, crée un joueur minimal et ajoute les données disponibles
        gender = Gender.MALE if data["gender"] == "m" else Gender.FEMALE
        player = Player(gender, data["first_name"], data["last_name"], data["country"])
        
        # Restaure les données disponibles
        if "stats" in data:
            player.stats = data["stats"]
        if "elo" in data:
            player.elo = data["elo"]
        if "atp_points" in data:
            player.career.atp_points = data["atp_points"]
        if "age" in data:
            player.career.age = data["age"]
        if "height" in data:
            player.physical.height = data["height"]
        if "dominant_hand" in data:
            player.physical.dominant_hand = data["dominant_hand"]
        
        return player
    
    def _create_minimal_player(self, data: Dict) -> Player:
        """Crée un joueur minimal depuis les données du monde"""
        gender = Gender.MALE if data["gender"] == "m" else Gender.FEMALE
        player = Player(gender, data["first_name"], data["last_name"], data["country"])
        player.elo = data.get("elo", 1500)
        player.career.atp_points = data.get("atp_points", 0)
        player.career.age = data.get("age", 25)
        
        return player
    
    def _reconstruct_tournament_history(self, history_manager: HistoryManager, 
                                      year: int, year_data: Dict) -> None:
        """Reconstruit l'historique des tournois avec des références"""
        for week_str, tournaments in year_data.items():
            week = int(week_str)
            
            for tournament_data in tournaments:
                # Trouve la catégorie
                category = None
                for cat in TournamentCategory:
                    if cat.value == tournament_data["category"]:
                        category = cat
                        break
                
                if not category:
                    continue
                
                # Crée des joueurs fictifs pour les références (ils seront remplacés lors du chargement complet)
                winner = None
                finalist = None
                if tournament_data.get("winner_ref"):
                    winner = self._create_reference_player(tournament_data["winner_ref"])
                if tournament_data.get("finalist_ref"):
                    finalist = self._create_reference_player(tournament_data["finalist_ref"])
                
                semifinalists = [self._create_reference_player(ref) for ref in tournament_data.get("semifinalists_refs", [])]
                quarterfinalists = [self._create_reference_player(ref) for ref in tournament_data.get("quarterfinalists_refs", [])]
                
                # Reconstruit all_results avec des joueurs de référence
                all_results = {}
                for player_name, round_reached in tournament_data.get("results", {}).items():
                    ref_player = self._create_reference_player(player_name)
                    all_results[ref_player] = round_reached
                
                # Reconstruit match_results avec des références de joueurs
                match_results = []
                for match_data in tournament_data.get("match_results", []):
                    if isinstance(match_data, dict) and "winner_ref" in match_data:
                        # Nouveau format avec références
                        from ..entities.tournament import MatchResult
                        winner_ref = self._create_reference_player(match_data["winner_ref"]) if match_data.get("winner_ref") else None
                        loser_ref = self._create_reference_player(match_data["loser_ref"]) if match_data.get("loser_ref") else None
                        if winner_ref and loser_ref:
                            match_result = MatchResult(
                                winner=winner_ref,
                                loser=loser_ref,
                                sets_won=match_data.get("sets_won", 2),
                                sets_lost=match_data.get("sets_lost", 0)
                            )
                            match_results.append(match_result)
                    # Si c'est l'ancien format, on l'ignore (pas sérialisable de toute façon)
                
                # Crée le TournamentResult
                tournament_result = TournamentResult(
                    tournament_name=tournament_data["tournament_name"],
                    category=category,
                    winner=winner,
                    finalist=finalist,
                    semifinalists=semifinalists,
                    quarterfinalists=quarterfinalists,
                    all_results=all_results,
                    match_results=match_results
                )
                
                # Ajoute à l'historique
                history_manager.tournament_history[year][week].append(tournament_result)
    
    def _create_reference_player(self, player_name: str) -> Player:
        """Crée un joueur de référence minimal"""
        # Cache les joueurs de référence pour éviter les doublons
        if player_name in self._player_cache:
            return self._player_cache[player_name]
        
        # Parse le nom (assume format "Prénom_Nom")
        parts = player_name.split('_', 1) if '_' in player_name else player_name.split(' ', 1)
        first_name = parts[0] if parts else "Unknown"
        last_name = parts[1] if len(parts) > 1 else "Player"
        
        # Crée un joueur minimal
        player = Player(Gender.MALE, first_name, last_name, "Unknown")
        self._player_cache[player_name] = player
        
        return player
    
    def list_enhanced_saves(self) -> List[Dict[str, Any]]:
        """Liste les sauvegardes optimisées disponibles"""
        saves = []
        
        # Parcourt tous les dossiers dans le répertoire de base
        for save_dir in self.base_save_directory.iterdir():
            if not save_dir.is_dir():
                continue
                
            # Cherche un fichier de métadonnées dans le dossier
            metadata_files = list(save_dir.glob("*.json"))
            if not metadata_files:
                continue
                
            try:
                metadata_file = metadata_files[0]  # Prend le premier fichier .json
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Vérifie que c'est une sauvegarde optimisée (nouvelle ou ancienne version)
                save_format = metadata.get("save_format", "")
                if save_format in ["enhanced_multi_file", "enhanced_multi_file_v2"]:
                    save_info = {
                        "save_name": metadata.get("save_name", save_dir.name),
                        "directory_name": save_dir.name,
                        "save_id": metadata.get("save_id"),
                        "save_date": metadata.get("save_date"),
                        "current_week": metadata.get("current_week"),
                        "current_year": metadata.get("current_year"),
                        "version": metadata.get("game_version"),
                        "stats": metadata.get("stats", {}),
                        "playtime": metadata.get("playtime_hours", 0.0),
                        "format_version": save_format
                    }
                    saves.append(save_info)
                    
            except Exception as e:
                continue
        
        # Trie par date de sauvegarde
        saves.sort(key=lambda x: x["save_date"] if x["save_date"] else "", reverse=True)
        return saves
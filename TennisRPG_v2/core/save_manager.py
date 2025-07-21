"""
Gestionnaire de sauvegarde et chargement - Save/Load System
"""
import json
import pickle
import os
from typing import Dict, Optional, Any, List
from dataclasses import asdict
from datetime import datetime

from ..entities.player import Player


class GameState:
    """État complet d'une partie"""
    
    def __init__(self):
        self.main_player: Optional[Player] = None
        self.all_players: Dict[str, Player] = {}
        self.current_week: int = 1
        self.current_year: int = 2024
        self.is_preliminary_complete: bool = False
        self.save_date: str = ""
        self.game_version: str = "2.0"
        self.playtime_hours: float = 0.0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'état en dictionnaire pour JSON"""
        return {
            "main_player": self.main_player.to_dict() if self.main_player else None,
            "all_players": {name: player.to_dict() for name, player in self.all_players.items()},
            "current_week": self.current_week,
            "current_year": self.current_year,
            "is_preliminary_complete": self.is_preliminary_complete,
            "save_date": self.save_date,
            "game_version": self.game_version,
            "playtime_hours": self.playtime_hours
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Crée un GameState depuis un dictionnaire"""
        state = cls()
        
        # Charge le joueur principal
        if data.get("main_player"):
            state.main_player = Player.from_dict(data["main_player"])
        
        # Charge tous les joueurs
        state.all_players = {
            name: Player.from_dict(player_data) 
            for name, player_data in data.get("all_players", {}).items()
        }
        
        # Charge les autres propriétés
        state.current_week = data.get("current_week", 1)
        state.current_year = data.get("current_year", 2024)
        state.is_preliminary_complete = data.get("is_preliminary_complete", False)
        state.save_date = data.get("save_date", "")
        state.game_version = data.get("game_version", "2.0")
        state.playtime_hours = data.get("playtime_hours", 0.0)
        
        return state


class SaveManager:
    """Gestionnaire de sauvegarde et chargement"""
    
    def __init__(self, save_directory: str = "saves"):
        """
        Initialise le gestionnaire de sauvegarde
        
        Args:
            save_directory: Répertoire où stocker les sauvegardes
        """
        self.save_directory = save_directory
        self._ensure_save_directory()
        
    def _ensure_save_directory(self) -> None:
        """S'assure que le répertoire de sauvegarde existe"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_game(self, game_state: GameState, filename: str = None) -> bool:
        """
        Sauvegarde l'état du jeu
        
        Args:
            game_state: État du jeu à sauvegarder
            filename: Nom du fichier (optionnel)
            
        Returns:
            True si la sauvegarde a réussi
        """
        try:
            if not filename:
                # Génère un nom de fichier automatique
                player_name = "unknown"
                if game_state.main_player:
                    player_name = f"{game_state.main_player.first_name}_{game_state.main_player.last_name}"
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{player_name}_{timestamp}.json"
            
            # Assure l'extension .json
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join(self.save_directory, filename)
            
            # Met à jour la date de sauvegarde
            game_state.save_date = datetime.now().isoformat()
            
            # Sauvegarde en JSON pour la lisibilité
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_state.to_dict(), f, indent=2, ensure_ascii=False)
            
            print(f"✅ Jeu sauvegardé: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_game(self, filename: str) -> Optional[GameState]:
        """
        Charge l'état du jeu
        
        Args:
            filename: Nom du fichier à charger
            
        Returns:
            GameState chargé ou None si échec
        """
        try:
            # Assure l'extension .json
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join(self.save_directory, filename)
            
            if not os.path.exists(filepath):
                print(f"❌ Fichier de sauvegarde non trouvé: {filename}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            game_state = GameState.from_dict(data)
            print(f"✅ Jeu chargé: {filename}")
            return game_state
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return None
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """
        Liste toutes les sauvegardes disponibles
        
        Returns:
            Liste des informations de sauvegarde
        """
        saves = []
        
        if not os.path.exists(self.save_directory):
            return saves
        
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.json'):
                filepath = os.path.join(self.save_directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extrait les informations importantes
                    save_info = {
                        "filename": filename,
                        "player_name": "Inconnu",
                        "week": data.get("current_week", 0),
                        "year": data.get("current_year", 0),
                        "save_date": data.get("save_date", ""),
                        "version": data.get("game_version", "1.0"),
                        "playtime": data.get("playtime_hours", 0.0),
                        "file_size": os.path.getsize(filepath)
                    }
                    
                    # Nom du joueur principal
                    if data.get("main_player"):
                        main_player_data = data["main_player"]
                        first_name = main_player_data.get("first_name", "")
                        last_name = main_player_data.get("last_name", "")
                        save_info["player_name"] = f"{first_name} {last_name}".strip()
                    
                    saves.append(save_info)
                    
                except Exception as e:
                    print(f"⚠️  Erreur lecture {filename}: {e}")
                    continue
        
        # Trie par date de sauvegarde (plus récent en premier)
        saves.sort(key=lambda x: x["save_date"], reverse=True)
        return saves
    
    def delete_save(self, filename: str) -> bool:
        """
        Supprime une sauvegarde
        
        Args:
            filename: Nom du fichier à supprimer
            
        Returns:
            True si la suppression a réussi
        """
        try:
            if not filename.endswith('.json'):
                filename += '.json'
                
            filepath = os.path.join(self.save_directory, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✅ Sauvegarde supprimée: {filename}")
                return True
            else:
                print(f"❌ Fichier non trouvé: {filename}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False
    
    def backup_save(self, filename: str) -> bool:
        """
        Crée une copie de sauvegarde
        
        Args:
            filename: Nom du fichier à sauvegarder
            
        Returns:
            True si la copie a réussi
        """
        try:
            if not filename.endswith('.json'):
                filename += '.json'
            
            source_path = os.path.join(self.save_directory, filename)
            backup_name = filename.replace('.json', '_backup.json')
            backup_path = os.path.join(self.save_directory, backup_name)
            
            if os.path.exists(source_path):
                import shutil
                shutil.copy2(source_path, backup_path)
                print(f"✅ Copie créée: {backup_name}")
                return True
            else:
                print(f"❌ Fichier source non trouvé: {filename}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la copie: {e}")
            return False
    
    def display_saves_menu(self) -> None:
        """Affiche le menu des sauvegardes"""
        saves = self.list_saves()
        
        if not saves:
            print("\n📁 Aucune sauvegarde trouvée")
            return
        
        print("\n💾 SAUVEGARDES DISPONIBLES:")
        print("=" * 70)
        print(f"{'#':<3} {'Joueur':<20} {'Semaine':<8} {'Année':<6} {'Date sauvegarde':<19}")
        print("-" * 70)
        
        for i, save in enumerate(saves, 1):
            save_date = save["save_date"][:19] if save["save_date"] else "Inconnue"
            print(f"{i:<3} {save['player_name']:<20} {save['week']:<8} {save['year']:<6} {save_date}")
        
        print("=" * 70)
    
    def get_save_by_index(self, index: int) -> Optional[str]:
        """
        Retourne le nom de fichier d'une sauvegarde par son index
        
        Args:
            index: Index de la sauvegarde (1-based)
            
        Returns:
            Nom du fichier ou None
        """
        saves = self.list_saves()
        if 1 <= index <= len(saves):
            return saves[index - 1]["filename"]
        return None

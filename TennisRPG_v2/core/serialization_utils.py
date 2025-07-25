"""
Utilitaires de sérialisation pour optimiser les sauvegardes
Supporte JSON, Pickle, MessagePack et compression
"""
import json
import pickle
import gzip
from typing import Any, Dict, Optional
from pathlib import Path
from enum import Enum

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False


class SerializationFormat(Enum):
    """Formats de sérialisation supportés"""
    JSON = "json"
    JSON_COMPRESSED = "json.gz"
    PICKLE = "pkl"
    PICKLE_COMPRESSED = "pkl.gz"
    MSGPACK = "msgpack"
    MSGPACK_COMPRESSED = "msgpack.gz"


class SerializationUtils:
    """Utilitaires pour la sérialisation optimisée"""
    
    @staticmethod
    def get_best_format_for_data(data: Any, size_threshold: int = 1024) -> SerializationFormat:
        """
        Détermine le meilleur format selon le type et la taille des données
        
        Args:
            data: Données à sérialiser
            size_threshold: Seuil en bytes pour activer la compression
            
        Returns:
            Format recommandé
        """
        # Estime la taille avec JSON pour référence
        json_size = len(json.dumps(data, default=str).encode('utf-8'))
        
        # Pour les petites données, JSON non compressé
        if json_size < size_threshold:
            return SerializationFormat.JSON
        
        # Pour les données moyennes, JSON compressé
        if json_size < 50000:  # 50KB
            return SerializationFormat.JSON_COMPRESSED
        
        # Pour les grandes données, privilégier la performance
        if MSGPACK_AVAILABLE:
            return SerializationFormat.MSGPACK_COMPRESSED
        else:
            return SerializationFormat.PICKLE_COMPRESSED
    
    @staticmethod
    def serialize(data: Any, format_type: SerializationFormat) -> bytes:
        """
        Sérialise les données dans le format spécifié
        
        Args:
            data: Données à sérialiser
            format_type: Format de sérialisation
            
        Returns:
            Données sérialisées
        """
        if format_type == SerializationFormat.JSON:
            return json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
        
        elif format_type == SerializationFormat.JSON_COMPRESSED:
            json_data = json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
            return gzip.compress(json_data)
        
        elif format_type == SerializationFormat.PICKLE:
            return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        
        elif format_type == SerializationFormat.PICKLE_COMPRESSED:
            pickle_data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            return gzip.compress(pickle_data)
        
        elif format_type == SerializationFormat.MSGPACK:
            if not MSGPACK_AVAILABLE:
                raise ImportError("msgpack not available")
            return msgpack.packb(data, use_bin_type=True)
        
        elif format_type == SerializationFormat.MSGPACK_COMPRESSED:
            if not MSGPACK_AVAILABLE:
                raise ImportError("msgpack not available")
            msgpack_data = msgpack.packb(data, use_bin_type=True)
            return gzip.compress(msgpack_data)
        
        else:
            raise ValueError(f"Format non supporté: {format_type}")
    
    @staticmethod
    def deserialize(data: bytes, format_type: SerializationFormat) -> Any:
        """
        Désérialise les données depuis le format spécifié
        
        Args:
            data: Données sérialisées
            format_type: Format de sérialisation
            
        Returns:
            Données désérialisées
        """
        if format_type == SerializationFormat.JSON:
            return json.loads(data.decode('utf-8'))
        
        elif format_type == SerializationFormat.JSON_COMPRESSED:
            json_data = gzip.decompress(data)
            return json.loads(json_data.decode('utf-8'))
        
        elif format_type == SerializationFormat.PICKLE:
            return pickle.loads(data)
        
        elif format_type == SerializationFormat.PICKLE_COMPRESSED:
            pickle_data = gzip.decompress(data)
            return pickle.loads(pickle_data)
        
        elif format_type == SerializationFormat.MSGPACK:
            if not MSGPACK_AVAILABLE:
                raise ImportError("msgpack not available")
            return msgpack.unpackb(data, raw=False)
        
        elif format_type == SerializationFormat.MSGPACK_COMPRESSED:
            if not MSGPACK_AVAILABLE:
                raise ImportError("msgpack not available")
            msgpack_data = gzip.decompress(data)
            return msgpack.unpackb(msgpack_data, raw=False)
        
        else:
            raise ValueError(f"Format non supporté: {format_type}")
    
    @staticmethod
    def save_to_file(data: Any, filepath: Path, format_type: Optional[SerializationFormat] = None) -> Dict[str, Any]:
        """
        Sauvegarde les données dans un fichier avec le format optimal
        
        Args:
            data: Données à sauvegarder
            filepath: Chemin du fichier
            format_type: Format forcé (optionnel)
            
        Returns:
            Métadonnées de la sauvegarde
        """
        if format_type is None:
            format_type = SerializationUtils.get_best_format_for_data(data)
        
        # Ajoute l'extension appropriée
        if not str(filepath).endswith(f".{format_type.value}"):
            filepath = filepath.with_suffix(f".{format_type.value}")
        
        # Sérialise et sauvegarde
        serialized_data = SerializationUtils.serialize(data, format_type)
        
        with open(filepath, 'wb') as f:
            f.write(serialized_data)
        
        # Retourne les métadonnées
        return {
            "filepath": str(filepath),
            "format": format_type.value,
            "size_bytes": len(serialized_data),
            "size_kb": len(serialized_data) / 1024
        }
    
    @staticmethod
    def load_from_file(filepath: Path) -> Any:
        """
        Charge les données depuis un fichier en détectant automatiquement le format
        
        Args:
            filepath: Chemin du fichier
            
        Returns:
            Données chargées
        """
        # Détecte le format depuis l'extension
        suffix = filepath.suffix.lower()
        if suffix == '.json':
            format_type = SerializationFormat.JSON
        elif suffix == '.gz' and filepath.stem.endswith('.json'):
            format_type = SerializationFormat.JSON_COMPRESSED
        elif suffix == '.pkl':
            format_type = SerializationFormat.PICKLE
        elif suffix == '.gz' and filepath.stem.endswith('.pkl'):
            format_type = SerializationFormat.PICKLE_COMPRESSED
        elif suffix == '.msgpack':
            format_type = SerializationFormat.MSGPACK
        elif suffix == '.gz' and filepath.stem.endswith('.msgpack'):
            format_type = SerializationFormat.MSGPACK_COMPRESSED
        else:
            raise ValueError(f"Format de fichier non reconnu: {filepath}")
        
        # Charge et désérialise
        with open(filepath, 'rb') as f:
            data = f.read()
        
        return SerializationUtils.deserialize(data, format_type)
    
    @staticmethod
    def compare_formats(data: Any) -> Dict[str, Dict[str, Any]]:
        """
        Compare les différents formats pour des données données
        
        Args:
            data: Données à analyser
            
        Returns:
            Dictionnaire avec les statistiques par format
        """
        results = {}
        
        for format_type in SerializationFormat:
            if format_type in [SerializationFormat.MSGPACK, SerializationFormat.MSGPACK_COMPRESSED] and not MSGPACK_AVAILABLE:
                continue
            
            try:
                serialized = SerializationUtils.serialize(data, format_type)
                results[format_type.value] = {
                    "size_bytes": len(serialized),
                    "size_kb": len(serialized) / 1024,
                    "compression_ratio": len(json.dumps(data, default=str).encode('utf-8')) / len(serialized)
                }
            except Exception as e:
                results[format_type.value] = {"error": str(e)}
        
        return results


class PlayerDataOptimizer:
    """Optimiseur spécialisé pour les données de joueurs"""
    
    @staticmethod
    def optimize_player_data(player_dict: Dict[str, Any], level: str = "full") -> Dict[str, Any]:
        """
        Optimise les données d'un joueur selon le niveau requis
        
        Args:
            player_dict: Données complètes du joueur
            level: Niveau d'optimisation ("minimal", "standard", "full")
            
        Returns:
            Données optimisées
        """
        if level == "minimal":
            return {
                "first_name": player_dict["first_name"],
                "last_name": player_dict["last_name"],
                "country": player_dict["country"],
                "gender": player_dict["gender"],
                "elo": player_dict.get("elo", 1500),
                "atp_points": player_dict.get("career", {}).get("atp_points", 0)
            }
        
        elif level == "standard":
            optimized = PlayerDataOptimizer.optimize_player_data(player_dict, "minimal")
            optimized.update({
                "stats": player_dict.get("stats", {}),
                "age": player_dict.get("career", {}).get("age", 25),
                "height": player_dict.get("physical", {}).get("height", 180),
                "dominant_hand": player_dict.get("physical", {}).get("dominant_hand", "Droite")
            })
            return optimized
        
        else:  # "full"
            return player_dict
    
    @staticmethod
    def batch_optimize_players(players_dict: Dict[str, Dict[str, Any]], 
                              active_players: set, 
                              main_player: str) -> Dict[str, Dict[str, Any]]:
        """
        Optimise un batch de joueurs selon leur importance
        
        Args:
            players_dict: Dictionnaire de tous les joueurs
            active_players: Set des joueurs actifs
            main_player: Nom du joueur principal
            
        Returns:
            Dictionnaire optimisé
        """
        optimized = {}
        
        for name, player_data in players_dict.items():
            if name == main_player:
                level = "full"
            elif name in active_players:
                level = "standard"
            else:
                level = "minimal"
            
            optimized[name] = PlayerDataOptimizer.optimize_player_data(player_data, level)
        
        return optimized


def benchmark_serialization(data: Any, iterations: int = 10) -> Dict[str, Dict[str, float]]:
    """
    Benchmark des performances de sérialisation/désérialisation
    
    Args:
        data: Données à tester
        iterations: Nombre d'itérations pour le benchmark
        
    Returns:
        Résultats du benchmark
    """
    import time
    
    results = {}
    
    for format_type in SerializationFormat:
        if format_type in [SerializationFormat.MSGPACK, SerializationFormat.MSGPACK_COMPRESSED] and not MSGPACK_AVAILABLE:
            continue
        
        try:
            # Test de sérialisation
            start_time = time.time()
            for _ in range(iterations):
                serialized = SerializationUtils.serialize(data, format_type)
            serialize_time = (time.time() - start_time) / iterations
            
            # Test de désérialisation
            start_time = time.time()
            for _ in range(iterations):
                deserialized = SerializationUtils.deserialize(serialized, format_type)
            deserialize_time = (time.time() - start_time) / iterations
            
            results[format_type.value] = {
                "serialize_time_ms": serialize_time * 1000,
                "deserialize_time_ms": deserialize_time * 1000,
                "total_time_ms": (serialize_time + deserialize_time) * 1000,
                "size_bytes": len(serialized)
            }
            
        except Exception as e:
            results[format_type.value] = {"error": str(e)}
    
    return results
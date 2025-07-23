"""
Cache Manager - Optimizes performance by caching expensive calculations
Addresses performance issues identified in the refactoring report
"""
import time
import hashlib
from typing import Dict, Any, Optional, Callable, Tuple
from functools import wraps
from ..utils.error_handler import logger, safe_calculation


class CacheManager:
    """Manages caching for expensive calculations"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.hit_count = 0
        self.miss_count = 0
        
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a unique cache key"""
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired"""
        return time.time() - timestamp > self.ttl
        
    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
            
    def _evict_oldest(self) -> None:
        """Evict oldest entries when cache is full"""
        if len(self.cache) >= self.max_size:
            # Remove 20% of oldest entries
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            
            evict_count = max(1, self.max_size // 5)
            for key, _ in sorted_items[:evict_count]:
                del self.cache[key]
                
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if not self._is_expired(timestamp):
                self.hit_count += 1
                return value
            else:
                del self.cache[key]
                
        self.miss_count += 1
        return None
        
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self._cleanup_expired()
        self._evict_oldest()
        
        self.cache[key] = (value, time.time())
        
    def invalidate(self, pattern: str = None) -> None:
        """Invalidate cache entries matching pattern"""
        if pattern is None:
            self.cache.clear()
        else:
            keys_to_remove = [
                key for key in self.cache.keys()
                if pattern in key
            ]
            for key in keys_to_remove:
                del self.cache[key]
                
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': round(hit_rate, 2),
            'ttl': self.ttl
        }


# Global cache instances
elo_cache = CacheManager(max_size=500, ttl=600)  # 10 minutes for ELO
ranking_cache = CacheManager(max_size=200, ttl=120)  # 2 minutes for rankings
tournament_cache = CacheManager(max_size=100, ttl=1800)  # 30 minutes for tournaments


def cached_elo_calculation(func: Callable) -> Callable:
    """Decorator for caching ELO calculations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key
        key = elo_cache._generate_key(func.__name__, args, kwargs)
        
        # Try to get from cache
        cached_result = elo_cache.get(key)
        if cached_result is not None:
            logger.debug(f"ELO cache hit for {func.__name__}")
            return cached_result
            
        # Calculate and cache result
        try:
            result = func(*args, **kwargs)
            elo_cache.set(key, result)
            logger.debug(f"ELO calculated and cached for {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"ELO calculation failed: {str(e)}")
            raise
            
    return wrapper


def cached_ranking_calculation(func: Callable) -> Callable:
    """Decorator for caching ranking calculations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key
        key = ranking_cache._generate_key(func.__name__, args, kwargs)
        
        # Try to get from cache
        cached_result = ranking_cache.get(key)
        if cached_result is not None:
            logger.debug(f"Ranking cache hit for {func.__name__}")
            return cached_result
            
        # Calculate and cache result
        try:
            result = func(*args, **kwargs)
            ranking_cache.set(key, result)
            logger.debug(f"Ranking calculated and cached for {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Ranking calculation failed: {str(e)}")
            raise
            
    return wrapper


def cached_tournament_data(func: Callable) -> Callable:
    """Decorator for caching tournament data"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key
        key = tournament_cache._generate_key(func.__name__, args, kwargs)
        
        # Try to get from cache
        cached_result = tournament_cache.get(key)
        if cached_result is not None:
            logger.debug(f"Tournament cache hit for {func.__name__}")
            return cached_result
            
        # Calculate and cache result
        try:
            result = func(*args, **kwargs)
            tournament_cache.set(key, result)
            logger.debug(f"Tournament data cached for {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Tournament data retrieval failed: {str(e)}")
            raise
            
    return wrapper


class LazyLoader:
    """Implements lazy loading for non-critical data"""
    
    def __init__(self):
        self._loaded_data: Dict[str, Any] = {}
        self._loaders: Dict[str, Callable] = {}
        
    def register_loader(self, key: str, loader_func: Callable) -> None:
        """Register a loader function for a specific data key"""
        self._loaders[key] = loader_func
        
    def get_data(self, key: str) -> Any:
        """Get data, loading it lazily if needed"""
        if key not in self._loaded_data:
            if key in self._loaders:
                try:
                    self._loaded_data[key] = self._loaders[key]()
                    logger.debug(f"Lazy loaded data for key: {key}")
                except Exception as e:
                    logger.error(f"Failed to lazy load {key}: {str(e)}")
                    return None
            else:
                logger.warning(f"No loader registered for key: {key}")
                return None
                
        return self._loaded_data.get(key)
        
    def preload(self, keys: list) -> None:
        """Preload specific data keys"""
        for key in keys:
            self.get_data(key)
            
    def clear(self, key: str = None) -> None:
        """Clear loaded data"""
        if key is None:
            self._loaded_data.clear()
        elif key in self._loaded_data:
            del self._loaded_data[key]


# Global lazy loader instance
lazy_loader = LazyLoader()


def invalidate_player_caches(player_name: str) -> None:
    """Invalidate all caches related to a specific player"""
    elo_cache.invalidate(player_name)
    ranking_cache.invalidate(player_name)
    logger.info(f"Caches invalidated for player: {player_name}")


def invalidate_all_caches() -> None:
    """Invalidate all caches"""
    elo_cache.invalidate()
    ranking_cache.invalidate()
    tournament_cache.invalidate()
    lazy_loader.clear()
    logger.info("All caches invalidated")


def get_cache_statistics() -> Dict[str, Any]:
    """Get statistics for all caches"""
    return {
        'elo_cache': elo_cache.get_stats(),
        'ranking_cache': ranking_cache.get_stats(),
        'tournament_cache': tournament_cache.get_stats(),
        'lazy_loader_items': len(lazy_loader._loaded_data)
    }


def optimize_cache_settings(performance_mode: str = "balanced") -> None:
    """Optimize cache settings based on performance mode"""
    global elo_cache, ranking_cache, tournament_cache
    
    if performance_mode == "memory_saver":
        # Smaller caches, shorter TTL
        elo_cache.max_size = 200
        elo_cache.ttl = 300
        ranking_cache.max_size = 100
        ranking_cache.ttl = 60
        tournament_cache.max_size = 50
        tournament_cache.ttl = 900
        
    elif performance_mode == "performance":
        # Larger caches, longer TTL
        elo_cache.max_size = 1000
        elo_cache.ttl = 1200
        ranking_cache.max_size = 500
        ranking_cache.ttl = 300
        tournament_cache.max_size = 200
        tournament_cache.ttl = 3600
        
    # balanced mode uses default settings
    
    logger.info(f"Cache settings optimized for {performance_mode} mode")
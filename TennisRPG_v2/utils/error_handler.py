"""
Centralized Error Handler
Provides consistent error handling and logging across the application
"""
import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps

from ..exceptions import (
    TennisRPGException, GameStateException, PlayerException,
    TournamentException, RankingException, SaveLoadException,
    ValidationException, NetworkException, ConfigurationException,
    PerformanceException
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tennisrpg.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling and recovery"""
    
    @staticmethod
    def handle_exception(exception: Exception, context: str = "") -> None:
        """Handle and log exceptions with context"""
        error_msg = f"Error in {context}: {str(exception)}"
        
        if isinstance(exception, TennisRPGException):
            logger.error(error_msg)
        else:
            logger.error(f"Unexpected {error_msg}")
            logger.debug(traceback.format_exc())
            
    @staticmethod
    def safe_execute(func: Callable, *args, default_return: Any = None, 
                    context: str = "", **kwargs) -> Any:
        """Safely execute a function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_exception(e, context or func.__name__)
            return default_return
            
    @staticmethod
    def validate_player_data(player_data: dict) -> None:
        """Validate player data integrity"""
        required_fields = ['name', 'nationality']
        
        for field in required_fields:
            if field not in player_data or not player_data[field]:
                raise ValidationException(f"Missing required field: {field}")
                
        if len(player_data['nationality']) != 3:
            raise ValidationException("Nationality must be 3 characters")
            
    @staticmethod
    def validate_game_state(game_state) -> None:
        """Validate game state integrity"""
        if not hasattr(game_state, 'main_player') or game_state.main_player is None:
            raise GameStateException("Main player is required")
            
        if not hasattr(game_state, 'current_week') or game_state.current_week < 1:
            raise GameStateException("Invalid current week")
            
        if not hasattr(game_state, 'current_year') or game_state.current_year < 2020:
            raise GameStateException("Invalid current year")


def error_boundary(exception_type: type = Exception, 
                  default_return: Any = None,
                  reraise: bool = False):
    """Decorator for creating error boundaries around functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_type as e:
                ErrorHandler.handle_exception(e, func.__name__)
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def safe_file_operation(func: Callable) -> Callable:
    """Decorator for safe file operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            raise SaveLoadException(f"File not found: {str(e)}")
        except PermissionError as e:
            raise SaveLoadException(f"Permission denied: {str(e)}")
        except OSError as e:
            raise SaveLoadException(f"File system error: {str(e)}")
    return wrapper


def safe_calculation(func: Callable) -> Callable:
    """Decorator for safe mathematical calculations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ZeroDivisionError:
            raise RankingException("Division by zero in calculation")
        except ValueError as e:
            raise RankingException(f"Invalid value in calculation: {str(e)}")
        except OverflowError:
            raise PerformanceException("Calculation overflow - values too large")
    return wrapper


def tournament_operation(func: Callable) -> Callable:
    """Decorator for tournament operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            raise TournamentException(f"Missing tournament data: {str(e)}")
        except IndexError as e:
            raise TournamentException(f"Invalid tournament index: {str(e)}")
        except Exception as e:
            raise TournamentException(f"Tournament operation failed: {str(e)}")
    return wrapper


def player_operation(func: Callable) -> Callable:
    """Decorator for player operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError as e:
            raise PlayerException(f"Invalid player attribute: {str(e)}")
        except ValueError as e:
            raise PlayerException(f"Invalid player value: {str(e)}")
        except Exception as e:
            raise PlayerException(f"Player operation failed: {str(e)}")
    return wrapper


# Recovery strategies
class ErrorRecovery:
    """Error recovery strategies"""
    
    @staticmethod
    def recover_corrupted_save(save_path: str) -> bool:
        """Attempt to recover a corrupted save file"""
        try:
            # Try to create a backup of the corrupted file
            import shutil
            backup_path = f"{save_path}.corrupted.backup"
            shutil.copy2(save_path, backup_path)
            logger.info(f"Corrupted save backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup corrupted save: {str(e)}")
            return False
            
    @staticmethod
    def reset_player_stats(player) -> bool:
        """Reset player stats to safe defaults"""
        try:
            safe_stats = {
                'forehand': 50, 'backhand': 50, 'serve': 50, 'volley': 50,
                'return': 50, 'speed': 50, 'endurance': 50, 'mental': 50
            }
            
            for stat, value in safe_stats.items():
                if hasattr(player, stat):
                    setattr(player, stat, value)
                    
            logger.info(f"Reset stats for player: {player.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset player stats: {str(e)}")
            return False
            
    @staticmethod
    def rebuild_rankings(ranking_manager) -> bool:
        """Rebuild corrupted rankings"""
        try:
            if hasattr(ranking_manager, 'rebuild_from_scratch'):
                ranking_manager.rebuild_from_scratch()
                logger.info("Rankings rebuilt successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to rebuild rankings: {str(e)}")
            return False
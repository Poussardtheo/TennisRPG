"""
Interfaces and abstractions for component decoupling
Defines contracts for the various game components to reduce coupling
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class IGameUI(ABC):
    """Interface for game user interface components"""
    
    @abstractmethod
    def display_welcome(self) -> None:
        """Display welcome message"""
        pass
    
    @abstractmethod
    def display_weekly_header(self, week: int, year: int, player: Any, ranking_manager: Any) -> None:
        """Display weekly header information"""
        pass
    
    @abstractmethod
    def display_main_menu(self) -> None:
        """Display main game menu"""
        pass
    
    @abstractmethod
    def get_user_input(self) -> str:
        """Get user input"""
        pass
    
    @abstractmethod
    def get_player_creation_data(self) -> Dict[str, Any]:
        """Get player creation data from user"""
        pass


class IGameState(ABC):
    """Interface for game state management"""
    
    @abstractmethod
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current game state"""
        pass
    
    @abstractmethod
    def is_managers_initialized(self) -> bool:
        """Check if managers are initialized"""
        pass
    
    @abstractmethod
    def start_session_timing(self) -> None:
        """Start session timing"""
        pass


class IGameController(ABC):
    """Interface for game flow control"""
    
    @abstractmethod
    def start_new_game(self) -> None:
        """Start a new game"""
        pass
    
    @abstractmethod
    def load_game_from_entry(self) -> bool:
        """Load game from entry menu"""
        pass
    
    @abstractmethod
    def _main_game_loop(self) -> None:
        """Main game loop"""
        pass
    
    @abstractmethod
    def _handle_user_action(self, action: str) -> None:
        """Handle user action"""
        pass


class IStateObserver(ABC):
    """Observer interface for state changes"""
    
    @abstractmethod
    def on_state_changed(self, state_type: str, old_value: Any, new_value: Any) -> None:
        """Called when state changes"""
        pass


class IStateSubject(ABC):
    """Subject interface for state management"""
    
    @abstractmethod
    def add_observer(self, observer: IStateObserver) -> None:
        """Add state observer"""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: IStateObserver) -> None:
        """Remove state observer"""
        pass
    
    @abstractmethod
    def notify_observers(self, state_type: str, old_value: Any, new_value: Any) -> None:
        """Notify all observers"""
        pass


class IManager(ABC):
    """Base interface for all game managers"""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the manager"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup manager resources"""
        pass


class ITournamentManager(IManager):
    """Interface for tournament management"""
    
    @abstractmethod
    def get_available_tournaments(self, week: int, year: int) -> List[Any]:
        """Get available tournaments for a given week"""
        pass
    
    @abstractmethod
    def register_player(self, tournament_id: str, player: Any) -> bool:
        """Register player for tournament"""
        pass


class IRankingManager(IManager):
    """Interface for ranking management"""
    
    @abstractmethod
    def update_rankings(self) -> None:
        """Update player rankings"""
        pass
    
    @abstractmethod
    def get_player_ranking(self, player: Any) -> int:
        """Get player's current ranking"""
        pass


class IPlayerGenerator(IManager):
    """Interface for player generation"""
    
    @abstractmethod
    def generate_players(self, count: int) -> List[Any]:
        """Generate specified number of players"""
        pass
    
    @abstractmethod
    def generate_player_pool(self) -> Dict[str, Any]:
        """Generate complete player pool"""
        pass


class IActivityManager(IManager):
    """Interface for weekly activity management"""
    
    @abstractmethod
    def process_weekly_activities(self, player: Any, week: int, year: int) -> None:
        """Process activities for the week"""
        pass
    
    @abstractmethod
    def get_available_activities(self, player: Any) -> List[str]:
        """Get available activities for player"""
        pass


class ISaveManager(IManager):
    """Interface for save/load functionality"""
    
    @abstractmethod
    def save_game(self, game_state: Dict[str, Any], filename: Optional[str] = None) -> bool:
        """Save game state"""
        pass
    
    @abstractmethod
    def load_game(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load game state"""
        pass
    
    @abstractmethod
    def list_saves(self) -> List[str]:
        """List available save files"""
        pass


class IConfigurationProvider(ABC):
    """Interface for configuration management"""
    
    @abstractmethod
    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        pass
    
    @abstractmethod
    def set_config(self, section: str, key: str, value: Any) -> None:
        """Set configuration value"""
        pass
    
    @abstractmethod
    def reload_config(self) -> None:
        """Reload configuration from sources"""
        pass
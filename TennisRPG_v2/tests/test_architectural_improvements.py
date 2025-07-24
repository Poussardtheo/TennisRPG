"""
Tests for architectural improvements (Part 1)
Tests the new interfaces, observer pattern, and configuration system
"""
import pytest
import tempfile
import json
import os
from unittest.mock import Mock

from ..core.interfaces import IStateObserver, IConfigurationProvider
from ..core.observable_state import ObservableState, StateLogger, StateValidator, StateChangeTracker
from ..utils.config_manager import ConfigurationManager


class TestObservableState:
    """Test the Observer pattern implementation"""
    
    def test_observer_registration(self):
        """Test observer registration and removal"""
        state = ObservableState()
        observer = Mock(spec=IStateObserver)
        
        # Test adding observer
        state.add_observer(observer)
        assert observer in state._observers
        
        # Test removing observer
        state.remove_observer(observer)
        assert observer not in state._observers
        
    def test_state_change_notification(self):
        """Test that observers are notified of state changes"""
        state = ObservableState()
        observer = Mock(spec=IStateObserver)
        state.add_observer(observer)
        
        # Change state and verify notification
        state.set_state("test_key", "test_value")
        observer.on_state_changed.assert_called_once_with("test_key", None, "test_value")
        
    def test_multiple_observers(self):
        """Test that multiple observers are all notified"""
        state = ObservableState()
        observer1 = Mock(spec=IStateObserver)
        observer2 = Mock(spec=IStateObserver)
        
        state.add_observer(observer1)
        state.add_observer(observer2)
        
        state.set_state("key", "value")
        
        observer1.on_state_changed.assert_called_once()
        observer2.on_state_changed.assert_called_once()
        
    def test_state_logger(self):
        """Test StateLogger observer"""
        state = ObservableState()
        logger = StateLogger(enabled=True)
        state.add_observer(logger)
        
        # This should not raise an exception
        state.set_state("player_name", "Test Player")
        
    def test_state_validator(self):
        """Test StateValidator observer"""
        state = ObservableState()
        validator = StateValidator()
        
        # Add validation rule
        validator.add_validation_rule("age", lambda x: isinstance(x, int) and 0 <= x <= 100)
        state.add_observer(validator)
        
        # Valid change should work
        state.set_state("age", 25)
        
        # Invalid change should trigger warning (but not fail)
        state.set_state("age", -5)
        
    def test_state_change_tracker(self):
        """Test StateChangeTracker observer"""
        state = ObservableState()
        tracker = StateChangeTracker(max_history=5)
        state.add_observer(tracker)
        
        # Make some changes
        state.set_state("score", 0)
        state.set_state("score", 15)
        state.set_state("score", 30)
        
        history = tracker.get_history("score")
        assert len(history) == 3
        assert history[0]['new_value'] == 0
        assert history[1]['new_value'] == 15
        assert history[2]['new_value'] == 30


class TestConfigurationManager:
    """Test the centralized configuration system"""
    
    def test_config_creation_with_temp_dir(self):
        """Test configuration manager with temporary directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test config file
            test_config = {
                "section1": {
                    "key1": "value1",
                    "nested": {
                        "key2": "value2"
                    }
                }
            }
            
            config_file = os.path.join(temp_dir, "game_balance.json")
            with open(config_file, 'w') as f:
                json.dump(test_config, f)
                
            # Test configuration manager
            config_manager = ConfigurationManager(temp_dir)
            
            # Test getting values
            assert config_manager.get_config("game_balance", "section1.key1") == "value1"
            assert config_manager.get_config("game_balance", "section1.nested.key2") == "value2"
            assert config_manager.get_config("game_balance", "nonexistent", "default") == "default"
            
    def test_config_setting(self):
        """Test setting configuration values"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigurationManager(temp_dir)
            
            # Set a value
            config_manager.set_config("test_section", "test.key", "test_value")
            
            # Verify it was set
            assert config_manager.get_config("test_section", "test.key") == "test_value"
            
    def test_config_validation(self):
        """Test configuration validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid config (talent distribution doesn't sum to 1.0)
            invalid_config = {
                "player_generation": {
                    "talent_distribution": {
                        "low": 0.5,
                        "medium": 0.3,
                        "high": 0.1
                        # Missing values, sums to 0.9 instead of 1.0
                    }
                }
            }
            
            config_file = os.path.join(temp_dir, "game_balance.json")
            with open(config_file, 'w') as f:
                json.dump(invalid_config, f)
                
            config_manager = ConfigurationManager(temp_dir)
            
            # Validate and check for issues
            issues = config_manager.validate_config()
            assert 'game_balance' in issues
            assert len(issues['game_balance']) > 0
            
    def test_interface_compliance(self):
        """Test that ConfigurationManager implements IConfigurationProvider"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigurationManager(temp_dir)
            
            # Should implement the interface
            assert isinstance(config_manager, IConfigurationProvider)
            
            # Should have all required methods
            assert hasattr(config_manager, 'get_config')
            assert hasattr(config_manager, 'set_config')
            assert hasattr(config_manager, 'reload_config')


class TestArchitecturalIntegration:
    """Integration tests for the architectural improvements"""
    
    def test_observer_with_config(self):
        """Test integration of observer pattern with configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config
            config_manager = ConfigurationManager(temp_dir)
            config_manager.set_config("game", "player_name", "Initial Name")
            
            # Create observable state
            state = ObservableState()
            tracker = StateChangeTracker()
            state.add_observer(tracker)
            
            # Change state based on config
            player_name = config_manager.get_config("game", "player_name", "Default")
            state.set_state("current_player", player_name)
            
            # Verify integration
            history = tracker.get_history("current_player")
            assert len(history) == 1
            assert history[0]['new_value'] == "Initial Name"


if __name__ == "__main__":
    pytest.main([__file__])
"""
Centralized Configuration Manager
Manages all game configuration from JSON files and provides a unified interface
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from ..core.interfaces import IConfigurationProvider


class ConfigurationManager(IConfigurationProvider):
    """Centralized configuration management system"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or self._get_default_config_dir()
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._load_all_configs()
        
    def _get_default_config_dir(self) -> str:
        """Get default configuration directory"""
        current_file = Path(__file__)
        package_root = current_file.parent.parent
        return str(package_root / "config")
        
    def _load_all_configs(self) -> None:
        """Load all configuration files"""
        config_files = {
            'game_balance': 'game_balance.json',
            'tournament_config': 'tournament_config.json', 
            'player_config': 'player_config.json',
            'ui_config': 'ui_config.json'
        }
        
        for config_name, filename in config_files.items():
            config_path = os.path.join(self.config_dir, filename)
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._configs[config_name] = json.load(f)
                print(f"✅ Loaded configuration: {config_name}")
            except FileNotFoundError:
                print(f"⚠️ Configuration file not found: {config_path}")
                self._configs[config_name] = {}
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in {config_path}: {e}")
                self._configs[config_name] = {}
                
    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        if section not in self._configs:
            return default
            
        config = self._configs[section]
        
        # Support nested keys with dot notation (e.g., "player_generation.talent_distribution")
        keys = key.split('.')
        current = config
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default
            
    def set_config(self, section: str, key: str, value: Any) -> None:
        """Set configuration value (runtime only, doesn't persist)"""
        if section not in self._configs:
            self._configs[section] = {}
            
        config = self._configs[section]
        keys = key.split('.')
        
        # Navigate to the parent of the final key
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
            
        # Set the final value
        current[keys[-1]] = value
        
    def reload_config(self) -> None:
        """Reload configuration from files"""
        self._configs.clear()
        self._load_all_configs()
        
    def save_config(self, section: str, filename: Optional[str] = None) -> bool:
        """Save configuration section to file"""
        if section not in self._configs:
            return False
            
        if not filename:
            filename = f"{section}.json"
            
        config_path = os.path.join(self.config_dir, filename)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._configs[section], f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Failed to save config {section}: {e}")
            return False
            
    def get_all_config_sections(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration sections"""
        return self._configs.copy()
        
    def validate_config(self) -> Dict[str, list]:
        """Validate all configurations and return any issues"""
        issues = {}
        
        # Validate game balance
        balance_issues = self._validate_game_balance()
        if balance_issues:
            issues['game_balance'] = balance_issues
            
        # Validate tournament config
        tournament_issues = self._validate_tournament_config()
        if tournament_issues:
            issues['tournament_config'] = tournament_issues
            
        # Validate player config
        player_issues = self._validate_player_config()
        if player_issues:
            issues['player_config'] = player_issues
            
        return issues
        
    def _validate_game_balance(self) -> list:
        """Validate game balance configuration"""
        issues = []
        balance = self._configs.get('game_balance', {})
        
        # Check talent distribution sums to 1.0
        talent_dist = balance.get('player_generation', {}).get('talent_distribution', {})
        if talent_dist:
            total = sum(talent_dist.values())
            if abs(total - 1.0) > 0.01:
                issues.append(f"Talent distribution sums to {total}, should be 1.0")
                
        # Check age ranges are logical
        age_range = balance.get('player_generation', {}).get('age_range', {})
        if age_range:
            min_age = age_range.get('min', 0)
            max_age = age_range.get('max', 0)
            if min_age >= max_age:
                issues.append(f"Min age ({min_age}) should be less than max age ({max_age})")
                
        return issues
        
    def _validate_tournament_config(self) -> list:
        """Validate tournament configuration"""
        issues = []
        tournaments = self._configs.get('tournament_config', {}).get('tournament_categories', {})
        
        for category, config in tournaments.items():
            # Check that points and prize arrays match rounds
            rounds = config.get('rounds', 0)
            points = config.get('atp_points', [])
            prizes = config.get('prize_money', [])
            
            if len(points) != rounds:
                issues.append(f"{category}: ATP points array length ({len(points)}) != rounds ({rounds})")
                
            if len(prizes) != rounds:
                issues.append(f"{category}: Prize money array length ({len(prizes)}) != rounds ({rounds})")
                
        return issues
        
    def _validate_player_config(self) -> list:
        """Validate player configuration"""
        issues = []
        player_config = self._configs.get('player_config', {})
        
        # Check nationality distribution
        nationalities = player_config.get('generation_settings', {}).get('nationalities', {})
        if nationalities:
            total = sum(nationalities.values())
            if abs(total - 1.0) > 0.01:
                issues.append(f"Nationality distribution sums to {total}, should be 1.0")
                
        # Check playing styles distribution
        styles = player_config.get('generation_settings', {}).get('playing_styles', {})
        if styles:
            total = sum(styles.values())
            if abs(total - 1.0) > 0.01:
                issues.append(f"Playing styles distribution sums to {total}, should be 1.0")
                
        return issues


# Global configuration instance
_config_manager = None


def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def get_config(section: str, key: str, default: Any = None) -> Any:
    """Convenience function to get configuration value"""
    return get_config_manager().get_config(section, key, default)


def set_config(section: str, key: str, value: Any) -> None:
    """Convenience function to set configuration value"""
    get_config_manager().set_config(section, key, value)


def reload_config() -> None:
    """Convenience function to reload configuration"""
    get_config_manager().reload_config()
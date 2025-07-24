"""
TennisRPG Custom Exceptions
Centralized exception handling for better error management
"""

class TennisRPGException(Exception):
    """Base exception for all TennisRPG errors"""
    pass


class GameStateException(TennisRPGException):
    """Exceptions related to game state management"""
    pass


class PlayerException(TennisRPGException):
    """Exceptions related to player operations"""
    pass


class TournamentException(TennisRPGException):
    """Exceptions related to tournament operations"""
    pass


class RankingException(TennisRPGException):
    """Exceptions related to ranking calculations"""
    pass


class SaveLoadException(TennisRPGException):
    """Exceptions related to save/load operations"""
    pass


class ValidationException(TennisRPGException):
    """Exceptions related to data validation"""
    pass


class NetworkException(TennisRPGException):
    """Exceptions related to network operations"""
    pass


class ConfigurationException(TennisRPGException):
    """Exceptions related to configuration issues"""
    pass


class PerformanceException(TennisRPGException):
    """Exceptions related to performance issues"""
    pass
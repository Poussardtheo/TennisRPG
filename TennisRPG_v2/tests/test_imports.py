#!/usr/bin/env python3
"""
Script de test pour vérifier les imports de TennisRPG v2
"""
import sys
import os

# Ajoute le répertoire TennisRPG_v2 au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'TennisRPG_v2'))

def test_imports():
    """Teste tous les imports critiques"""
    print("🧪 Test des imports TennisRPG v2...")
    
    try:
        # Test entities
        print("  📦 Test entities...")
        from entities.player import Player, Gender
        from entities.ranking import Ranking, RankingType
        print("    ✅ entities.player OK")
        
        # Test utils
        print("  📦 Test utils...")
        from utils.constants import TIME_CONSTANTS, Hand, BackhandStyle
        from utils.helpers import get_gender_agreement
        print("    ✅ utils OK")
        
        # Test data
        print("  📦 Test data...")
        from data.tournaments_database import tournois
        from data.countries import COUNTRIES
        print("    ✅ data OK")
        
        # Test managers
        print("  📦 Test managers...")
        from managers.player_generator import PlayerGenerator
        from managers.tournament_manager import TournamentManager
        from managers.ranking_manager import RankingManager
        print("    ✅ managers OK")
        
        # Test core
        print("  📦 Test core...")
        from core.enhanced_save_manager import SaveManager, GameState
        from core.game_session import GameSession
        print("    ✅ core OK")
        
        print("\n🎉 TOUS LES IMPORTS SONT OK !")
        
        # Test création d'un joueur simple
        print("\n🧪 Test création joueur...")
        player = Player(
            gender=Gender.MALE,
            first_name="Test",
            last_name="Player", 
            country="France"
        )
        print(f"    ✅ Joueur créé: {player.full_name}")
        
        # Test création session de jeu
        print("\n🧪 Test création session de jeu...")
        session = GameSession()
        print(f"    ✅ Session créée - Semaine: {session.current_week}")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ ERREUR D'IMPORT: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERREUR GÉNÉRALE: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ Le jeu peut probablement démarrer sans erreur !")
    else:
        print("\n❌ Des corrections sont nécessaires avant de pouvoir démarrer le jeu.")
        sys.exit(1)
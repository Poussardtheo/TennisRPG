#!/usr/bin/env python3
"""
Test des affichages de retraite améliorés
"""

def test_imports():
    """Test des imports nécessaires"""
    print("🧪 Test des imports...")
    
    try:
        from TennisRPG_v2.managers.retirement_manager import RetirementManager
        from TennisRPG_v2.entities.player import Player, Gender
        from TennisRPG_v2.utils.helpers import calculate_retirement_probability, should_player_retire
        from TennisRPG_v2.utils.constants import RETIREMENT_CONSTANTS
        print("✅ Tous les imports réussis")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_retirement_display_functionality():
    """Test de la fonctionnalité d'affichage des retraites"""
    print("\n🧪 Test de l'affichage des retraites...")
    
    try:
        # Crée quelques joueurs de test
        players = {}
        
        # Joueurs âgés (candidats à la retraite)
        old_players = [
            Player(Gender.MALE, "Roger", "Veteran", "Suisse", age=38),
            Player(Gender.FEMALE, "Serena", "Legend", "USA", age=40),
            Player(Gender.MALE, "Rafael", "Clay", "Espagne", age=36),
        ]
        
        # Jeunes joueurs
        young_players = [
            Player(Gender.MALE, "Carlos", "Rising", "Espagne", age=20),
            Player(Gender.FEMALE, "Coco", "Future", "USA", age=19),
        ]
        
        # Ajoute tous les joueurs au dictionnaire
        all_test_players = old_players + young_players
        for player in all_test_players:
            players[player.full_name] = player
        
        print(f"   ✅ Créé {len(players)} joueurs de test")
        
        # Test du gestionnaire de retraites
        manager = RetirementManager()
        
        # Simule quelques retraites
        for player in old_players:
            prob = calculate_retirement_probability(player.career.age, atp_ranking=None)
            print(f"   📊 {player.full_name} ({player.career.age} ans): {prob*100:.1f}% de probabilité de retraite")
        
        # Test des statistiques de retraite
        print(f"\n   📈 Test des statistiques vides:")
        empty_stats = manager.get_retirement_stats(2024)
        print(f"   Stats vides: {empty_stats}")
        
        print("✅ Fonctionnalité d'affichage testée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'affichage: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_retirement_probability_ranges():
    """Test des plages de probabilité de retraite"""
    print("\n🧪 Test des plages de probabilité de retraite...")
    
    try:
        from TennisRPG_v2.utils.helpers import calculate_retirement_probability
        
        # Test des différents âges
        test_cases = [
            (25, None, "Jeune joueur"),
            (30, None, "Âge minimum de retraite"),
            (35, 10, "Vétéran top 10"),
            (35, 200, "Vétéran classement moyen"),
            (40, None, "Joueur âgé"),
            (45, None, "Retraite forcée"),
        ]
        
        for age, ranking, description in test_cases:
            prob = calculate_retirement_probability(age, ranking)
            print(f"   {description:<25} ({age} ans, #{ranking or 'N/C'}): {prob*100:5.1f}%")
        
        print("✅ Test des probabilités réussi")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des probabilités: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🎾 TEST DU SYSTÈME D'AFFICHAGE DES RETRAITES")
    print("=" * 50)
    
    success = True
    
    # Execute tous les tests
    success &= test_imports()
    success &= test_retirement_display_functionality()
    success &= test_retirement_probability_ranges()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✨ Le système d'affichage des retraites est fonctionnel!")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return success

if __name__ == "__main__":
    main()
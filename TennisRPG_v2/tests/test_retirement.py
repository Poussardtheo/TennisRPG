"""
Test rapide du système de retraite
"""
from TennisRPG_v2.utils.helpers import calculate_retirement_probability, should_player_retire
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.retirement_manager import RetirementManager

def test_retirement_probability():
    """Test des probabilités de retraite"""
    print("🧪 Test des probabilités de retraite")
    
    # Test de différents âges
    ages = [25, 30, 32, 35, 38, 40, 45]
    for age in ages:
        prob = calculate_retirement_probability(age)
        print(f"   Âge {age}: {prob:.3f} ({prob*100:.1f}%)")
    
    print("\n🧪 Test avec classement ATP")
    age = 35
    rankings = [10, 50, 100, 200, 500, 1000]
    for ranking in rankings:
        prob = calculate_retirement_probability(age, ranking)
        print(f"   Âge {age}, Classement #{ranking}: {prob:.3f} ({prob*100:.1f}%)")

def test_player_retirement():
    """Test de retraite sur un joueur réel"""
    print("\n🧪 Test de retraite sur joueur")
    
    # Crée un joueur de 35 ans
    player = Player(
        gender=Gender.MALE,
        first_name="Roger", 
        last_name="Testeur",
        country="Suisse",
        age=35
    )
    
    print(f"Joueur: {player.full_name}, Âge: {player.career.age}")
    
    # Test 100 fois pour voir la distribution
    retirements = 0
    for _ in range(100):
        if should_player_retire(player, atp_ranking=200):
            retirements += 1
    
    print(f"Sur 100 tests: {retirements} retraites ({retirements}%)")

def test_retirement_manager():
    """Test du gestionnaire de retraites"""
    print("\n🧪 Test du gestionnaire de retraites")
    
    manager = RetirementManager()
    print("RetirementManager créé avec succès")
    
    # Test de statistiques vides
    stats = manager.get_retirement_stats()
    print(f"Statistiques vides: {stats}")

if __name__ == "__main__":
    try:
        test_retirement_probability()
        test_player_retirement()
        test_retirement_manager()
        print("\n✅ Tous les tests sont passés!")
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
"""
Tests de charge et stress pour TennisRPG v2
"""
import concurrent.futures
import time
from TennisRPG.entities.player import Player, Gender
from TennisRPG.managers.player_generator import PlayerGenerator
from TennisRPG.managers.tournament_manager import TournamentManager


def stress_test_tournament_system():
    """Test de stress du système de tournois"""
    print("🏃 Démarrage du test de stress...")
    
    # Génère beaucoup de joueurs
    generator = PlayerGenerator()
    players = []
    
    print("👥 Génération de 1000 joueurs...")
    start_time = time.time()
    
    for i in range(1000):
        player = generator.generate_player(Gender.MALE)
        players.append(player)
        
        if (i + 1) % 100 == 0:
            print(f"   ✓ {i + 1}/1000 joueurs générés")
    
    generation_time = time.time() - start_time
    print(f"⚡ Génération terminée en {generation_time:.2f}s")
    
    # Test de simulation parallèle
    print("\n🎾 Simulation de tournois parallèles...")
    manager = TournamentManager()
    
    def simulate_tournament(week):
        tournaments = manager.get_tournaments_for_week(week)
        if tournaments:
            tournament = tournaments[0]
            # Nettoie le tournoi
            tournament.participants.clear()
            tournament.match_results.clear()
            tournament.eliminated_players.clear()
            
            # Ajoute des participants (subset des joueurs)
            import random
            selected_players = random.sample(players, min(32, len(players)))
            for player in selected_players:
                tournament.add_participant(player)
            
            result = tournament.play_tournament(verbose=False)
            return result
        return None
    
    start_time = time.time()
    
    # Simule 10 tournois en parallèle
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for week in range(1, 11):
            future = executor.submit(simulate_tournament, week)
            futures.append(future)
        
        results = []
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            if result:
                results.append(result)
                print(f"   ✓ Tournoi {i+1} terminé")
    
    simulation_time = time.time() - start_time
    print(f"⚡ Simulations parallèles terminées en {simulation_time:.2f}s")
    print(f"✅ {len(results)} tournois simulés avec succès")
    
    # Test de charge ELO
    print("\n🎯 Test de charge calcul ELO...")
    start_time = time.time()
    
    for player in players:
        player.update_elo()
    
    elo_time = time.time() - start_time
    print(f"⚡ Calcul ELO pour 1000 joueurs terminé en {elo_time:.2f}s")
    
    # Résumé
    print(f"\n📊 RÉSUMÉ DU TEST DE STRESS:")
    print(f"   Génération de 1000 joueurs: {generation_time:.2f}s")
    print(f"   Simulation de 10 tournois: {simulation_time:.2f}s") 
    print(f"   Calcul ELO 1000 joueurs: {elo_time:.2f}s")
    print(f"   Total: {generation_time + simulation_time + elo_time:.2f}s")
    
    # Validation des performances
    assert generation_time < 30.0, "Génération trop lente"
    assert simulation_time < 60.0, "Simulation trop lente"
    assert elo_time < 5.0, "Calcul ELO trop lent"
    
    print("✅ Tous les tests de performance sont passés!")


def memory_stress_test():
    """Test de stress mémoire"""
    print("\n🧠 Test de stress mémoire...")
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Crée beaucoup d'objets
    generator = PlayerGenerator()
    players = []
    
    for i in range(5000):
        player = generator.generate_player(Gender.MALE)
        players.append(player)
        
        if (i + 1) % 1000 == 0:
            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"   📈 {i + 1} joueurs - Mémoire: {current_memory:.1f}MB")
    
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = final_memory - initial_memory
    
    print(f"💾 Utilisation mémoire:")
    print(f"   Initial: {initial_memory:.1f}MB")
    print(f"   Final: {final_memory:.1f}MB")
    print(f"   Augmentation: {memory_increase:.1f}MB")
    
    # Nettoie
    del players
    
    # Vérifie pas de fuite mémoire majeure
    assert memory_increase < 500, f"Possible fuite mémoire: {memory_increase}MB"
    print("✅ Test mémoire OK")


if __name__ == "__main__":
    try:
        stress_test_tournament_system()
        memory_stress_test()
        print("\n🎉 TOUS LES TESTS DE CHARGE SONT PASSÉS!")
    except Exception as e:
        print(f"\n❌ ERREUR DANS LES TESTS: {e}")
        raise
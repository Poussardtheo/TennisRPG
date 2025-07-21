"""
Script de profiling mémoire pour TennisRPG v2
"""
from memory_profiler import profile
from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.player_generator import PlayerGenerator
from TennisRPG_v2.managers.tournament_manager import TournamentManager


@profile
def test_player_generation():
    """Test profiling génération joueurs"""
    generator = PlayerGenerator()
    players = []
    
    for i in range(1000):
        player = generator.generate_player(Gender.MALE)
        players.append(player)
    
    return players


@profile  
def test_tournament_simulation():
    """Test profiling simulation tournoi"""
    from TennisRPG_v2.data.tournaments_database import tournois
    
    # Prend un tournoi
    week_tournaments = tournois.get(10, [])
    if not week_tournaments:
        return None
        
    tournament = week_tournaments[0]
    
    # Génère des joueurs
    generator = PlayerGenerator()
    players = [generator.generate_player(Gender.MALE) for _ in range(64)]
    
    # Nettoie et configure le tournoi
    tournament.participants.clear()
    tournament.match_results.clear()
    tournament.eliminated_players.clear()
    
    for player in players:
        tournament.add_participant(player)
    
    # Simule
    result = tournament.play_tournament(verbose=False)
    return result


@profile
def test_ranking_system():
    """Test profiling système de classement"""
    from TennisRPG_v2.managers.ranking_manager import RankingManager
    
    generator = PlayerGenerator()
    players = [generator.generate_player(Gender.MALE) for _ in range(500)]
    
    ranking_manager = RankingManager(players)
    atp_ranking = ranking_manager.get_atp_ranking()
    elo_ranking = ranking_manager.get_elo_ranking()
    
    return atp_ranking, elo_ranking


if __name__ == "__main__":
    print("🧠 Profiling mémoire - Génération de joueurs")
    players = test_player_generation()
    
    print("\n🧠 Profiling mémoire - Simulation tournoi")  
    result = test_tournament_simulation()
    
    print("\n🧠 Profiling mémoire - Système de classement")
    rankings = test_ranking_system()
    
    print("✅ Profiling terminé")
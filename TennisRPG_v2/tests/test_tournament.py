"""
Script de test pour profiling CPU des tournois
"""
import time
import sys

from TennisRPG_v2.managers.atp_points_manager import ATPPointsManager
from TennisRPG_v2.managers.ranking_manager import RankingManager

sys.path.append('..')

from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.tournament_manager import TournamentManager
from TennisRPG_v2.managers.player_generator import PlayerGenerator


def test_elimination_tournament():
    """Test d'un tournoi à élimination directe"""
    print("=== TEST TOURNOI À ÉLIMINATION DIRECTE ===")
    
    # Utilise le gestionnaire de tournois pour prendre un ATP 250 existant
    tournament_manager = TournamentManager()

    week = 21
    # Prend le Geneva Open de la semaine 21
    tournament = tournament_manager.get_tournament_by_name("Gonet Geneva Open", week=week)
    
    if tournament is None:
        print("Geneva Open non trouvé, utilise le premier tournoi disponible de la semaine 21")
        tournaments = tournament_manager.get_tournaments_for_week(week)
        if tournaments:
            tournament = tournaments[0]
        else:
            raise ValueError(f"Aucun tournoi trouvé pour la semaine {week}")
    
    # Générer des joueurs de test
    generator = PlayerGenerator()
    players = {}
    
    # Créer un joueur principal
    main_player = Player(
        gender=Gender.MALE,
        first_name="Rafael",
        last_name="Testdal",
        country="Spain",
        is_main_player=True
    )
    # Ajuster ses stats pour qu'il soit compétitif
    main_player.stats.coup_droit = 85
    main_player.stats.revers = 80
    main_player.stats.service = 82
    main_player.stats.vollee = 75
    main_player._recalculate_all_elo_ratings()
    players[main_player.full_name] = main_player
    
    # Générer 31 autres joueurs (32 - 1 main_player = 31)
    generated_players = {}
    for i in range(31):
        player = generator.generate_player(Gender.MALE)
        generated_players[player.full_name] = player
    
    # S'assurer que tous les noms sont uniques avant d'ajouter au dictionnaire
    for player in generated_players.values():
        base_name = player.full_name
        counter = 1
        unique_name = base_name
        
        # Si le nom existe déjà, ajouter un suffixe numérique
        while unique_name in players:
            unique_name = f"{base_name} {counter}"
            counter += 1
        
        # Mettre à jour le nom du joueur si nécessaire
        if unique_name != base_name:
            player.last_name = f"{player.last_name} {counter-1}"
        
        players[player.full_name] = player
    
    # Ajouter les participants
    for player in players.values():
        tournament.add_participant(player)

    print(f"\nParticipants:")
    for i, player in enumerate(tournament.participants, 1):
        print(f"{i}. {player.full_name} (ELO: {player.elo})")

    # Crée d'abord le ranking manager
    players_list = list(players.values())
    ranking_manager = RankingManager(players_list)
    
    # génère le gestionnaire de points ATP avec tous les joueurs
    atp_points_manager = ATPPointsManager(players, ranking_manager)

    # Jouer le tournoi
    result = tournament.play_tournament(atp_points_manager=atp_points_manager, week=week)
    
    print(f"\n=== RÉSULTAT FINAL ===")
    print(f"🏆 Vainqueur: {result.winner.full_name}")
    print(f"🥈 Finaliste: {result.finalist.full_name if result.finalist else 'N/A'}")
    print(f"🥉 Demi-finalistes: {', '.join([p.full_name for p in result.semifinalists])}")
    
    return result


def test_atp_finals():
    """Test du tournoi ATP Finals"""
    print("\n\n=== TEST ATP FINALS ===")
    
    # Utilise le gestionnaire pour prendre l'ATP Finals
    tournament_manager = TournamentManager()
    
    # Prend l'ATP Finals de la semaine 46
    tournament = tournament_manager.get_tournament_by_name("Nitto ATP Finals", week=46)
    
    if tournament is None:
        print("ATP Finals non trouvé, utilise le premier tournoi disponible de la semaine 46")
        tournaments = tournament_manager.get_tournaments_for_week(46)
        if tournaments:
            tournament = tournaments[0]
        else:
            raise ValueError("Aucun tournoi trouvé pour la semaine 46")
    
    # Générer 8 joueurs de haut niveau
    generator = PlayerGenerator()
    players = {}
    
    # Créer un joueur principal
    main_player = Player(
        gender=Gender.MALE,
        first_name="Novak",
        last_name="Testokovic",
        country="Serbia",
        is_main_player=True
    )
    # Stats de très haut niveau
    main_player.stats.coup_droit = 90
    main_player.stats.revers = 88
    main_player.stats.service = 85
    main_player.stats.vollee = 80
    main_player.stats.puissance = 87
    main_player.stats.vitesse = 82
    main_player.stats.endurance = 90
    main_player.stats.reflexes = 88
    main_player._recalculate_all_elo_ratings()
    players[main_player.full_name] = main_player
    
    # Générer 7 autres joueurs de haut niveau
    generated_players = []
    for i in range(7):
        player = generator.generate_player(Gender.MALE)
        # Boost leurs stats pour simuler les 8 meilleurs mondiaux
        player.stats.coup_droit = min(95, player.stats.coup_droit + 15)
        player.stats.revers = min(95, player.stats.revers + 15)
        player.stats.service = min(95, player.stats.service + 15)
        player.stats.vollee = min(95, player.stats.vollee + 10)
        player.stats.puissance = min(95, player.stats.puissance + 15)
        player.stats.vitesse = min(95, player.stats.vitesse + 15)
        player.stats.endurance = min(95, player.stats.endurance + 10)
        player.stats.reflexes = min(95, player.stats.reflexes + 10)
        player._recalculate_all_elo_ratings()
        generated_players.append(player)
    
    # S'assurer que tous les noms sont uniques avant d'ajouter au dictionnaire
    for player in generated_players:
        base_name = player.full_name
        counter = 1
        unique_name = base_name
        
        # Si le nom existe déjà, ajouter un suffixe numérique
        while unique_name in players:
            unique_name = f"{base_name} {counter}"
            counter += 1
        
        # Mettre à jour le nom du joueur si nécessaire
        if unique_name != base_name:
            player.last_name = f"{player.last_name} {counter-1}"
        
        players[player.full_name] = player
    
    # Ajouter les participants
    for player in players.values():
        tournament.add_participant(player)

    print(f"\nParticipants (Top 8 mondial):")
    for i, player in enumerate(tournament.participants, 1):
        print(f"{i}. {player.full_name} (ELO: {player.elo})")

    # Crée d'abord le ranking manager
    players_list = list(players.values())
    ranking_manager = RankingManager(players_list)
    
    # génère le gestionnaire de points ATP avec tous les joueurs
    atp_points_manager = ATPPointsManager(players, ranking_manager)

    # Jouer le tournoi
    result = tournament.play_tournament(atp_points_manager=atp_points_manager, week=46)
    
    print(f"\n=== RÉSULTAT FINAL ===")
    print(f"🏆 Champion ATP Finals: {result.winner.full_name}")
    print(f"🥈 Finaliste: {result.finalist.full_name}")
    print(f"🥉 Demi-finalistes: {', '.join([p.full_name for p in result.semifinalists])}")
    
    return result


if __name__ == "__main__":
    try:
        # Test du tournoi à élimination directe
        result1 = test_elimination_tournament()
        
        # Test du tournoi ATP Finals
        result2 = test_atp_finals()
        
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("Le système de tournois v2 fonctionne correctement.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DU TEST: {e}")
        import traceback
        traceback.print_exc()

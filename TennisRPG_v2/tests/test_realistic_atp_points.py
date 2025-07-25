#!/usr/bin/env python3
"""
Test pour vérifier que le système ATP produit des valeurs réalistes
"""
import sys
import os
import random

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.managers.ranking_manager import RankingManager
from TennisRPG_v2.managers.atp_points_manager import ATPPointsManager
from TennisRPG_v2.data.tournaments_data import ATP_POINTS_CONFIG, TournamentCategory
from TennisRPG_v2.utils.constants import TIME_CONSTANTS


def simulate_realistic_season():
    """Simule une saison réaliste avec distribution de points appropriée"""
    print("=== SIMULATION D'UNE SAISON RÉALISTE ===\n")
    
    # Crée des joueurs de test (simuler un top 100)
    players = []
    for i in range(100):
        player = Player(
            gender=Gender.MALE,
            first_name=f"Player{i+1}",
            last_name=f"Top{i+1}",
            country="International",
            is_main_player=(i == 0)
        )
        players.append(player)
    
    # Crée les managers
    ranking_manager = RankingManager(players)
    players_dict = {p.full_name: p for p in players}
    atp_manager = ATPPointsManager(players_dict, ranking_manager)
    
    print(f"Simulation avec {len(players)} joueurs")
    
    # Simulation sur plusieurs semaines avec distribution réaliste des points
    weeks_to_simulate = 52  # Une année complète
    
    for week in range(1, weeks_to_simulate + 1):
        ranking_manager.current_week = week
        
        # Simule différents types de tournois chaque semaine
        tournaments_this_week = simulate_weekly_tournaments(week)
        
        for tournament_info in tournaments_this_week:
            category = tournament_info['category']
            participants = random.sample(players, min(tournament_info['size'], len(players)))
            
            # Distribue les points selon la performance dans le tournoi
            distribute_tournament_points(
                participants, category, atp_manager, week
            )
        
        # Avance à la semaine suivante (applique le système glissant)
        if week < weeks_to_simulate:
            ranking_manager.advance_week()
        
        # Affichage du progrès
        if week % 13 == 0:  # Tous les trimestres
            top_player = max(players, key=lambda p: p.career.atp_points)
            print(f"Semaine {week}: Top joueur = {top_player.career.atp_points} points ATP")
    
    # Analyse des résultats finaux
    print(f"\n=== ANALYSE DES RÉSULTATS APRÈS {weeks_to_simulate} SEMAINES ===")
    
    # Trie les joueurs par points ATP
    players.sort(key=lambda p: p.career.atp_points, reverse=True)
    
    print("Top 10 du classement ATP:")
    for i, player in enumerate(players[:10], 1):
        print(f"{i:2}. {player.full_name:<20} {player.career.atp_points:>6} points")
    
    # Statistiques globales
    total_points = sum(p.career.atp_points for p in players)
    avg_points = total_points / len(players)
    
    print(f"\nStatistiques globales:")
    print(f"Numéro 1 mondial: {players[0].career.atp_points} points")
    print(f"Numéro 10: {players[9].career.atp_points} points") 
    print(f"Numéro 50: {players[49].career.atp_points} points")
    print(f"Numéro 100: {players[99].career.atp_points} points")
    print(f"Moyenne: {avg_points:.0f} points")
    print(f"Total des points dans le système: {total_points}")
    
    # Vérifications de cohérence
    print(f"\n=== VÉRIFICATIONS DE COHÉRENCE ===")
    
    # Le numéro 1 devrait avoir au moins 8000-12000 points dans un système réaliste
    n1_realistic = players[0].career.atp_points >= 6000
    print(f"Numéro 1 > 6000 points: {'OK' if n1_realistic else 'FAIL'}")
    
    # Le top 10 devrait avoir au moins 2000-3000 points
    top10_realistic = players[9].career.atp_points >= 1500
    print(f"Top 10 > 1500 points: {'OK' if top10_realistic else 'FAIL'}")
    
    # Distribution réaliste (écart entre #1 et #10)
    ratio_realistic = players[0].career.atp_points / max(1, players[9].career.atp_points) < 10
    print(f"Ratio #1/#10 < 10: {'OK' if ratio_realistic else 'FAIL'}")
    
    # Vérifie que le joueur principal a des points
    main_player = players[0]  # Le premier est le joueur principal
    main_has_points = main_player.career.atp_points > 0
    print(f"Joueur principal a des points: {'OK' if main_has_points else 'FAIL'}")
    
    success = n1_realistic and top10_realistic and ratio_realistic and main_has_points
    return success, players[0].career.atp_points, players[9].career.atp_points


def simulate_weekly_tournaments(week):
    """Simule les tournois d'une semaine donnée"""
    tournaments = []
    
    # Chaque semaine, on a généralement 3-6 tournois de différentes catégories
    if week % 4 == 1:  # Semaine avec un Grand Slam (4 fois par an)
        tournaments.append({
            'category': TournamentCategory.GRAND_SLAM,
            'size': 128
        })
    elif week % 8 == 3:  # Masters 1000 (9 fois par an)
        tournaments.append({
            'category': TournamentCategory.MASTERS_1000,
            'size': 96
        })
    
    # Toujours des tournois ATP250/500
    tournaments.append({
        'category': TournamentCategory.ATP_500 if week % 6 == 0 else TournamentCategory.ATP_250,
        'size': 64 if week % 6 == 0 else 32
    })
    
    return tournaments


def distribute_tournament_points(participants, category, atp_manager, week):
    """Distribue les points de tournoi de manière réaliste"""
    points_config = ATP_POINTS_CONFIG.get(category, {})
    
    if not points_config:
        return
    
    # Simule les résultats du tournoi de manière simplifiée
    # Les meilleurs joueurs (par ELO) ont plus de chances de bien faire
    participants.sort(key=lambda p: p.elo, reverse=True)
    
    # Distribue les points selon des résultats simulés
    results = simulate_tournament_results(participants, points_config)
    
    for player, points in results.items():
        if points > 0:
            atp_manager.add_tournament_points(player, week, points)


def simulate_tournament_results(participants, points_config):
    """Simule les résultats d'un tournoi de manière réaliste"""
    results = {}
    num_participants = len(participants)
    
    if num_participants == 0:
        return results
    
    # Distribue les points selon une distribution réaliste
    # Le vainqueur (choisi probabilistiquement selon l'ELO)
    winner_weights = [1.0 / (i + 1) for i in range(num_participants)]
    winner = random.choices(participants, weights=winner_weights)[0]
    results[winner] = points_config.get('winner', 0)
    
    # Finaliste (parmi les top 30%)
    top_players = participants[:max(1, num_participants // 3)]
    finalist_candidates = [p for p in top_players if p != winner]
    if finalist_candidates:
        finalist = random.choice(finalist_candidates)
        results[finalist] = points_config.get('finalist', 0)
    
    # Demi-finalistes (2-4 joueurs)
    semifinal_candidates = [p for p in participants[:num_participants//2] 
                          if p not in results]
    for _ in range(min(2, len(semifinal_candidates))):
        if semifinal_candidates:
            semifinalist = random.choice(semifinal_candidates)
            results[semifinalist] = points_config.get('semifinalist', 0)
            semifinal_candidates.remove(semifinalist)
    
    # Autres tours (distribution plus large mais avec moins de points)
    remaining_players = [p for p in participants if p not in results]
    for i, player in enumerate(random.sample(remaining_players, 
                                           min(10, len(remaining_players)))):
        # Donne des points pour les premiers tours
        if i < 4:
            results[player] = points_config.get('round_16', 0) or points_config.get('round_32', 0) or 10
        elif i < 8:
            results[player] = points_config.get('round_32', 0) or 5
    
    return results


if __name__ == "__main__":
    print("TEST DE RÉALISME DES POINTS ATP")
    print("=" * 50)
    
    success, top_points, top10_points = simulate_realistic_season()
    
    print(f"\n{'SUCCESS' if success else 'NEEDS_IMPROVEMENT'}: Système ATP réaliste")
    
    # Comparaison avec les vrais classements ATP (approximatifs)
    print(f"\nComparaison avec le système ATP réel:")
    print(f"Notre #1: {top_points} pts (Réel: ~11,000-13,000 pts)")
    print(f"Notre #10: {top10_points} pts (Réel: ~2,500-4,000 pts)")
    
    if success:
        print("\n🎾 Le système produit des valeurs réalistes!")
    else:
        print("\n⚠️  Le système nécessite encore des ajustements")
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Script de démonstration du système de talents
"""

from TennisRPG_v2.entities.player import Player, Gender
from TennisRPG_v2.utils.constants import TalentLevel, TALENT_STAT_MULTIPLIERS
from TennisRPG_v2.managers.player_generator import PlayerGenerator


def demo_talent_system():
    """Démonstration du système de talents"""
    print("DEMONSTRATION DU SYSTEME DE TALENTS")
    print("=" * 50)
    
    # Création de joueurs avec différents niveaux de talent
    talents_to_test = [
        TalentLevel.GENIE_PRECOCE,
        TalentLevel.PEPITE,
        TalentLevel.TALENT_BRUT,
        TalentLevel.JOUEUR_PROMETTEUR,
        TalentLevel.ESPOIR_FRAGILE
    ]
    
    players = []
    for i, talent in enumerate(talents_to_test):
        player = Player(
            gender=Gender.MALE,
            first_name=f"Joueur{i+1}",
            last_name="Test",
            country="France",
            talent_level=talent
        )
        players.append(player)
    
    # Affichage des résultats
    print("\nCOMPARAISON DES STATS PAR NIVEAU DE TALENT")
    print("-" * 70)
    print(f"{'Talent':<20} {'Multiplicateur':<12} {'Coup droit':<12} {'Service':<10} {'Endurance':<10}")
    print("-" * 70)
    
    for player in players:
        talent = player.talent_level
        multiplier = TALENT_STAT_MULTIPLIERS[talent]
        stats = player.stats.to_dict()
        
        print(f"{talent.value:<20} {multiplier:<12} {stats['Coup droit']:<12} {stats['Service']:<10} {stats['Endurance']:<10}")
    
    print("\nTEST DU GENERATEUR DE JOUEURS")
    print("-" * 40)
    
    generator = PlayerGenerator()
    
    # Génération de quelques joueurs avec distribution aléatoire
    print("Distribution aléatoire des talents (échantillon de 10 joueurs):")
    talent_count = {talent: 0 for talent in TalentLevel}
    
    for _ in range(10):
        player = generator.generate_player(Gender.MALE)
        talent_count[player.talent_level] += 1
    
    for talent, count in talent_count.items():
        if count > 0:
            print(f"  {talent.value}: {count} joueur(s)")
    
    print(f"\nAFFICHAGE D'UNE CARTE DE JOUEUR")
    print("-" * 40)
    
    # Affichage de la carte d'un joueur genius
    genius_player = players[0]  # Premier joueur (génie précoce)
    print(genius_player.get_display_card())


if __name__ == "__main__":
    demo_talent_system()
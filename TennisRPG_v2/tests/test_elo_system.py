#!/usr/bin/env python3
"""
Test script pour vérifier le nouveau système d'ELO avec stockage par surface.
"""
import sys

from ..entities.player import Player, Gender


def test_elo_storage_system():
    """Test du système de stockage d'ELO par surface"""
    print("=== Test du système d'ELO avec stockage par surface ===\n")
    
    # Créer un joueur de test
    player = Player(
        gender=Gender.MALE,
        first_name="Test",
        last_name="Player",
        country="France",
        is_main_player=True
    )
    
    print(f"Joueur créé: {player.full_name}")
    print(f"Stats initiales: {player.stats.to_dict()}")
    
    # Tester l'ELO général
    elo_general = player.elo
    print(f"\nELO général: {elo_general}")
    
    # Tester l'ELO sur différentes surfaces
    surfaces = ["Hard", "Clay", "Grass", "Indoor Hard", "Carpet"]
    elo_surfaces = {}
    
    for surface in surfaces:
        elo = player.get_elo(surface)
        elo_surfaces[surface] = elo
        print(f"ELO sur {surface}: {elo}")
    
    # Vérifier que les ELO sont stockés
    print(f"\nELO stockés dans player.career.elo_ratings:")
    for surface, elo in player.career.elo_ratings.items():
        print(f"  {surface}: {elo}")
    
    # Test de recalcul après changement de stats
    print(f"\n=== Test de recalcul après changement de stats ===")
    print(f"Ancien ELO général: {elo_general}")
    print(f"Ancien ELO Clay: {elo_surfaces['Clay']}")
    
    # Donner des AP points et les assigner
    player.career.ap_points = 10
    
    # Améliorer les stats manuellement pour tester
    stats_dict = player.stats.to_dict()
    stats_dict["Coup droit"] += 5
    stats_dict["Service"] += 3
    stats_dict["Endurance"] += 2
    player.stats.update_from_dict(stats_dict)
    player.career.ap_points = 0  # Simuler l'utilisation des points AP
    
    # Recalculer explicitement (normalement fait automatiquement)
    player._recalculate_all_elo_ratings()
    
    new_elo_general = player.elo
    new_elo_clay = player.get_elo("Clay")
    
    print(f"Nouveau ELO général: {new_elo_general} (différence: {new_elo_general - elo_general})")
    print(f"Nouveau ELO Clay: {new_elo_clay} (différence: {new_elo_clay - elo_surfaces['Clay']})")
    
    # Test de sérialisation/désérialisation
    print(f"\n=== Test de sauvegarde/chargement ===")
    player_dict = player.to_dict()
    loaded_player = Player.from_dict(player_dict)
    
    print(f"ELO général du joueur chargé: {loaded_player.elo}")
    print(f"ELO Clay du joueur chargé: {loaded_player.get_elo('Clay')}")
    
    # Vérifier que les ELO sont identiques
    assert loaded_player.elo == player.elo, "ELO général différent après chargement"
    assert loaded_player.get_elo("Clay") == player.get_elo("Clay"), "ELO Clay différent après chargement"
    
    print("\n✅ Tous les tests sont passés avec succès!")
    
    return True


if __name__ == "__main__":
    try:
        test_elo_storage_system()
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

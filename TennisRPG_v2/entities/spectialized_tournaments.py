"""
Tournois spécialisés avec logique spécifique
"""
from typing import Dict, List, Optional, Tuple
import random
from collections import defaultdict

from .tournament import Tournament, TournamentResult, TournamentStatus
from ..data.tournaments_data import TournamentCategory, SPECIAL_TOURNAMENT_CONFIG
from ..utils.constants import TOURNAMENT_CONSTANTS


class EliminationTournament(Tournament):
	"""Tournoi à élimination directe classique"""

	def play_tournament(self, verbose: bool = None, atp_points_manager=None, week: int = None) -> TournamentResult:
		"""Joue un tournoi à élimination directe"""
		if len(self.participants) < 2:
			raise ValueError("Pas assez de participants pour le tournoi")

		self.status = TournamentStatus.IN_PROGRESS

		# Trouve le joueur principal et initialise le tracking
		main_player = None
		main_player_atp_points = 0
		main_player_xp_points = 0
		
		for player in self.participants:
			if hasattr(player, 'is_main_player') and player.is_main_player:
				main_player = player
				break

		# Détermine si on affiche les détails (automatiquement si joueur principal présent)
		if verbose is None:
			verbose = self.has_main_player
		
		# Affichage du début du tournoi seulement si verbose
		if verbose:
			print(f"\n{'='*60}")
			print(f"🎾 {self.name}")
			print(f"📍 {self.location} • 🏟️  {self.surface} • 🏆 {self.category.value}")
			print(f"👥 {len(self.participants)} participants")
			print(f"{'='*60}")

		# Initialise les rounds
		current_round = list(self.participants)
		random.shuffle(current_round)  # Mélange les joueurs

		# Applique les têtes de série si nécessaire
		if len(current_round) >= 8:
			current_round = self._apply_seeding(current_round)

		round_names = self._get_round_names(len(current_round))

		# Joue tous les rounds
		for round_idx, round_name in enumerate(round_names):
			if len(current_round) <= 1:
				break

			# Affichage du round seulement si verbose
			if verbose:
				round_display = self._get_round_display_name(round_name)
				print(f"\n📊 {round_display} ({len(current_round)} joueurs)")
				print("-" * 40)

			next_round = []

			# Joue tous les matches du round
			for i in range(0, len(current_round), 2):
				if i + 1 < len(current_round):
					player1 = current_round[i]
					player2 = current_round[i + 1]

					# Affiche le match seulement si verbose
					if verbose:
						print(f"⚔️  {player1.full_name} vs {player2.full_name}")

					match_result = self.simulate_match(player1, player2)
					self.match_results.append(match_result)

					# Affiche le résultat seulement si verbose
					if verbose:
						print(f"   ✅ {match_result.winner.full_name} gagne {match_result.sets_won}-{match_result.sets_lost}")

					# Le vainqueur passe au tour suivant
					next_round.append(match_result.winner)

					# Enregistre l'élimination
					self.eliminated_players[match_result.loser] = round_name

					# Affiche l'élimination du joueur principal (toujours affiché)
					if hasattr(match_result.loser, 'is_main_player') and match_result.loser.is_main_player:
						phase_name = self._get_elimination_message(round_name)

					# Attribue points ATP et XP
					atp_points = self.assign_atp_points(match_result.loser, round_name, atp_points_manager, week)
					xp_points = self.assign_xp_points(match_result.loser, round_name)
					
					# Suit les points du joueur principal
					if main_player and match_result.loser == main_player:
						main_player_atp_points += atp_points
						main_player_xp_points += xp_points
				else:
					# Joueur qualifié d'office
					if verbose:
						print(f"👍 {current_round[i].full_name} qualifié(e) d'office")
					next_round.append(current_round[i])

			current_round = next_round

		# Le dernier joueur est le vainqueur
		winner = current_round[0]

		# Affichage du vainqueur seulement si verbose ou si joueur principal gagne
		if verbose or (hasattr(winner, 'is_main_player') and winner.is_main_player):
			print(f"\n🏆 VAINQUEUR: {winner.full_name}")
			if verbose:
				print(f"{'='*60}")

		# Attribue les points au vainqueur
		atp_points_winner = self.assign_atp_points(winner, "winner", atp_points_manager, week)
		xp_points_winner = self.assign_xp_points(winner, "winner")

		# Bonus d'expérience pour avoir terminé le tournoi
		winner.gain_experience(TOURNAMENT_CONSTANTS["TOURNAMENT_COMPLETION_BONUS"])

		# Récapitulatif pour le joueur principal
		if main_player:
			if winner == main_player:
				# Le joueur principal a gagné
				main_player_atp_points += atp_points_winner
				main_player_xp_points += xp_points_winner + TOURNAMENT_CONSTANTS["TOURNAMENT_COMPLETION_BONUS"]
			
			print(f"\n📊 RÉCAPITULATIF DU TOURNOI:")
			print(f"   💰 Points ATP gagnés: {main_player_atp_points}")
			print(f"   ⭐ Points XP gagnés: {main_player_xp_points}")

		self.status = TournamentStatus.COMPLETED

		return self._create_tournament_result(winner)

	def _apply_seeding(self, players: List['Player']) -> List['Player']:
		"""Applique un système de têtes de série"""
		num_seeds = min(len(players) // 4, 8)  # Maximum 8 têtes de série
		seeded_players = self.get_seeded_players(num_seeds)

		# Sépare têtes de série et autres joueurs
		unseeded = [p for p in players if p not in seeded_players]
		random.shuffle(unseeded)

		# Répartit les têtes de série
		seeded_positions = []
		if len(seeded_players) >= 1:
			seeded_positions.append(0)  # Tête de série n°1
		if len(seeded_players) >= 2:
			seeded_positions.append(len(players) - 1)  # Tête de série n°2
		if len(seeded_players) >= 4:
			seeded_positions.extend([len(players) // 2 - 1, len(players) // 2])

		# Remplit les autres positions
		for i in range(len(seeded_players) - len(seeded_positions)):
			seeded_positions.append(i * 2 + 1)

		# Construit le tableau final
		result = [None] * len(players)

		# Place les têtes de série
		for i, pos in enumerate(seeded_positions[:len(seeded_players)]):
			result[pos] = seeded_players[i]

		# Place les autres joueurs
		unseeded_idx = 0
		for i in range(len(players)):
			if result[i] is None:
				result[i] = unseeded[unseeded_idx]
				unseeded_idx += 1

		return result

	def _get_round_names(self, num_players: int) -> List[str]:
		"""Génère les noms des rounds selon le nombre de joueurs"""
		rounds = []
		current = num_players

		while current > 1:
			if current == 2:
				rounds.append("finalist")
			elif current == 4:
				rounds.append("semifinalist")
			elif current == 8:
				rounds.append("quarterfinalist")
			elif current == 16:
				rounds.append("round_16")
			elif current == 32:
				rounds.append("round_32")
			elif current == 64:
				rounds.append("round_64")
			elif current == 128:
				rounds.append("round_128")
			else:
				rounds.append(f"round_{current}")

			current //= 2

		return rounds

	def _get_round_display_name(self, round_name: str) -> str:
		"""Convertit le nom interne du round en nom d'affichage"""
		display_names = {
			"finalist": "FINALE",
			"semifinalist": "DEMI-FINALES",
			"quarterfinalist": "QUARTS DE FINALE",
			"round_16": "8ème DE FINALE",
			"round_32": "16ème DE FINALE",
			"round_64": "32ème DE FINALE",
			"round_128": "64ème DE FINALE"
		}
		return display_names.get(round_name, f"TOUR {round_name.upper()}")

	def _get_elimination_message(self, round_name: str) -> str:
		"""Retourne le message d'élimination approprié"""
		messages = {
			"finalist": "en finale",
			"semifinalist": "en demi-finale",
			"quarterfinalist": "en quart de finale",
			"round_16": "en 8ème de finale",
			"round_32": "au 1er tour",
			"round_64": "au 1er tour",
			"round_128": "au 1er tour"
		}
		return messages.get(round_name, f"au {round_name}")

	def _create_tournament_result(self, winner: 'Player') -> TournamentResult:
		"""Crée le résultat final du tournoi"""
		# Identifie les finalistes, demi-finalistes, etc.
		finalist = None
		semifinalists = []
		quarterfinalists = []

		for player, round_eliminated in self.eliminated_players.items():
			if round_eliminated == "finalist":
				finalist = player
			elif round_eliminated == "semifinalist":
				semifinalists.append(player)
			elif round_eliminated == "quarterfinalist":
				quarterfinalists.append(player)

		return TournamentResult(
			tournament_name=self.name,
			category=self.category,
			winner=winner,
			finalist=finalist,
			semifinalists=semifinalists,
			quarterfinalists=quarterfinalists,
			all_results=self.eliminated_players.copy(),
			match_results=self.match_results.copy()
		)



class ATPFinals(Tournament):
	"""Tournoi ATP Finals avec format spécial (poules + élimination)"""

	def __init__(self, name: str, location: str, surface: str):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.ATP_FINALS,
			num_players=8,
			sets_to_win=2
		)

		self.config = SPECIAL_TOURNAMENT_CONFIG["ATP_FINALS"]

	def play_tournament(self, verbose: bool = None, atp_points_manager=None, week: int = None) -> TournamentResult:
		"""Joue le tournoi ATP Finals"""
		if len(self.participants) != 8:
			print(f"⚠️ il n'y a actuellement que {len(self.participants)} joueurs.")
			raise ValueError("ATP Finals nécessite exactement 8 joueurs")

		self.status = TournamentStatus.IN_PROGRESS

		# Détermine si on affiche les détails
		if verbose is None:
			verbose = self.has_main_player

		# Affichage du début du tournoi seulement si verbose
		if verbose:
			print(f"\n{'='*60}")
			print(f"🏆 ATP FINALS - {self.name}")
			print(f"📍 {self.location} • 🏟️  {self.surface}")
			print(f"🌟 Les 8 meilleurs joueurs de l'année")
			print(f"{'='*60}")

		# Phase de poules
		if verbose:
			print(f"\n📊 PHASE DE POULES")
			print("-" * 30)
		qualified_players = self._play_group_stage(verbose)

		# Phase finale (demi-finales + finale)
		if verbose:
			print(f"\n📊 PHASE FINALE")
			print("-" * 30)
		winner = self._play_knockout_stage(qualified_players, verbose)

		# Affichage du vainqueur seulement si verbose ou si joueur principal gagne
		if verbose or (hasattr(winner, 'is_main_player') and winner.is_main_player):
			print(f"\n🏆 CHAMPION ATP FINALS: {winner.full_name}")
			if verbose:
				print(f"🎉 Félicitations pour cette victoire exceptionnelle!")
				print(f"{'='*60}")

		# Attribue les points au vainqueur
		self.assign_atp_points(winner, "winner", atp_points_manager, week)
		self.assign_xp_points(winner, "winner")

		# Bonus pour avoir terminé le tournoi
		winner.gain_experience(TOURNAMENT_CONSTANTS["TOURNAMENT_COMPLETION_BONUS"])

		self.status = TournamentStatus.COMPLETED

		return self._create_tournament_result(winner)

	def _play_group_stage(self, verbose: bool = True) -> List['Player']:
		"""Joue la phase de poules"""
		# Divise en 2 groupes de 4 joueurs
		group1 = self.participants[:4]
		group2 = self.participants[4:]

		if verbose:
			print(f"🔵 GROUPE A: {', '.join([p.full_name for p in group1])}")
			print(f"🔴 GROUPE B: {', '.join([p.full_name for p in group2])}")
			print()

		# Joue chaque groupe
		qualified1 = self._play_group(group1, "A", verbose)
		qualified2 = self._play_group(group2, "B", verbose)

		if verbose:
			print(f"\n✅ Qualifiés du Groupe A: {', '.join([p.full_name for p in qualified1])}")
			print(f"✅ Qualifiés du Groupe B: {', '.join([p.full_name for p in qualified2])}")

		return qualified1 + qualified2

	def _play_group(self, players: List['Player'], group_name: str, verbose: bool = True) -> List['Player']:
		"""Joue un groupe de 4 joueurs"""
		if verbose:
			print(f"\n📊 GROUPE {group_name}")
			print("-" * 20)
		
		# Chaque joueur joue contre les 3 autres
		results = defaultdict(lambda: {"wins": 0, "losses": 0, "sets_won": 0, "sets_lost": 0})

		for i in range(len(players)):
			for j in range(i + 1, len(players)):
				if verbose:
					print(f"⚔️  {players[i].full_name} vs {players[j].full_name}")
				
				match_result = self.simulate_match(players[i], players[j])
				self.match_results.append(match_result)

				if verbose:
					print(f"   ✅ {match_result.winner.full_name} gagne {match_result.sets_won}-{match_result.sets_lost}")

				# Met à jour les statistiques
				results[match_result.winner]["wins"] += 1
				results[match_result.winner]["sets_won"] += match_result.sets_won
				results[match_result.winner]["sets_lost"] += match_result.sets_lost

				results[match_result.loser]["losses"] += 1
				results[match_result.loser]["sets_won"] += match_result.sets_lost
				results[match_result.loser]["sets_lost"] += match_result.sets_won

				# Points ATP pour chaque victoire en poule
				self.assign_atp_points(match_result.winner, "round_robin_win", atp_points_manager, week)
				self.assign_xp_points(match_result.winner, "round_robin_win")

		# Affiche le classement du groupe seulement si verbose
		if verbose:
			print(f"\n📈 Classement Groupe {group_name}:")
			temp_sorted = sorted(players, key=lambda p: (
				results[p]["wins"],
				results[p]["sets_won"] / max(1, results[p]["sets_lost"])
			), reverse=True)
			
			for i, player in enumerate(temp_sorted, 1):
				status = "✅ Qualifié" if i <= 2 else "❌ Éliminé"
				print(f"{i}. {player.full_name} - {results[player]['wins']}V-{results[player]['losses']}D ({results[player]['sets_won']}-{results[player]['sets_lost']}) {status}")

		# Classe les joueurs par nombre de victoires, puis par ratio de sets
		sorted_players = sorted(players, key=lambda p: (
			results[p]["wins"],
			results[p]["sets_won"] / max(1, results[p]["sets_lost"])
		), reverse=True)

		# Les 2 premiers se qualifient
		qualified = sorted_players[:2]

		# Marque les autres comme éliminés
		for player in sorted_players[2:]:
			self.eliminated_players[player] = "round_robin"

		return qualified

	def _play_knockout_stage(self, qualified_players: List['Player'], verbose: bool = True) -> 'Player':
		"""Joue la phase finale (demi-finales + finale)"""
		if verbose:
			print(f"\n🥉 DEMI-FINALES")
			print("-" * 15)
		
		# Demi-finales
		if verbose:
			print(f"⚔️  {qualified_players[0].full_name} vs {qualified_players[3].full_name}")
		semi1 = self.simulate_match(qualified_players[0], qualified_players[3])
		if verbose:
			print(f"   ✅ {semi1.winner.full_name} gagne {semi1.sets_won}-{semi1.sets_lost}")
		
		if verbose:
			print(f"⚔️  {qualified_players[1].full_name} vs {qualified_players[2].full_name}")
		semi2 = self.simulate_match(qualified_players[1], qualified_players[2])
		if verbose:
			print(f"   ✅ {semi2.winner.full_name} gagne {semi2.sets_won}-{semi2.sets_lost}")

		self.match_results.extend([semi1, semi2])

		# Enregistre les demi-finalistes éliminés
		self.eliminated_players[semi1.loser] = "semifinalist"
		self.eliminated_players[semi2.loser] = "semifinalist"

		# Attribue les points
		self.assign_atp_points(semi1.loser, "semifinalist", atp_points_manager, week)
		self.assign_atp_points(semi2.loser, "semifinalist", atp_points_manager, week)
		self.assign_xp_points(semi1.loser, "semifinalist")
		self.assign_xp_points(semi2.loser, "semifinalist")

		if verbose:
			print(f"\n🥇 FINALE")
			print("-" * 10)
		
		# Finale
		if verbose:
			print(f"🎾 {semi1.winner.full_name} vs {semi2.winner.full_name}")
		final_match = self.simulate_match(semi1.winner, semi2.winner)
		if verbose:
			print(f"   🏆 {final_match.winner.full_name} gagne {final_match.sets_won}-{final_match.sets_lost}")
		
		self.match_results.append(final_match)

		# Enregistre le finaliste
		self.eliminated_players[final_match.loser] = "finalist"

		# Attribue les points au finaliste
		self.assign_atp_points(final_match.loser, "finalist", atp_points_manager, week)
		self.assign_xp_points(final_match.loser, "finalist")

		return final_match.winner

	def _create_tournament_result(self, winner: 'Player') -> TournamentResult:
		"""Crée le résultat final du tournoi"""
		finalist = None
		semifinalists = []

		for player, round_eliminated in self.eliminated_players.items():
			if round_eliminated == "finalist":
				finalist = player
			elif round_eliminated == "semifinalist":
				semifinalists.append(player)

		return TournamentResult(
			tournament_name=self.name,
			category=self.category,
			winner=winner,
			finalist=finalist,
			semifinalists=semifinalists,
			quarterfinalists=[],  # Pas de quarts aux ATP Finals
			all_results=self.eliminated_players.copy(),
			match_results=self.match_results.copy()
		)


class GrandSlam(EliminationTournament):
	"""Tournoi Grand Chelem"""
	def __init__(self, name, location, num_players, surface):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.GRAND_SLAM,
			num_players=num_players,
			sets_to_win=3
		)


class Masters1000(EliminationTournament):
	"""Tournoi Masters 1000"""
	def __init__(self, name, location, num_players, surface, num_rounds=6):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.MASTERS_1000,
			num_players=num_players,
			sets_to_win=2
		)
		self.num_rounds = num_rounds


class ATP500(EliminationTournament):
	"""Tournoi ATP 500"""
	def __init__(self, name, location, num_players, surface, num_rounds=5):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.ATP_500,
			num_players=num_players,
			sets_to_win=2
		)
		self.num_rounds = num_rounds


class ATP250(EliminationTournament):
	"""Tournoi ATP 250"""
	def __init__(self, name, location, num_players, surface, num_rounds=5):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.ATP_250,
			num_players=num_players,
			sets_to_win=2
		)
		self.num_rounds = num_rounds


class CHALLENGERS175(EliminationTournament):
	"""Tournoi Challenger 175"""
	def __init__(self, name, location, surface):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.CHALLENGER_175,
			num_players=32,
			sets_to_win=2
		)


class CHALLENGERS125(EliminationTournament):
	"""Tournoi Challenger 125"""
	def __init__(self, name, location, surface):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.CHALLENGER_125,
			num_players=32,
			sets_to_win=2
		)


class CHALLENGERS100(EliminationTournament):
	"""Tournoi Challenger 100"""
	def __init__(self, name, location, surface):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.CHALLENGER_100,
			num_players=32,
			sets_to_win=2
		)


class CHALLENGERS75(EliminationTournament):
	"""Tournoi Challenger 75"""
	def __init__(self, name, location, surface):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.CHALLENGER_75,
			num_players=32,
			sets_to_win=2
		)


class CHALLENGERS50(EliminationTournament):
	"""Tournoi Challenger 50"""
	def __init__(self, name, location, surface):
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.CHALLENGER_50,
			num_players=32,
			sets_to_win=2
		)


class ITFM25(EliminationTournament):
	"""Tournoi ITF M25"""
	def __init__(self, location, surface, edition=None):
		name = f"M25 {location} {edition}" if edition else f"M25 {location}"
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.ITF_M25,
			num_players=32,
			sets_to_win=2
		)


class ITFM15(EliminationTournament):
	"""Tournoi ITF M15"""
	def __init__(self, location, surface, edition=None):
		name = f"M15 {location} {edition}" if edition else f"M15 {location}"
		super().__init__(
			name=name,
			location=location,
			surface=surface,
			category=TournamentCategory.ITF_M15,
			num_players=32,
			sets_to_win=2
		)

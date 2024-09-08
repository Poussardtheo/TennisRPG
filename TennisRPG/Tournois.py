""" Ce fichier contient la liste de tous les tournois que l'on peut retrouver sur une année"""

import math
import random

import numpy as np


def est_eligible_pour_tournoi(joueur, tournoi, classement):
	classement_joueur = classement.obtenir_rang(joueur, type="atp")
	
	return classement_joueur <= tournoi.eligibility_threshold


def seed(n):
	"""returns list of n in standard tournament seed order

	Note that n need not be a power of 2 - 'byes' are returned as zero
	"""
	ol = [1]
	
	for i in range(math.ceil(math.log(n) / math.log(2))):
		l = 2 * len(ol) + 1
		ol = [e if e <= n else 0 for s in [[el, l - el] for el in ol] for e in s]
	
	ol = [e if e <= n else 0 for e in ol]
	
	return ol


def selectionner_joueurs_pour_tournoi(
		tournoi, joueurs_disponibles, classement, type="elo"
):
	joueurs_eligibles = [j for j in joueurs_disponibles if j.peut_jouer() and j.should_participate(tournoi, classement)]
	participants = sorted(
		joueurs_eligibles, key=lambda j: classement.obtenir_rang(j, type)
	)
	if isinstance(tournoi, ATPFinals):
		participants = sorted(
			joueurs_eligibles, key=lambda j: classement.obtenir_rang(j, "atp_race")
		)
	return participants[: tournoi.nb_joueurs]


###############################################################
#                           CLASSE                            #
#                      MÈRE POUR TOURNOI                      #
###############################################################

class Tournoi:
	POINTS_ATP = {}
	XP_PAR_TOUR = {}
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, sets_gagnants=2):
		self.nom = nom
		self.emplacement = emplacement
		self.nb_joueurs = nb_joueurs
		self.surface = surface
		self.sets_gagnants = sets_gagnants
		self.importance_tournoi = 0
	
	def attribuer_points_atp(self, joueur, dernier_tour):
		points = self.POINTS_ATP.get(dernier_tour, 0)
		joueur.atp_points += points
		joueur.atp_race_points += points
	
	def jouer(self, joueur, participants, classement, type="atp"):
		# Si le joueur n'est pas dans la liste des participants, ont l'ajoute et on retire un participant
		if joueur not in participants:
			participants.append(joueur)
			
			# qu'on trie par classement
			participants = sorted(
				participants, key=lambda j: classement.obtenir_rang(j, type)
			)
			
			if joueur == participants[-1]:  # Si le joueur est dernier du classement, on retire celui avant lui
				participants.pop(-2)
			else:
				participants.pop(-1)  # Sinon, on retire le dernier
		
		resultat = self.simuler_tournoi(participants, classement, type)  # On peut simuler le tournoi
		return resultat
	
	def simuler_tournoi(self, participants, classement, type="elo", preliminaire=False):
		assert len(participants) == self.nb_joueurs, f"Tournoi {self.nom} : {len(participants)}/{self.nb_joueurs}"
		
		nb_tours = math.ceil(math.log2(self.nb_joueurs))
		nb_tetes_de_serie = 2 ** (nb_tours - 2)
		
		noms_phases = {
			nb_tours: "en finale",
			nb_tours - 1: "en demi-finale",
			nb_tours - 2: "en quart de finale"
		}
		
		joueurs_tries = sorted(
			participants, key=lambda j: classement.obtenir_rang(j, type)
		)
		# Sélectionner les têtes de série
		tetes_de_serie = joueurs_tries[:nb_tetes_de_serie]
		
		# Sélectionner les autres participants aléatoirement
		autres_participants = joueurs_tries[nb_tetes_de_serie: self.nb_joueurs]
		
		ordre_placement = seed(self.nb_joueurs)
		
		# Créer le tableau du tournoi
		tableau = []
		participants = tetes_de_serie + autres_participants
		
		for i in range(0, len(ordre_placement), 2):
			if i + 1 < len(ordre_placement):
				pos1, pos2 = ordre_placement[i], ordre_placement[i + 1]
				if pos1 != 0 and pos2 != 0:
					tableau.append((participants[pos1 - 1], participants[pos2 - 1]))
				elif pos1 != 0:
					tableau.append((participants[pos1 - 1], None))
				elif pos2 != 0:
					tableau.append((participants[pos2 - 1], None))
		
		derniers_tours = {joueur: 0 for joueur in participants}
		
		for tour in range(1, nb_tours + 1):
			# Garantit que si l'on est en finale, on applique la logique de la finale
			est_finale = True if tour == nb_tours else False

			prochain_tour = []
			for match in tableau:
				joueur1, joueur2 = match
				if joueur1 and joueur2:
					gagnant, perdant = self.simuler_match(joueur1, joueur2, est_finale)[0:2]  # Prend le gagnant et le perdant
					derniers_tours[perdant] = tour
					if perdant is not None and perdant.principal:
						phase = noms_phases.get(tour, f"au tour {tour}")
						accord = "e" if perdant.sexe.lower() == 'f' else ""
						print(f"\n{perdant.prenom} {perdant.nom} a été éliminé{accord} {phase}")
					prochain_tour.append(gagnant)
				elif joueur1:
					prochain_tour.append(joueur1)
				elif joueur2:
					prochain_tour.append(joueur2)
			
			tableau = [
				(
					(prochain_tour[i], prochain_tour[i + 1])
					if i + 1 < len(prochain_tour)
					else (prochain_tour[i], None)
				)
				for i in range(0, len(prochain_tour), 2)
			]
		
		vainqueur = prochain_tour[0]
		derniers_tours[vainqueur] = "Vainqueur"
		if not preliminaire:
			print(f"\nVainqueur du tournoi {self.nom}:\n{vainqueur.prenom} {vainqueur.nom}")
		
		resultats = {}
		for joueur, dernier_tour in derniers_tours.items():
			self.attribuer_points_atp(joueur, dernier_tour)
			xp_gagne = self.XP_PAR_TOUR.get(dernier_tour, 0)
			resultats[joueur] = self.POINTS_ATP.get(dernier_tour, 0)
			joueur.gagner_experience(xp_gagne)
		
		# Note the return will be useful when we'll save the info in a database
		return resultats

	@staticmethod
	def determiner_vainqueur_finale(joueur1, joueur2):
		"""Détermine le vainqueur de la finale selon la gravité de la blessure et la fatigue des joueurs"""
		if joueur1.blessure.gravite < joueur2.blessure.gravite:
			return joueur1, joueur2, 0, 0
		elif joueur2.blessure.gravite < joueur1.blessure.gravite:
			return joueur1, joueur2, 0, 0
		else:
			return joueur1, joueur2, 0, 0 if joueur1.fatigue < joueur2.fatigue else joueur2, joueur1, 0, 0

	def simuler_match(self, joueur1, joueur2, est_finale=False):
		# Gère les abandons en tournoi si un (ou les deux) joueurs sont blessés
		joueur1_peut_jouer = joueur1.peut_jouer()
		joueur2_peut_jouer = joueur2.peut_jouer()

		if not joueur1_peut_jouer and not joueur2_peut_jouer:
			# Les deux joueurs sont blessés,
			if est_finale:
				return self.determiner_vainqueur_finale(joueur1, joueur2)
			else:
				# match annulé
				return None, None, 0, 0
		elif not joueur1_peut_jouer:
			return joueur2, joueur1, 0, 0
		elif not joueur2_peut_jouer:
			return joueur1, joueur2, 0, 0

		elo1 = joueur1.calculer_elo(surface=self.surface) - joueur1.fatigue ** 1.25  # La fatigue diminue les performances
		elo2 = joueur2.calculer_elo(surface=self.surface) - joueur2.fatigue ** 1.25
		
		proba1 = 1 / (1 + 10 ** ((elo2 - elo1) / 400))
		
		# Logique sur le score du match.
		sets_joueur1, sets_joueur2 = 0, 0
		
		while max(sets_joueur1, sets_joueur2) < self.sets_gagnants:
			if random.random() < proba1:
				sets_joueur1 += 1
			else:
				sets_joueur2 += 1

		# Détermine le gagnant
		if sets_joueur1 > sets_joueur2:
			gagnant, perdant = joueur1, joueur2
			sets_gagnant, sets_perdant = sets_joueur1, sets_joueur2
		else:
			gagnant, perdant = joueur2, joueur1
			sets_gagnant, sets_perdant = sets_joueur2, sets_joueur1

		sets_joues=sets_gagnant+sets_perdant

		# Gère la fatigue des deux joueurs
		gagnant.gerer_fatigue(self, sets_joues=sets_joues)
		perdant.gerer_fatigue(self, sets_joues=sets_joues)

		# Mise à jour des Elo
		k = 32 # Todo: revoir cela pour l'évolution de l'elo dans le temps
		elo_change = k * (1 - 1 / (1 + 10 ** ((perdant.elo - gagnant.elo) / 400)))
		
		gagnant.elo += elo_change
		perdant.elo -= elo_change
		
		return gagnant, perdant, sets_gagnant, sets_perdant


###############################################################
#                           CLASSE                            #
#                      FILLE POUR TOURNOI                     #
###############################################################
class GrandSlam(Tournoi):
	POINTS_ATP = {1: 10, 2: 50, 3: 100, 4: 200, 5: 400, 6: 800, 7: 1300, "Vainqueur": 2000}
	XP_PAR_TOUR = {1: 100, 2: 200, 3: 400, 4: 600, 5: 750, 6: 900, 7: 1300, "Vainqueur": 2000}
	eligibility_threshold = 130
	
	def __init__(self, nom, emplacement, nb_joueurs, surface):
		super().__init__(nom, emplacement, nb_joueurs, surface, sets_gagnants=3)
		self.importance_tournoi = 1


class ATPFinals(Tournoi):
	XP_PAR_TOUR = {1: 125, 2: 250, 3: 500, "Vainqueur": 1000}
	
	eligibility_threshold = 8
	
	def __init__(self, nom, emplacement, nb_joueurs, surface):
		super().__init__(nom, emplacement, nb_joueurs, surface)
		self.importance_tournoi = 1
	
	def simuler_tournoi(self, participants, classement, type="elo", preliminaire=False):
		# Todo: add a logic for the players that are injured (add the two substitutes)
		if len(participants) != 8:
			raise ValueError("L'ATP Finals nécessite exactement 8 participants")
		
		# Trier les joueurs par classement
		joueurs_tries = sorted(participants, key=lambda j: classement.obtenir_rang(j, "atp_race"))
		
		# répartir les joueurs en deux poules
		# Todo: rajouter de l'aléatoire dans la création des poules
		poule_a = [joueurs_tries[0], joueurs_tries[3], joueurs_tries[4], joueurs_tries[7]]
		poule_b = [joueurs_tries[1], joueurs_tries[2], joueurs_tries[5], joueurs_tries[6]]
		
		# Simuler les matchs de poules
		resultats_poule_a = self.simuler_matchs_poule(poule_a)
		resultats_poule_b = self.simuler_matchs_poule(poule_b)
		
		resultats = {}
		for poule in [resultats_poule_a, resultats_poule_b]:
			for joueur, resultat in poule.items():
				points_victoires = resultat["victoires"] * 200  # +200 pts par victoire en poule
				joueur.atp_points += points_victoires
				resultats[joueur] = points_victoires
		
		# Sélectionner les deux meilleurs de chaque poule
		qualifies_a = self.selectionner_qualifies(resultats_poule_a)
		qualifies_b = self.selectionner_qualifies(resultats_poule_b)
		
		# Demi finales
		demi_finale_1 = self.simuler_match(qualifies_a[0], qualifies_b[1], est_finale=True)[0]
		demi_finale_2 = self.simuler_match(qualifies_b[0], qualifies_a[1], est_finale=True)[0]
		
		for demi_finaliste in [demi_finale_1, demi_finale_2]:
			resultats[demi_finaliste] += 400  # 400 points pour une victoire en demi-finale
			demi_finaliste.atp_points += 400
		
		# Finale
		vainqueur = self.simuler_match(demi_finale_1, demi_finale_2, est_finale=True)[0]
		resultats[vainqueur] += 500
		vainqueur.atp_points += 500  # +500pts si victoire en finale
		if not preliminaire:
			print(f"\nVainqueur du tournoi {self.nom}:\n{vainqueur.prenom} {vainqueur.nom}")
		
		# Progression des joueurs
		# Todo: inclure ici la gestion des points atp (Permet de s'astreindre du paramètre est une finale).
		#  Prévoir également la gestion des remplaçants
		for joueur in participants:
			if joueur == vainqueur:
				xp_gagne = self.XP_PAR_TOUR["Vainqueur"]
			elif joueur in [demi_finale_1, demi_finale_2]:
				xp_gagne = self.XP_PAR_TOUR[3]
			elif joueur in qualifies_a + qualifies_b:
				xp_gagne = self.XP_PAR_TOUR[2]
			else:
				xp_gagne = self.XP_PAR_TOUR[1]
			joueur.gagner_experience(xp_gagne)
		
		return resultats
	
	def simuler_matchs_poule(self, poule):
		resultats = {joueur: {'victoires': 0, 'sets_gagnes': 0, 'confrontations': {}} for joueur in poule}
		for i in range(len(poule)):
			for j in range(i + 1, len(poule)):
				gagnant, perdant, sets_gagnant, sets_perdant = self.simuler_match(poule[i], poule[j])
				# Update infos sur le gagnant
				resultats[gagnant]['victoires'] += 1
				resultats[gagnant]['sets_gagnes'] += sets_gagnant
				resultats[gagnant]["confrontations"][perdant] = 'V'
				
				# Update infos sur le perdant
				resultats[perdant]['sets_gagnes'] += sets_perdant
				resultats[perdant]["confrontations"][gagnant] = 'D'
		return resultats
	
	@staticmethod
	def selectionner_qualifies(resultats_poule):
		joueurs_tries = sorted(resultats_poule.items(), key=lambda x: x[1]['victoires'], reverse=True)
		
		# Si pas d'égalité pour les deux premières places
		if joueurs_tries[1][1]['victoires'] > joueurs_tries[2][1]['victoires']:
			return [joueurs_tries[0][0], joueurs_tries[1][0]]
		
		# En cas d'égalités
		joueurs_a_egalite = [j for j, r in joueurs_tries if r['victoires'] == joueurs_tries[1][1]['victoires']]
		
		# À 2
		if len(joueurs_a_egalite) == 2:
			# On compare les confrontations directes
			if resultats_poule[joueurs_a_egalite[0]]["confrontations"][joueurs_a_egalite[1]] == 'V':
				if resultats_poule[joueurs_a_egalite[0]]['confrontations'][joueurs_a_egalite[1]] == 'V':
					return [joueurs_tries[0][0], joueurs_a_egalite[0]]
				else:
					return [joueurs_tries[0][0], joueurs_a_egalite[1]]
		# À 3
		else:
			
			return [joueurs_tries[0][0], joueurs_tries[1][0]]


class Masters1000(Tournoi):
	POINTS_ATP_6_TOURS = {1: 10, 2: 50, 3: 100, 4: 200, 5: 400, 6: 650, "Vainqueur": 1000}
	XP_PAR_TOUR_6_TOURS = {1: 50, 2: 75, 3: 125, 4: 200, 5: 400, 6: 650, "Vainqueur": 1000}
	
	POINTS_ATP_7_TOURS = {1: 10, 2: 30, 3: 50, 4: 100, 5: 200, 6: 400, 7: 650, "Vainqueur": 1000}
	XP_PAR_TOUR_7_TOURS = {1: 50, 2: 75, 3: 100, 4: 150, 5: 200, 6: 400, 7: 650, "Vainqueur": 1000}
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, nb_tours=6):
		super().__init__(nom, emplacement, nb_joueurs, surface)
		self.importance_tournoi = 2
		self.eligibility_threshold = 70 if nb_tours == 6 else 100
		self.nb_tours = nb_tours
		
		if nb_tours == 6:
			self.POINTS_ATP = Masters1000.POINTS_ATP_6_TOURS
			self.XP_PAR_TOUR = Masters1000.XP_PAR_TOUR_6_TOURS
		elif nb_tours == 7:
			self.POINTS_ATP = Masters1000.POINTS_ATP_7_TOURS
			self.XP_PAR_TOUR = Masters1000.XP_PAR_TOUR_7_TOURS


class ATP500(Tournoi):
	POINTS_ATP_5_TOURS = {1: 0, 2: 50, 3: 100, 4: 200, 5: 330, "Vainqueur": 500}
	XP_PAR_TOUR_5_TOURS = {1: 25, 2: 50, 3: 80, 4: 150, 5: 330, "Vainqueur": 500}
	
	POINTS_ATP_6_TOURS = {1: 0, 2: 25, 3: 50, 4: 100, 5: 200, 6: 330, "Vainqueur": 500}
	XP_PAR_TOUR_6_TOURS = {1: 25, 2: 50, 3: 75, 4: 100, 5: 200, 6: 330, "Vainqueur": 500}
	
	eligibility_threshold = 120
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, nb_tours=5):
		super().__init__(nom, emplacement, nb_joueurs, surface)
		self.importance_tournoi = 3
		
		if nb_tours == 5:
			self.POINTS_ATP = ATP500.POINTS_ATP_5_TOURS
			self.XP_PAR_TOUR = ATP500.XP_PAR_TOUR_5_TOURS
		elif nb_tours == 6:
			self.POINTS_ATP = ATP500.POINTS_ATP_6_TOURS
			self.XP_PAR_TOUR = ATP500.XP_PAR_TOUR_6_TOURS


class ATP250(Tournoi):
	POINTS_ATP_5_TOURS = {1: 0, 2: 25, 3: 50, 4: 100, 5: 165, "Vainqueur": 250}
	XP_PAR_TOUR_5_TOURS = {1: 50, 2: 75, 3: 100, 4: 130, 5: 165, "Vainqueur": 250}
	
	POINTS_ATP_6_TOURS = {1: 0, 2: 13, 3: 25, 4: 50, 5: 100, 6: 165, "Vainqueur": 250}
	XP_PAR_TOUR_6_TOURS = {1: 50, 2: 60, 3: 75, 4: 100, 5: 130, 6: 165, "Vainqueur": 250}
	
	eligibility_threshold = 150
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, nb_tours=5):
		super().__init__(nom, emplacement, nb_joueurs, surface)
		self.importance_tournoi = 4
		
		if nb_tours == 5:
			self.POINTS_ATP = ATP250.POINTS_ATP_5_TOURS
			self.XP_PAR_TOUR = ATP250.XP_PAR_TOUR_5_TOURS
		elif nb_tours == 6:
			self.POINTS_ATP = ATP250.POINTS_ATP_6_TOURS
			self.XP_PAR_TOUR = ATP250.XP_PAR_TOUR_6_TOURS


class CHALLENGERS175(Tournoi):
	POINTS_ATP = {1: 0, 2: 13, 3: 25, 4: 50, 5: 90, "Vainqueur": 175}
	XP_PAR_TOUR = {1: 45, 2: 60, 3: 80, 4: 100, 5: 125, "Vainqueur": 175}
	
	eligibility_threshold = 200
	
	def __init__(self, nom, emplacement, surface):
		super().__init__(nom, emplacement, 32, surface)
		self.importance_tournoi = 5


class CHALLENGERS125(Tournoi):
	POINTS_ATP = {1: 0, 2: 8, 3: 16, 4: 35, 5: 64, "Vainqueur": 125}
	XP_PAR_TOUR = {1: 37, 2: 45, 3: 60, 4: 80, 5: 100, "Vainqueur": 125}
	
	eligibility_threshold = 250
	
	def __init__(self, nom, emplacement, surface):
		super().__init__(nom, emplacement, 32, surface)
		self.importance_tournoi = 6


class CHALLENGERS100(Tournoi):
	POINTS_ATP = {1: 0, 2: 7, 3: 14, 4: 25, 5: 50, "Vainqueur": 100}
	XP_PAR_TOUR = {1: 30, 2: 37, 3: 45, 4: 60, 5: 80, "Vainqueur": 100}
	
	eligibility_threshold = 500
	
	def __init__(self, nom, emplacement, surface):
		super().__init__(nom, emplacement, 32, surface)
		self.importance_tournoi = 7


class CHALLENGERS75(Tournoi):
	POINTS_ATP = {1: 0, 2: 6, 3: 12, 4: 22, 5: 44, "Vainqueur": 75}
	XP_PAR_TOUR = {1: 25, 2: 30, 3: 37, 4: 45, 5: 60, "Vainqueur": 80}
	
	eligibility_threshold = 800
	
	def __init__(self, nom, emplacement, surface):
		super().__init__(nom, emplacement, 32, surface)
		self.importance_tournoi = 8


class CHALLENGERS50(Tournoi):
	POINTS_ATP = {1: 0, 2: 4, 3: 8, 4: 14, 5: 25, "Vainqueur": 50}
	XP_PAR_TOUR = {1: 22, 2: 25, 3: 30, 4: 37, 5: 45, "Vainqueur": 60}
	
	eligibility_threshold = 1000
	
	def __init__(self, nom, emplacement, surface):
		super().__init__(nom, emplacement, 32, surface)
		self.importance_tournoi = 9


class ITFM25(Tournoi):
	POINTS_ATP = {1: 0, 2: 1, 3: 3, 4: 8, 5: 16, "Vainqueur": 25}
	XP_PAR_TOUR = {1: 17, 2: 22, 3: 25, 4: 30, 5: 37, "Vainqueur": 45}
	
	eligibility_threshold = 800
	
	def __init__(self, emplacement, surface, edition=None):
		nom = f"M15 {emplacement} {edition}" if edition else f"M15 {emplacement}"
		super().__init__(nom, emplacement, 32, surface)
		self.importance_tournoi = 10


class ITFM15(Tournoi):
	POINTS_ATP = {1: 0, 2: 1, 3: 2, 4: 4, 5: 8, "Vainqueur": 15}
	XP_PAR_TOUR = {1: 15, 2: 17, 3: 22, 4: 25, 5: 30, "Vainqueur": 37}
	
	eligibility_threshold = np.inf
	
	def __init__(self, emplacement, surface, edition=None):
		nom = f"M15 {emplacement} {edition}" if edition else f"M15 {emplacement}"
		super().__init__(nom, emplacement, 32, surface)
		self.importance_tournoi = 11


# Todo:
#  We will add the ITF M tournaments
#  when will have the possibility to create a huge number of players and keeping them in a database
tournois = {
	1: [ATP250("Brisbane International", "Brisbane", 32, "Hard", nb_tours=5),
		 ATP250("Bank Of China Honk Kong Tennis Open", "Hong Kong", 28, "Hard", nb_tours=5),
		 CHALLENGERS125("Workday Canberra International", "Canberra", "Hard"),
		 CHALLENGERS100("Open SIFA Nouvelle-Calédonie", "Nouméa", "Hard"),
		 CHALLENGERS75("Bangkok Open 1", "Nonthaburi", "Hard"),
		 CHALLENGERS50("Oeiras Indoor Open 1", "Oeiras", "Indoor Hard"),
		 # ITFM25("Esch/Alzette", "Indoor Hard", 1),
		 # ITFM15("Monastir", "Hard", 1),
		 # ITFM15("Kish Island", "Clay", 1)
	],
	2: [ATP250("Adelaide International", "Adelaide", 28, "Hard", nb_tours=5),
	 	 ATP250("ASB Classic", "Auckland", 28, "Hard", nb_tours=5),
		 CHALLENGERS75("Bangkok Open 2", "Nonthaburi", "Hard"),
		 CHALLENGERS75("Oeiras Indoor Open 2", "Oeiras", "Indoor Hard"),
		 CHALLENGERS50("Challenger AAT de TCA 1", "Buenos Aires", "Clay"),
		 # ITFM25("Loughborough", "Indoor Hard"),
		 # ITFM25("Mandya", "Hard"),
		 # ITFM15("Antalya", "Clay", 1),
		 # ITFM15("Manacor", "Hard", 1),
		 # ITFM15("Monastir", "Hard", 2),
		 # ITFM15("Kish Island", "Clay", 2),
		 # ITFM15("Doha", "Hard", 1)
	],
	3: [GrandSlam("Australian Open", "Melbourne", 128, "Hard"),
	    CHALLENGERS100("Tenerife Challenger 1", "Tenerife", "Hard"),
	    CHALLENGERS75("Bangkok Open 3", "Nonthaburi", "Hard"),
	    CHALLENGERS50("Challenger AAT de TCA 2", "Buenos Aires", "Clay"),
	    CHALLENGERS50("Southern California Open 1", "Indian Wells", "Hard"),
	    # ITFM25("Doha", "Hard"),
	    # ITFM25("Ithaca, NY", "Indoor Hard"),
	    # ITFM25("Bhopal", "Hard"),
	    # ITFM25("Sunderland", "Hard"),
	    # ITFM15("Cadolzburg", "Carpet", 2),
	    # ITFM15("Bressuire", "Indoor Hard"),
	    # ITFM15("Antalya", "Clay", 2),
	    # ITFM15("Manacor", "Hard", 2),
	    # ITFM15("Monastir", "Hard", 3)
	],
	4: [CHALLENGERS125("BW Open", "Ottiginies-Louvain-la-Neuve", "Indoor Hard"),
	    CHALLENGERS125("Open Quimper Bretagne Occidentale", "Quimper", "Indoor Hard"),
	    CHALLENGERS75("Punta del Este Open", "Punta del Este", "Clay"),
	    CHALLENGERS50("Southern California Open 2", "Indian Wells", "Hard"),
	    # ITFM25("Nussloch", "Carpet"),
	    # ITFM25("Wesley Chapel, FL", "Hard"),
	    # ITFM25("Chennai", "Hard"),
	    # ITFM25("Zahra", "Hard"),
	    # ITFM15("Bagnoles de l'Orne", "Clay"),
	    # ITFM15("Antalya", "Clay", 3),
	    # ITFM15("Manacor", "Hard", 3),
	    # ITFM15("Monastir", "Hard", 4)
	    
	],
	5: [ATP250("Open Sud de France", "Montpellier", 28, "Hard", nb_tours=5),
	    CHALLENGERS100("Koblenz Open", "Koblenz", "Indoor Hard"),
	    CHALLENGERS75("Brasil Tennis Challenger", "Piracicaba", "Clay"),
	    CHALLENGERS75("Cleveland Open", "Cleveland, OH", "Indoor Hard"),
	    CHALLENGERS75("HCi Burnie International 1", "Burnie", "Hard"),
	    # ITFM25("Antalya", "Clay", 1),
	    # ITFM25("Hammamet", "Clay", 1),
	    # ITFM15("Monastir", "Hard", 5),
	    # ITFM15("Sharm Elsheikh", "Hard", 1),
	    # ITFM15("Veigy Foncenex", "Carpet")
	],
	6: [ATP250("Cordoba Open", "Cordoba", 28, "Clay", nb_tours=5),
		 ATP250("Dallas Open", "Dallas", 28, "Indoor Hard", nb_tours=5),
		 ATP250("Open 13 Provence", "Marseille", 28, "Indoor Hard", nb_tours=5),
		 CHALLENGERS100("Chennai Open", "Chennai", "Hard"),
		 CHALLENGERS75("HCi Burnie International 2", "Burnie", "Hard"),
		 CHALLENGERS75("Lexus Notthingham Challenger", "Notthingham", "Indoor Hard"),
		 # ITFM25("Antalya", "Clay", 2),
		 # ITFM25("Punta del Este", "Clay", 1),
		 # ITFM25("Hammamet", "Clay", 2),
		 # ITFM25("Monastir", "Hard", 1),
		 # ITFM15("Monastir", "Hard", 6),
		 # ITFM15("Sunrise, FL", "Clay"),
		 # ITFM15("Grenoble", "Indoor Hard"),
		 # ITFM15("Sharm Elsheikh", "Hard", 2)
	],
	7: [ATP250("ABN Amro Open", "Rotterdam", 32, "Indoor Hard", nb_tours=5),
		 ATP250("IEB+ Argentina Open", "Buenos Aires", 28, "Clay", nb_tours=5),
		 ATP250("Delray Beach Open", "Delray Beach", 28, "Hard", nb_tours=5),
		 CHALLENGERS125("Bahrain Ministry of Interior Tennis Challenger", "Manama", "Hard"),
		 CHALLENGERS100("Bengaluru Open", "Bengalore", "Hard"),
		 CHALLENGERS75("Challenger Cherbourg La Manche", "Cherbourg", "Indoor Hard"),
		 CHALLENGERS50("Lexus Glasgow Challenger", "Glasgow", "Indoor Hard"),
		 # ITFM25("Antalya", "Clay", 3),
		 # ITFM25("Punta del Este", "Clay", 2),
		 # ITFM25("Vila Real de Santo Antonio", "Hard", 1),
		 # ITFM25("Hammamet", "Clay", 3),
		 # ITFM25("Monastir", "Hard", 2),
		 # ITFM15("Monastir", "Hard", 7),
		 # ITFM15("Palm Coast, FL", "Clay"),
		 # ITFM15("Nakhon Si Thammarat", "Hard", 1),
		 # ITFM15("Sharm Elsheikh", "Hard", 3),
		 # ITFM15("Oberhaching", "Indoor Hard"),
	],
	8: [ATP500("Rio Open", "Rio de Janeiro", 32, "Clay", nb_tours=5),
		 ATP250("Qater Exxonmobil Open", "Doha", 28, "Hard", nb_tours=5),
		 ATP250("Mifel Tennis Open", "Los Cabos", 28, "Hard", nb_tours=5),
		 CHALLENGERS125("Teréga Open Pau pyrénées", "Pau", "Indoor Hard"),
		 CHALLENGERS100("Pune Metropolitan Region Challenger", "Pune", "Hard"),
		 CHALLENGERS75("Tenerife Challenger 2", "Tenerife", "Hard")
	],
	9: [ATP500("Abierto Mexicano", "Acapulco", 32, "Hard", nb_tours=5),
		 ATP500("Dubai Duty Free Tennis Championships", "Dubai", 32, "Hard", nb_tours=5),
		 ATP250("Movistar Chile Open", "Santiago", 28, "Clay", nb_tours=5),
		 CHALLENGERS100("Play in Challenger", "Lille", "Indoor Hard"),
		 CHALLENGERS75("Delhi Open", "New Dehli", "Hard"),
		 CHALLENGERS75("Tenerife Challenger 3", "Tenerife", "Hard"),
		 CHALLENGERS50("Rwanda Challenger 1", "Kigali", "Clay")
	],
	10: [Masters1000("BNP Paribas Open", "Indian Wells", 96, "Hard", nb_tours=7),
	     CHALLENGERS75("4° Città di Lugano", "Lugano", "Indoor Hard"),
	     CHALLENGERS75("Challenger Bolivia", "Santa Cruz de la Sierra", "Clay"),
	     CHALLENGERS50("Rwanda Challenger 2", "Kigali", "Clay")
	],
	11: [CHALLENGERS175("Arizona Tennis Classic", "Phoenix, AZ", "Hard"),
	     CHALLENGERS75("Copa Kia Challenger de Santiago", "Santiago", "Clay"),
	     CHALLENGERS75("Kiskut Open", "Székesfehérvár", "Clay"),
	     CHALLENGERS50("Hamburg Ladies & Gents Cup", "Hamburg", "Indoor Hard")
	],
	12: [Masters1000("Miami Open", "Miami", 96, "Hard", nb_tours=7),
	     CHALLENGERS75("Paraguay Open Dove Men+Care", "Asuncion", "Clay"),
	     CHALLENGERS75("Challenger Costa Calida Region de Murcia", "Murcia", "Clay"),
	     CHALLENGERS75("Falkensteiner Punta Skala Zadar Open", "Zadar", "Clay"),
	     CHALLENGERS50("Yucatan Open", "Merida", "Clay")
	],
	13: [CHALLENGERS125("Napoli Tennis Cup", "Naples", "Clay"),
	     CHALLENGERS100("Eurofirms Girona - Costa Brava", "Gérone", "Clay"),
	     CHALLENGERS75("San Luis Open", "San Luis Potosi", "Clay"),
	     CHALLENGERS75("Sao Léo", "Sao Leopoldo", "Clay")
	],
	14: [ATP250("Millennium Estoril Open", "Estoril", 28, "Clay", nb_tours=5),
		 ATP250("Grand Prix Hassan II", "Marrakech", 28, "Clay", nb_tours=5),
		 ATP250("Fayez Sarofim Clay Court Championships", "Houston", 28, "Clay", nb_tours=5),
		 CHALLENGERS125("Mexico City Open", "Mexico", "Clay"),
		 CHALLENGERS75("ENGIE Open", "Florianopolis", "Clay"),
		 CHALLENGERS75("Emilio Sanchez Challenger by Waterdrop", "Barcelone", "Clay"),
		 CHALLENGERS75("Open Città della Disfida", "Barletta", "Clay")
	],
	15: [Masters1000("Rolex Monte Carlo Masters", "Monte-Carlo", 56, "Clay", nb_tours=6),
	     CHALLENGERS125("Vitro Busan Open", "Pusan", "Hard"),
	     CHALLENGERS100("Il Open Comunidad de Madrid", "Madrid", "Clay"),
	     CHALLENGERS75("Elizabeth Moore Sarasota Open", "Sarasota", "Clay"),
	     CHALLENGERS75("Morelos Open presentado por Metaxchange", "Cuernavaca", "Hard"),
	     CHALLENGERS75("Split Open", "Split", "Clay")
	],
	16: [ATP500("Barcelona Open Banc Sabadell", "Barcelona", 48, "Clay", nb_tours=6),
		 ATP250("BMW Open", "Munich", 28, "Clay", nb_tours=5),
		 ATP250("Tiriac Open", "Bucharest", 28, "Clay", nb_tours=5),
		 CHALLENGERS125("GNP Seguros Tennis Open", "Acapulco", "Hard"),
		 CHALLENGERS125("Oeiras Indoor Open 3", "Oeiras", "Clay"),
		 CHALLENGERS75("Gwangju Open Challenger", "Gwangju", "Hard"),
		 CHALLENGERS75("Tallahassee Tennis Challenger", "Tallahassee", "Clay"),
		 CHALLENGERS50("AAT Challenger Santander Edicion Tucuman", "San Miguel de Tucuman", "Clay")
	],
	17: [Masters1000("Mutua Madrid Open", "Madrid", 96, "Clay", nb_tours=7),
	     CHALLENGERS75("Ostra Group Open", "Ostrava", "Clay"),
	     CHALLENGERS75("Roma Garden Open", "Rome", "Clay"),
	     CHALLENGERS75("Savannah Challenger", "Savannah, GA", "Clay"),
	     CHALLENGERS75("Shenzhen Luohu Challenger", "Shenzhen", "Hard"),
	     CHALLENGERS50("Challenger Dove Men+Care Concepcion", "Concepcion", "Clay")
	],
	18: [CHALLENGERS175("Open Aix Provence Crédit Agricole", "Aix-en-Provence", "Clay"),
	     CHALLENGERS175("Sardegna Open", "Cagliari", "Clay"),
	     CHALLENGERS75("Guangzhou Nansha International Challenger", "Guangzhou", "Hard"),
	     CHALLENGERS50("Brasil Tennis Open", "Porto Alegre", "Clay")
	],
	19: [Masters1000("Internazionali BNL d'Italia", "Rome", 96, "Clay", nb_tours=7),
	     CHALLENGERS100("Danube Upper Austria Open powered by SKE", "Mauthausen", "Clay"),
	     CHALLENGERS75("Advantage Cars Prague Open by Sport-Technik Bohemia", "Prague", "Clay"),
	     CHALLENGERS75("Wuxi Open", "Wuxi", "Hard"),
	     CHALLENGERS75("Internazionali di Tennis Francavilla al Mare", "Francavilla al Mare", "Clay"),
	     CHALLENGERS50("Santos Brasil Tennis Cup", "Santos", "Clay")
	],
	20: [CHALLENGERS175("BNP Paribas Primrose", "Bordeaux", "Clay"),
	     CHALLENGERS175("Piemonte Open Intesa Sanpaolo", "Turin", "Clay"),
	     CHALLENGERS75("Santaizi Challenger", "Taipei", "Hard"),
	     CHALLENGERS75("Oeiras Indoor Open 4", "Oeiras", "Clay"),
	     CHALLENGERS75("KIA Tunis Open", "Tunis", "Clay")
	],
	21: [ATP250("Gonet Geneva Open", "Geneva", 28, "Clay", nb_tours=5),
		 ATP250("Open Parc", "Lyon", 28, "Clay", nb_tours=5),
		 CHALLENGERS75("Macedonian Open", "Skopje", "Clay"),
		 CHALLENGERS75("Kachreti Challenger", "Kachreti", "Hard"),
		 CHALLENGERS50("Schwaben Open", "Augsbourg", "Clay")
	],
	22: [GrandSlam("Roland-Garros", "Paris", 128, "Clay"),
	     CHALLENGERS75("UAMS Health Little Rock Open", "Little Rock", "Hard"),
	     CHALLENGERS75("Trofeo FL Service - Città di Vicenza", "Vicence", "Clay")
	],
	23: [CHALLENGERS125("Lexus Surbiton Trophy", "Surbiton", "Grass"),
	      CHALLENGERS100("Neckarcup", "Heilbronn", "Clay"),
	      CHALLENGERS100("Unicredit Czech Open", "Prostějov", "Clay"),
	      CHALLENGERS75("Tyler Tennis Championships", "Tyler, TX", "Hard"),
	      CHALLENGERS75("Zagreb Open", "Zagreb", "Clay"),
	      CHALLENGERS50("AAT Challenger Santander Edicion Santa Fe", "Santa Fe", "Clay")
	],
	24: [ATP250("Libema Open", "'s-Hertogenbosch", 28, "Grass", nb_tours=5),
		 ATP250("Boss Open", "Stuttgart", 28, "Grass", nb_tours=5),
		 CHALLENGERS125("Rothesay Open", "Nottigham", "Grass"),
		 CHALLENGERS125("Internazionali di Tennis Città di Perugia", "Pérousse", "Clay"),
		 CHALLENGERS100("Bratislava Open", "Bratislava", "Clay"),
		 CHALLENGERS100("Open Sopra Steria", "Lyon", "Clay"),
		 CHALLENGERS50("Lima Challenger", "Lima", "Clay")
	],
	25: [ATP500("Terra Wortmann Open", "Halle", 32, "Grass", nb_tours=5),
		 ATP500("Cinch Championships", "London", 32, "Grass", nb_tours=5),
		 CHALLENGERS125("Emilia-Romagna Tennis Cup", "Sassuolo", "Clay"),
		 CHALLENGERS125("Lexus Ilkley Trophy", "Ilkley", "Grass"),
		 CHALLENGERS75("Enea Poznan Open", "Poznan", "Clay"),
		 CHALLENGERS50("Internationaux de Tennis de Blois", "Blois", "Clay"),
		 CHALLENGERS50("Challenger Bolivia 2", "Santa Cruz de la Sierra", "Clay")
	],
	26: [ATP250("Mallorca Championships", "Mallorca", 28, "Grass", nb_tours=5),
		 ATP250("Rothesay International", "Eastbourne", 28, "Grass", nb_tours=5),
		 CHALLENGERS75("Aspria Tennis Cup", "Milan", "Clay"),
		 CHALLENGERS50("Ibague Open", "Ibague", "Clay")
	],
	27: [GrandSlam("Wimbledon", "London", 128, "Grass"),
	     CHALLENGERS75("Cranbrook Tennis Classic", "Bloomfield Hills, MI", "Hard"),
	     CHALLENGERS75("Ion Țiriac Challenger", "Brașov", "Clay"),
	     CHALLENGERS75("Tennis Open Karlsruhe", "Karlsruhe", "Clay"),
	     CHALLENGERS75("Modena Challenger", "Modène", "Clay"),
	     CHALLENGERS50("Internationaux de Tennis de Troyes", "Troyes", "Clay")
	],
	28: [CHALLENGERS125("Brawo Open", "Brunswick", "Clay"),
	     CHALLENGERS125("Sparkasse Salzburg Open", "Salzburg", "Clay"),
	     CHALLENGERS100("Concord Iași Open", "Iași", "Clay"),
	     CHALLENGERS100("Citta di Trieste Challenger", "Trieste", "Clay"),
	     CHALLENGERS75("Winnipeg National Bank Challenger", "Winnipeg", "Hard")
	],
	29: [ATP500("Hamburg Open", "Hamburg", 32, "Clay", nb_tours=5),
		 ATP250("Nordea Open", "Bastad", 28, "Clay", nb_tours=5),
		 ATP250("EFG Swiss Open Gstaad", "Gstaad", 28, "Clay", nb_tours=5),
		 ATP250("Infosys Hall Of Fame Open", "Newport", 28, "Grass", nb_tours=5),
		 CHALLENGERS75("Les Championnats Banque Nationale de Granby", "Granby", "Hard"),
		 CHALLENGERS75("Van Mossel KIA Dutch Open", "Amersfoort", "Clay"),
		 CHALLENGERS50("President's Cup", "Astana", "Hard"),
		 CHALLENGERS50("Open de Tenis Ciudad de Pozoblanco", "Pozoblanco", "Hard"),
	],
	30: [ATP250("Plava Laguna Croatia Open Umag", "Umag", 28, "Clay", nb_tours=5),
		 ATP250("Generali Open", "Kitzbuhel", 28, "Clay", nb_tours=5),
		 ATP250("Atlanta Open", "Atlanta", 28, "Hard", nb_tours=5),
		 CHALLENGERS125("Dialectic Zug Open", "Zoug", "Clay"),
		 CHALLENGERS100("Internazionali di Tennis Verona", "Vérone", "Clay"),
		 CHALLENGERS75("Chicago Men's Challenger", "Chicago", "Hard"),
		 CHALLENGERS75("Tampere Open", "Tampere", "Clay"),
		 CHALLENGERS50("Open Castilla y León", "Ségovie", "Hard")
	],
	31: [ATP500("Mubadala Citi DC Open", "Washington DC", 48, "Hard", nb_tours=6),
	     CHALLENGERS125("Porto Open", "Porto", "Hard"),
	     CHALLENGERS125("San Marino Tennis Open", "Saint-Marin", "Clay"),
	     CHALLENGERS100("Platzmann Open", "Lüdenscheid", "Clay"),
	     CHALLENGERS75("Lexington Challenger", "Lexington, KY", "Hard"),
	     CHALLENGERS75("Svijany Open", "Liberec", "Clay")
	],
	32: [Masters1000("National Bank Open", "Montreal", 56, "Hard", nb_tours=6),
	     CHALLENGERS75("DirecTV Open Bogota", "Bogota", "Clay"),
	     CHALLENGERS75("Lincoln Challenger", "Lincoln, NE", "Hard"),
	     CHALLENGERS75("Bonn Open", "Bonn", "Clay"),
	     CHALLENGERS75("Serena Wines 1881 - Acqua Maniva Tennis Cup", "Cordenons", "Clay")
	],
	33: [Masters1000("Cincinnati Open", "Cincinnati", 56, "Hard", nb_tours=6),
	     CHALLENGERS125("RD Open", "Saint-Domingue", "Clay"),
	     CHALLENGERS100("Cary Tennis Classic", "Cary", "Hard"),
	     CHALLENGERS75("Kozerki Open", "Grodzisk Mazowiecki", "Hard"),
	     CHALLENGERS75("Internazionali di Tennis Citta di Todi", "Todi", "Clay")
	],
	34: [ATP250("Winston Salem Open", "Winston Salem", 48, "Hard", nb_tours=6),
	     CHALLENGERS50("IZIDA Cup", "Dobrich", "Clay"),
	     CHALLENGERS50("Jinan Open", "Jinan", "Hard")
	],
	35: [GrandSlam("US Open", "New York", 128, "Hard"),
	     CHALLENGERS75("Challenger Città di Como", "Côme", "Clay"),
	     CHALLENGERS75("Rafa Nadal Open", "Manacor", "Hard"),
	     CHALLENGERS75("Zhangjiagang International Challenger", "Zhangjiagang", "Hard"),
	     CHALLENGERS75("Clube de Ténis do Porto", "Porto", "Clay")
	],
	36: [CHALLENGERS125("AON Open Challenger", "Gênes", "Clay"),
	     CHALLENGERS125("Copa Sevilla", "Séville", "Clay"),
	     CHALLENGERS100("Road to the Rolex Shanghai Masters", "Shanghai", "Hard"),
	     CHALLENGERS100("NO OPEN powered by EVN", "Tullin", "Clay"),
	     CHALLENGERS75("Cassis Open Provence by Cabesto", "Cassis", "Hard"),
	     CHALLENGERS75("Istanbul Challenger TED Open", "Istanbul", "Hard")
	],
	37: [CHALLENGERS125("Invest in Szczecin Open", "Szczecin", "Clay"),
	     CHALLENGERS100("Guangzhou Huangpu International Tennis Open", "Guangzhou", "Hard"),
	     CHALLENGERS100("Open Blot Rennes", "Rennes", "Indoor Hard"),
	     CHALLENGERS75("Las Vegas Tennis Open", "Las Vegas", "Hard"),
	     CHALLENGERS50("IZIDA by GENESIS Trading Cup", "Dobrich", "Clay")
	],
	38: [ATP250("Chengdu Open", "Chengdu", 28, "Hard", nb_tours=5),
		 ATP250("Hangzhou Open", "Hangzhou", 28, "Hard", nb_tours=5),
		 CHALLENGERS125("Bad Waltersdorf Trophy", "Bad Waltersdorf", "Clay"),
		 CHALLENGERS125("Saint-Tropez Open", "Saint-Tropez", "Hard"),
		 CHALLENGERS75("Columbus Challenger", "Colombus, OH ", "Indoor Hard"),
		 CHALLENGERS75("Directv Open Cali", "Cali", "Clay"),
		 CHALLENGERS50("BCR Sibiu Open", "Sibiu", "Clay")
	],
	39: [ATP500("Kinoshita Group Japan Open", "Tokyo", 32, "Hard", nb_tours=5),
		 ATP500("China Open", "Beijing", 32, "Hard", nb_tours=5),
		 CHALLENGERS125("Co'met Orleans Open", "Orléans", "Indoor Hard"),
		 CHALLENGERS100("Challenger Dove Men+Care Antofagasta", "Antofagasta", "Clay"),
		 CHALLENGERS100("Del Monte Lisboa Belém Open", "Lisbon", "Clay"),
		 CHALLENGERS100("Bangkok Challenger", "Nonthaburi", "Hard"),
		 CHALLENGERS75("LTP Challenger", "Charleston, SC", "Hard")
	],
	40: [Masters1000("Rolex Shanghai Masters", "Shanghai", 96, "Hard", nb_tours=7),
	     CHALLENGERS100("Villena Open", "Villena", "Hard"),
	     CHALLENGERS100("Open de Vendée", "Mouilleron-le-Captif", "Indoor Hard"),
	     CHALLENGERS75("Braga Open", "Braga", "Clay"),
	     CHALLENGERS75("Challenger de Buenos Aires", "Buenos Aires", "Clay"),
	     CHALLENGERS75("Challenger Tiburon", "Tiburon, CA", "Hard")
	],
	41: [CHALLENGERS125("Hangzhou", "Hangzhou", "Hard"),
	     CHALLENGERS125("Copa Faukcombridge Marcos Automocion", "Valencia", "Clay"),
	     CHALLENGERS100("Open de Roanne Auvergne-Rhône-Alpes", "Roanne", "Indoor Hard"),
	     CHALLENGERS100("AAT Challenger Santander Edicion Villa María", "Villa María", "Clay"),
	     CHALLENGERS75("Taube - Grossman Pro Tennis Tournament", "Fairfield, CA", "Hard")
	],
	42: [ATP250("European Open", "Antwerp", 28, "Indoor Hard", nb_tours=5),
		 ATP250("Almaty Open", "Almaty", 28, "Indoor Hard", nb_tours=5),
		 ATP250("BNP Paribas Nordic Open", "Stockholm", 28, "Indoor Hard", nb_tours=5),
		 CHALLENGERS125("Olbia Challenger", "Olbia", "Hard"),
		 CHALLENGERS100("Shenzhen Longhua Open", "Shenzhen", "Hard"),
		 CHALLENGERS100("Campeonato Internacional de Tênis", "Campinas", "Clay"),
		 CHALLENGERS75("Calgary National Bank Challenger", "Calgary", "Indoor Hard"),
		 CHALLENGERS75("Open Saint-Brieuc Armor Agglomération", "Saint-Brieuc", "Indoor Hard")
	],
	43: [ATP500("Swiss Indoors Basel", "Basel", 32, "Indoor Hard", nb_tours=5),
		 ATP500("Erste Bank Open", "Vienna", 32, "Indoor Hard", nb_tours=5),
		 CHALLENGERS125("Taipei 2", "Taipei", "Indoor Hard"),
		 CHALLENGERS100("Open Brest-Credit Agricole", "Brest", "Indoor Hard"),
		 CHALLENGERS100("Festval Challenger", "Curitiba", "Clay"),
		 CHALLENGERS75("City of Playford Tennis International", "Playford", "Hard"),
		 CHALLENGERS75("Sioux Falls", "Sioux Falls, SD", "Indoor Hard")
	],
	44: [Masters1000("Rolex Paris Masters", "Paris", 56, "Indoor Hard", nb_tours=6),
	     CHALLENGERS125("Slovak Open", "Bratislava", "Indoor Hard"),
	     CHALLENGERS100("Pleisure Seoul Open", "Séoul", "Hard"),
	     CHALLENGERS75("Jonathan Fried Pro Challenger", "Charlottesville, VA", "Indoor Hard"),
	     CHALLENGERS75("Challenger Ciudad de Guayaquil", "Guayaquil", "Clay"),
	     CHALLENGERS75("NSW Open", "Sydney", "Hard")
	],
	45: [ATP250("Moselle Open", "Metz", 28, "Indoor Hard", nb_tours=5),
		 ATP250("Watergen Gijon Open", "Gijon", 28, "Indoor Hard", nb_tours=5),
		 CHALLENGERS125("HPP Open", "Helsinki", "Indoor Hard"),
		 CHALLENGERS75("Knoxville Challenger", "Knoxville, TN", "Indoor Hard"),
		 CHALLENGERS75("Directv Open Lima", "Lima", "Clay"),
		 CHALLENGERS75("Unicharm Trophy Ehime", "Matsuyama", "Hard")
	],
	46: [ATPFinals("Nitto ATP Finals", "Turin", 8, "Indoor Hard"),
	     CHALLENGERS100("Hyogo Noah Challenger", "Kobe", "Indoor Hard"),
	     CHALLENGERS100("Uruguay Open", "Montevideo", "Clay"),
	     CHALLENGERS75("Paine Schartz Partners Challenger", "Champaign, IL", "Indoor Hard"),
	     CHALLENGERS75("Challenger Banque Nationale de Drummondville", "Drummondville", "Indoor Hard")
	],
	47: [CHALLENGERS100("Citta'Di Rovereto", "Rovereto", "Indoor Hard"),
	     CHALLENGERS75("São Paulo", "São Paulo", "Hard"),
	     CHALLENGERS75("Montemar", "Montemar", "Clay"),
	     CHALLENGERS75("Yokohama Keio Challenger", "Yokohama", "Hard")
	],
	48: [CHALLENGERS100("Challenger Dove Men+Care Temuco", "Temuco", "Hard"),
	     CHALLENGERS100("Maia Open", "Maia", "Clay"),
	     CHALLENGERS75("eó Hotels Maspalomas Challenger", "Maspalomas", "Clay"),
	     CHALLENGERS75("Yokkaichi Challenger", "Yokkaichi", "Hard")
	]
}

""" Ce fichier contient la liste de tous les tournois que l'on peut retrouver sur une année"""

import math
import random


# Todo: Cette fonction est à revoir avec la nouvelle logique de sous-classes.
#  Il faudra également l'update lorsque l'on aura plus de tournois (Challengers et ITF)
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
	joueurs_eligibles = [j for j in joueurs_disponibles if j.peut_jouer() and j.should_participate(tournoi)]
	participants = sorted(
		joueurs_eligibles, key=lambda j: classement.obtenir_rang(j, type)
	)
	if isinstance(tournoi, ATPFinals):
		participants = sorted(
			joueurs_eligibles, key=lambda j: classement.obtenir_rang(j, "atp_race")
		)
	return participants[: tournoi.nb_joueurs]


class Tournoi:
	POINTS_ATP = {}
	XP_PAR_TOUR = {}
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, week, sets_gagnants=2):
		self.nom = nom
		self.emplacement = emplacement
		self.nb_joueurs = nb_joueurs
		self.surface = surface
		self.week = week
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
			prochain_tour = []
			for match in tableau:
				joueur1, joueur2 = match
				if joueur1 and joueur2:
					gagnant = self.simuler_match(joueur1, joueur2)[0]
					perdant = joueur2 if gagnant == joueur1 else joueur1
					derniers_tours[perdant] = tour
					if perdant.principal:
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
			joueur.gerer_fatigue("Tournoi")
		
		# Note the return will be useful when we'll save the info in a database
		return resultats
	
	def simuler_match(self, joueur1, joueur2):
		elo1 = joueur1.calculer_elo(surface=self.surface)
		elo2 = joueur2.calculer_elo(surface=self.surface)
		
		proba1 = 1 / (1 + 10 ** ((elo2 - elo1) / 400))
		
		# Logique sur le score du match.
		# Note: On pourra se servir de cela pour simuler la fatigue d'un joueur
		#  (plus un match est long et plus les joueurs seront fatigués)
		sets_joueur1, sets_joueur2 = 0, 0
		
		while max(sets_joueur1, sets_joueur2) < self.sets_gagnants:
			if random.random() < proba1:
				sets_joueur1 += 1
			else:
				sets_joueur2 += 1
		
		if sets_joueur1 > sets_joueur2:
			gagnant, perdant = joueur1, joueur2
			sets_gagnant, sets_perdant = sets_joueur1, sets_joueur2
		else:
			gagnant, perdant = joueur2, joueur1
			sets_gagnant, sets_perdant = sets_joueur2, sets_joueur1
		
		# Mise à jour des Elo
		k = 32
		elo_change = k * (1 - 1 / (1 + 10 ** ((perdant.elo - gagnant.elo) / 400)))
		
		gagnant.elo += elo_change
		perdant.elo -= elo_change
		
		return gagnant, perdant, sets_gagnant, sets_perdant


class GrandSlam(Tournoi):
	POINTS_ATP = {1: 10, 2: 50, 3: 100, 4: 200, 5: 400, 6: 800, 7: 1300, "Vainqueur": 2000}
	XP_PAR_TOUR = {1: 100, 2: 200, 3: 400, 4: 600, 5: 750, 6: 900, 7: 1000, "Vainqueur": 1000}
	eligibility_threshold = 130
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, week):
		super().__init__(nom, emplacement, nb_joueurs, surface, week, sets_gagnants=3)
		self.importance_tournoi = 1


class Masters1000(Tournoi):
	POINTS_ATP_6_TOURS = {1: 10, 2: 50, 3: 100, 4: 200, 5: 400, 6: 650, "Vainqueur": 1000}
	XP_PAR_TOUR_6_TOURS = {1: 50, 2: 75, 3: 100, 4: 150, 5: 200, 6: 250, "Vainqueur": 500}
	
	POINTS_ATP_7_TOURS = {1: 10, 2: 30, 3: 50, 4: 100, 5: 200, 6: 400, 7: 650, "Vainqueur": 1000}
	XP_PAR_TOUR_7_TOURS = {1: 50, 2: 75, 3: 100, 4: 150, 5: 200, 6: 250, 7: 350, "Vainqueur": 500}
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, week, nb_tours=6):
		super().__init__(nom, emplacement, nb_joueurs, surface, week)
		self.importance_tournoi = 2
		self.eligibility_threshold = 60 if nb_tours == 6 else 100
		
		if nb_tours == 6:
			self.POINTS_ATP = Masters1000.POINTS_ATP_6_TOURS
			self.XP_PAR_TOUR = Masters1000.XP_PAR_TOUR_6_TOURS
		elif nb_tours == 7:
			self.POINTS_ATP = Masters1000.POINTS_ATP_7_TOURS
			self.XP_PAR_TOUR = Masters1000.XP_PAR_TOUR_7_TOURS
	

class ATP500(Tournoi):
	POINTS_ATP_5_TOURS = {1: 0, 2: 50, 3: 100, 4: 200, 5: 330, "Vainqueur": 500}
	XP_PAR_TOUR_5_TOURS = {1: 25, 2: 50, 3: 75, 4: 100, 5: 150, "Vainqueur": 250}
	
	POINTS_ATP_6_TOURS = {1: 0, 2: 25, 3: 50, 4: 100, 5: 200, 6: 330, "Vainqueur": 500}
	XP_PAR_TOUR_6_TOURS = {1: 25, 2: 50, 3: 75, 4: 100, 5: 150, 6: 200, "Vainqueur": 250}
	
	eligibility_threshold = 120
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, week, nb_tours=5):
		super().__init__(nom, emplacement, nb_joueurs, surface, week)
		self.importance_tournoi = 3
		
		if nb_tours == 5:
			self.POINTS_ATP = ATP500.POINTS_ATP_5_TOURS
			self.XP_PAR_TOUR = ATP500.XP_PAR_TOUR_5_TOURS
		elif nb_tours == 6:
			self.POINTS_ATP = ATP500.POINTS_ATP_6_TOURS
			self.XP_PAR_TOUR = ATP500.XP_PAR_TOUR_6_TOURS


class ATP250(Tournoi):
	POINTS_ATP_5_TOURS = {1: 0, 2: 25, 3: 50, 4: 100, 5: 165, "Vainqueur": 250}
	XP_PAR_TOUR_5_TOURS = {1: 25, 2: 30, 3: 40, 4: 80, 5: 100, "Vainqueur": 125}
	
	POINTS_ATP_6_TOURS = {1: 0, 2: 13, 3: 25, 4: 50, 5: 100, 6: 165, "Vainqueur": 250}
	XP_PAR_TOUR_6_TOURS = {1: 25, 2: 30, 3: 40, 4: 80, 5: 100, 6: 110, "Vainqueur": 125}
	
	eligibility_threshold = 150
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, week, nb_tours=5):
		super().__init__(nom, emplacement, nb_joueurs, surface, week)
		self.importance_tournoi = 4
		
		if nb_tours == 5:
			self.POINTS_ATP = ATP250.POINTS_ATP_5_TOURS
			self.XP_PAR_TOUR = ATP250.XP_PAR_TOUR_5_TOURS
		elif nb_tours == 6:
			self.POINTS_ATP = ATP250.POINTS_ATP_6_TOURS
			self.XP_PAR_TOUR = ATP250.XP_PAR_TOUR_6_TOURS


class ATPFinals(Tournoi):
	XP_PAR_TOUR = {1: 125, 2: 250, 3: 500, "Vainqueur": 1000}
	
	eligibility_threshold = 8
	
	def __init__(self, nom, emplacement, nb_joueurs, surface, week):
		super().__init__(nom, emplacement, nb_joueurs, surface, week)
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
		demi_finale_1 = self.simuler_match(qualifies_a[0], qualifies_b[1])[0]
		demi_finale_2 = self.simuler_match(qualifies_b[0], qualifies_a[1])[0]
		
		for demi_finaliste in [demi_finale_1, demi_finale_2]:
			resultats[demi_finaliste] += 400  # 400 points pour une victoire en demi-finale
			demi_finaliste.atp_points += 400
		
		# Finale
		vainqueur = self.simuler_match(demi_finale_1, demi_finale_2)[0]
		resultats[vainqueur] += 500
		vainqueur.atp_points += 500  # +500pts si victoire en finale
		if not preliminaire:
			print(f"\nVainqueur du tournoi {self.nom}:\n{vainqueur.prenom} {vainqueur.nom}")
		
		# Progression des joueurs
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
			for j in range(i+1, len(poule)):
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


tournoi = {
	1: [
		ATP250("Brisbane International", "Brisbane", 32, "Hard", 1, nb_tours=5),
		ATP250("Bank Of China Honk Kong Tennis Open", "Hong Kong", 28, "Hard", 1, nb_tours=5),
	],
	2: [
		ATP250("Adelaide International", "Adelaide", 28, "Hard", 2, nb_tours=5),
		ATP250("ASB Classic", "Auckland", 28, "Hard", 2, nb_tours=5),
	],
	3: [GrandSlam("Australian Open", "Melbourne", 128, "Hard", 3)],
	5: [ATP250("Open Sud de France", "Montpellier", 28, "Hard", 5, nb_tours=5)],
	6: [
		ATP250("Cordoba Open", "Cordoba", 28, "Clay", 6, nb_tours=5),
		ATP250("Dallas Open", "Dallas", 28, "Indoor Hard", 6, nb_tours=5),
		ATP250("Open 13 Provence", "Marseille", 28, "Indoor Hard", 6, nb_tours=5),
	],
	7: [
		ATP250("ABN Amro Open", "Rotterdam", 32, "Indoor Hard", 7, nb_tours=5),
		ATP250("IEB+ Argentina Open", "Buenos Aires", 28, "Clay", 7,nb_tours=5),
		ATP250("Delray Beach Open", "Delray Beach", 28, "Hard", 7, nb_tours=5),
	],
	8: [
		ATP500("Rio Open", "Rio de Janeiro", 32, "Clay", 8, nb_tours=5),
		ATP250("Qater Exxonmobil Open", "Doha", 28, "Hard", 8, nb_tours=5),
		ATP250("Mifel Tennis Open", "Los Cabos", 28, "Hard", 8, nb_tours=5),
	],
	9: [
		ATP500("Abierto Mexicano", "Acapulco", 32, "Hard", 9, nb_tours=5),
		ATP500("Dubai Duty Free Tennis Championships", "Dubai", 32, "Hard", 9, nb_tours=5),
		ATP250("Movistar Chile Open", "Santiago", 28, "Clay", 9, nb_tours=5),
	],
	10: [Masters1000("BNP Paribas Open", "Indian Wells", 96, "Hard", 10, nb_tours=7)],
	12: [Masters1000("Miami Open", "Miami", 96, "Hard", 12, nb_tours=7)],
	14: [
		ATP250("Millennium Estoril Open", "Estoril", 28, "Clay", 14, nb_tours=5),
		ATP250("Grand Prix Hassan II", "Marrakech", 28, "Clay", 14, nb_tours=5),
		ATP250("Fayez Sarofim Clay Court Championships", "Houston", 28, "Clay", 14, nb_tours=5),
	],
	15: [Masters1000("Rolex Monte Carlo Masters", "Monte-Carlo", 56, "Clay", 15, nb_tours=6)],
	16: [
		ATP500("Barcelona Open Banc Sabadell", "Barcelona", 48, "Clay", 16, nb_tours=6),
		ATP250("BMW Open", "Munich", 28, "Clay", 16, nb_tours=5),
		ATP250("Tiriac Open", "Bucharest", 28, "Clay", 16, nb_tours=5),
	],
	17: [Masters1000("Mutua Madrid Open", "Madrid", 96, "Clay", 17, nb_tours=7)],
	19: [Masters1000("Internazionali BNL d'Italia", "Rome", 96, "Clay", 19, nb_tours=7)],
	21: [
		ATP250("Gonet Geneva Open", "Geneva", 28, "Clay", 21, nb_tours=5),
		ATP250("Open Parc", "Lyon", 28, "Clay", 21, nb_tours=5),
	],
	22: [GrandSlam("Roland-Garros", "Paris", 128, "Clay", 22)],
	24: [
		ATP250("Libema Open", "'s-Hertogenbosch", 28, "Grass", 24, nb_tours=5),
		ATP250("Boss Open", "Stuttgart", 28, "Grass", 24, nb_tours=5),
	],
	25: [
		ATP500("Terra Wortmann Open", "Halle", 32, "Grass", 25, nb_tours=5),
		ATP500("Cinch Championships", "London", 32, "Grass", 25, nb_tours=5),
	],
	26: [
		ATP250("Mallorca Championships", "Mallorca", 28, "Grass", 26, nb_tours=5),
		ATP250("Rothesay International", "Eastbourne", 28, "Grass", 26, nb_tours=5),
	],
	27: [GrandSlam("Wimbledon", "London", 128, "Grass", 27)],
	29: [
		ATP500("Hamburg Open", "Hamburg", 32, "Clay", 29, nb_tours=5),
		ATP250("Nordea Open", "Bastad", 28, "Clay", 29, nb_tours=5),
		ATP250("EFG Swiss Open Gstaad", "Gstaad", 28, "Clay", 29, nb_tours=5),
		ATP250("Infosys Hall Of Fame Open", "Newport", 28, "Grass", 29, nb_tours=5),
	],
	30: [
		ATP250("Plava Laguna Croatia Open Umag", "Umag", 28, "Clay", 30, nb_tours=5),
		ATP250("Generali Open", "Kitzbuhel", 28, "Clay", 30, nb_tours=5),
		ATP250("Atlanta Open", "Atlanta", 28, "Hard", 30, nb_tours=5),
	],
	31: [ATP500("Mubadala Citi DC Open", "Washington DC", 48, "Hard", 31, nb_tours=6)],
	32: [Masters1000("National Bank Open", "Montreal", 56, "Hard", 32, nb_tours=6)],
	33: [Masters1000("Cincinnati Open", "Cincinnati", 56, "Hard", 33, nb_tours=6)],
	34: [ATP250("Winston Salem Open", "Winston Salem", 48, "Hard", 34, nb_tours=6)],
	35: [GrandSlam("US Open", "New York", 128, "Hard", 35)],
	38: [
		ATP250("Chengdu Open", "Chengdu", 28, "Hard", 38, nb_tours=5),
		ATP250("Hangzhou Open", "Hangzhou", 28, "Hard", 38, nb_tours=5),
	],
	39: [
		ATP500("Kinoshita Group Japan Open", "Tokyo", 32, "Hard", 39, nb_tours=5),
		ATP500("China Open", "Beijing", 32, "Hard", 39, nb_tours=5),
	],
	40: [Masters1000("Rolex Shanghai Masters", "Shanghai", 96, "Hard", 40, nb_tours=7)],
	42: [
		ATP250("European Open", "Antwerp", 28, "Indoor Hard", 42, nb_tours=5),
		ATP250("Almaty Open", "Almaty", 28, "Indoor Hard", 42, nb_tours=5),
		ATP250("BNP Paribas Nordic Open", "Stockholm", 28, "Indoor Hard", 42, nb_tours=5),
	],
	43: [
		ATP500("Swiss Indoors Basel", "Basel", 32, "Indoor Hard", 43, nb_tours=5),
		ATP500("Erste Bank Open", "Vienna", 32, "Indoor Hard", 43, nb_tours=5),
	],
	44: [Masters1000("Rolex Paris Masters", "Paris", 56, "Indoor Hard", 44, nb_tours=6)],
	45: [
		ATP250("Moselle Open", "Metz", 28, "Indoor Hard", 45, nb_tours=5),
		ATP250("Watergen Gijon Open", "Gijon", 28, "Indoor Hard", 45, nb_tours=5),
	],
	46: [ATPFinals("Nitto ATP Finals", "Turin", 8, "Indoor Hard", 46)],
}

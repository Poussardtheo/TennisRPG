"""
Générateur de joueurs automatiques (PNJ)
"""
import random
from typing import Dict
from faker import Faker
from transliterate import translit
from unidecode import unidecode

from ..entities.player import Player, Gender
from ..data.countries import COUNTRIES_LOCALES
from ..utils.constants import RETIREMENT_CONSTANTS, TalentLevel


class PlayerGenerator:
	"""Générateur de joueurs automatiques"""

	def __init__(self):
		self.generated_names = set()  # Pour éviter les doublons

	def generate_player(self, gender: Gender, level_range: tuple = (1, 25), age_range: tuple = None, talent_level: TalentLevel = None) -> Player:
		"""
		Génère un joueur aléatoire

		Args:
			gender: Genre du joueur
			level_range: Plage de niveaux possible
			age_range: Plage d'âges possible (défaut: jeunes joueurs)
			talent_level: Niveau de talent (défaut: aléatoire)

		Returns:
			Joueur généré
		"""
		# Sélection du pays et de la locale
		country = random.choice(list(COUNTRIES_LOCALES.keys()))
		locale = self._get_random_locale(country)

		# Génération du nom
		fake = Faker(locale)
		first_name, last_name = self._generate_names(fake, gender)

		# Translittération si nécessaire
		first_name, last_name = self._transliterate_names(first_name, last_name, locale)

		# Éviter les doublons
		full_name = f"{first_name} {last_name}"
		counter = 1
		original_full_name = full_name
		while full_name in self.generated_names:
			full_name = f"{original_full_name} {counter}"
			counter += 1
			first_name = f"{fake.first_name_male() if gender == Gender.MALE else fake.first_name_female()} {counter}"

		self.generated_names.add(full_name)

		# Génération du niveau
		level = random.randint(*level_range)
		
		# Génération de l'âge
		if age_range is None:
			# On génère des joueurs de tout âge si préliminaire et jeune joueur sinon
			age = random.randint(RETIREMENT_CONSTANTS["YOUNG_PLAYER_MIN_AGE"], RETIREMENT_CONSTANTS["MAX_CAREER_AGE"])
		else:
			age = random.randint(*age_range)

		# Génération du talent si non spécifié
		if talent_level is None:
			talent_level = self._generate_random_talent()

		return Player(
			gender=gender,
			first_name=first_name,
			last_name=last_name,
			country=country,
			level=level,
			is_main_player=False,
			age=age,
			talent_level=talent_level
		)

	def _get_random_locale(self, country: str) -> str:
		"""Sélectionne une locale aléatoire pour le pays"""
		locales = COUNTRIES_LOCALES[country]
		return random.choice(locales) if len(locales) > 1 else locales[0]

	def _generate_names(self, fake: Faker, gender: Gender) -> tuple:
		"""Génère prénom et nom"""
		if gender == Gender.MALE:
			first_name = fake.first_name_male()
		else:
			first_name = fake.first_name_female()

		last_name = fake.last_name()
		return first_name, last_name

	def _transliterate_names(self, first_name: str, last_name: str, locale: str) -> tuple:
		"""Translittère les noms si nécessaire"""
		if locale in ["ru_RU", "bg_BG", "uk_UA"]:
			first_name = translit(first_name, "ru", reversed=True)
			last_name = translit(last_name, "ru", reversed=True)
		elif locale in ["el_GR", "zh_CN", "ja_JP"]:
			first_name = unidecode(first_name)
			last_name = unidecode(last_name)

		return first_name, last_name

	def _generate_random_talent(self) -> TalentLevel:
		"""Génère un niveau de talent aléatoire avec distribution réaliste"""
		# Distribution pondérée pour rendre les talents élevés plus rares
		choices = [
			TalentLevel.ESPOIR_FRAGILE,     # 30%
			TalentLevel.JOUEUR_PROMETTEUR,  # 35%
			TalentLevel.TALENT_BRUT,        # 25%
			TalentLevel.PEPITE,             # 8%
			TalentLevel.GENIE_PRECOCE       # 2%
		]
		weights = [30, 35, 25, 8, 2]
		return random.choices(choices, weights=weights)[0]

	def generate_player_pool(self, count: int, gender: Gender, level_range: tuple = (1, 25), age_range: tuple = None) -> Dict[str, Player]:
		"""
		Génère un pool de joueurs

		Args:
			count: Nombre de joueurs à générer
			gender: Genre des joueurs
			level_range: Plage de niveaux
			age_range: Plage d'âges possible (défaut: jeunes joueurs)

		Returns:
			Dictionnaire {nom_complet: Player}
		"""
		players = {}

		for _ in range(count):
			player = self.generate_player(gender, level_range, age_range)
			players[player.full_name] = player

		return players

	def generate_simulation_player_pool(self, count: int, gender: Gender, level_range: tuple = (1, 25)) -> Dict[str, Player]:
		"""
		Génère un pool de joueurs de tous âges pour la simulation préliminaire
		
		Args:
			count: Nombre de joueurs à générer
			gender: Genre des joueurs
			level_range: Plage de niveaux
			
		Returns:
			Dictionnaire {nom_complet: Player} avec joueurs de 16 à 45 ans
		"""
		age_range = (RETIREMENT_CONSTANTS["YOUNG_PLAYER_MIN_AGE"], RETIREMENT_CONSTANTS["MAX_CAREER_AGE"])
		return self.generate_player_pool(count, gender, level_range, age_range)


# Fonction de compatibilité avec l'ancien code
def generer_pnj(nombre: int, sexe: str) -> Dict[str, Player]:
	"""
	Fonction de compatibilité avec l'ancien système

	Args:
		nombre: Nombre de joueurs à générer
		sexe: Genre ('m' ou 'f')

	Returns:
		Dictionnaire de joueurs
	"""
	gender = Gender.MALE if sexe.lower() == 'm' else Gender.FEMALE
	generator = PlayerGenerator()
	return generator.generate_player_pool(nombre, gender)


def generer_pnj_thread(nb_joueurs: int, sexe: str, pool: Dict[str, Player]):
	"""
	Fonction de compatibilité pour génération en thread

	Args:
		nb_joueurs: Nombre de joueurs
		sexe: Genre
		pool: Dictionnaire à remplir
	"""
	generated_pool = generer_pnj(nb_joueurs, sexe)
	pool.update(generated_pool)
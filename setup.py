from setuptools import setup, find_packages

setup(
	name='TennisRPG',
	version='0.2.1',
	packages=find_packages(),
	install_requires=[
		'Faker>=25.8.0',
		'transliterate>=1.10.2',
		'unidecode~=1.3.8'
	],
	entry_points={
		'console_scripts': [
			"play = TennisRPG.main:main"
		]
	}
)

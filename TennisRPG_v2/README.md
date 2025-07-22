Voici la nouvelle architecture du jeu: 

TennisRPG/
├── core/              # Logique métier centrale
│   ├── __init__.py
│   ├── game_engine.py       # Moteur de jeu principal
│   ├── game_state.py        # État du jeu
│   └── events.py            # Système d'événements
├── entities/          # Entités du jeu
│   ├── __init__.py
│   ├── player.py            # Joueur (ex-Personnage)
│   ├── tournament.py        # Tournois
│   ├── ranking.py           # Classements
│   └── injury.py            # Blessures
├── managers/          # Gestionnaires spécialisés
│   ├── __init__.py
│   ├── season_manager.py    # Gestion des saisons
│   ├── tournament_manager.py # Gestion des tournois
│   ├── player_manager.py    # Gestion des joueurs
│   └── atp_points_manager.py # Gestion des points ATP
├── ui/               # Interface utilisateur
│   ├── __init__.py
│   ├── menu_manager.py      # Gestion des menus
│   ├── display.py           # Affichage
│   └── input_handler.py     # Gestion des entrées
├── utils/            # Utilitaires
│   ├── __init__.py
│   ├── constants.py         # Constantes
│   ├── helpers.py          # Fonctions utilitaires
│   └── validators.py       # Validation
├── data/             # Données et configuration
│   ├── __init__.py
│   ├── countries.py        # Données pays
│   ├── tournaments_data.py # Données tournois
│   └── surface_data.py     # Données surfaces
└── main.py           # Point d'entrée

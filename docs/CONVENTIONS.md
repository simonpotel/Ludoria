# Conventions de Code

Ce document décrit les conventions de code utilisées dans le projet Smart Games.

## Structure du Projet

```
smart_games/
├── src/
│   ├── katerenga/     # Jeu Katarenga
│   ├── isolation/     # Jeu Isolation
│   ├── congress/      # Jeu Congress
│   ├── network/       # Composants réseau
│   └── utils/         # Utilitaires communs
├── docs/             # Documentation
├── tests/            # Tests unitaires
├── configs/          # Fichiers de configuration
└── saves/            # Sauvegardes des parties
```

## Style de Code

### Nommage

1. Classes :
   - PascalCase
   - Noms descriptifs
   - Exemple : `GameSession`, `NetworkClient`

2. Fonctions et méthodes :
   - snake_case
   - Verbes d'action
   - Exemple : `create_game`, `handle_client`

3. Variables :
   - snake_case
   - Noms explicites
   - Exemple : `player_number`, `game_state`

4. Constantes :
   - MAJUSCULES_AVEC_UNDERSCORES
   - Exemple : `MAX_PLAYERS`, `DEFAULT_PORT`

### Documentation

1. Docstrings :
   ```python
   def fonction(param1, param2):
       """
       fonction : description courte
       params :
           param1 - description du premier paramètre
           param2 - description du deuxième paramètre
       retour : description de la valeur retournée
       """
   ```

2. Commentaires en ligne :
   - En anglais pour les logs
   - En français pour les commentaires de code
   - Exemple :
   ```python
   # vérifie si le mouvement est valide
   if not available_move(board, start, end):
       Logger.warning("Game", "Invalid move detected")
   ```

## Exemple Complet

```python
from typing import Optional
from src.utils.logger import Logger

MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

class GameManager:
    """
    classe : gère une partie de jeu
    """
    def __init__(self, game_id: str):
        """
        procédure : initialise le gestionnaire de jeu
        params :
            game_id - identifiant unique de la partie
        """
        self.game_id = game_id
        self.players = []
        self.current_turn = 0

    def add_player(self, player_id: str) -> bool:
        """
        fonction : ajoute un joueur à la partie
        params :
            player_id - identifiant du joueur
        retour : True si l'ajout réussit, False sinon
        """
        try:
            # vérifie si la partie est pleine
            if len(self.players) >= 2:
                Logger.warning("Game", "Cannot add player: game is full")
                return False

            self.players.append(player_id)
            Logger.info("Game", f"Player {player_id} added to game {self.game_id}")
            return True

        except Exception as e:
            Logger.error("Game", f"Error adding player: {str(e)}")
            return False
```


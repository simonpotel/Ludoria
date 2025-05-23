# Conventions de Code

Ce document décrit les conventions de code utilisées dans le projet Ludoria.

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

### Décorateurs de Classe

1. `@classmethod` :
   - Utilisé pour les méthodes qui n'ont pas besoin d'instance (self)
   - Premier paramètre est `cls` (la classe elle-même)
   - Utile pour :
     - Factory methods (création d'objets)
     - Méthodes utilitaires liées à la classe
     - Pattern Singleton
   - Exemple :
   ```python
   class Logger:
       @classmethod
       def initialize(cls):
           if cls._instance is None:
               cls._instance = Logger()
   ```

2. `@staticmethod` :
   - Méthode qui n'a pas besoin de la classe ni de l'instance
   - Pas de paramètre `cls` ou `self`
   - Utile pour les fonctions utilitaires
   - Exemple :
   ```python
   class MathUtils:
       @staticmethod
       def calculate_distance(x1, y1, x2, y2):
           return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
   ```

3. `@property` :
   - Transforme une méthode en attribut en lecture seule
   - Utile pour les getters
   - Exemple :
   ```python
   class Player:
       @property
       def score(self):
           return self._calculate_score()
   ```

### Typage

1. Annotations de type :
   - Utiliser le module `typing` pour les types complexes
   - Indiquer les types de retour avec `->`
   - Exemple :
   ```python
   from typing import List, Dict, Optional

   def get_player(game_id: str) -> Optional[Player]:
       pass

   def get_scores() -> Dict[str, int]:
       pass
   ```

2. Types courants :
   - `str`, `int`, `float`, `bool` : types de base
   - `List[T]` : liste d'éléments de type T
   - `Dict[K, V]` : dictionnaire clé K, valeur V
   - `Optional[T]` : peut être T ou None
   - `Union[T1, T2]` : peut être T1 ou T2
   - `Any` : type quelconque

3. Variables de classe :
   - Définir les types dans `__init__`
   - Exemple :
   ```python
   class Game:
       def __init__(self):
           self.players: List[Player] = []
           self.current_turn: int = 0
   ```

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


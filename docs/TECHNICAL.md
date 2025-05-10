# Ludoria - Documentation Technique

> [!NOTE]
> Cette documentation est destinée aux contributeurs et développeurs souhaitant comprendre l'architecture et les mécanismes du projet Ludoria.

## Table des matières
- [Ludoria - Documentation Technique](#ludoria---documentation-technique)
  - [Table des matières](#table-des-matières)
  - [Choix technologiques](#choix-technologiques)
    - [Langage de programmation](#langage-de-programmation)
    - [Librairie graphique](#librairie-graphique)
  - [Structures de données](#structures-de-données)
    - [Modélisation du plateau](#modélisation-du-plateau)
    - [Modélisation des quadrants](#modélisation-des-quadrants)
    - [Modélisation des pions](#modélisation-des-pions)
    - [Modélisation des joueurs](#modélisation-des-joueurs)
  - [Composants graphiques](#composants-graphiques)
    - [Rendu du plateau](#rendu-du-plateau)
    - [Animations et effets visuels](#animations-et-effets-visuels)
    - [Interface utilisateur](#interface-utilisateur)
  - [Algorithmes de jeu](#algorithmes-de-jeu)
    - [Gestion des déplacements](#gestion-des-déplacements)
    - [Algorithmes de victoire - Katarenga](#algorithmes-de-victoire---katarenga)
    - [Algorithmes de victoire - Congress](#algorithmes-de-victoire---congress)
    - [Algorithmes de victoire - Isolation](#algorithmes-de-victoire---isolation)
  - [Communication réseau](#communication-réseau)
    - [Architecture client-serveur](#architecture-client-serveur)
    - [Protocole de communication](#protocole-de-communication)
    - [Gestion des sessions](#gestion-des-sessions)
  - [Tests et assurance qualité](#tests-et-assurance-qualité)
    - [Utilisation des mocks dans les tests](#utilisation-des-mocks-dans-les-tests)
    - [Suite complète de tests](#suite-complète-de-tests)
    - [Détails sur les Tests](#détails-sur-les-tests)

## Choix technologiques

### Langage de programmation
Le projet Ludoria est développé en Python, un choix motivé par :

- **Productivité de développement** : Python permet un développement rapide avec une syntaxe claire et concise.
- **Bibliothèques riches** : Large écosystème de bibliothèques, pour simplifier traitement d'images (PIL) et la mise en réseau (socket).
- **Portabilité** : Fonctionne sur différentes plateformes sans modification majeure du code. L'utilisation du C ou C++ aurait entraîné des temps de développement et de tests plus longs, car il aurait fallu compiler le code sur plusieurs appareils (Linux, Windows, Mac, etc.).

### Librairie graphique
Pour le rendu graphique, le projet utilise principalement :

- **Pygame** : Bibliothèque spécialisée pour le développement de jeux en Python
  - Gestion des fenêtres, événements, surfaces et sprites
  - Support du rendu 2D optimisé
  - Gestion des entrées clavier/souris
  - Audio et effets sonores
  
- **Pillow (PIL)** : Utilisée pour le traitement d'images avancé
  - Chargement et manipulation d'images
  - Application d'effets (flou gaussien pour l'arrière-plan, etc.)
  - Redimensionnement et conversion de formats d'image

Ces bibliothèques complémentaires nous permettent de créer un jeu rapide et d'apporter une touche de design et de branding sans être confrontés à des difficultés trop techniques.

## Structures de données

### Modélisation du plateau

Le plateau de jeu est modélisé par la classe `Board` qui encapsule la structure de données représentant l'état du jeu:

```python
class Board:
    def __init__(self, quadrants, game_number):
        self.quadrants = quadrants
        self.game_number = game_number
        self.board = self.get_board()
        self.setup_board()
```

Le plateau (`board`) est représenté par un tableau dont la taille dépend du jeu :
- 8x8 pour Isolation et Congress
- 10x10 pour Katarenga (8x8 de base + camps aux coins)

Chaque cellule du plateau contient un tableau à deux éléments `[joueur, type_case]` :
- `joueur` : 0 (joueur 1), 1 (joueur 2), ou None (case vide)
- `type_case` : valeur entière représentant le type/couleur de la case (0-5)

### Modélisation des quadrants

Le plateau complet est construit à partir de 4 quadrants de 4x4 cases, qui sont assemblés puis complétés dans le cas de Katarenga (ajout des camps). Cette approche modulaire permet de créer différentes configurations de plateau notamment sur la fenêtre Lobby (selector).

Les quadrants sont définis comme des matrices 4x4 où chaque cellule contient le type de terrain. Lors de l'initialisation du plateau, ces quadrants sont positionnés selon le schéma suivant :

```
[Quadrant 0] [Quadrant 1]
[Quadrant 2] [Quadrant 3]
```

Un utilitaire existe pour créer des quadrants voir [tools/](tools/)

### Modélisation des pions

Les pions sont directement intégrés dans la structure du plateau sous formes de tableaux. Chaque case peut contenir une référence au joueur qui occupe cette case.

Pour Katarenga, le système suit également les pièces "verrouillées", qui sont des pions ayant atteint un camp adverse :

```python
self.locked_pieces = [] # pièces arrivées dans un camp adverse
```

### Modélisation des joueurs

Les joueurs sont identifiés par des indices (0 pour le premier joueur, 1 pour le second). 
> [!NOTE]
> En partie contre un Bot, le joueur est toujours indice 0 et le bot toujours indice 1.


Pour les modes de jeu contre l'IA, des classes de bot spécifiques sont implémentées pour chaque jeu:
- `KaterengaBot`
- `CongressBot`
- `IsolationBot`

Ces classes d'IA contiennent la logique de décision pour choisir les mouvements.

## Composants graphiques

### Rendu du plateau

Le rendu graphique est géré par la classe `Render`, qui utilise Pygame pour afficher le plateau et les pièces :

```python
class Render:
    def __init__(self, game, canvas_size=600, window_width=1280, window_height=720):
        self.game = game
        self.canvas_size = canvas_size
        self.board_size = len(game.board.board) if game.board and game.board.board else 10
        self.cell_size = self.canvas_size // self.board_size
        # ...
```

Le rendu utilise plusieurs surfaces Pygame :
- `screen` : surface principale de la fenêtre
- `board_surface` : surface dédiée au plateau de jeu
- `info_surface` : surface pour la barre d'informations

### Animations et effets visuels

Le système de rendu inclut plusieurs effets visuels pour améliorer l'expérience utilisateur :

1. **Effets d'ombre** pour les pièces, calculés dynamiquement :
   ```python
   SHADOW_OFFSET = (2, 2)      # décalage de l'ombre des pièces (x, y)
   SHADOW_ALPHA = 128          # transparence de l'ombre (0-255)
   ```

2. **Arrière-plan flouté** créé en temps réel à partir d'une image de base :
   ```python
   # application du flou gaussien
   blurred = bg.filter(ImageFilter.GaussianBlur(radius=10))
   ```

3. **Mise en évidence des sélections** pour indiquer les pièces sélectionnées :
   ```python
   SELECTION_COLOR = (255, 255, 255)  # couleur du cadre de sélection (blanc)
   SELECTION_WIDTH = 4         # épaisseur du cadre de sélection
   ```

### Interface utilisateur

L'interface utilisateur se compose de :

1. **Barre d'information** en haut de l'écran, affichant l'état du jeu et les instructions
2. **Plateau de jeu** au centre, avec les cases et les pièces
3. **Indicateurs visuels** pour les sélections et mouvements disponibles
4. **Messages de statut** pour le mode réseau, indiquant l'état de la connexion

## Algorithmes de jeu

### Gestion des déplacements

La logique de déplacement est gérée par plusieurs fonctions dans le module `moves.py` qui détermine les mouvements autorisés selon le type de case et le jeu en cours.

**Règles de déplacement :**
- **Case rouge** : déplacement orthogonal (comme une tour aux échecs)
- **Case verte** : déplacement en "L" (comme un cavalier aux échecs)
- **Case bleue** : déplacement d'une case dans toutes les directions (comme un roi)
- **Case marron** : déplacement en diagonale (comme un fou aux échecs)


L'algorithme vérifie la couleur de la case et applique les règles correspondantes :

```python
def available_move(board, row, col, dest_row, dest_col):
    """
    fonction : détermine si un déplacement est possible d'une case à une autre
    """
    # Vérification du type de case et application des règles correspondantes
    cell_type = board[row][col][1]
    
    match cell_type:
        case 0:  # Rouge - diagonales (fou)
            return is_diagonal_move(row, col, dest_row, dest_col, board)
        case 1:  # Vert - orthogonal (tour)
            return is_orthogonal_move(row, col, dest_row, dest_col, board)
        # ...
```

Ces fonctions vérifient non seulement le motif de déplacement, mais aussi les obstacles sur le chemin pour assurer que les règles du jeu sont respectées.

### Algorithmes de victoire - Katarenga

Les deux conditions sont :

1. **Occupation des deux camps adverses** : 
   - Le joueur doit occuper ou avoir verrouillé les deux camps opposés
   - Une pièce est considérée comme verrouillée lorsqu'elle atteint un camp adverse

2. **Blocage de l'adversaire** : 
   - L'adversaire n'a plus aucun mouvement valide
   - Nécessite une vérification de tous les pions de l'adversaire et de leurs mouvements possibles

### Algorithmes de victoire - Congress

Le jeu Congress implémente une condition de victoire telle que un des joueurs doit avoir tous ses pions orthogonaux entre eux (tous connectés entre eux)

### Algorithmes de victoire - Isolation

Pour le jeu Isolation, la victoire est déterminée lorsqu'un joueur ne peut plus effectuer de mouvement valide.

## Communication réseau

### Architecture client-serveur

Le jeu utilise une architecture client-serveur classique pour le mode multijoueur :

```
Client 1 <---> Serveur <---> Client 2
```

Le serveur (`game_server.py`) gère plusieurs sessions de jeu simultanées, chacune représentée par un objet `GameSession`.

### Protocole de communication

La communication entre le client et le serveur est basée sur un échange de messages JSON via TCP/IP :

```python
def _send_json(self, client_socket: socket.socket, packet_dict: Dict):
    json_string = json.dumps(packet_dict)
    message_to_send = (json_string + '\n').encode('utf-8')
    client_socket.sendall(message_to_send)
```

Chaque paquet contient un type et des données associées :

```python
{
    "type": PacketType.GAME_ACTION,
    "data": {
        "action_type": "move",
        "board_state": {
            "board": [...],
            "round_turn": 0
        }
    }
}
```

Les principaux types de paquets sont définis dans l'énumération `PacketType` :
- `CONNECT` : établissement de connexion
- `DISCONNECT` : fermeture de connexion
- `GAME_ACTION` : action de jeu (mouvement, etc.)

### Gestion des sessions

Le serveur maintient un dictionnaire des parties en cours :

```python
self.games: Dict[str, GameSession] = {}
self.client_to_game: Dict[socket.socket, str] = {}
```

Lorsqu'un client se connecte :
1. Il envoie un paquet `CONNECT` avec un nom de joueur et de partie
2. Le serveur crée une nouvelle session ou ajoute le joueur à une session existante
3. Le serveur assigne un numéro de joueur (1 ou 2)
4. Une fois deux joueurs connectés, la partie commence

Lorsqu'un joueur effectue une action :
1. Le client envoie un paquet `GAME_ACTION` avec l'état du plateau après le mouvement
2. Le serveur valide l'action et la transmet à l'autre joueur
3. Le client adverse met à jour son affichage en fonction de l'état reçu

> [!NOTE]
> Nous avons pris la décision technique de gérer la victoire et les mouvements secondaires du côté client pour garantir une version de développement correcte pour les modes Solo/Bot/Réseau, permettant aux joueurs de jouer sans lancer de serveur. Nous ne voulons pas implémenter les règles de victoire et de mouvement du côté serveur pour des raisons de délai et d'optimisation du code.
> Cependant, la sécurité du tour côté serveur est renforcée pour éviter les problèmes techniques/abus.
> À chaque tour, la victoire est vérifiée sur les deux clients; si au moins un client se déconnecte (fin de partie), le serveur enverra le packet à l'autre client et fermera la session.

## Tests et assurance qualité

### Utilisation des mocks dans les tests

Les tests utilisent largement le concept de **mocking** pour isoler les composants testés et éviter les dépendances externes. Voici les principales techniques utilisées :

**Mock et MagicMock :**
- Un **mock** est un objet simulé qui remplace un composant réel dans un test.
- **MagicMock** est une version avancée qui permet de simuler des objets complexes avec un minimum de configuration.
- Les mocks permettent de vérifier que certaines méthodes sont appelées avec les bons paramètres via `assert_called_with()`.

**Patch :**
- La fonction `patch` permet de remplacer temporairement un objet ou une fonction par un mock.
- Utilisation courante : `@patch('module.Class')` ou `with patch('module.function'):`
- Permet d'isoler le code testé des composants externes comme Pygame ou les connexions réseau.

**Mocking de Render et Pygame :**
- De nombreux tests simulent l'interface graphique pour éviter d'ouvrir des fenêtres réelles pendant les tests.
- Exemple : `mock_render = MagicMock(spec=Render)` pour simuler le rendu du jeu.
- Les fonctions Pygame comme `pygame.display.flip()` sont remplacées par des mocks pour éviter les erreurs d'affichage.

**Simulation des comportements :**
- Les mocks peuvent retourner des valeurs spécifiques pour simuler des comportements.
- Exemple : `with patch('src.captures.has_valid_move', return_value=False):` pour simuler qu'un joueur n'a plus de coups valides.
- Permet de tester des situations difficiles à reproduire comme les conditions de victoire.

### Suite complète de tests

Ludoria comprend une suite complète de tests qui vérifient le fonctionnement de toutes les composantes du jeu. Voici un tableau détaillé de ces tests :

| Fichier de test | Catégorie | Description | Mécanismes testés |
|----------------|-----------|-------------|-------------------|
| `001_selector_init.py` | Interface | Vérifie l'initialisation correcte du sélecteur de jeu | <ul><li>Instanciation des composants (`quadrant_handler`, `config_loader`, etc.)</li><li>Initialisation des attributs</li><li>Configuration initiale des quadrants</li></ul> |
| `002_game_selection.py` | Interface | Teste la sélection des jeux dans l'interface | <ul><li>Fonctionnement du composant `Dropdown`</li><li>Sélection des jeux (katerenga, isolation, congress)</li><li>Changement de sélection et récupération des valeurs</li></ul> |
| `003_quadrant_rotation.py` | Plateau | Vérifie la rotation des quadrants du plateau | <ul><li>Rotation à droite des quadrants</li><li>Rotation à gauche des quadrants</li><li>Préservation des autres quadrants lors de la rotation</li><li>Retour à l'état initial après 4 rotations</li></ul> |
| `004_king_moves.py` | Mouvements | Teste les déplacements sur cases bleues (comme un roi) | <ul><li>Déplacements valides dans les 8 directions</li><li>Limites de distance (une seule case)</li><li>Comportement en bord de plateau</li></ul> |
| `005_knight_moves.py` | Mouvements | Teste les déplacements sur cases vertes (comme un cavalier) | <ul><li>Déplacements en L</li><li>Capacité à sauter par-dessus d'autres pièces</li><li>Mouvements invalides</li><li>Comportement en bord de plateau</li></ul> |
| `006_rook_moves.py` | Mouvements | Teste les déplacements sur cases rouges (comme une tour avec contraintes) | <ul><li>Déplacements orthogonaux</li><li>Blocage par des obstacles</li><li>Contrainte spéciale : arrêt à la première case rouge rencontrée</li><li>Capture de pièces adverses</li></ul> |
| `007_bishop_moves.py` | Mouvements | Teste les déplacements sur cases jaunes/marrons (comme un fou avec contraintes) | <ul><li>Déplacements en diagonale</li><li>Blocage par des obstacles</li><li>Contrainte spéciale : arrêt à la première case jaune/marron rencontrée</li><li>Capture de pièces adverses</li></ul> |
| `008_katerenga_victory.py` | Victoire | Vérifie la condition de victoire dans Katerenga | <ul><li>Chargement du fichier de sauvegarde (dev_katerenga.json)</li><li>Détection de pièces pouvant se déplacer vers un camp adverse</li><li>Coup gagnant occupant deux camps adverses</li><li>Détection de la victoire via `check_win`</li></ul> |
| `009_congress_victory.py` | Victoire | Vérifie la condition de victoire dans Congress | <ul><li>Chargement du fichier de sauvegarde (dev_congress.json)</li><li>Recherche de coups gagnants</li><li>Simulation d'un mouvement connectant toutes les pièces</li><li>Détection de la victoire via `check_connected_pieces`</li></ul> |
| `010_isolation_victory.py` | Victoire | Vérifie la condition de victoire dans Isolation | <ul><li>Chargement du fichier de sauvegarde (dev_isolation.json)</li><li>Recherche d'un coup bloquant tous les mouvements adverses</li><li>Vérification que le coup gagnant est correctement détecté</li><li>Fin de partie lorsque l'adversaire n'a plus de mouvements valides</li></ul> |
| `011_katerenga_network.py` | Réseau | Teste les communications réseau pour Katerenga | <ul><li>Vérification que la manipulation de la classe Game pour la connexion, les actions de jeu, le chat et la déconnexion initie correctement les communications réseau attendues.</li></ul> |
| `012_congress_network.py` | Réseau | Teste les communications réseau pour Congress | <ul><li>Vérification que la manipulation de la classe Game pour la connexion, les actions de jeu, le chat et la déconnexion initie correctement les communications réseau attendues.</li></ul> |
| `013_isolation_network.py` | Réseau | Teste les communications réseau pour Isolation | <ul><li>Vérification que la manipulation de la classe Game pour la connexion, le placement de tour, le chat et la déconnexion initie correctement les communications réseau attendues.</li></ul> |
| `014_congress_network_victory.py` | Intégration réseau | Vérifie la communication réseau lors d'une victoire dans Congress | <ul><li>Chargement d'une configuration de test</li><li>Préparation d'un plateau où les pièces sont presque connectées</li><li>Simulation d'un mouvement gagnant via la méthode `on_click` de la classe Game</li><li>Vérification que la classe Game initie l'envoi des informations de victoire (coordonnées source et destination) sur le réseau</li><li>Vérification que le jeu s'arrête correctement après détection de la victoire</li></ul> |
| `015_isolation_network_victory.py` | Intégration réseau | Vérifie la communication réseau lors d'une victoire dans Isolation | <ul><li>Configuration d'un plateau de test avec des pièces séparées</li><li>Simulation d'un placement de tour via la méthode `on_click` de la classe Game</li><li>Vérification que la classe Game initie l'envoi des informations de placement sur le réseau</li><li>Vérification que les informations de victoire (prochain joueur sans coups) sont correctement communiquées</li></ul> |
| `016_katerenga_network_victory.py` | Intégration réseau | Vérifie la communication réseau lors d'une victoire dans Katerenga | <ul><li>Chargement du fichier de sauvegarde (dev_katerenga.json)</li><li>Recherche d'une pièce du joueur 1 pouvant se déplacer vers un camp adverse (9,9)</li><li>Exécution du coup gagnant en deux appels à `on_click` (sélection puis déplacement) sur la classe Game</li><li>Vérification que la classe Game initie l'envoi des informations de victoire (coordonnées source et destination) sur le réseau</li><li>Vérification que la fonction `check_win` détecte correctement la victoire et que cet état est communiqué</li></ul> |

### Détails sur les Tests

**Tests de victoire (008, 009, 010)**
- Ces tests s'assurent que les jeux reconnaissent correctement une situation de victoire. Ils utilisent des scénarios de fin de partie sauvegardés (`dev_katerenga.json`, etc.) pour vérifier que, lorsqu'un coup gagnant est joué, le jeu identifie bien le vainqueur, que ce soit en mode solo ou contre l'ordinateur. Note que ces tests concernent uniquement les modes `Solo` et `Bot`.

**Tests de communication réseau (011, 012, 013)**
- Ces tests vérifient le bon fonctionnement des interactions réseau de base pour chaque jeu. Ils s'assurent que lorsque les joueurs effectuent des actions comme se connecter, jouer un coup, envoyer un message dans le chat, ou se déconnecter, la logique du jeu initie correctement l'envoi des informations correspondantes sur le réseau.

**Tests d'intégration réseau & victoire (014, 015, 016)**
- Ces tests importants s'assurent que la détection d'une victoire en mode réseau fonctionne comme prévu et que les informations de victoire sont correctement communiquées. Pour chaque jeu, on simule une situation où un joueur est sur le point de gagner. Ensuite, on simule le coup gagnant (comme si le joueur cliquait sur le plateau). Le test vérifie alors que la logique du jeu non seulement reconnaît la victoire, mais aussi qu'elle prépare et envoie correctement les informations de cette victoire sur le réseau, avec tous les détails nécessaires (comme les coordonnées du coup).

# Mode Réseau

Ce document explique le fonctionnement du mode réseau des Smart Games.

## Architecture

Le mode réseau utilise une architecture client-serveur :
- Un serveur central gère les connexions et les parties
- Les clients se connectent au serveur pour jouer

### Côté Serveur

#### Configuration
- Le serveur écoute sur une adresse IP et un port configurables
- Configuration dans `configs/server.json` :
```json
{
    "host": "localhost",
    "port": 5000,
    "max_players": 100,
    "timeout": 60
}
```

#### Gestion des Sessions
- Chaque partie est une session unique
- Une session contient :
  - Un identifiant unique
  - Deux joueurs maximum
  - L'état du plateau
  - Le tour actuel

#### Fonctionnalités
1. Connexion des joueurs :
   - Attribution d'un numéro de joueur (1 ou 2)
   - Création ou rejointe d'une session
   - Notification aux joueurs

2. Gestion des tours :
   - Alternance entre les joueurs
   - Validation des actions
   - Synchronisation de l'état du jeu

3. Déconnexions :
   - Détection des déconnexions
   - Notification à l'autre joueur
   - Nettoyage des ressources

### Côté Client

#### Configuration
- Les paramètres de connexion sont dans `configs/server.json`
- Le client tente de se connecter au démarrage du mode réseau

#### États du Client
1. Non connecté :
   - Tentative de connexion au serveur
   - Affichage des erreurs de connexion

2. En attente :
   - Connexion établie
   - Attente d'un autre joueur

3. En jeu :
   - Partie en cours
   - Alternance des tours
   - Synchronisation avec le serveur

#### Fonctionnalités
1. Interface réseau :
   - Affichage du statut de connexion
   - Indication du tour actuel
   - Messages d'état

2. Actions de jeu :
   - Envoi des coups au serveur
   - Réception des coups adverses
   - Mise à jour du plateau

3. Gestion des erreurs :
   - Reconnexion automatique
   - Affichage des messages d'erreur
   - Sauvegarde de l'état

## Protocole de Communication

### Types de Paquets
1. `CONNECT` : Connexion d'un joueur
2. `DISCONNECT` : Déconnexion volontaire
3. `PLAYER_DISCONNECTED` : Déconnexion de l'adversaire
4. `GAME_ACTION` : Action de jeu
5. `PLAYER_ASSIGNMENT` : Attribution du numéro de joueur
6. `GAME_STATE` : État complet du jeu
7. `WAIT_TURN` : Attente du tour
8. `YOUR_TURN` : Début du tour

### Format des Paquets
```python
{
    "type": PacketType,     # Type de paquet
    "data": dict,          # Données spécifiques
    "game_id": str        # Identifiant de la partie
}
```

### Exemple de Séquence
1. Client → Serveur : `CONNECT`
2. Serveur → Client : `PLAYER_ASSIGNMENT`
3. Serveur → Client : `WAIT_TURN` ou `YOUR_TURN`
4. Client → Serveur : `GAME_ACTION`
5. Serveur → Autre Client : `GAME_ACTION`
6. Serveur → Clients : Alternance de `WAIT_TURN` et `YOUR_TURN`

## Sécurité

1. Validation des actions :
   - Vérification du tour
   - Validation des mouvements
   - Protection contre la triche

2. Gestion des timeouts :
   - Détection des clients inactifs
   - Nettoyage des sessions mortes

3. Protection des données :
   - Validation des paquets
   - Sanitization des entrées


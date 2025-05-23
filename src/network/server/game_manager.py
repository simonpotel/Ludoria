import socket
from typing import Dict, Optional, List
from src.utils.logger import Logger
from src.network.server.game_session import GameSession
from src.network.common.packets import (
    create_player_assignment_dict,
    create_wait_turn_dict,
    create_your_turn_dict
)

class GameManager:
    """
    classe : gère les parties de jeu et les sessions
    """
    def __init__(self):
        """
        procédure : initialise le gestionnaire de jeu
        """
        self.games: Dict[str, GameSession] = {} # dictionnaire des parties de jeu (identifiant, session)

    def create_game(self, game_id: str, game_type: str) -> GameSession:
        """
        fonction : crée une nouvelle partie
        params :
            game_id - l'identifiant de la partie
            game_type - le type de jeu
        retour : la session de jeu créée
        """
        game = GameSession(game_id, game_type) # on crée la session de jeu
        self.games[game_id] = game # on ajoute la session de jeu au dictionnaire
        return game # on retourne la session de jeu

    def get_game(self, game_id: str) -> Optional[GameSession]:
        """
        fonction : récupère une partie
        params :
            game_id - l'identifiant de la partie
        retour : la session de jeu ou None
        """
        return self.games.get(game_id) # on retourne la session de jeu ou None

    def remove_game(self, game_id: str) -> None:
        """
        procédure : supprime une partie
        params :
            game_id - l'identifiant de la partie à supprimer
        """
        if game_id in self.games: # on vérifie si la partie existe
            del self.games[game_id] # on retire la session de jeu du dictionnaire
            Logger.server_internal("Server", f"Removed game session: {game_id}") # on log la suppression de la partie

    def get_available_games(self) -> List[Dict]:
        """
        fonction : récupère la liste des parties disponibles
        retour : liste des parties disponibles avec leurs informations
        """
        return [
            {
                "game_id": game_id,
                "game_type": game.game_type,
                "player_count": game.get_player_count(),
                "max_players": game.get_max_players()
            }
            for game_id, game in self.games.items()
            if not game.is_full() and game.active # on vérifie si la partie est pleine et si elle est active (on ne retourne pas les parties pleines)
        ]

    def handle_player_join(self, game: GameSession, client_socket: socket.socket, player_name: str, connection_manager) -> bool:
        """
        fonction : gère l'ajout d'un joueur à une partie
        params :
            game - la session de jeu
            client_socket - le socket du client
            player_name - le nom du joueur
            connection_manager - le gestionnaire de connexion
        retour : True si le joueur a été ajouté avec succès, False sinon
        """
        try:
            player_number = game.add_player(client_socket) # on ajoute le joueur à la partie
            
            assignment_dict = create_player_assignment_dict(player_number, game.game_id, game.game_type) # on crée le paquet de réception du joueur
            if not connection_manager.send_json(client_socket, assignment_dict): # on envoie le paquet de réception du joueur au client
                game.remove_player(client_socket) # on retire le joueur de la partie
                return False

            Logger.server_internal("Server", f"Assigned player {player_name} as Player {player_number} in game {game.game_id}")

            if game.is_full(): # on vérifie si la partie est pleine
                self._start_game(game, connection_manager) # on démarre la partie

            return True

        except Exception as e:
            Logger.server_error("Server", f"Error setting up player {player_name}: {str(e)}")
            game.remove_player(client_socket) # on retire le joueur de la partie
            return False

    def _start_game(self, game: GameSession, connection_manager) -> None:
        """
        procédure : démarre une partie
        params :
            game - la session de jeu à démarrer
            connection_manager - le gestionnaire de connexion
        """
        Logger.server_internal("Server", f"Game {game.game_id} is full, starting game.")
        game.start() # on démarre la partie

        player1_socket = game.players.get(1) # on récupère le socket du premier joueur
        player2_socket = game.players.get(2) # on récupère le socket du deuxième joueur

        if not player1_socket or not player2_socket: # on vérifie si les sockets des joueurs existent
            Logger.server_error("Server", f"Could not find both player sockets for game {game.game_id} to start.")
            return

        your_turn_dict = create_your_turn_dict(game.game_id) # on crée le paquet de réception du joueur
        wait_turn_dict = create_wait_turn_dict(game.game_id) # on crée le paquet de réception du joueur

        connection_manager.send_json(player1_socket, your_turn_dict) # on envoie le paquet de réception du joueur au premier joueur
        connection_manager.send_json(player2_socket, wait_turn_dict) # on envoie le paquet de réception du joueur au deuxième joueur

    def handle_player_disconnect(self, game_id: str, client_socket: socket.socket, connection_manager) -> Optional[int]:
        """
        fonction : gère la déconnexion d'un joueur
        params :
            game_id - l'identifiant de la partie
            client_socket - le socket du client déconnecté
            connection_manager - le gestionnaire de connexion
        retour : le numéro du joueur déconnecté ou None
        """
        game = self.games.get(game_id) # on récupère la partie
        if not game: # on vérifie si la partie existe 
            return None

        player_number = game.remove_player(client_socket) # on retire le joueur de la partie
        game.active = False

        if player_number:
            other_socket = game.get_other_player_socket(client_socket) # on récupère le socket de l'autre joueur dans la partie (session)
            if other_socket: # on vérifie si l'autre joueur existe
                from src.network.common.packets import create_player_disconnected_dict
                disconnect_msg = f"Player {player_number} disconnected"
                player_disconnected_dict = create_player_disconnected_dict(disconnect_msg, game_id) # on crée le paquet de déconnexion du joueur 
                connection_manager.send_json(other_socket, player_disconnected_dict) # on envoie le paquet de déconnexion du joueur à l'autre joueur

        self.remove_game(game_id) 

        return player_number 
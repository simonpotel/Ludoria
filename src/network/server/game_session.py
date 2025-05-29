import socket
from typing import Dict, Optional

class GameSession:
    """
    classe : session de jeu qui gère les joueurs et les tours de jeu
    """
    def __init__(self, game_id: str, game_type: str):
        """
        procédure : initialise une session de jeu
        params :
            game_id - l'identifiant de la partie
            game_type - le type de jeu
        """
        self.game_id = game_id # identifiant de la partie (unique)
        self.game_type = game_type # type de la partie (katerenga, isolation, congress)
        self.players: Dict[int, socket.socket] = {} # dictionnaire des joueurs (numéro du joueur, socket du joueur)
        self.current_turn = 1 # numéro du joueur actuel (1 ou 2)
        self.active = True # indique si la partie est active

    def add_player(self, player_socket: socket.socket) -> int:
        """
        fonction : ajoute un joueur à la partie
        params :
            player_socket - le socket du joueur à ajouter
        retour : le numéro du joueur ajouté
        """
        if len(self.players) >= 2: # on vérifie si la partie est pleine
            raise ValueError("Game session is full")
        player_number = 1 if 1 not in self.players else 2 # on détermine le numéro du joueur
        self.players[player_number] = player_socket # on ajoute le joueur au dictionnaire
        return player_number

    def remove_player(self, player_socket: socket.socket) -> Optional[int]:
        """
        fonction : retire un joueur de la partie
        params :
            player_socket - le socket du joueur à retirer
        retour : le numéro du joueur retiré ou None
        """
        player_to_remove = None # on initialise le numéro du joueur à retirer
        for player_number, sock in self.players.items(): # on parcourt le dictionnaire des joueurs
            if sock == player_socket: # on vérifie si le socket du joueur est le même que le socket du joueur à retirer
                player_to_remove = player_number # on détermine le numéro du joueur à retirer
                break
        if player_to_remove is not None: # on vérifie si le numéro du joueur à retirer existe
            del self.players[player_to_remove] # on retire le joueur du dictionnaire
            return player_to_remove # on retourne le numéro du joueur retiré
        return None 

    def get_other_player_socket(self, current_socket: socket.socket) -> Optional[socket.socket]:
        """
        fonction : retourne le socket du joueur opposé
        params :
            current_socket - le socket du joueur actuel
        retour : le socket du joueur opposé ou None
        """
        for sock in self.players.values(): # on parcourt le dictionnaire des joueurs
            if sock != current_socket: # on vérifie si le socket du joueur est différent du socket du joueur actuel
                return sock # on retourne le socket du joueur opposé
        return None # on retourne None si le joueur opposé n'existe pas

    def get_player_number(self, player_socket: socket.socket) -> Optional[int]:
        """
        fonction : retourne le numéro du joueur
        params :
            player_socket - le socket du joueur
        retour : le numéro du joueur ou None
        """
        for player_number, sock in self.players.items(): # on parcourt le dictionnaire des joueurs
            if sock == player_socket: # on vérifie si le socket du joueur est le même que le socket du joueur
                return player_number # on retourne le numéro du joueur
        return None # on retourne None si le numéro du joueur n'existe pas

    def is_player_turn(self, player_socket: socket.socket) -> bool:
        """
        fonction : vérifie si le joueur est au tour
        params :
            player_socket - le socket du joueur
        retour : True si c'est le tour du joueur, False sinon
        """
        player_number = self.get_player_number(player_socket) # on récupère le numéro du joueur
        return player_number is not None and player_number == self.current_turn # on vérifie si le numéro du joueur est le même que le numéro du joueur actuel

    def is_full(self) -> bool:
        """
        fonction : vérifie si la partie est pleine
        retour : True si la partie est pleine, False sinon
        """
        return len(self.players) == 2

    def is_empty(self) -> bool:
        """
        fonction : vérifie si la partie est vide
        retour : True si la partie est vide, False sinon
        """
        return len(self.players) == 0

    def start(self) -> None:
        """
        procédure : démarre la partie
        """
        self.active = True
        self.current_turn = 1

    def get_player_count(self) -> int:
        """
        fonction : retourne le nombre de joueurs dans la partie
        retour : le nombre de joueurs
        """
        return len(self.players)

    def get_max_players(self) -> int:
        """
        fonction : retourne le nombre maximum de joueurs
        retour : le nombre maximum de joueurs autorisés
        """
        return 2

    def is_game_in_progress(self) -> bool:
        """
        fonction : indique si la partie est en cours
        retour : True si la partie est active et contient des joueurs, False sinon
        """
        return self.active and len(self.players) > 0


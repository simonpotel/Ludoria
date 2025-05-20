import socket
from typing import Dict, Optional

class GameSession:
    """
    classe : session de jeu qui gère les joueurs et les tours de jeu 
    """
    def __init__(self, game_id: str):
        self.game_id = game_id  # on initialise l'identifiant de la partie
        self.players: Dict[int, socket.socket] = {}  # on initialise les joueurs
        self.current_turn = 1  # on initialise le tour
        self.active = True  # on initialise l'activité de la partie

    def add_player(self, player_socket: socket.socket) -> int:
        """
        procédure : ajoute un joueur à la partie
        """
        if len(self.players) >= 2:
            raise ValueError("Game session is full") 
        player_number = 1 if 1 not in self.players else 2 
        self.players[player_number] = player_socket 
        
        return player_number 

    def remove_player(self, player_socket: socket.socket) -> Optional[int]:
        """
        procédure : retire un joueur de la partie
        """
        player_to_remove = None 
        for player_number, sock in self.players.items(): 
            if sock == player_socket: 
                player_to_remove = player_number 
                break 
        if player_to_remove is not None: 
            del self.players[player_to_remove] 
            
            return player_to_remove 
        return None 

    def get_other_player_socket(self, current_socket: socket.socket) -> Optional[socket.socket]:
        """
        procédure : retourne le socket du joueur opposé
        """
        for sock in self.players.values(): 
            if sock != current_socket: 
                return sock 
        return None 

    def get_player_number(self, player_socket: socket.socket) -> Optional[int]:
        """
        procédure : retourne le numéro du joueur
        """
        for player_number, sock in self.players.items(): 
            if sock == player_socket: 
                return player_number 
        return None 

    def is_player_turn(self, player_socket: socket.socket) -> bool:
        """
        procédure : vérifie si le joueur est au tour
        """
        player_number = self.get_player_number(player_socket) 
        return player_number is not None and player_number == self.current_turn 

    def is_full(self) -> bool:
        """
        procédure : vérifie si la partie est pleine
        """
        return len(self.players) == 2 

    def is_empty(self) -> bool:
        """
        procédure : vérifie si la partie est vide
        """
        return len(self.players) == 0 

    def start(self):
        """
        procédure : démarre la partie
        """
        self.active = True 
        self.current_turn = 1 

    def get_player_count(self) -> int:
        """
        fonction : retourne le nombre de joueurs dans la partie
        """
        return len(self.players)
    
    def get_max_players(self) -> int:
        """
        fonction : retourne le nombre maximum de joueurs
        """
        return 2  
    
    def is_game_in_progress(self) -> bool:
        """
        fonction : indique si la partie est en cours
        """
        return self.active and len(self.players) > 0


import socket
import json
import threading
import random
from typing import Dict, Set, Optional
from pathlib import Path
from src.network.packets import (
    Packet, PacketType, create_player_assignment_packet,
    create_wait_turn_packet, create_your_turn_packet,
    create_disconnect_packet, create_player_disconnected_packet
)
from src.utils.logger import Logger
import pickle

class GameSession:
    """
    classe : gère une session de jeu entre deux joueurs
    """
    def __init__(self, game_id: str):
        """
        procédure : initialise une session de jeu
        params :
            game_id - identifiant de la partie
        """
        self.game_id = game_id
        self.players: Dict[int, socket.socket] = {}
        self.player_buffers: Dict[socket.socket, bytearray] = {}
        self.current_turn = 1
        self.active = True

    def add_player(self, player_socket: socket.socket) -> int:
        """
        fonction : ajoute un joueur à la session
        params :
            player_socket - socket du joueur
        retour : numéro du joueur (1 ou 2)
        """
        if len(self.players) >= 2:
            raise ValueError("Game session is full")
        
        player_number = 1 if 1 not in self.players else 2
        self.players[player_number] = player_socket
        self.player_buffers[player_socket] = bytearray()
        return player_number

    def remove_player(self, player_socket: socket.socket) -> Optional[int]:
        """
        fonction : retire un joueur de la session
        params :
            player_socket - socket du joueur
        retour : numéro du joueur retiré ou None
        """
        for player_number, sock in self.players.items():
            if sock == player_socket:
                del self.players[player_number]
                if player_socket in self.player_buffers:
                    del self.player_buffers[player_socket]
                return player_number
        return None

    def get_other_player_socket(self, current_socket: socket.socket) -> Optional[socket.socket]:
        """
        fonction : récupère le socket de l'autre joueur
        params :
            current_socket - socket du joueur actuel
        retour : socket de l'autre joueur ou None
        """
        for sock in self.players.values():
            if sock != current_socket:
                return sock
        return None

    def get_player_number(self, player_socket: socket.socket) -> Optional[int]:
        """
        fonction : récupère le numéro d'un joueur
        params :
            player_socket - socket du joueur
        retour : numéro du joueur ou None
        """
        for player_number, sock in self.players.items():
            if sock == player_socket:
                return player_number
        return None

    def is_player_turn(self, player_socket: socket.socket) -> bool:
        """
        fonction : vérifie si c'est le tour d'un joueur
        params :
            player_socket - socket du joueur
        retour : bool indiquant si c'est son tour
        """
        player_number = self.get_player_number(player_socket)
        return player_number is not None and player_number == self.current_turn

    def is_full(self) -> bool:
        """
        fonction : vérifie si la session est pleine
        retour : bool indiquant si la session est pleine
        """
        return len(self.players) == 2

    def is_empty(self) -> bool:
        """
        fonction : vérifie si la session est vide
        retour : bool indiquant si la session est vide
        """
        return len(self.players) == 0

    def start(self):
        """
        procédure : démarre la session de jeu
        """
        self.active = True
        self.current_turn = 1

    def broadcast(self, packet: Packet, exclude_socket: Optional[socket.socket] = None):
        """
        procédure : envoie un paquet à tous les joueurs
        params :
            packet - paquet à envoyer
            exclude_socket - socket à exclure de l'envoi
        """
        data = packet.to_bytes()
        for player_socket in self.players.values():
            if player_socket != exclude_socket:
                try:
                    player_socket.sendall(data)
                except:
                    pass

class GameServer:
    """
    classe : serveur de jeu gérant les connexions et les sessions
    """
    def __init__(self):
        """
        procédure : initialise le serveur
        """
        self.load_config()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: Set[socket.socket] = set()
        self.games: Dict[str, GameSession] = {}
        self.client_to_game: Dict[socket.socket, str] = {}
        Logger.initialize()

    def load_config(self):
        """
        procédure : charge la configuration du serveur
        """
        try:
            with open('configs/server.json', 'r') as f:
                config = json.load(f)
                self.host = config['host']
                self.port = config['port']
                self.max_players = config['max_players']
                self.timeout = config['timeout']
        except Exception as e:
            Logger.error("Server", f"Failed to load config: {str(e)}")
            raise

    def start(self):
        """
        procédure : démarre le serveur
        """
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_players)
            Logger.info("Server", f"Server started on {self.host}:{self.port}")
            
            while True:
                client_socket, address = self.server_socket.accept()
                client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                Logger.info("Server", f"New connection from {address}")
                self.clients.add(client_socket)
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
        except Exception as e:
            Logger.error("Server", f"Server error: {str(e)}")
        finally:
            self.cleanup()

    def handle_client(self, client_socket: socket.socket):
        """
        procédure : gère la connexion d'un client
        params :
            client_socket - socket du client
        """
        receive_buffer = bytearray()
        try:
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    Logger.info("Server", "Client disconnected")
                    break

                receive_buffer.extend(chunk)
                self._process_client_data(client_socket, receive_buffer)
                receive_buffer = bytearray()

        except Exception as e:
            Logger.error("Server", f"Error handling client: {str(e)}")
        finally:
            self.disconnect_client(client_socket)

    def _process_client_data(self, client_socket: socket.socket, data: bytearray):
        """
        procédure : traite les données reçues d'un client
        params :
            client_socket - socket du client
            data - données reçues
        """
        try:
            packet = pickle.loads(data)
            self.process_packet(client_socket, packet)
        except (pickle.UnpicklingError, EOFError):
            pass

    def process_packet(self, client_socket: socket.socket, packet: Packet):
        """
        procédure : traite un paquet reçu
        params :
            client_socket - socket du client
            packet - paquet à traiter
        """
        try:
            if not packet or not hasattr(packet, 'type'):
                Logger.error("Server", "Invalid packet received")
                return
            
            handlers = {
                PacketType.CONNECT: self.handle_connect,
                PacketType.DISCONNECT: lambda s, p: self.disconnect_client(s),
                PacketType.GAME_ACTION: self.handle_game_action
            }
            
            if packet.type in handlers:
                handlers[packet.type](client_socket, packet)
            else:
                Logger.warning("Server", f"Unknown packet type: {packet.type}")
                
        except Exception as e:
            Logger.error("Server", f"Error processing packet: {str(e)}")
            self.disconnect_client(client_socket)

    def handle_connect(self, client_socket: socket.socket, packet: Packet):
        """
        procédure : gère une demande de connexion
        params :
            client_socket - socket du client
            packet - paquet de connexion
        """
        try:
            if not packet.data:
                Logger.error("Server", "Empty connect packet received")
                return
            
            player_name = packet.data.get("player_name", "Unknown")
            game_name = packet.data.get("game_name", "game_1")
            
            game = self._get_or_create_game(game_name)
            if not game or not self._can_join_game(game, client_socket, game_name):
                return

            self._setup_player(client_socket, game, player_name, game_name)

        except Exception as e:
            Logger.error("Server", f"Error handling connection: {str(e)}")
            self.disconnect_client(client_socket)

    def _get_or_create_game(self, game_name: str) -> Optional[GameSession]:
        """
        fonction : récupère ou crée une session de jeu
        params :
            game_name - nom de la partie
        retour : session de jeu ou None
        """
        if game_name in self.games:
            return self.games[game_name]
        else:
            game = GameSession(game_name)
            self.games[game_name] = game
            Logger.info("Server", f"Created new game session: {game_name}")
            return game

    def _can_join_game(self, game: GameSession, client_socket: socket.socket, game_name: str) -> bool:
        """
        fonction : vérifie si un joueur peut rejoindre une partie
        params :
            game - session de jeu
            client_socket - socket du client
            game_name - nom de la partie
        retour : bool indiquant si le joueur peut rejoindre
        """
        if game.is_full():
            Logger.warning("Server", f"Game {game_name} is full")
            disconnect_packet = create_disconnect_packet("Game is full", game_name)
            client_socket.sendall(pickle.dumps(disconnect_packet))
            self.disconnect_client(client_socket)
            return False
        return True

    def _setup_player(self, client_socket: socket.socket, game: GameSession, player_name: str, game_name: str):
        """
        procédure : configure un nouveau joueur
        params :
            client_socket - socket du client
            game - session de jeu
            player_name - nom du joueur
            game_name - nom de la partie
        """
        try:
            player_number = game.add_player(client_socket)
            self.client_to_game[client_socket] = game_name

            assignment_packet = create_player_assignment_packet(player_number, game_name)
            client_socket.sendall(pickle.dumps(assignment_packet))
            Logger.info("Server", f"Assigned player {player_name} as Player {player_number} in game {game_name}")

            if game.is_full():
                self._start_game(game, game_name)

        except Exception as e:
            Logger.error("Server", f"Error setting up player: {str(e)}")
            if client_socket in self.client_to_game:
                del self.client_to_game[client_socket]
            self.disconnect_client(client_socket)

    def _start_game(self, game: GameSession, game_name: str):
        """
        procédure : démarre une partie
        params :
            game - session de jeu
            game_name - nom de la partie
        """
        Logger.info("Server", f"Game {game_name} is full, starting game")
        game.start()
        
        your_turn_packet = create_your_turn_packet(game_name)
        wait_turn_packet = create_wait_turn_packet(game_name)
        
        game.players[1].sendall(pickle.dumps(your_turn_packet))
        game.players[2].sendall(pickle.dumps(wait_turn_packet))
        Logger.info("Server", "Sent initial turn packets to players")

    def handle_game_action(self, client_socket: socket.socket, packet: Packet):
        """
        procédure : gère une action de jeu
        params :
            client_socket - socket du client
            packet - paquet d'action
        """
        try:
            if not self._validate_game_action(client_socket, packet):
                return

            game_id = self.client_to_game[client_socket]
            game = self.games[game_id]
            other_socket = game.get_other_player_socket(client_socket)
            
            if other_socket:
                self._process_game_action(game, game_id, other_socket, packet)

        except Exception as e:
            Logger.error("Server", f"Error handling game action: {str(e)}")
            self.disconnect_client(client_socket)

    def _validate_game_action(self, client_socket: socket.socket, packet: Packet) -> bool:
        """
        fonction : valide une action de jeu
        params :
            client_socket - socket du client
            packet - paquet d'action
        retour : bool indiquant si l'action est valide
        """
        if not packet.data:
            Logger.error("Server", "Empty game action received")
            return False
            
        game_id = self.client_to_game.get(client_socket)
        if not game_id:
            Logger.error("Server", "No game found for client")
            return False

        game = self.games.get(game_id)
        if not game:
            Logger.error("Server", "Game not found")
            return False

        if not game.is_player_turn(client_socket):
            Logger.warning("Server", "Not player's turn")
            return False
            
        return True

    def _process_game_action(self, game: GameSession, game_id: str, other_socket: socket.socket, packet: Packet):
        """
        procédure : traite une action de jeu
        params :
            game - session de jeu
            game_id - identifiant de la partie
            other_socket - socket de l'autre joueur
            packet - paquet d'action
        """
        try:
            other_socket.sendall(pickle.dumps(packet))
            Logger.info("Server", "Forwarded game action to other player")
            
            game.current_turn = 3 - game.current_turn
            Logger.info("Server", f"Turn switched to Player {game.current_turn}")
            
            your_turn_packet = create_your_turn_packet(game_id)
            wait_turn_packet = create_wait_turn_packet(game_id)
            
            other_socket.sendall(pickle.dumps(your_turn_packet))
            game.players[3 - game.current_turn].sendall(pickle.dumps(wait_turn_packet))
            
        except Exception as e:
            Logger.error("Server", f"Error processing game action: {str(e)}")
            raise

    def disconnect_client(self, client_socket: socket.socket):
        """
        procédure : déconnecte un client
        params :
            client_socket - socket du client
        """
        try:
            game_id = self.client_to_game.get(client_socket)
            if game_id and game_id in self.games:
                game = self.games[game_id]
                player_number = game.remove_player(client_socket)
                
                if player_number:
                    other_socket = game.get_other_player_socket(client_socket)
                    if other_socket:
                        disconnect_packet = create_player_disconnected_packet(f"Player {player_number} disconnected", game_id)
                        other_socket.sendall(pickle.dumps(disconnect_packet))
                
                if game.is_empty():
                    del self.games[game_id]
                    
            if client_socket in self.client_to_game:
                del self.client_to_game[client_socket]
                
            self.clients.discard(client_socket)
            
            try:
                client_socket.close()
            except:
                pass
                
        except Exception as e:
            Logger.error("Server", f"Error disconnecting client: {str(e)}")

    def cleanup(self):
        """
        procédure : nettoie les ressources du serveur
        """
        for client in self.clients.copy():
            self.disconnect_client(client)
            
        try:
            self.server_socket.close()
        except:
            pass

if __name__ == "__main__":
    server = GameServer()
    server.start() 
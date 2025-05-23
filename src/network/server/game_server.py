import socket
import json
import threading
from typing import Dict, Optional, Tuple
from src.utils.logger import Logger
from src.network.common.packets import PacketType, create_game_list_dict
from src.network.server.connection_manager import ConnectionManager
from src.network.server.game_manager import GameManager
from src.network.server.chat_manager import ChatManager
from src.network.server.config_manager import ConfigManager
from src.network.server.game_session import GameSession

class GameServer:
    """
    classe : serveur principal qui gère les connexions et les parties
    """
    def __init__(self):
        """
        procédure : initialise le serveur de jeu
        """
        self.config_manager = ConfigManager() # pour récupérer les paramètres du serveur
        self.config_manager.load_config() # on charge les paramètres du serveur
        
        self.connection_manager = ConnectionManager() # pour gérer les connexions des clients 
        self.game_manager = GameManager() # pour gérer les parties
        self.chat_manager = ChatManager() # pour gérer les messages de chat
        
        self.connection_manager.set_game_manager(self.game_manager) # on associe le gestionnaire de parties au gestionnaire de connexions
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # on crée le socket du serveur
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # on permet la réutilisation de l'adresse du socket : on peut relancer le serveur sans attendre le timeout
        Logger.initialize()

    def start(self) -> None:
        """
        procédure : démarre le serveur et commence à écouter les connexions
        """
        try:
            self.server_socket.bind((self.config_manager.get_host(), self.config_manager.get_port())) # on lie le socket à l'adresse et au port
            self.server_socket.listen(self.config_manager.get_max_players()) # on écoute les connexions entrantes
            Logger.server_internal("Server", f"Server started on {self.config_manager.get_host()}:{self.config_manager.get_port()}, listening...")
            
            while True:
                client_socket, address = self.server_socket.accept() # on accepte une connexion entrante
                Logger.server_internal("Server", f"New connection from {address}") # on log la nouvelle connexion
                self.connection_manager.add_client(client_socket) # on ajoute le client au gestionnaire de connexions
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True) # on crée un thread pour gérer la connexion du client
                client_thread.start() # on démarre le thread
        except OSError as e:
            Logger.server_error("Server", f"Failed to bind or listen: {e}") 
        except Exception as e:
            Logger.server_error("Server", f"Server error: {str(e)}")
        finally:
            self.cleanup()

    def handle_client(self, client_socket: socket.socket, address: Tuple[str, int]) -> None:
        """
        procédure : gère la connexion d'un client
        params :
            client_socket - le socket du client
            address - l'adresse du client
        """
        addr_str = f"{address[0]}:{address[1]}" # on récupère l'adresse du client
        try:
            while True:
                chunk = client_socket.recv(4096) # on reçoit les données du client (maximum x octets) qui forment un chunk de données 
                # les chunks de données sont reçus par le serveur et stockés dans le buffer du client
                # le buffer est ensuite traité par le serveur pour extraire les paquets JSON
                # les paquets JSON sont ensuite traités par le serveur pour extraire les données
                if not chunk:
                    Logger.server_internal("Server", f"Client {addr_str} disconnected (received empty chunk).")
                    break

                messages = self.connection_manager.process_received_data(client_socket, chunk) # on traite les données reçues du client
                for packet_dict in messages: # on parcourt les paquets JSON reçus
                    self.process_json_packet(client_socket, packet_dict) # on traite le paquet JSON

        except ConnectionResetError:
            Logger.server_internal("Server", f"Client {addr_str} disconnected forcefully (connection reset).")
        except socket.timeout:
            Logger.server_error("Server", f"Client {addr_str} timed out.")
            self.connection_manager.disconnect_client(client_socket, "Timeout")
        except Exception as e:
            Logger.server_error("Server", f"Error handling client {addr_str}: {str(e)}")
        finally:
            self.connection_manager.disconnect_client(client_socket, "Closing connection")

    def process_json_packet(self, client_socket: socket.socket, packet_dict: Dict) -> None:
        """
        procédure : traite un paquet JSON reçu
        params :
            client_socket - le socket du client
            packet_dict - le paquet à traiter
        """
        try:
            if not isinstance(packet_dict, dict) or "type" not in packet_dict or "data" not in packet_dict: # on vérifie si le paquet est valide
                Logger.server_error("Server", f"Invalid packet structure received from {client_socket.getpeername()}: {packet_dict}")
                return

            packet_type_val = packet_dict.get("type") # on récupère le type du paquet
            packet_data = packet_dict.get("data", {}) # on récupère les données du paquet

            try:
                packet_type_enum = PacketType(packet_type_val) # on convertit le type du paquet en énumération
            except ValueError:
                Logger.server_error("Server", f"Unknown packet type value from {client_socket.getpeername()}: {packet_type_val}")
                return

            Logger.server_internal("Server", f"Processing packet from {client_socket.getpeername()}: Type={packet_type_enum.name}, Data={packet_data}")

            # call les fonctions de traitement des paquets (handle CtoS)
            if packet_type_enum == PacketType.CONNECT: # on vérifie si le type du paquet est CONNECT
                self.handle_connect(client_socket, packet_data)
            elif packet_type_enum == PacketType.DISCONNECT:
                self.connection_manager.disconnect_client(client_socket, packet_data.get("reason", "Client requested disconnect"))
            elif packet_type_enum == PacketType.GAME_ACTION:
                self.handle_game_action(client_socket, packet_data)
            elif packet_type_enum == PacketType.CHAT_SEND:
                self.handle_chat_message(client_socket, packet_data)
            elif packet_type_enum == PacketType.GET_GAME_LIST:
                self.handle_get_game_list(client_socket)
            else:
                Logger.server_error("Server", f"No handler for packet type from {client_socket.getpeername()}: {packet_type_enum.name}")

        except Exception as e:
            Logger.server_error("Server", f"Error processing packet content from {client_socket.getpeername()}: {str(e)}")
            self.connection_manager.disconnect_client(client_socket, "Error processing packet")

    def handle_connect(self, client_socket: socket.socket, packet_data: Dict) -> None:
        """
        procédure : gère une demande de connexion
        params :
            client_socket - le socket du client
            packet_data - les données de la demande
        """
        try:
            player_name = packet_data.get("player_name", f"Player_{hash(client_socket) % 900 + 100}") # on récupère le nom du joueur
            game_name = packet_data.get("game_name") # on récupère le nom de la partie
            game_type = packet_data.get("game_type") # on récupère le type de la partie

            if not game_name or not game_type: # on vérifie si le nom de la partie et le type de la partie sont présents
                self.connection_manager.disconnect_client(client_socket, "Missing game_name or game_type in CONNECT packet") # on déconnecte le client car le nom de la partie et le type de la partie sont obligatoires
                return

            Logger.server_internal("Server", f"Connect request from {player_name} for game '{game_name}' (type: {game_type})")

            game = self.game_manager.get_game(game_name) # on récupère la partie
            if not game: # on vérifie si la partie existe
                game = self.game_manager.create_game(game_name, game_type) # on crée la partie

            if game.is_full(): # on vérifie si la partie est pleine
                self.connection_manager.disconnect_client(client_socket, f"Game '{game_name}' is full") # on déconnecte le client car la partie est pleine
                return

            if self.game_manager.handle_player_join(game, client_socket, player_name, self.connection_manager): # on ajoute le joueur à la partie
                self.connection_manager.set_client_game(client_socket, game_name) # on associe le client à la partie

        except Exception as e:
            Logger.server_error("Server", f"Error handling connection: {str(e)}")
            self.connection_manager.disconnect_client(client_socket, "Server error during connection handling")

    def handle_game_action(self, client_socket: socket.socket, packet_data: Dict) -> None:
        """
        procédure : gère une action de jeu
        params :
            client_socket - le socket du client
            packet_data - les données de l'action
        """
        game_id = self.connection_manager.get_client_game(client_socket) # on récupère l'identifiant de la partie
        if not game_id: # on vérifie si le client est dans une partie
            return

        game = self.game_manager.get_game(game_id) # on récupère la partie
        if not game or not game.active or not game.is_full(): # on vérifie si la partie existe et si elle est active et si elle est pleine
            return

        if not game.is_player_turn(client_socket): # on vérifie si c'est le tour du joueur
            return

        other_socket = game.get_other_player_socket(client_socket) # on récupère le socket de l'autre joueur dans la partie (session)
        if other_socket: # on vérifie si l'autre joueur existe 
            action_packet_dict = {
                "type": PacketType.GAME_ACTION.value,
                "data": packet_data
            }
            if self.connection_manager.send_json(other_socket, action_packet_dict): # on envoie l'action à l'autre joueur
                game.current_turn = 3 - game.current_turn # on met à jour le tour du joueur
                self._send_turn_updates(game) # on envoie les mises à jour de tour aux joueurs

    def handle_chat_message(self, client_socket: socket.socket, packet_data: Dict) -> None:
        """
        procédure : gère un message de chat
        params :
            client_socket - le socket du client
            packet_data - les données du message
        """
        game_id = self.connection_manager.get_client_game(client_socket) # on récupère l'identifiant de la partie
        if not game_id: # on vérifie si le client est dans une partie
            return

        game = self.game_manager.get_game(game_id) # on récupère la partie
        if not game: # on vérifie si la partie existe
            return

        self.chat_manager.handle_chat_message(game, client_socket, packet_data, self.connection_manager) # on traite le message de chat

    def handle_get_game_list(self, client_socket: socket.socket) -> None:
        """
        procédure : gère une demande de liste des parties
        params :
            client_socket - le socket du client
        """
        games_list = self.game_manager.get_available_games() # on récupère la liste des parties disponibles
        response = create_game_list_dict(games_list) # on crée le paquet de réponse
        self.connection_manager.send_json(client_socket, response) # on envoie la liste des parties disponibles au client

    def _send_turn_updates(self, game: GameSession) -> None:
        """
        procédure : envoie les mises à jour de tour aux joueurs
        params :
            game - la session de jeu
        """
        from src.network.common.packets import create_your_turn_dict, create_wait_turn_dict
        
        current_player_socket = game.players.get(game.current_turn) # on récupère le socket du joueur actuel
        waiting_player_socket = game.players.get(3 - game.current_turn) # on récupère le socket du joueur en attente

        if current_player_socket:
            your_turn_dict = create_your_turn_dict(game.game_id) 
            self.connection_manager.send_json(current_player_socket, your_turn_dict)
        if waiting_player_socket:
            wait_turn_dict = create_wait_turn_dict(game.game_id)
            self.connection_manager.send_json(waiting_player_socket, wait_turn_dict)

    def cleanup(self) -> None:
        """
        procédure : nettoie les ressources du serveur
        """
        Logger.server_internal("Server", "Shutting down server and cleaning up...")
        try:
            self.server_socket.close()
            Logger.server_internal("Server", "Server socket closed.")
        except Exception as e:
            Logger.server_error("Server", f"Error closing server socket: {e}")

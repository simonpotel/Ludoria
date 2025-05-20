import socket
import json
import threading
import random
from typing import Dict, Set, Optional, Any, List
from pathlib import Path
from src.network.common.packets import (
    PacketType, 
    create_player_assignment_dict, create_wait_turn_dict,
    create_your_turn_dict, create_disconnect_dict, 
    create_player_disconnected_dict, create_chat_receive_dict,
    create_game_list_dict
)
from src.utils.logger import Logger
from src.network.server.game_session import GameSession

class GameServer:
    """
    classe : serveur de jeu qui gère les connexions des joueurs et les parties de jeu   
    """
    def __init__(self):
        self.load_config() 
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # on configure le socket pour réutiliser l'adresse
        self.clients: Dict[socket.socket, bytes] = {} 
        self.games: Dict[str, GameSession] = {} 
        self.client_to_game: Dict[socket.socket, str] = {} 
        Logger.initialize() 

    def load_config(self):
        """
        procédure : charge la configuration du serveur
        """
        try:
            config_path = Path('configs/server.json') 
            if not config_path.is_file(): 
                 raise FileNotFoundError(f"Config file not found at {config_path.resolve()}") 
            with open(config_path, 'r') as f: 
                config = json.load(f) 
                self.host = config['host'] 
                self.port = config['port'] 
                
                self.max_players = config.get('max_players', 10) 
                self.timeout = config.get('timeout', 60) 
                Logger.info("Server", f"Config loaded from {config_path.resolve()}") 
        except Exception as e:
            Logger.error("Server", f"Failed to load config: {str(e)}") 
            
            self.host = "0.0.0.0" 
            self.port = 5000 
            self.max_players = 10 
            self.timeout = 60 
            Logger.warning("Server", f"Using default config: {self.host}:{self.port}") 
            

    def start(self):
        """
        procédure : démarre le serveur
        """
        try:
            self.server_socket.bind((self.host, self.port)) 
            self.server_socket.listen(self.max_players) 
            Logger.info("Server", f"Server started on {self.host}:{self.port}, listening...") 
            
            while True:
                client_socket, address = self.server_socket.accept() # on accepte une nouvelle connexion
                Logger.info("Server", f"New connection from {address}") 
                self.clients[client_socket] = b""  # on initialise le buffer du client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True) # on crée un thread pour gérer la connexion
                client_thread.start() # on démarre le thread
        except OSError as e:
             Logger.error("Server", f"Failed to bind or listen: {e}") 
        except Exception as e:
            Logger.error("Server", f"Server error: {str(e)}") 
        finally:
            self.cleanup() 

    def handle_client(self, client_socket: socket.socket, address: tuple):
        """
        procédure : gère les connexions des clients
        """
        addr_str = f"{address[0]}:{address[1]}" 
        try:
            while True:
                chunk = client_socket.recv(4096) # on reçoit un chunk de données
                if not chunk:
                    Logger.info("Server", f"Client {addr_str} disconnected (received empty chunk).") 
                    break 
                
                self.clients[client_socket] += chunk  # on ajoute le chunk au buffer du client
                
                buffer = self.clients[client_socket]
                while b'\n' in buffer:
                    message_bytes, remaining_buffer = buffer.split(b'\n', 1)  # on sépare le message en un message et le reste du buffer
                    buffer = remaining_buffer  # on met à jour le buffer
                    self.clients[client_socket] = buffer  # on met à jour le buffer du client

                    message_string = message_bytes.decode('utf-8').strip()  # on décode le message
                    if not message_string:
                        continue  # on continue si le message est vide

                    Logger.info("Server", f"Received Raw JSON from {addr_str}: {message_string}")  # on affiche le message reçu
                    try:
                        packet_dict = json.loads(message_string) 
                        self.process_json_packet(client_socket, packet_dict) 
                    except json.JSONDecodeError:
                        Logger.error("Server", f"Invalid JSON received from {addr_str}: {message_string}") 
                        
                        self.disconnect_client(client_socket, "Invalid JSON format") 
                        return 
                    except Exception as e:
                         Logger.error("Server", f"Error processing packet dict from {addr_str}: {e}") 
                         
                         
        except ConnectionResetError:
             Logger.info("Server", f"Client {addr_str} disconnected forcefully (connection reset).") 
        except socket.timeout:
            Logger.warning("Server", f"Client {addr_str} timed out.") 
            self.disconnect_client(client_socket, "Timeout") 
        except Exception as e:
            
            Logger.error("Server", f"Error handling client {addr_str}: {str(e)}") 
        finally:
            
            self.disconnect_client(client_socket, "Closing connection") 
            
    def _send_json(self, client_socket: socket.socket, packet_dict: Dict):
        """
        procédure : envoie un paquet JSON au client
        """
        try:
            json_string = json.dumps(packet_dict) # on convertit le paquet en une chaîne JSON
            message_to_send = (json_string + '\n').encode('utf-8') # on encode la chaîne JSON
            client_socket.sendall(message_to_send) # on envoie le message au client
            Logger.info("Server", f"Sent JSON to {client_socket.getpeername()}: {json_string}") # on affiche le message envoyé
            return True
        except BrokenPipeError:
             Logger.warning("Server", f"Failed to send to {client_socket.getpeername()}: Broken pipe (client likely disconnected)") 
             self.disconnect_client(client_socket, "Broken pipe during send") 
             return False
        except Exception as e:
            Logger.error("Server", f"Error sending JSON to {client_socket.getpeername()}: {str(e)}") 
            
            self.disconnect_client(client_socket, f"Send error: {e}") 
            return False

    

    def process_json_packet(self, client_socket: socket.socket, packet_dict: Dict):
        """
        procédure : traite un paquet JSON
        """
        try:
            if not isinstance(packet_dict, dict) or "type" not in packet_dict or "data" not in packet_dict:
                Logger.error("Server", f"Invalid packet structure received from {client_socket.getpeername()}: {packet_dict}")
                return

            packet_type_val = packet_dict.get("type") 
            packet_data = packet_dict.get("data", {}) 

            # on vérifie si le type du paquet est valide
            try:
                packet_type_enum = PacketType(packet_type_val)
            except ValueError:
                Logger.warning("Server", f"Unknown packet type value from {client_socket.getpeername()}: {packet_type_val}") 
                return

            Logger.info("Server", f"Processing packet from {client_socket.getpeername()}: Type={packet_type_enum.name}, Data={packet_data}") 

            handlers = {
                PacketType.CONNECT: self.handle_connect, # on gère le paquet CONNECT
                PacketType.DISCONNECT: lambda s, pt, pd: self.disconnect_client(s, pd.get("reason", "Client requested disconnect")), # on gère le paquet DISCONNECT
                PacketType.GAME_ACTION: self.handle_game_action, # on gère le paquet GAME_ACTION
                PacketType.CHAT_SEND: self.handle_chat_message, # on gère le paquet CHAT_SEND
                PacketType.GET_GAME_LIST: self.handle_get_game_list, # on gère le paquet GET_GAME_LIST
            }
            
            if packet_type_enum in handlers:
                handlers[packet_type_enum](client_socket, packet_type_enum, packet_data)
            else:
                Logger.warning("Server", f"No handler for packet type from {client_socket.getpeername()}: {packet_type_enum.name}")
                
        except Exception as e:
            Logger.error("Server", f"Error processing packet content from {client_socket.getpeername()}: {str(e)}") 
            self.disconnect_client(client_socket, "Error processing packet") 

    def handle_connect(self, client_socket: socket.socket, packet_type: PacketType, packet_data: Dict):
        """
        procédure : gère le paquet CONNECT
        """
        try:
            player_name = packet_data.get("player_name", f"Player_{random.randint(100, 999)}") # on récupère le nom du joueur
            game_name = packet_data.get("game_name") # on récupère le nom de la partie
            game_type = packet_data.get("game_type") # on récupère le type de jeu
            
            if not game_name:
                Logger.error("Server", f"CONNECT packet from {client_socket.getpeername()} missing 'game_name'.") 
                self.disconnect_client(client_socket, "Missing game_name in CONNECT packet") 
                return
                
            if not game_type:
                Logger.error("Server", f"CONNECT packet from {client_socket.getpeername()} missing 'game_type'.") 
                self.disconnect_client(client_socket, "Missing game_type in CONNECT packet") 
                return

            Logger.info("Server", f"Connect request from {player_name} for game '{game_name}' (type: {game_type})") 
            
            game = self._get_or_create_game(game_name, game_type)
            if not game:
                self.disconnect_client(client_socket, f"Failed to create/find game '{game_name}'") 
                return
                
            if not self._can_join_game(game, client_socket, game_name): 
                return 

            self._setup_player(client_socket, game, player_name, game_name, game_type) 

        except Exception as e:
            Logger.error("Server", f"Error handling connection for {client_socket.getpeername()}: {str(e)}") 
            self.disconnect_client(client_socket, "Server error during connection handling")

    def _get_or_create_game(self, game_name: str, game_type: str) -> Optional[GameSession]:
        """
        fonction : récupère ou crée une partie
        """
        if game_name in self.games:
            return self.games[game_name]
            
        game = GameSession(game_name, game_type)
        self.games[game_name] = game
        return game

    def _can_join_game(self, game: GameSession, client_socket: socket.socket, game_name: str) -> bool:
        """
        procédure : vérifie si le joueur peut rejoindre la partie
        """
        if game.is_full():
            Logger.warning("Server", f"Game {game_name} is full. Rejecting {client_socket.getpeername()}") 
            disconnect_dict = create_disconnect_dict(f"Game '{game_name}' is full") 
            self._send_json(client_socket, disconnect_dict) 
            return False
        return True

    def _setup_player(self, client_socket: socket.socket, game: GameSession, player_name: str, game_name: str, game_type: str):
        """
        procédure : configure le joueur
        """
        try:
            player_number = game.add_player(client_socket) 
            self.client_to_game[client_socket] = game_name 

            assignment_dict = create_player_assignment_dict(player_number, game_name, game_type)
            if not self._send_json(client_socket, assignment_dict):
                 raise ConnectionError("Failed to send player assignment") 

            Logger.info("Server", f"Assigned player {player_name} ({client_socket.getpeername()}) as Player {player_number} in game {game_name}")    

            
            if game.is_full():
                self._start_game(game, game_name)

        except Exception as e:
            Logger.error("Server", f"Error setting up player {player_name} ({client_socket.getpeername()}): {str(e)}")
            
            if client_socket in self.client_to_game:
                del self.client_to_game[client_socket] 
            game.remove_player(client_socket) 
            self.disconnect_client(client_socket, "Error during player setup")

    def _start_game(self, game: GameSession, game_name: str):
        """
        procédure : démarre une partie
        """
        Logger.info("Server", f"Game {game_name} is full, starting game.")
        game.start()
        
        
        player1_socket = game.players.get(1) # on récupère le socket du joueur 1
        player2_socket = game.players.get(2) # on récupère le socket du joueur 2

        if not player1_socket or not player2_socket:
             Logger.error("Server", f"Could not find both player sockets for game {game_name} to start.")   
             
             return
        
        
        your_turn_dict = create_your_turn_dict(game_name)  # on crée le paquet YOUR_TURN
        wait_turn_dict = create_wait_turn_dict(game_name)  # on crée le paquet WAIT_TURN
        
        
        Logger.info("Server", f"Sending YOUR_TURN to Player 1 ({player1_socket.getpeername()}) in game {game_name}")  # on envoie le paquet YOUR_TURN au joueur 1
        if not self._send_json(player1_socket, your_turn_dict):
             Logger.error("Server", f"Failed to send YOUR_TURN to Player 1 in game {game_name}") 
             
             
        Logger.info("Server", f"Sending WAIT_TURN to Player 2 ({player2_socket.getpeername()}) in game {game_name}")  # on envoie le paquet WAIT_TURN au joueur 2   
        if not self._send_json(player2_socket, wait_turn_dict):
             Logger.error("Server", f"Failed to send WAIT_TURN to Player 2 in game {game_name}") 
             

    def handle_game_action(self, client_socket: socket.socket, packet_type: PacketType, packet_data: Dict):
        """
        procédure : gère les actions de jeu
        """
        game_id = None 
        try:
            if not self._validate_game_action(client_socket, packet_data):
                return 

            game_id = self.client_to_game.get(client_socket)
            if not game_id: 
                Logger.error("Server", f"No game ID found for client {client_socket.getpeername()} sending action.") 
                return
                
            game = self.games[game_id] 
            other_socket = game.get_other_player_socket(client_socket) 
            
            if other_socket:
                self._process_game_action(game, game_id, client_socket, other_socket, packet_data)
            else:
                Logger.warning("Server", f"No other player found in game {game_id} to forward action to.") 
                

        except KeyError as e:
             Logger.error("Server", f"Missing expected key during game action processing: {e}") 
             if game_id and game_id in self.games: del self.games[game_id] 
             self.disconnect_client(client_socket, "Internal server error during action") 
        except Exception as e:
            Logger.error("Server", f"Error handling game action from {client_socket.getpeername()}: {str(e)}") 
            self.disconnect_client(client_socket, "Server error handling game action") 

    def _validate_game_action(self, client_socket: socket.socket, packet_data: Dict) -> bool:
        """
        procédure : valide les actions de jeu
        """
        game_id = self.client_to_game.get(client_socket) 
        if not game_id:
            Logger.error("Server", f"No game found for client {client_socket.getpeername()} sending action.") 
            return False

        game = self.games.get(game_id) 
        if not game:
            Logger.error("Server", f"Game {game_id} not found for client {client_socket.getpeername()} sending action.") 
            return False
            
        if not game.active:
            Logger.warning("Server", f"Action received for inactive game {game_id} from {client_socket.getpeername()}") 
            
            return False

        if not game.is_full():
            Logger.warning("Server", f"Action received for game {game_id} with only one player. Ignoring action.") 
            return False

        if not game.is_player_turn(client_socket):
            Logger.warning("Server", f"Not player's turn ({client_socket.getpeername()}) in game {game_id}. Ignoring action.") 
            
            return False
        return True

    def _process_game_action(self, game: GameSession, game_id: str, sending_socket: socket.socket, other_socket: socket.socket, action_data: Dict):
        """
        procédure : traite les actions de jeu
        """
        try:
            # on crée le paquet GAME_ACTION
            action_packet_dict = {
                "type": PacketType.GAME_ACTION.value,
                "data": action_data
            }
            Logger.info("Server", f"Forwarding game action from {sending_socket.getpeername()} to {other_socket.getpeername()} in game {game_id}")  # on envoie le paquet GAME_ACTION au joueur 2
            if not self._send_json(other_socket, action_packet_dict):
                Logger.error("Server", f"Failed to forward action to other player in game {game_id}") 
                
                return
            
            
            game.current_turn = 3 - game.current_turn # on change le tour (1 -> 2, 2 -> 1)
            Logger.info("Server", f"Turn switched to Player {game.current_turn} in game {game_id}")  # on affiche le tour
            
            
            your_turn_dict = create_your_turn_dict(game_id)  # on crée le paquet YOUR_TURN
            wait_turn_dict = create_wait_turn_dict(game_id)  # on crée le paquet WAIT_TURN
            
            
            current_player_socket = game.players.get(game.current_turn) 
            
            waiting_player_socket = game.players.get(3 - game.current_turn) 
            
            if current_player_socket:
                 Logger.info("Server", f"Sending YOUR_TURN to Player {game.current_turn} ({current_player_socket.getpeername()}) in game {game_id}")  # on envoie le paquet YOUR_TURN au joueur 1
                 self._send_json(current_player_socket, your_turn_dict)
            if waiting_player_socket:
                 Logger.info("Server", f"Sending WAIT_TURN to Player {3 - game.current_turn} ({waiting_player_socket.getpeername()}) in game {game_id}")  # on envoie le paquet WAIT_TURN au joueur 2
                 self._send_json(waiting_player_socket, wait_turn_dict)
            
        except Exception as e:
            Logger.error("Server", f"Error processing game action logic for game {game_id}: {str(e)}") 
            
            

    def disconnect_client(self, client_socket: socket.socket, reason: str = "Unknown reason"):
        """
        procédure : déconnecte un client
        """
        if client_socket not in self.clients: 
            return
            
        addr = client_socket.getpeername() if client_socket.fileno() != -1 else "disconnected socket"
        Logger.info("Server", f"Disconnecting client {addr}. Reason: {reason}") 
        
        try:
            game_id = self.client_to_game.pop(client_socket, None) 
            
            if game_id and game_id in self.games:
                game = self.games[game_id] 
                player_number = game.remove_player(client_socket) 
                game.active = False 
                
                if player_number:
                    Logger.info("Server", f"Removed Player {player_number} from game {game_id}.") 
                    other_socket = game.get_other_player_socket(client_socket) 
                    if other_socket:
                        disconnect_msg = f"Player {player_number} disconnected ({reason})"
                        player_disconnected_dict = create_player_disconnected_dict(disconnect_msg, game_id) 
                        self._send_json(other_socket, player_disconnected_dict) 
                
                if game.is_empty():
                    if game_id in self.games:
                         del self.games[game_id]
                         Logger.info("Server", f"Removed empty game session: {game_id}") 
                else:
                    del self.games[game_id]
                    Logger.info("Server", f"Removed game session: {game_id} (inactive but not empty)") 
                    
            
            if client_socket in self.clients:
                 del self.clients[client_socket] 
            
            try:
                client_socket.shutdown(socket.SHUT_RDWR) 
            except OSError:
                pass 
            try:
                client_socket.close() 
            except OSError:
                pass
                
        except Exception as e:
            Logger.error("Server", f"Error during client ({addr}) disconnect cleanup: {str(e)}") 

    def cleanup(self):
        """
        procédure : nettoie les ressources
        """
        Logger.info("Server", "Shutting down server and cleaning up...") 
        client_sockets = list(self.clients.keys()) 
        for client_socket in client_sockets:
            self.disconnect_client(client_socket, "Server shutting down") 
            
        try:
            self.server_socket.close() 
            Logger.info("Server", "Server socket closed.") 
        except Exception as e:
             Logger.error("Server", f"Error closing server socket: {e}") 

    def handle_chat_message(self, client_socket: socket.socket, packet_type: PacketType, packet_data: Dict):
        """
        procédure : gère les messages de chat
        """
        try:
            if "sender_name" not in packet_data or "message" not in packet_data or "game_id" not in packet_data:
                Logger.error("Server", f"Missing required fields in CHAT_SEND from {client_socket.getpeername()}")
                return
                
            game_id = packet_data["game_id"]
            if game_id not in self.games:
                Logger.error("Server", f"Game {game_id} not found for chat message from {client_socket.getpeername()}")
                return
                
            sender_name = packet_data["sender_name"]
            message = packet_data["message"]
            player_number = packet_data.get("player_number", 0)
            
            game = self.games[game_id]
            
            # vérifie que l'expéditeur est bien dans cette partie
            if client_socket not in [sock for sock in game.players.values()]:
                Logger.warning("Server", f"Client {client_socket.getpeername()} tried to send chat to game {game_id} but is not a player")
                return
                
            Logger.info("Server", f"Chat message from Player {player_number} in game {game_id}: {message}")
            
            # envoie le message à tous les joueurs de la partie (y compris l'expéditeur pour confirmation)
            chat_packet = create_chat_receive_dict(
                sender_name=sender_name,
                message=message,
                player_number=player_number,
                game_id=game_id
            )
            
            for player_socket in game.players.values():
                if player_socket != client_socket:  # évite de renvoyer au même client
                    Logger.info("Server", f"Forwarding chat message to {player_socket.getpeername()} in game {game_id}")
                    self._send_json(player_socket, chat_packet)
                    
        except Exception as e:
            Logger.error("Server", f"Error handling chat message from {client_socket.getpeername()}: {str(e)}")

    def handle_get_game_list(self, client_socket: socket.socket, packet_type: PacketType, packet_data: Dict):
        """
        procédure : gère la demande de liste des parties
        """
        try:
            games_list = []
            for game_id, game in self.games.items():
                if not game.is_full() and game.active:
                    games_list.append({
                        "game_id": game_id,
                        "game_type": game.game_type,
                        "player_count": game.get_player_count(),
                        "max_players": game.get_max_players()
                    })
            
            response = create_game_list_dict(games_list)
            if not self._send_json(client_socket, response):
                Logger.error("Server", f"Failed to send game list to {client_socket.getpeername()}")
                
        except Exception as e:
            Logger.error("Server", f"Error handling game list request from {client_socket.getpeername()}: {str(e)}")
            self.disconnect_client(client_socket, "Error processing game list request")

import socket
import json
import threading
from typing import Dict
from src.utils.logger import Logger
from src.network.common.packets import PacketType, create_game_list_dict
from src.network.server.connection_manager import ConnectionManager
from src.network.server.game_manager import GameManager
from src.network.server.chat_manager import ChatManager
from src.network.server.config_manager import ConfigManager

class GameServer:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config_manager.load_config()
        
        self.connection_manager = ConnectionManager()
        self.game_manager = GameManager()
        self.chat_manager = ChatManager()
        
        # Set the game manager in the connection manager
        self.connection_manager.set_game_manager(self.game_manager)
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        Logger.initialize()

    def start(self):
        try:
            self.server_socket.bind((self.config_manager.get_host(), self.config_manager.get_port()))
            self.server_socket.listen(self.config_manager.get_max_players())
            Logger.info("Server", f"Server started on {self.config_manager.get_host()}:{self.config_manager.get_port()}, listening...")
            
            while True:
                client_socket, address = self.server_socket.accept()
                Logger.info("Server", f"New connection from {address}")
                self.connection_manager.add_client(client_socket)
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True)
                client_thread.start()
        except OSError as e:
            Logger.error("Server", f"Failed to bind or listen: {e}")
        except Exception as e:
            Logger.error("Server", f"Server error: {str(e)}")
        finally:
            self.cleanup()

    def handle_client(self, client_socket: socket.socket, address: tuple):
        addr_str = f"{address[0]}:{address[1]}"
        try:
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    Logger.info("Server", f"Client {addr_str} disconnected (received empty chunk).")
                    break

                messages = self.connection_manager.process_received_data(client_socket, chunk)
                for packet_dict in messages:
                    self.process_json_packet(client_socket, packet_dict)

        except ConnectionResetError:
            Logger.info("Server", f"Client {addr_str} disconnected forcefully (connection reset).")
        except socket.timeout:
            Logger.warning("Server", f"Client {addr_str} timed out.")
            self.connection_manager.disconnect_client(client_socket, "Timeout")
        except Exception as e:
            Logger.error("Server", f"Error handling client {addr_str}: {str(e)}")
        finally:
            self.connection_manager.disconnect_client(client_socket, "Closing connection")

    def process_json_packet(self, client_socket: socket.socket, packet_dict: Dict):
        try:
            if not isinstance(packet_dict, dict) or "type" not in packet_dict or "data" not in packet_dict:
                Logger.error("Server", f"Invalid packet structure received from {client_socket.getpeername()}: {packet_dict}")
                return

            packet_type_val = packet_dict.get("type")
            packet_data = packet_dict.get("data", {})

            try:
                packet_type_enum = PacketType(packet_type_val)
            except ValueError:
                Logger.warning("Server", f"Unknown packet type value from {client_socket.getpeername()}: {packet_type_val}")
                return

            Logger.info("Server", f"Processing packet from {client_socket.getpeername()}: Type={packet_type_enum.name}, Data={packet_data}")

            if packet_type_enum == PacketType.CONNECT:
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
                Logger.warning("Server", f"No handler for packet type from {client_socket.getpeername()}: {packet_type_enum.name}")

        except Exception as e:
            Logger.error("Server", f"Error processing packet content from {client_socket.getpeername()}: {str(e)}")
            self.connection_manager.disconnect_client(client_socket, "Error processing packet")

    def handle_connect(self, client_socket: socket.socket, packet_data: Dict):
        try:
            player_name = packet_data.get("player_name", f"Player_{hash(client_socket) % 900 + 100}")
            game_name = packet_data.get("game_name")
            game_type = packet_data.get("game_type")

            if not game_name or not game_type:
                self.connection_manager.disconnect_client(client_socket, "Missing game_name or game_type in CONNECT packet")
                return

            Logger.info("Server", f"Connect request from {player_name} for game '{game_name}' (type: {game_type})")

            game = self.game_manager.get_game(game_name)
            if not game:
                game = self.game_manager.create_game(game_name, game_type)

            if game.is_full():
                self.connection_manager.disconnect_client(client_socket, f"Game '{game_name}' is full")
                return

            if self.game_manager.handle_player_join(game, client_socket, player_name, self.connection_manager):
                self.connection_manager.set_client_game(client_socket, game_name)

        except Exception as e:
            Logger.error("Server", f"Error handling connection: {str(e)}")
            self.connection_manager.disconnect_client(client_socket, "Server error during connection handling")

    def handle_game_action(self, client_socket: socket.socket, packet_data: Dict):
        game_id = self.connection_manager.get_client_game(client_socket)
        if not game_id:
            return

        game = self.game_manager.get_game(game_id)
        if not game or not game.active or not game.is_full():
            return

        if not game.is_player_turn(client_socket):
            return

        other_socket = game.get_other_player_socket(client_socket)
        if other_socket:
            action_packet_dict = {
                "type": PacketType.GAME_ACTION.value,
                "data": packet_data
            }
            if self.connection_manager.send_json(other_socket, action_packet_dict):
                game.current_turn = 3 - game.current_turn
                self._send_turn_updates(game)

    def handle_chat_message(self, client_socket: socket.socket, packet_data: Dict):
        game_id = self.connection_manager.get_client_game(client_socket)
        if not game_id:
            return

        game = self.game_manager.get_game(game_id)
        if not game:
            return

        self.chat_manager.handle_chat_message(game, client_socket, packet_data, self.connection_manager)

    def handle_get_game_list(self, client_socket: socket.socket):
        games_list = self.game_manager.get_available_games()
        response = create_game_list_dict(games_list)
        self.connection_manager.send_json(client_socket, response)

    def _send_turn_updates(self, game):
        from src.network.common.packets import create_your_turn_dict, create_wait_turn_dict
        
        current_player_socket = game.players.get(game.current_turn)
        waiting_player_socket = game.players.get(3 - game.current_turn)

        if current_player_socket:
            your_turn_dict = create_your_turn_dict(game.game_id)
            self.connection_manager.send_json(current_player_socket, your_turn_dict)
        if waiting_player_socket:
            wait_turn_dict = create_wait_turn_dict(game.game_id)
            self.connection_manager.send_json(waiting_player_socket, wait_turn_dict)

    def cleanup(self):
        Logger.info("Server", "Shutting down server and cleaning up...")
        try:
            self.server_socket.close()
            Logger.info("Server", "Server socket closed.")
        except Exception as e:
            Logger.error("Server", f"Error closing server socket: {e}")

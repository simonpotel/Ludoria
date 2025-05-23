import socket
import json
from typing import Dict, Optional
from src.utils.logger import Logger
from src.network.common.packets import PacketType, create_disconnect_dict, create_player_disconnected_dict

class ConnectionManager:
    def __init__(self):
        self.clients: Dict[socket.socket, bytes] = {}
        self.client_to_game: Dict[socket.socket, str] = {}
        self.game_manager = None  # Will be set by GameServer

    def set_game_manager(self, game_manager):
        self.game_manager = game_manager

    def add_client(self, client_socket: socket.socket):
        self.clients[client_socket] = b""

    def remove_client(self, client_socket: socket.socket):
        if client_socket in self.clients:
            del self.clients[client_socket]

    def get_client_game(self, client_socket: socket.socket) -> Optional[str]:
        return self.client_to_game.get(client_socket)

    def set_client_game(self, client_socket: socket.socket, game_id: str):
        self.client_to_game[client_socket] = game_id

    def remove_client_game(self, client_socket: socket.socket) -> Optional[str]:
        return self.client_to_game.pop(client_socket, None)

    def send_json(self, client_socket: socket.socket, packet_dict: Dict) -> bool:
        try:
            json_string = json.dumps(packet_dict)
            message_to_send = (json_string + '\n').encode('utf-8')
            client_socket.sendall(message_to_send)
            Logger.info("Server", f"Sent JSON to {client_socket.getpeername()}: {json_string}")
            return True
        except BrokenPipeError:
            Logger.warning("Server", f"Failed to send to {client_socket.getpeername()}: Broken pipe")
            return False
        except Exception as e:
            Logger.error("Server", f"Error sending JSON to {client_socket.getpeername()}: {str(e)}")
            return False

    def disconnect_client(self, client_socket: socket.socket, reason: str = "Unknown reason", is_recursive_call: bool = False):
        if client_socket not in self.clients:
            return

        addr = client_socket.getpeername() if client_socket.fileno() != -1 else "disconnected socket"
        Logger.info("Server", f"Disconnecting client {addr}. Reason: {reason}")

        try:
            # Get the game session before removing the client
            game_id = self.get_client_game(client_socket)
            if game_id and self.game_manager and not is_recursive_call:
                game = self.game_manager.get_game(game_id)
                if game:
                    # Get the other player's socket
                    other_socket = game.get_other_player_socket(client_socket)
                    if other_socket:
                        try:
                            # Send disconnect notification to the other player
                            disconnect_packet = create_player_disconnected_dict(game_id, f"Other player disconnected: {reason}")
                            self.send_json(other_socket, disconnect_packet)
                        except Exception as e:
                            Logger.warning("Server", f"Failed to send disconnect notification to other player: {e}")
                        
                        # Disconnect the other player as well, but mark it as recursive
                        self.disconnect_client(other_socket, "Game session ended", True)
                    
                    # Remove the game session
                    self.game_manager.remove_game(game_id)

            # Clean up client data
            if client_socket in self.clients:
                del self.clients[client_socket]
            self.remove_client_game(client_socket)

            try:
                if client_socket.fileno() != -1:
                    client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                client_socket.close()
            except OSError:
                pass

        except Exception as e:
            Logger.error("Server", f"Error during client ({addr}) disconnect cleanup: {str(e)}")

    def process_received_data(self, client_socket: socket.socket, chunk: bytes) -> list:
        if not chunk:
            return []

        self.clients[client_socket] += chunk
        buffer = self.clients[client_socket]
        messages = []

        while b'\n' in buffer:
            message_bytes, remaining_buffer = buffer.split(b'\n', 1)
            buffer = remaining_buffer
            self.clients[client_socket] = buffer

            message_string = message_bytes.decode('utf-8').strip()
            if message_string:
                try:
                    packet_dict = json.loads(message_string)
                    messages.append(packet_dict)
                except json.JSONDecodeError:
                    Logger.error("Server", f"Invalid JSON received from {client_socket.getpeername()}: {message_string}")
                    self.disconnect_client(client_socket, "Invalid JSON format")
                    return []

        return messages 
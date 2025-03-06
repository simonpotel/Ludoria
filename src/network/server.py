import socket
import json
import threading
import random
from typing import Dict, Set, Optional
from pathlib import Path
from src.network.packets import Packet, PacketType, create_player_assignment_packet, create_wait_turn_packet, create_your_turn_packet, create_disconnect_packet
from src.utils.logger import Logger
import pickle

class GameSession:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: Dict[int, socket.socket] = {}
        self.player_buffers: Dict[socket.socket, bytearray] = {}
        self.current_turn = 1
        self.board_state = None
        self.active = True

    def add_player(self, player_socket: socket.socket) -> int:
        if len(self.players) >= 2:
            raise ValueError("Game session is full")
        
        player_number = 1 if 1 not in self.players else 2
        self.players[player_number] = player_socket
        self.player_buffers[player_socket] = bytearray()
        return player_number

    def remove_player(self, player_socket: socket.socket) -> Optional[int]:
        for player_number, sock in self.players.items():
            if sock == player_socket:
                del self.players[player_number]
                if player_socket in self.player_buffers:
                    del self.player_buffers[player_socket]
                return player_number
        return None

    def get_other_player_socket(self, current_socket: socket.socket) -> Optional[socket.socket]:
        for player_number, sock in self.players.items():
            if sock != current_socket:
                return sock
        return None

    def get_player_number(self, player_socket: socket.socket) -> Optional[int]:
        for player_number, sock in self.players.items():
            if sock == player_socket:
                return player_number
        return None

    def is_player_turn(self, player_socket: socket.socket) -> bool:
        player_number = self.get_player_number(player_socket)
        return player_number is not None and player_number == self.current_turn

    def is_full(self) -> bool:
        return len(self.players) == 2

    def is_empty(self) -> bool:
        return len(self.players) == 0

    def start(self):
        self.active = True
        self.current_turn = 1

    def update_board_state(self, state):
        self.board_state = state

    def get_board_state(self):
        return self.board_state

    def broadcast(self, packet: Packet, exclude_socket: Optional[socket.socket] = None):
        data = packet.to_bytes()
        for player_socket in self.players.values():
            if player_socket != exclude_socket:
                try:
                    player_socket.sendall(data)
                except:
                    pass

class GameServer:
    def __init__(self):
        self.load_config()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: Set[socket.socket] = set()
        self.games: Dict[str, GameSession] = {}
        self.client_to_game: Dict[socket.socket, str] = {}
        Logger.initialize()

    def load_config(self):
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
        receive_buffer = bytearray()
        try:
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    Logger.info("Server", "Client disconnected")
                    break

                receive_buffer.extend(chunk)
                
                try:
                    packet = pickle.loads(receive_buffer)
                    receive_buffer = bytearray()
                    self.process_packet(client_socket, packet)
                except (pickle.UnpicklingError, EOFError):
                    continue

        except Exception as e:
            Logger.error("Server", f"Error handling client: {str(e)}")
        finally:
            self.disconnect_client(client_socket)

    def process_packet(self, client_socket: socket.socket, packet: Packet):
        try:
            if not packet or not hasattr(packet, 'type'):
                Logger.error("Server", "Invalid packet received")
                return
            
            Logger.info("Server", f"Processing packet type: {packet.type}")
            
            if packet.type == PacketType.CONNECT:
                self.handle_connect(client_socket, packet)
            elif packet.type == PacketType.DISCONNECT:
                self.disconnect_client(client_socket)
            elif packet.type == PacketType.GAME_ACTION:
                self.handle_game_action(client_socket, packet)
            else:
                Logger.warning("Server", f"Unknown packet type: {packet.type}")
        except Exception as e:
            Logger.error("Server", f"Error processing packet: {str(e)}")
            self.disconnect_client(client_socket)

    def handle_connect(self, client_socket: socket.socket, packet: Packet):
        try:
            if not packet.data:
                Logger.error("Server", "Empty connect packet received")
                return
            
            player_name = packet.data.get("player_name", "Unknown")
            game_name = packet.data.get("game_name", "game_1")
            Logger.info("Server", f"Player {player_name} connecting to game {game_name}")

            if game_name in self.games:
                game = self.games[game_name]
                if game.is_full():
                    Logger.warning("Server", f"Game {game_name} is full")
                    disconnect_packet = create_disconnect_packet("Game is full", game_name)
                    client_socket.sendall(pickle.dumps(disconnect_packet))
                    self.disconnect_client(client_socket)
                    return
            else:
                game = GameSession(game_name)
                self.games[game_name] = game
                Logger.info("Server", f"Created new game session: {game_name}")

            try:
                player_number = game.add_player(client_socket)
                self.client_to_game[client_socket] = game_name

                assignment_packet = create_player_assignment_packet(player_number, game_name)
                client_socket.sendall(pickle.dumps(assignment_packet))
                Logger.info("Server", f"Assigned player {player_name} as Player {player_number} in game {game_name}")

                if game.is_full():
                    Logger.info("Server", f"Game {game_name} is full, starting game")
                    game.start()
                    
                    your_turn_packet = create_your_turn_packet(game_name)
                    wait_turn_packet = create_wait_turn_packet(game_name)
                    
                    game.players[1].sendall(pickle.dumps(your_turn_packet))
                    game.players[2].sendall(pickle.dumps(wait_turn_packet))
                    Logger.info("Server", "Sent initial turn packets to players")

            except Exception as e:
                Logger.error("Server", f"Error setting up player: {str(e)}")
                if client_socket in self.client_to_game:
                    del self.client_to_game[client_socket]
                self.disconnect_client(client_socket)

        except Exception as e:
            Logger.error("Server", f"Error handling connection: {str(e)}")
            self.disconnect_client(client_socket)

    def handle_game_action(self, client_socket: socket.socket, packet: Packet):
        try:
            if not packet.data:
                Logger.error("Server", "Empty game action received")
                return
            
            game_id = self.client_to_game.get(client_socket)
            if not game_id:
                Logger.error("Server", "No game found for client")
                return

            game = self.games.get(game_id)
            if not game:
                Logger.error("Server", "Game not found")
                return

            if not game.is_player_turn(client_socket):
                Logger.warning("Server", "Not player's turn")
                return

            current_player = game.get_player_number(client_socket)
            other_socket = game.get_other_player_socket(client_socket)
            
            if other_socket:
                try:
                    other_socket.sendall(pickle.dumps(packet))
                    Logger.info("Server", f"Forwarded game action to other player")
                    
                    # Change turn
                    game.current_turn = 3 - game.current_turn
                    Logger.info("Server", f"Turn switched to Player {game.current_turn}")
                    
                    # Send turn notifications
                    your_turn_packet = create_your_turn_packet(game_id)
                    wait_turn_packet = create_wait_turn_packet(game_id)
                    
                    other_socket.sendall(pickle.dumps(your_turn_packet))
                    client_socket.sendall(pickle.dumps(wait_turn_packet))
                    Logger.info("Server", "Sent turn update packets to both players")
                    
                except Exception as e:
                    Logger.error("Server", f"Error sending packets to other player: {str(e)}")
                    self.handle_disconnect(other_socket)

        except Exception as e:
            Logger.error("Server", f"Error handling game action: {str(e)}")
            self.disconnect_client(client_socket)

    def handle_disconnect(self, client_socket):
        try:
            game_id = self.client_to_game.get(client_socket)
            if not game_id:
                return

            game = self.games.get(game_id)
            if not game:
                return

            player_number = game.get_player_number(client_socket)
            Logger.info("Server", f"Player {player_number} disconnected from game {game_id}")

            other_socket = game.get_other_player_socket(client_socket)
            game.remove_player(client_socket)

            if other_socket:
                try:
                    disconnect_packet = create_disconnect_packet(f"Player {player_number} disconnected", game_id)
                    other_socket.sendall(pickle.dumps(disconnect_packet))
                    Logger.info("Server", "Sent disconnect notification to other player")
                except Exception as e:
                    Logger.error("Server", f"Error notifying other player of disconnect: {str(e)}")

            if game.is_empty():
                del self.games[game_id]
                Logger.info("Server", f"Game {game_id} ended - no players remaining")
            else:
                Logger.info("Server", f"Game {game_id} continues with remaining player")

        except Exception as e:
            Logger.error("Server", f"Error handling disconnect: {str(e)}")
        finally:
            if client_socket in self.client_to_game:
                del self.client_to_game[client_socket]
            self.clients.discard(client_socket)
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
            except:
                pass

    def disconnect_client(self, client_socket: socket.socket):
        self.handle_disconnect(client_socket)

    def cleanup(self):
        for client in self.clients:
            try:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
            except:
                pass
        try:
            self.server_socket.close()
        except:
            pass

if __name__ == "__main__":
    server = GameServer()
    server.start() 
import socket
import json
import threading
import random
from typing import Dict, Set, Optional
from pathlib import Path
from src.network.packets import Packet, create_player_assignment_packet, create_wait_turn_packet, create_your_turn_packet
from src.utils.logger import Logger

class GameSession:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: Dict[int, socket.socket] = {}
        self.current_turn = 1
        self.board_state = None

    def add_player(self, player_socket: socket.socket) -> int:
        if len(self.players) >= 2:
            raise ValueError("Game session is full")
        
        player_number = 1 if 1 not in self.players else 2
        self.players[player_number] = player_socket
        return player_number

    def get_other_player_socket(self, current_player: int) -> Optional[socket.socket]:
        other_player = 2 if current_player == 1 else 1
        return self.players.get(other_player)

    def is_full(self) -> bool:
        return len(self.players) == 2

    def update_board_state(self, state):
        self.board_state = state

    def get_board_state(self):
        return self.board_state

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
                Logger.info("Server", f"New connection from {address}")
                self.clients.add(client_socket)
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
        except Exception as e:
            Logger.error("Server", f"Server error: {str(e)}")
        finally:
            self.cleanup()

    def handle_client(self, client_socket: socket.socket):
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                packet = Packet.from_json(data)
                self.process_packet(client_socket, packet)

        except Exception as e:
            Logger.error("Server", f"Error handling client: {str(e)}")
        finally:
            self.disconnect_client(client_socket)

    def process_packet(self, client_socket: socket.socket, packet: Packet):
        try:
            match packet.type.value:
                case "connect":
                    self.handle_connect(client_socket, packet)
                case "disconnect":
                    self.disconnect_client(client_socket)
                case "game_action":
                    self.handle_game_action(client_socket, packet)
                case _:
                    Logger.warning("Server", f"Unknown packet type: {packet.type}")
        except Exception as e:
            Logger.error("Server", f"Error processing packet: {str(e)}")

    def handle_connect(self, client_socket: socket.socket, packet: Packet):
        available_game = next((game for game in self.games.values() 
                             if not game.is_full()), None)
        
        if available_game is None:
            game_id = f"game_{len(self.games) + 1}"
            available_game = GameSession(game_id)
            self.games[game_id] = available_game
        
        try:
            player_number = available_game.add_player(client_socket)
            self.client_to_game[client_socket] = available_game.game_id
            
            assignment_packet = create_player_assignment_packet(player_number, available_game.game_id)
            client_socket.send(assignment_packet.to_json().encode('utf-8'))
            
            if available_game.is_full():
                p1_socket = available_game.players[1]
                p2_socket = available_game.players[2]
                
                p1_socket.send(create_your_turn_packet(available_game.game_id).to_json().encode('utf-8'))
                p2_socket.send(create_wait_turn_packet(available_game.game_id).to_json().encode('utf-8'))
                
        except Exception as e:
            Logger.error("Server", f"Error handling connect: {str(e)}")

    def handle_game_action(self, client_socket: socket.socket, packet: Packet):
        game_id = packet.game_id
        if not game_id or game_id not in self.games:
            return
        
        game = self.games[game_id]
        
        player_number = next((num for num, sock in game.players.items() 
                            if sock == client_socket), None)
        if player_number is None or player_number != game.current_turn:
            return
        
        if "board_state" in packet.data:
            game.update_board_state(packet.data["board_state"])
        
        other_socket = game.get_other_player_socket(player_number)
        if other_socket:
            other_socket.send(packet.to_json().encode('utf-8'))
            
            game.current_turn = 3 - game.current_turn
            
            other_socket.send(create_your_turn_packet(game_id).to_json().encode('utf-8'))
            client_socket.send(create_wait_turn_packet(game_id).to_json().encode('utf-8'))

    def disconnect_client(self, client_socket: socket.socket):
        if client_socket in self.client_to_game:
            game_id = self.client_to_game[client_socket]
            if game_id in self.games:
                game = self.games[game_id]
                for player_socket in game.players.values():
                    if player_socket != client_socket:
                        try:
                            player_socket.send(Packet(
                                type="disconnect",
                                data={"message": "Other player disconnected"},
                                game_id=game_id
                            ).to_json().encode('utf-8'))
                        except:
                            pass
                del self.games[game_id]
            del self.client_to_game[client_socket]
        
        self.clients.discard(client_socket)
        try:
            client_socket.close()
        except:
            pass

    def cleanup(self):
        for client in self.clients:
            try:
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
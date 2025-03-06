import socket
import json
import threading
from typing import Optional, Callable, Dict
from src.network.packets import Packet, PacketType, create_connect_packet, create_game_action_packet
from src.utils.logger import Logger
import pickle

class NetworkClient:
    def __init__(self):
        self.load_config()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.game_id: Optional[str] = None
        self.player_number: Optional[int] = None
        self.is_my_turn = False
        self.handlers: Dict[str, Callable] = {}
        self.receive_buffer = bytearray()
        Logger.initialize()

    def load_config(self):
        try:
            with open('configs/server.json', 'r') as f:
                config = json.load(f)
                self.host = config['host']
                self.port = config['port']
        except Exception as e:
            Logger.error("NetworkClient", f"Failed to load config: {str(e)}")
            raise

    def connect(self, game_name: str) -> bool:
        try:
            self.socket.connect((self.host, self.port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.connected = True
            self.game_id = game_name
            
            self.listen_thread = threading.Thread(target=self.listen_for_messages)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            
            connect_packet = create_connect_packet(game_name, game_name)
            self.send_packet(connect_packet)
            
            Logger.info("NetworkClient", f"Connected to server for game {game_name}")
            return True
            
        except Exception as e:
            Logger.error("NetworkClient", f"Connection failed: {str(e)}")
            self.connected = False
            return False

    def disconnect(self):
        if self.connected:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.socket.close()
            except:
                pass
            self.connected = False
            self.is_my_turn = False
            self.game_id = None
            self.player_number = None
            Logger.info("NetworkClient", "Disconnected from server")
            self.call_handler("player_disconnected", "Disconnected from server")

    def send_packet(self, packet: Packet):
        try:
            Logger.info("NetworkClient", f"Sending packet: {packet.type}")
            self.socket.sendall(pickle.dumps(packet))
        except Exception as e:
            Logger.error("NetworkClient", f"Error sending packet: {str(e)}")
            self.disconnect()

    def send_game_action(self, action: Dict):
        if not self.connected:
            Logger.error("NetworkClient", "Cannot send action: not connected")
            return
        
        if not self.game_id:
            Logger.error("NetworkClient", "Cannot send action: no game ID")
            return
        
        if not self.is_my_turn:
            Logger.warning("NetworkClient", f"Cannot send game action: not your turn (Player {self.player_number})")
            return
        
        try:
            packet = create_game_action_packet(action, self.game_id)
            self.send_packet(packet)
            Logger.info("NetworkClient", f"Sent game action as Player {self.player_number}: {action}")
        except Exception as e:
            Logger.error("NetworkClient", f"Error sending game action: {str(e)}")
            self.disconnect()

    def listen_for_messages(self):
        while self.connected:
            try:
                chunk = self.socket.recv(4096)
                if not chunk:
                    Logger.info("NetworkClient", "Server closed connection")
                    self.call_handler("player_disconnected", "Connection to server lost")
                    break
                
                self.receive_buffer.extend(chunk)
                
                try:
                    packet = pickle.loads(self.receive_buffer)
                    self.receive_buffer = bytearray()
                    if packet:
                        Logger.info("NetworkClient", f"Received packet: {packet.type}")
                        self.handle_packet(packet)
                except (pickle.UnpicklingError, EOFError) as e:
                    Logger.warning("NetworkClient", f"Error unpickling packet: {str(e)}")
                    self.receive_buffer = bytearray()
                    continue
                    
            except Exception as e:
                Logger.error("NetworkClient", f"Error receiving message: {str(e)}")
                self.call_handler("player_disconnected", "Connection error: lost connection to server")
                break
                
        self.disconnect()

    def handle_packet(self, packet):
        try:
            if not packet or not hasattr(packet, 'type'):
                Logger.error("NetworkClient", "Invalid packet received")
                return
            
            Logger.info("NetworkClient", f"Processing packet: {packet.type}")
            
            if packet.type == PacketType.PLAYER_ASSIGNMENT:
                if not packet.data or "player_number" not in packet.data:
                    Logger.error("NetworkClient", "Invalid player assignment packet")
                    return
                
                self.player_number = packet.data["player_number"]
                if "game_id" in packet.data:
                    self.game_id = packet.data["game_id"]
                Logger.info("NetworkClient", f"Assigned as Player {self.player_number} in game {self.game_id}")
                self.call_handler("player_assignment", packet.data)
                
            elif packet.type == PacketType.YOUR_TURN:
                self.is_my_turn = True
                Logger.info("NetworkClient", f"Starting turn for Player {self.player_number}")
                self.call_handler("turn_started")
                
            elif packet.type == PacketType.WAIT_TURN:
                self.is_my_turn = False
                other_player = 2 if self.player_number == 1 else 1
                Logger.info("NetworkClient", f"Player {self.player_number} waiting for Player {other_player}'s turn")
                self.call_handler("turn_ended")
                
            elif packet.type == PacketType.GAME_ACTION:
                if not packet.data:
                    Logger.error("NetworkClient", "Received empty game action")
                    return
                Logger.info("NetworkClient", f"Player {self.player_number} received game action: {packet.data}")
                self.call_handler("game_action", packet.data)
                
            elif packet.type == PacketType.GAME_STATE:
                if not packet.data:
                    Logger.error("NetworkClient", "Received empty game state")
                    return
                Logger.info("NetworkClient", f"Received game state update: {packet.data}")
                self.call_handler("game_state", packet.data)
                
            elif packet.type == PacketType.PLAYER_DISCONNECTED:
                message = packet.data.get("message", "Other player disconnected")
                Logger.info("NetworkClient", f"Player disconnected: {message}")
                self.call_handler("player_disconnected", message)
                
            elif packet.type == PacketType.DISCONNECT:
                message = packet.data.get("message", "Disconnected from server")
                Logger.info("NetworkClient", f"Received disconnect packet: {message}")
                self.disconnect()
                
        except Exception as e:
            Logger.error("NetworkClient", f"Error handling packet: {str(e)}")
            Logger.error("NetworkClient", f"Packet data: {packet.data if hasattr(packet, 'data') else 'No data'}")
            Logger.error("NetworkClient", "Stack trace:", exc_info=True)

    def register_handler(self, event: str, handler: Callable):
        self.handlers[event] = handler
        Logger.info("NetworkClient", f"Registered handler for event: {event}")

    def call_handler(self, event: str, data=None):
        if event in self.handlers:
            try:
                if data is not None:
                    self.handlers[event](data)
                else:
                    self.handlers[event]()
            except Exception as e:
                Logger.error("NetworkClient", f"Error in handler for {event}: {str(e)}")
        else:
            Logger.warning("NetworkClient", f"No handler registered for event: {event}")

    def disconnect(self):
        if self.connected:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.socket.close()
            except:
                pass
            self.connected = False
            self.is_my_turn = False
            self.game_id = None
            self.player_number = None
            Logger.info("NetworkClient", "Disconnected from server")
            self.call_handler("player_disconnected", "Disconnected from server") 
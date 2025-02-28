import socket
import json
import threading
from typing import Optional, Callable, Dict
from src.network.packets import Packet, create_connect_packet, create_game_action_packet
from src.utils.logger import Logger

class NetworkClient:
    def __init__(self):
        self.load_config()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.game_id: Optional[str] = None
        self.player_number: Optional[int] = None
        self.is_my_turn = False
        self.handlers: Dict[str, Callable] = {}
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

    def connect(self, player_name: str) -> bool:
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            self.listen_thread = threading.Thread(target=self.listen_for_messages)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            
            connect_packet = create_connect_packet(player_name)
            self.send_packet(connect_packet)
            
            Logger.info("NetworkClient", f"Connected to server as {player_name}")
            return True
            
        except Exception as e:
            Logger.error("NetworkClient", f"Connection failed: {str(e)}")
            self.connected = False
            return False

    def disconnect(self):
        if self.connected:
            try:
                self.socket.close()
            except:
                pass
            self.connected = False
            self.game_id = None
            self.player_number = None
            Logger.info("NetworkClient", "Disconnected from server")

    def send_packet(self, packet: Packet):
        if not self.connected:
            return
        try:
            self.socket.send(packet.to_json().encode('utf-8'))
        except Exception as e:
            Logger.error("NetworkClient", f"Failed to send packet: {str(e)}")
            self.disconnect()

    def send_game_action(self, action: Dict):
        if not self.game_id or not self.is_my_turn:
            return
        packet = create_game_action_packet(action, self.game_id)
        self.send_packet(packet)

    def listen_for_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                packet = Packet.from_json(data)
                self.handle_packet(packet)
                
            except Exception as e:
                Logger.error("NetworkClient", f"Error receiving message: {str(e)}")
                break
                
        self.disconnect()

    def handle_packet(self, packet: Packet):
        try:
            match packet.type.value:
                case "player_assignment":
                    self.player_number = packet.data["player_number"]
                    self.game_id = packet.game_id
                    Logger.info("NetworkClient", f"Assigned as Player {self.player_number}")
                    
                case "your_turn":
                    self.is_my_turn = True
                    if "turn_started" in self.handlers:
                        self.handlers["turn_started"]()
                    
                case "wait_turn":
                    self.is_my_turn = False
                    if "turn_ended" in self.handlers:
                        self.handlers["turn_ended"]()
                    
                case "game_action":
                    if "game_action" in self.handlers:
                        self.handlers["game_action"](packet.data)
                    
                case "disconnect":
                    if "player_disconnected" in self.handlers:
                        self.handlers["player_disconnected"](packet.data.get("message", ""))
                    self.disconnect()
                    
        except Exception as e:
            Logger.error("NetworkClient", f"Error handling packet: {str(e)}")

    def register_handler(self, event: str, handler: Callable):
        self.handlers[event] = handler 
import socket
import json
import threading
from typing import Optional, Callable, Dict
from src.network.common.packets import Packet, PacketType, create_connect_packet, create_game_action_packet
from src.utils.logger import Logger
import pickle

class NetworkClient:
    """
    classe : client réseau pour la communication avec le serveur de jeu
    """
    def __init__(self):
        """
        procédure : initialise le client réseau
        """
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
        """
        procédure : charge la configuration du serveur
        """
        try:
            with open('configs/server.json', 'r') as f:
                config = json.load(f)
                self.host = config['host']
                self.port = config['port']
        except Exception as e:
            Logger.error("NetworkClient", f"Failed to load config: {str(e)}")
            raise

    def connect(self, game_name: str) -> bool:
        """
        fonction : connecte le client au serveur
        params :
            game_name - nom de la partie à rejoindre
        retour : bool indiquant si la connexion a réussi
        """
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
        """
        procédure : déconnecte le client du serveur
        """
        if self.connected:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.socket.close()
            except:
                pass
            self._reset_state()
            Logger.info("NetworkClient", "Disconnected from server")
            self.call_handler("player_disconnected", "Disconnected from server")

    def _reset_state(self):
        """
        procédure : réinitialise l'état du client
        """
        self.connected = False
        self.is_my_turn = False
        self.game_id = None
        self.player_number = None

    def send_packet(self, packet: Packet):
        """
        procédure : envoie un paquet au serveur
        params :
            packet - paquet à envoyer
        """
        try:
            Logger.info("NetworkClient", f"Sending packet: {packet.type}")
            self.socket.sendall(pickle.dumps(packet))
        except Exception as e:
            Logger.error("NetworkClient", f"Error sending packet: {str(e)}")
            self.disconnect()

    def send_game_action(self, action: Dict):
        """
        procédure : envoie une action de jeu au serveur
        params :
            action - données de l'action à envoyer
        """
        if not self._can_send_action():
            return
        
        try:
            packet = create_game_action_packet(action, self.game_id)
            self.send_packet(packet)
            Logger.info("NetworkClient", f"Sent game action as Player {self.player_number}: {action}")
        except Exception as e:
            Logger.error("NetworkClient", f"Error sending game action: {str(e)}")
            self.disconnect()

    def _can_send_action(self) -> bool:
        """
        fonction : vérifie si le client peut envoyer une action
        retour : bool indiquant si l'envoi est possible
        """
        if not self.connected:
            Logger.error("NetworkClient", "Cannot send action: not connected")
            return False
        
        if not self.game_id:
            Logger.error("NetworkClient", "Cannot send action: no game ID")
            return False
        
        if not self.is_my_turn:
            Logger.warning("NetworkClient", f"Cannot send game action: not your turn (Player {self.player_number})")
            return False
            
        return True

    def listen_for_messages(self):
        """
        procédure : écoute les messages du serveur
        """
        while self.connected:
            try:
                chunk = self.socket.recv(4096)
                if not chunk:
                    Logger.info("NetworkClient", "Server closed connection")
                    self.call_handler("player_disconnected", "Connection to server lost")
                    break
                
                self.receive_buffer.extend(chunk)
                self._process_buffer()
                    
            except Exception as e:
                Logger.error("NetworkClient", f"Error receiving message: {str(e)}")
                self.call_handler("player_disconnected", "Connection error: lost connection to server")
                break
                
        self.disconnect()

    def _process_buffer(self):
        """
        procédure : traite les données reçues dans le buffer
        """
        try:
            packet = pickle.loads(self.receive_buffer)
            self.receive_buffer = bytearray()
            if packet:
                Logger.info("NetworkClient", f"Received packet: {packet.type}")
                self.handle_packet(packet)
        except (pickle.UnpicklingError, EOFError) as e:
            Logger.warning("NetworkClient", f"Error unpickling packet: {str(e)}")
            self.receive_buffer = bytearray()

    def handle_packet(self, packet):
        """
        procédure : traite un paquet reçu
        params :
            packet - paquet à traiter
        """
        try:
            if not packet or not hasattr(packet, 'type'):
                Logger.error("NetworkClient", "Invalid packet received")
                return
            
            Logger.info("NetworkClient", f"Processing packet: {packet.type}")
            
            handlers = {
                PacketType.PLAYER_ASSIGNMENT: self._handle_player_assignment,
                PacketType.YOUR_TURN: self._handle_your_turn,
                PacketType.WAIT_TURN: self._handle_wait_turn,
                PacketType.GAME_ACTION: self._handle_game_action,
                PacketType.GAME_STATE: self._handle_game_state,
                PacketType.PLAYER_DISCONNECTED: self._handle_player_disconnected,
                PacketType.DISCONNECT: self._handle_disconnect
            }
            
            if packet.type in handlers:
                handlers[packet.type](packet)
                
        except Exception as e:
            Logger.error("NetworkClient", f"Error handling packet: {str(e)}")
            Logger.error("NetworkClient", f"Packet data: {packet.data if hasattr(packet, 'data') else 'No data'}")

    def _handle_player_assignment(self, packet):
        """
        procédure : traite l'assignation du numéro de joueur
        params :
            packet - paquet d'assignation
        """
        if not packet.data or "player_number" not in packet.data:
            Logger.error("NetworkClient", "Invalid player assignment packet")
            return
        
        self.player_number = packet.data["player_number"]
        if "game_id" in packet.data:
            self.game_id = packet.data["game_id"]
        Logger.info("NetworkClient", f"Assigned as Player {self.player_number} in game {self.game_id}")
        self.call_handler("player_assignment", packet.data)

    def _handle_your_turn(self, packet):
        """
        procédure : traite le début du tour du joueur
        """
        self.is_my_turn = True
        Logger.info("NetworkClient", f"Starting turn for Player {self.player_number}")
        self.call_handler("turn_started")

    def _handle_wait_turn(self, packet):
        """
        procédure : traite l'attente du tour
        """
        self.is_my_turn = False
        other_player = 2 if self.player_number == 1 else 1
        Logger.info("NetworkClient", f"Player {self.player_number} waiting for Player {other_player}'s turn")
        self.call_handler("turn_ended")

    def _handle_game_action(self, packet):
        """
        procédure : traite une action de jeu reçue
        params :
            packet - paquet d'action
        """
        if not packet.data:
            Logger.error("NetworkClient", "Received empty game action")
            return
        Logger.info("NetworkClient", f"Player {self.player_number} received game action: {packet.data}")
        self.call_handler("game_action", packet.data)

    def _handle_game_state(self, packet):
        """
        procédure : traite une mise à jour de l'état du jeu
        params :
            packet - paquet d'état
        """
        if not packet.data:
            Logger.error("NetworkClient", "Received empty game state")
            return
        Logger.info("NetworkClient", f"Received game state update: {packet.data}")
        self.call_handler("game_state", packet.data)

    def _handle_player_disconnected(self, packet):
        """
        procédure : traite la déconnexion d'un joueur
        params :
            packet - paquet de déconnexion
        """
        message = packet.data.get("message", "Other player disconnected")
        Logger.info("NetworkClient", f"Player disconnected: {message}")
        self.call_handler("player_disconnected", message)

    def _handle_disconnect(self, packet):
        """
        procédure : traite un paquet de déconnexion
        params :
            packet - paquet de déconnexion
        """
        message = packet.data.get("message", "Disconnected from server")
        Logger.info("NetworkClient", f"Received disconnect packet: {message}")
        self.disconnect()

    def register_handler(self, event: str, handler: Callable):
        """
        procédure : enregistre un gestionnaire d'événement
        params :
            event - nom de l'événement
            handler - fonction de traitement
        """
        self.handlers[event] = handler
        Logger.info("NetworkClient", f"Registered handler for event: {event}")

    def call_handler(self, event: str, data=None):
        """
        procédure : appelle un gestionnaire d'événement
        params :
            event - nom de l'événement
            data - données de l'événement
        """
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
import socket
import json
import threading
import random
from typing import Optional, Callable, Dict, Any
from pathlib import Path
from src.network.common.packets import (
    PacketType, create_connect_dict, create_game_action_dict, create_chat_send_dict
)
from src.utils.logger import Logger

class NetworkClient:
    """
    classe : client réseau pour la communication avec le serveur de jeu
    """
    def __init__(self):
        """
        procédure : initialise le client réseau
        """
        self._load_config()
        self.socket: Optional[socket.socket] = None # socket de communication
        self.connected = False # indique si le client est connecté
        self.listen_thread: Optional[threading.Thread] = None # thread de réception des messages
        self.game_id: Optional[str] = None # id de la partie
        self.player_number: Optional[int] = None # numéro du joueur
        self.is_my_turn = False # indique si c'est le tour du joueur
        self.handlers: Dict[str, Callable] = {} # dictionnaire des gestionnaires d'événements
        self.receive_buffer = b"" # buffer de réception des messages
        Logger.initialize()

    def _load_config(self):
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
                Logger.info("NetworkClient", f"Config loaded from {config_path.resolve()}: host={self.host}, port={self.port}")
        except Exception as e:
            Logger.error("NetworkClient", f"Failed to load config: {str(e)}")
            # données brut si le fichier de configuration n'est pas trouvé
            self.host = "127.0.0.1"
            self.port = 5000    
            Logger.warning("NetworkClient", f"Using default config: host={self.host}, port={self.port}")

    def connect(self, player_name: str, game_name: str) -> bool:
        """
        fonction : connecte le client au serveur
        params :
            player_name - nom du joueur
            game_name - nom de la partie à rejoindre
        retour : bool indiquant si la connexion a réussi
        """
        if self.connected:
            Logger.warning("NetworkClient", "Already connected.")
            return True
            
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.game_id = game_name 
            Logger.info("NetworkClient", f"Socket connected to {self.host}:{self.port}")
            # démarrage du thread de réception des messages *après* la connexion de la socket
            self.listen_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
            self.listen_thread.start()
            # envoi du paquet initial CONNECT
            connect_dict = create_connect_dict(player_name, game_name)
            if not self._send_json(connect_dict):
                # si l'envoi échoue, déconnexion immédiate
                self.disconnect("Failed to send initial connect packet")
                return False
            
            Logger.info("NetworkClient", f"Successfully connected and sent CONNECT for game '{game_name}' as player '{player_name}'")
            return True
            
        except socket.gaierror as e:
             Logger.error("NetworkClient", f"Connection failed: Address-related error for {self.host}:{self.port} - {e}")
             self._reset_state()
             return False
        except ConnectionRefusedError as e:
             Logger.error("NetworkClient", f"Connection failed: Connection refused by server at {self.host}:{self.port} - {e}")
             self._reset_state()
             return False
        except Exception as e:
            Logger.error("NetworkClient", f"Connection failed: {str(e)}")
            self._reset_state() # réinitialisation de l'état
            # fermeture de la socket si elle a été créée
            if self.socket:
                try:
                    self.socket.close()
                except: pass
                self.socket = None
            return False

    def disconnect(self, reason="No reason specified"):
        """
        procédure : déconnecte le client du serveur
        """
        if not self.connected:
            return
            
        self.connected = False # flag pour arrêter les boucles
        Logger.info("NetworkClient", f"Disconnected from server. Reason: {reason}")

        # fermeture de la socket
        if self.socket:
            try:
                # shutdown peut ne pas être nécessaire ou ne fonctionner si la connexion est déjà brisée
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass # ignore les erreurs si la socket est déjà fermée/brisée
            except Exception as e:
                 Logger.warning("NetworkClient", f"Exception during socket shutdown: {e}")
            try:
                self.socket.close()
            except OSError:
                pass
            except Exception as e:
                 Logger.warning("NetworkClient", f"Exception during socket close: {e}")
            self.socket = None
            
        self._reset_state() # réinitialisation de l'état (nécessaire pour les prochaines connexions)
        Logger.info("NetworkClient", "Socket closed and state reset.")
        # appel du gestionnaire *après* la réinitialisation de l'état
        self.call_handler("player_disconnected", reason)

    def _reset_state(self):
        """
        procédure : réinitialise l'état du client
        """
        self.connected = False
        self.is_my_turn = False
        self.game_id = None
        self.player_number = None
        self.receive_buffer = b"" 
        self.listen_thread = None

    def _send_json(self, packet_dict: Dict) -> bool:
        """
        procédure : envoie un paquet au serveur
        params :
            packet - paquet à envoyer
        """
        if not self.connected or not self.socket:
            Logger.error("NetworkClient", "Cannot send: not connected.")
            return False
        try:
            json_string = json.dumps(packet_dict) # dumps : convertit un dictionnaire en chaîne de caractères JSON
            message_to_send = (json_string + '\n').encode('utf-8') # ajout d'un saut de ligne et conversion en bytes
            self.socket.sendall(message_to_send) # envoi du message au serveur
            Logger.info("NetworkClient", f"Sent JSON: {json_string}")
            return True
        except BrokenPipeError:
             Logger.warning("NetworkClient", "Failed to send: Broken pipe (server likely disconnected)")
             self.disconnect("Broken pipe during send") # déconnexion
             return False
        except Exception as e:
            Logger.error("NetworkClient", f"Error sending JSON: {str(e)}")
            self.disconnect(f"Send error: {e}") # déconnexion
            return False

    def send_game_action(self, action: Dict[str, Any]):
        """
        procédure : envoie une action de jeu au serveur
        params :
            action - données de l'action à envoyer
        """
        if not self._can_send_action(): # vérifie si le client peut envoyer une action
            return
        
        action_dict = create_game_action_dict(action, self.game_id) # création du dictionnaire de l'action
        if self._send_json(action_dict): # envoi de l'action au serveur
            Logger.info("NetworkClient", f"Sent game action as Player {self.player_number}: {action}")
        
    def _can_send_action(self) -> bool:
        """
        fonction : vérifie si le client est dans un état où il peut envoyer une action de jeu
        """
        if not self.connected:
            Logger.error("NetworkClient", "Cannot send action: not connected")
            return False
        if not self.game_id:
            Logger.error("NetworkClient", "Cannot send action: no game ID assigned yet")
            return False
        if not self.player_number:
             Logger.error("NetworkClient", "Cannot send action: no player number assigned yet")
             return False
        if not self.is_my_turn:
            Logger.warning("NetworkClient", f"Cannot send game action: not Player {self.player_number}'s turn")
            return False
        return True

    def _listen_for_messages(self):
        """
        procédure : écoute les messages du serveur
        """
        while self.connected and self.socket: 
            try:
                chunk = self.socket.recv(4096) # réception des messages (par blocs de 4096 bytes)
                if not chunk:
                    Logger.info("NetworkClient", "Server closed connection (received empty chunk).")
                    self.disconnect("Server closed connection")
                    break 
                
                self.receive_buffer += chunk
                
                while b'\n' in self.receive_buffer: # traitement du buffer pour les messages complets
                    message_bytes, self.receive_buffer = self.receive_buffer.split(b'\n', 1) # séparation du message en bytes et mise à jour du buffer
                    message_string = message_bytes.decode('utf-8').strip() # conversion en chaîne de caractères et suppression des espaces
                    
                    if not message_string:
                        continue 
                        
                    Logger.info("NetworkClient", f"Received Raw JSON: {message_string}")
                    try:
                        packet_dict = json.loads(message_string) # conversion en dictionnaire
                        self._handle_packet_dict(packet_dict) # traitement du paquet
                    except json.JSONDecodeError:
                        Logger.error("NetworkClient", f"Invalid JSON received: {message_string}")
                    except Exception as e:
                        Logger.error("NetworkClient", f"Error handling packet dict: {e}")
                        
            except ConnectionResetError:
                 Logger.info("NetworkClient", "Connection reset by server.")
                 self.disconnect("Connection reset")
                 break
            except socket.timeout:
                 Logger.warning("NetworkClient", "Socket timeout during receive.")
                 self.disconnect("Socket timeout")
                 break
            except OSError as e:
                 if self.connected:
                      Logger.error("NetworkClient", f"Socket error receiving message: {e}")
                 self.disconnect(f"Socket error: {e}")
                 break
            except Exception as e:
                if self.connected: 
                     Logger.error("NetworkClient", f"Unexpected error receiving message: {str(e)}")
                self.disconnect(f"Receive error: {e}")
                break 
                
        Logger.info("NetworkClient", "Listen thread finished.")
        if self.connected:
            self.disconnect("Listen loop terminated unexpectedly")

    def _handle_packet_dict(self, packet_dict: Dict):
        """
        procédure : gère un paquet reçu en fonction de son type
        params :
            packet_dict - dictionnaire analysé à partir de JSON
        """
        try:
            if not isinstance(packet_dict, dict) or "type" not in packet_dict or "data" not in packet_dict:
                # structure invalide du paquet
                Logger.error("NetworkClient", f"Invalid packet structure received: {packet_dict}")
                return

            packet_type_val = packet_dict.get("type") # récupération du type du paquet
            packet_data = packet_dict.get("data", {}) # récupération des données du paquet
            
            try:
                packet_type_enum = PacketType(packet_type_val)
            except ValueError:
                 Logger.warning("NetworkClient", f"Unknown packet type value received: {packet_type_val}")
                 return
            
            Logger.info("NetworkClient", f"Processing packet: Type={packet_type_enum.name}, Data={packet_data}")
            
            # définition des gestionnaires pour les types de paquets
            # permet de définir le traitement à effectuer pour chaque type de paquet
            # les gestionnaires sont des fonctions qui traitent les paquets reçus
            handlers = {
                PacketType.PLAYER_ASSIGNMENT: self._handle_player_assignment,
                PacketType.YOUR_TURN: self._handle_your_turn,
                PacketType.WAIT_TURN: self._handle_wait_turn,
                PacketType.GAME_ACTION: self._handle_game_action,
                PacketType.GAME_STATE: self._handle_game_state,
                PacketType.PLAYER_DISCONNECTED: self._handle_player_disconnected,
                PacketType.DISCONNECT: self._handle_disconnect, # Server forcing disconnect
                PacketType.CHAT_RECEIVE: self._handle_chat_message,
            }
            
            if packet_type_enum in handlers:
                handlers[packet_type_enum](packet_data)
            else:
                 Logger.warning("NetworkClient", f"No handler implemented for packet type: {packet_type_enum.name}")
                
        except Exception as e:
            Logger.error("NetworkClient", f"Error handling packet content: {str(e)}")
            Logger.error("NetworkClient", f"Packet data: {packet_dict}")

    def _handle_player_assignment(self, packet_data: Dict):
        if not isinstance(packet_data, dict) or "player_number" not in packet_data:
            Logger.error("NetworkClient", f"Invalid player assignment data: {packet_data}")
            return
        
        self.player_number = packet_data["player_number"]
        if "game_id" in packet_data:
            self.game_id = packet_data["game_id"]
            
        Logger.info("NetworkClient", f"Assigned as Player {self.player_number} in game {self.game_id}")
        self.call_handler("player_assignment", packet_data) # Pass the data dict to UI/game logic

    def _handle_your_turn(self, packet_data: Dict):
        self.is_my_turn = True
        Logger.info("NetworkClient", f"Starting turn for Player {self.player_number}")
        self.call_handler("turn_started") 

    def _handle_wait_turn(self, packet_data: Dict):
        self.is_my_turn = False
        other_player = 2 if self.player_number == 1 else (1 if self.player_number == 2 else "?")
        Logger.info("NetworkClient", f"Player {self.player_number} waiting for Player {other_player}'s turn")
        self.call_handler("turn_ended") 

    def _handle_game_action(self, packet_data: Dict):
        Logger.info("NetworkClient", f"Player {self.player_number} received game action: {packet_data}")
        self.call_handler("game_action", packet_data)

    def _handle_game_state(self, packet_data: Dict):
        Logger.info("NetworkClient", f"Received game state update: {packet_data}")
        self.call_handler("game_state", packet_data)

    def _handle_player_disconnected(self, packet_data: Dict):
        message = packet_data.get("message", "Other player disconnected")
        Logger.info("NetworkClient", f"Received player disconnected notification: {message}")
        self.call_handler("player_disconnected", message)

    def _handle_disconnect(self, packet_data: Dict):
        message = packet_data.get("message", "Server initiated disconnect")
        Logger.info("NetworkClient", f"Received disconnect command from server: {message}")
        self.disconnect(message)

    def _handle_chat_message(self, packet_data: Dict):
        """
        procédure : gère les messages de chat reçus
        params :
            packet_data - données du message de chat
        """
        if not isinstance(packet_data, dict):
            Logger.error("NetworkClient", f"Invalid chat message data: {packet_data}")
            return
            
        sender_name = packet_data.get("sender_name", "Unknown")
        message = packet_data.get("message", "")
        player_number = packet_data.get("player_number", 0)
        
        Logger.info("NetworkClient", f"Received chat message from Player {player_number} ({sender_name}): {message}")
        self.call_handler("chat_message", packet_data)

    def register_handler(self, event: str, handler: Callable):
        """
        procédure : enregistre une fonction de gestionnaire pour un événement réseau spécifique
        params :
            event - nom de l'événement (e.g., 'player_assignment', 'turn_started')
            handler - la fonction à appeler lorsque l'événement se produit
        """
        self.handlers[event] = handler
        Logger.info("NetworkClient", f"Registered handler for event: {event}")

    def call_handler(self, event: str, data: Any = None):
        """
        procédure : appelle le gestionnaire enregistré pour un événement donné
        params :
            event - nom de l'événement
            data - données optionnelles à passer au gestionnaire
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

    def send_chat_message(self, message: str, sender_name: str):
        """
        procédure : envoie un message de chat au serveur
        params :
            message - contenu du message à envoyer
            sender_name - nom de l'expéditeur
        """
        if not self.connected:
            Logger.error("NetworkClient", "Cannot send chat: not connected")
            return
        if not self.game_id or not self.player_number:
            Logger.error("NetworkClient", "Cannot send chat: game or player not initialized")
            return
            
        chat_dict = create_chat_send_dict(sender_name, message, self.player_number, self.game_id)
        if self._send_json(chat_dict):
            Logger.info("NetworkClient", f"Sent chat message as Player {self.player_number}: {message}") 
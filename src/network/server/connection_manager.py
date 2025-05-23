import socket
import json
from typing import Dict, Optional, List
from src.utils.logger import Logger
from src.network.common.packets import PacketType, create_disconnect_dict, create_player_disconnected_dict

class ConnectionManager:
    """
    classe : gère les connexions des clients et la communication réseau
    """
    def __init__(self):
        """
        procédure : initialise le gestionnaire de connexion
        """
        self.clients: Dict[socket.socket, bytes] = {} # dictionnaire des clients connectés (socket, données reçues)
        self.client_to_game: Dict[socket.socket, str] = {} # dictionnaire des clients connectés à une partie (socket, identifiant de la partie)
        self.game_manager = None # GameManager

    def set_game_manager(self, game_manager) -> None:
        """
        procédure : définit le gestionnaire de jeu
        params :
            game_manager - le gestionnaire de jeu à utiliser
        """
        self.game_manager = game_manager

    def add_client(self, client_socket: socket.socket) -> None:
        """
        procédure : ajoute un nouveau client
        params :
            client_socket - le socket du client à ajouter
        """
        self.clients[client_socket] = b""

    def remove_client(self, client_socket: socket.socket) -> None:
        """
        procédure : retire un client
        params :
            client_socket - le socket du client à retirer
        """
        if client_socket in self.clients:
            del self.clients[client_socket]

    def get_client_game(self, client_socket: socket.socket) -> Optional[str]:
        """
        fonction : récupère l'identifiant de la partie d'un client
        params :
            client_socket - le socket du client
        retour : l'identifiant de la partie ou None
        """
        return self.client_to_game.get(client_socket)

    def set_client_game(self, client_socket: socket.socket, game_id: str) -> None:
        """
        procédure : associe un client à une partie
        params :
            client_socket - le socket du client
            game_id - l'identifiant de la partie
        """
        self.client_to_game[client_socket] = game_id

    def remove_client_game(self, client_socket: socket.socket) -> Optional[str]:
        """
        fonction : retire l'association d'un client avec une partie
        params :
            client_socket - le socket du client
        retour : l'identifiant de la partie ou None
        """
        return self.client_to_game.pop(client_socket, None)

    def send_json(self, client_socket: socket.socket, packet_dict: Dict) -> bool:
        """
        fonction : envoie un message JSON à un client
        params :
            client_socket - le socket du client
            packet_dict - le dictionnaire à envoyer
        retour : True si l'envoi a réussi, False sinon
        """
        try:
            json_string = json.dumps(packet_dict) # on convertit le dictionnaire en chaîne de caractères JSON
            message_to_send = (json_string + '\n').encode('utf-8') # on ajoute un retour à la ligne et on encode en UTF-8
            client_socket.sendall(message_to_send) # on envoie le message au client
            Logger.server_send("Server", f"Sent JSON to {client_socket.getpeername()}: {json_string}") 
            return True
        except BrokenPipeError:
            Logger.server_error("Server", f"Failed to send to {client_socket.getpeername()}: Broken pipe") 
            return False
        except Exception as e:
            Logger.server_error("Server", f"Error sending JSON to {client_socket.getpeername()}: {str(e)}")
            return False

    def disconnect_client(self, client_socket: socket.socket, reason: str = "Unknown reason", is_recursive_call: bool = False) -> None:
        """
        procédure : déconnecte un client
        params :
            client_socket - le socket du client à déconnecter
            reason - la raison de la déconnexion
            is_recursive_call - indique si l'appel est récursif
        """
        if client_socket not in self.clients:
            return

        addr = client_socket.getpeername() if client_socket.fileno() != -1 else "disconnected socket" # on récupère l'adresse du client
        Logger.server_internal("Server", f"Disconnecting client {addr}. Reason: {reason}") # on log la déconnexion

        try:
            game_id = self.get_client_game(client_socket) # on récupère l'identifiant de la partie du client
            if game_id and self.game_manager and not is_recursive_call: # on vérifie si le client est dans une partie et si le GameManager existe
                game = self.game_manager.get_game(game_id) # on récupère la partie
                if game: # on vérifie si la partie existe
                    other_socket = game.get_other_player_socket(client_socket) # on récupère le socket de l'autre joueur dans la partie (session)
                    if other_socket: # on vérifie si l'autre joueur existe
                        try:
                            disconnect_packet = create_player_disconnected_dict(game_id, f"Other player disconnected: {reason}") # on crée le paquet de déconnexion
                            self.send_json(other_socket, disconnect_packet) # on envoie le paquet de déconnexion à l'autre joueur
                        except Exception as e:
                            Logger.server_error("Server", f"Failed to send disconnect notification to other player: {e}")
                        
                        self.disconnect_client(other_socket, "Game session ended", True) # on déconnecte l'autre joueur
                    
                    self.game_manager.remove_game(game_id) # on retire la partie

            if client_socket in self.clients: # on retire le client du dictionnaire des clients
                del self.clients[client_socket]
            self.remove_client_game(client_socket) # on retire l'association du client avec une partie

            try:
                if client_socket.fileno() != -1: # on ferme la connexion
                    client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                client_socket.close() # on ferme le socket
            except OSError:
                pass

        except Exception as e:
            Logger.server_error("Server", f"Error during client ({addr}) disconnect cleanup: {str(e)}")

    def process_received_data(self, client_socket: socket.socket, chunk: bytes) -> List[Dict]:
        """
        fonction : traite les données reçues d'un client
        params :
            client_socket - le socket du client
            chunk - les données reçues
        retour : liste des messages JSON traités
        """
        if not chunk:
            return []

        self.clients[client_socket] += chunk # on ajoute les données reçues au buffer
        buffer = self.clients[client_socket] # on récupère le buffer
        messages = [] # on initialise la liste des messages

        while b'\n' in buffer: # on parcourt le buffer jusqu'à trouver un retour à la ligne
            message_bytes, remaining_buffer = buffer.split(b'\n', 1) # on sépare le buffer en deux parties : le message et le reste
            buffer = remaining_buffer # on met à jour le buffer
            self.clients[client_socket] = buffer # on met à jour le buffer

            message_string = message_bytes.decode('utf-8').strip() # on décode le message en UTF-8 et on retire les espaces
            if message_string: # on vérifie si le message n'est pas vide
                try:
                    packet_dict = json.loads(message_string) # on convertit le message en dictionnaire
                    Logger.server_receive("Server", f"Received JSON from {client_socket.getpeername()}: {message_string}") 
                    messages.append(packet_dict) # on ajoute le dictionnaire au tableau des messages
                except json.JSONDecodeError:
                    Logger.server_error("Server", f"Invalid JSON received from {client_socket.getpeername()}: {message_string}")
                    self.disconnect_client(client_socket, "Invalid JSON format") # on déconnecte le client car le message n'est pas valide
                    return []

        return messages # on retourne la liste des messages
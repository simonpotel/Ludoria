from typing import Dict, Optional
from src.utils.logger import Logger
from src.network.common.packets import create_chat_receive_dict

class ChatManager:
    """
    classe : gère les messages de chat entre les joueurs
    """
    def handle_chat_message(self, game, client_socket, packet_data: Dict, connection_manager) -> bool:
        """
        fonction : gère un message de chat reçu
        params :
            game - la partie concernée
            client_socket - le socket du client qui envoie
            packet_data - les données du message
            connection_manager - le gestionnaire de connexion
        retour : True si le message a été traité avec succès, False sinon
        """
        try:
            if not self._validate_chat_data(packet_data): # on vérifie si les données sont valides 
                Logger.server_error("Server", f"Missing required fields in CHAT_SEND from {client_socket.getpeername()}")
                return False

            game_id = packet_data["game_id"]
            sender_name = packet_data["sender_name"]
            message = packet_data["message"]
            player_number = packet_data.get("player_number", 0)

            if client_socket not in [sock for sock in game.players.values()]: # on vérifie si le client est un joueur de la partie
                Logger.server_error("Server", f"Client {client_socket.getpeername()} tried to send chat to game {game_id} but is not a player")
                return False

            Logger.server_internal("Server", f"Chat message from Player {player_number} in game {game_id}: {message}")

            chat_packet = create_chat_receive_dict(
                sender_name=sender_name,
                message=message,
                player_number=player_number,
                game_id=game_id
            ) # on crée le paquet de réception du chat
 
            for player_socket in game.players.values(): # on envoie le message à tous les joueurs de la partie
                if player_socket != client_socket: # on envoie le message à tous les joueurs de la partie sauf le client qui a envoyé le message
                    # (le client qui a envoyé le message affiche son propre message)
                    Logger.server_internal("Server", f"Forwarding chat message to {player_socket.getpeername()} in game {game_id}")
                    connection_manager.send_json(player_socket, chat_packet) # on envoie le message aux destinataires

            return True

        except Exception as e:
            Logger.server_error("Server", f"Error handling chat message from {client_socket.getpeername()}: {str(e)}")
            return False

    def _validate_chat_data(self, packet_data: Dict) -> bool:
        """
        fonction : vérifie si les données du message sont valides
        params :
            packet_data - les données du message à valider
        retour : True si les données sont valides, False sinon
        """
        required_fields = ["sender_name", "message", "game_id"] # on définit les champs requis pour un message de chat
        return all(field in packet_data for field in required_fields) # on vérifie si les champs requis sont présents dans les données du message
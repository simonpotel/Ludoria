from src.utils.logger import Logger
from src.network.common.packets import create_chat_receive_dict

class ChatManager:
    def handle_chat_message(self, game, client_socket, packet_data, connection_manager):
        try:
            if not self._validate_chat_data(packet_data):
                Logger.error("Server", f"Missing required fields in CHAT_SEND from {client_socket.getpeername()}")
                return False

            game_id = packet_data["game_id"]
            sender_name = packet_data["sender_name"]
            message = packet_data["message"]
            player_number = packet_data.get("player_number", 0)

            if client_socket not in [sock for sock in game.players.values()]:
                Logger.warning("Server", f"Client {client_socket.getpeername()} tried to send chat to game {game_id} but is not a player")
                return False

            Logger.info("Server", f"Chat message from Player {player_number} in game {game_id}: {message}")

            chat_packet = create_chat_receive_dict(
                sender_name=sender_name,
                message=message,
                player_number=player_number,
                game_id=game_id
            )

            for player_socket in game.players.values():
                if player_socket != client_socket:
                    Logger.info("Server", f"Forwarding chat message to {player_socket.getpeername()} in game {game_id}")
                    connection_manager.send_json(player_socket, chat_packet)

            return True

        except Exception as e:
            Logger.error("Server", f"Error handling chat message from {client_socket.getpeername()}: {str(e)}")
            return False

    def _validate_chat_data(self, packet_data):
        required_fields = ["sender_name", "message", "game_id"]
        return all(field in packet_data for field in required_fields) 
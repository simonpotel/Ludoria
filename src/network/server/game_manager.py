import socket
from typing import Dict, Optional
from src.utils.logger import Logger
from src.network.server.game_session import GameSession
from src.network.common.packets import (
    create_player_assignment_dict,
    create_wait_turn_dict,
    create_your_turn_dict
)

class GameManager:
    def __init__(self):
        self.games: Dict[str, GameSession] = {}

    def create_game(self, game_id: str, game_type: str) -> GameSession:
        game = GameSession(game_id, game_type)
        self.games[game_id] = game
        return game

    def get_game(self, game_id: str) -> Optional[GameSession]:
        return self.games.get(game_id)

    def remove_game(self, game_id: str):
        if game_id in self.games:
            del self.games[game_id]
            Logger.server_internal("Server", f"Removed game session: {game_id}")

    def get_available_games(self):
        return [
            {
                "game_id": game_id,
                "game_type": game.game_type,
                "player_count": game.get_player_count(),
                "max_players": game.get_max_players()
            }
            for game_id, game in self.games.items()
            if not game.is_full() and game.active
        ]

    def handle_player_join(self, game: GameSession, client_socket: socket.socket, player_name: str, connection_manager) -> bool:
        try:
            player_number = game.add_player(client_socket)
            
            assignment_dict = create_player_assignment_dict(player_number, game.game_id, game.game_type)
            if not connection_manager.send_json(client_socket, assignment_dict):
                game.remove_player(client_socket)
                return False

            Logger.server_internal("Server", f"Assigned player {player_name} as Player {player_number} in game {game.game_id}")

            if game.is_full():
                self._start_game(game, connection_manager)

            return True

        except Exception as e:
            Logger.server_error("Server", f"Error setting up player {player_name}: {str(e)}")
            game.remove_player(client_socket)
            return False

    def _start_game(self, game: GameSession, connection_manager):
        Logger.server_internal("Server", f"Game {game.game_id} is full, starting game.")
        game.start()

        player1_socket = game.players.get(1)
        player2_socket = game.players.get(2)

        if not player1_socket or not player2_socket:
            Logger.server_error("Server", f"Could not find both player sockets for game {game.game_id} to start.")
            return

        your_turn_dict = create_your_turn_dict(game.game_id)
        wait_turn_dict = create_wait_turn_dict(game.game_id)

        connection_manager.send_json(player1_socket, your_turn_dict)
        connection_manager.send_json(player2_socket, wait_turn_dict)

    def handle_player_disconnect(self, game_id: str, client_socket: socket.socket, connection_manager) -> Optional[int]:
        game = self.games.get(game_id)
        if not game:
            return None

        player_number = game.remove_player(client_socket)
        game.active = False

        if player_number:
            other_socket = game.get_other_player_socket(client_socket)
            if other_socket:
                from src.network.common.packets import create_player_disconnected_dict
                disconnect_msg = f"Player {player_number} disconnected"
                player_disconnected_dict = create_player_disconnected_dict(disconnect_msg, game_id)
                connection_manager.send_json(other_socket, player_disconnected_dict)

        if game.is_empty():
            self.remove_game(game_id)
        else:
            self.remove_game(game_id)

        return player_number 
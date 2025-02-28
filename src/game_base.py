from tkinter import messagebox
from src.network.client import NetworkClient
from src.utils.logger import Logger
from src.saves import save_game
import json

class GameBase:
    def __init__(self, game_save, quadrants, game_mode="Solo"):
        self.game_save = game_save
        self.game_mode = game_mode
        self.network_client = None
        self.is_network_game = game_mode == "Network"
        self.player_number = None
        self.is_my_turn = False
        self.game_started = not self.is_network_game
        self.render = None
        
        if self.is_network_game:
            self.setup_network()

    def setup_network(self):
        self.network_client = NetworkClient()
        self.network_client.register_handler("turn_started", self.on_turn_started)
        self.network_client.register_handler("turn_ended", self.on_turn_ended)
        self.network_client.register_handler("game_action", self.on_network_action)
        self.network_client.register_handler("player_disconnected", self.on_player_disconnected)
        self.network_client.register_handler("player_assignment", self.on_player_assignment)
        self.network_client.register_handler("game_state", self.on_game_state)
        
        if not self.network_client.connect(self.game_save):
            messagebox.showerror("Error", "Failed to connect to game server")
            return
            
        Logger.info("Game", "Connected to game server")

    def update_status_message(self, message: str):
        if self.render:
            self.render.edit_info_label(message)

    def on_player_assignment(self, data):
        self.player_number = data["player_number"]
        self.game_id = data["game_id"]
        self.update_status_message(f"You are Player {self.player_number}. Waiting for game to start...")
        Logger.info("Game", f"Assigned as Player {self.player_number}")

    def on_turn_started(self):
        self.game_started = True
        self.is_my_turn = True
        self.update_status_message("Your turn")
        if self.render:
            self.render.render_board()

    def on_turn_ended(self):
        self.game_started = True
        self.is_my_turn = False
        self.update_status_message("Waiting for other player...")
        if self.render:
            self.render.render_board()

    def on_network_action(self, action_data):
        pass

    def on_game_state(self, state_data):
        pass

    def on_player_disconnected(self, message):
        messagebox.showinfo("Game Over", f"Game ended: {message}")
        if self.render:
            self.render.root.destroy()

    def send_network_action(self, action_data):
        if self.is_network_game and self.network_client:
            action_data["board_state"] = self.get_board_state()
            self.network_client.send_game_action(action_data)
            save_game(self)

    def get_board_state(self):
        return {
            "board": [[cell[:] for cell in row] for row in self.board.board],
            "round_turn": self.round_turn,
            "first_turn": self.first_turn
        }

    def can_play(self) -> bool:
        if not self.is_network_game:
            return True
        return self.game_started and self.is_my_turn

    def cleanup(self):
        if self.network_client:
            self.network_client.disconnect() 
from tkinter import messagebox, Frame, Label
from src.network.client.client import NetworkClient
from src.utils.logger import Logger
from src.saves import save_game
import json
import random
from typing import Optional, Dict

class GameBase:
    """
    classe : base commune pour tous les jeux
    """
    def __init__(self, game_save, quadrants, game_mode="Solo", player_name=None):
        """
        procédure : initialise un jeu
        params :
            game_save - sauvegarde à charger ou None
            quadrants - configuration des quadrants
            game_mode - mode de jeu (Solo ou Network)
            player_name - nom du joueur local (requis pour le mode réseau)
        """
        self.game_save = game_save
        self.quadrants = quadrants
        self.game_mode = game_mode
        self.is_network_game = game_mode == "Network"
        self.local_player_name = player_name
        self.game_started = False
        self.player_number = None
        self.is_my_turn = False
        self.network_client: Optional[NetworkClient] = None
        self.render = None
        self.selected_piece = None
        self.status_frame = None
        self.status_label = None
        self.game_id = None
        
        if self.is_network_game:
            if not self.local_player_name:
                self.local_player_name = f"Player_{random.randint(100, 999)}"
                Logger.warning("GameBase", f"No player name provided for network game, using default: {self.local_player_name}")
            self.setup_network()

    def setup_network(self):
        """
        procédure : initialise le mode réseau
        """
        if not self.local_player_name:
            Logger.error("GameBase", "Cannot setup network without a local player name.")
            messagebox.showerror("Network Error", "Local player name is missing.")
            return
        if not self.game_save:
            Logger.error("GameBase", "Cannot setup network without a game name (game_save).")
            messagebox.showerror("Network Error", "Game name/ID is missing.")
            return

        self.network_client = NetworkClient()
        self._register_network_handlers()
        
        game_name = self.game_save
        Logger.info("GameBase", f"Connecting to server for game '{game_name}' as player '{self.local_player_name}'")
        if not self.network_client.connect(self.local_player_name, game_name):
            messagebox.showerror("Connection Error", "Failed to connect to the game server.")
            self.cleanup()
            return
            
        Logger.info("GameBase", "Connected to game server, waiting for assignment...")
        self.update_status_message("Connected, waiting for player assignment...", "blue")

    def _register_network_handlers(self):
        """
        procédure : enregistre les gestionnaires d'événements réseau
        """
        if not self.network_client:
            return
        self.network_client.register_handler("player_assignment", self.on_player_assignment)
        self.network_client.register_handler("turn_started", self.on_turn_started)
        self.network_client.register_handler("turn_ended", self.on_turn_ended)
        self.network_client.register_handler("game_action", self.on_network_action)
        self.network_client.register_handler("player_disconnected", self.on_player_disconnected)

    def setup_status_display(self, parent):
        """
        procédure : configure l'affichage des messages d'état
        params :
            parent - widget parent
        """
        if self.is_network_game:
            self.status_frame = Frame(parent)
            self.status_frame.pack(side="bottom", fill="x", padx=10, pady=5)
            self.status_label = Label(self.status_frame, text="Connecting to server...", fg="blue")
            self.status_label.pack()

    def update_status_message(self, message: str, color: str = "black"):
        """
        procédure : met à jour le message d'état
        params :
            message - nouveau message
            color - couleur du texte
        """
        if self.is_network_game and self.status_label:
            self.status_label.config(text=message, fg=color)

    def on_player_assignment(self, data):
        """
        procédure : gère l'assignation du numéro de joueur
        params :
            data - données d'assignation
        """
        try:
            self.player_number = data["player_number"]
            self.game_id = data.get("game_id", self.game_save)
            self.game_started = True
            self.update_status_message(f"Assigned as Player {self.player_number}. Waiting...", "blue")
            Logger.info("GameBase", f"Assigned as Player {self.player_number} in game {self.game_id}")
        except KeyError:
            Logger.error("GameBase", f"Received invalid player assignment data: {data}")
            self.update_status_message("Error receiving player assignment!", "red")
        except Exception as e:
            Logger.error("GameBase", f"Error in on_player_assignment: {e}")
        self.player_number = data["player_number"]
        self.game_id = data.get("game_id")
        self.game_started = True
        self.update_status_message(f"You are Player {self.player_number}. Waiting for other player...", "blue")
        Logger.info("Game", f"Assigned as Player {self.player_number} in game {self.game_id}")

    def on_turn_started(self):
        """
        procédure : gère le début du tour du joueur
        """
        self.game_started = True
        self.is_my_turn = True
        self.update_status_message(f"Your turn (Player {self.player_number})", "green")
        if self.render:
            self.render.render_board()
        Logger.info("Game", "Turn started")

    def on_turn_ended(self):
        """
        procédure : gère la fin du tour du joueur
        """
        self.game_started = True
        self.is_my_turn = False
        other_player = 2 if self.player_number == 1 else 1
        self.update_status_message(f"Player {other_player}'s turn", "orange")
        if self.render:
            self.render.render_board()
        Logger.info("Game", "Turn ended")

    def on_network_action(self, action_data):
        """
        procédure : gère une action reçue du réseau
        params :
            action_data - données de l'action
        """
        Logger.info("Game", "Received network action from other player")
        if "board_state" in action_data:
            self.update_board_from_state(action_data["board_state"])
            self.render.render_board()

    def update_board_from_state(self, state):
        """
        procédure : met à jour l'état du plateau
        params :
            state - nouvel état du plateau
        """
        if not state:
            return
        self.board.board = [[cell[:] for cell in row] for row in state["board"]]
        self.round_turn = state["round_turn"]
        self.first_turn = state["first_turn"]
        Logger.info("Game", "Board state updated from network action")

    def on_player_disconnected(self, message):
        """
        procédure : gère la déconnexion d'un joueur
        params :
            message - message de déconnexion
        """
        Logger.info("Game", f"Disconnection event: {message}")
        self.game_started = False
        self.is_my_turn = False
        self.update_status_message(f"Game ended: {message}", "red")
        messagebox.showinfo("Game Over", f"Game ended: {message}")
        
        play_again = messagebox.askyesno("Play Again?", "Would you like to start a new game?")
        
        if self.render and hasattr(self.render, 'root') and self.render.root:
            root = self.render.root
            self.render.root = None
            
            def start_new_game():
                try:
                    root.destroy()
                except:
                    pass
                self.cleanup()
                if play_again:
                    from src.selector import Selector
                    Selector()
            
            root.after(100, start_new_game)

    def send_network_action(self, action_data):
        """
        procédure : envoie une action au serveur
        params :
            action_data - données de l'action
        """
        if self.is_network_game and self.network_client and self.is_my_turn:
            action_data["board_state"] = self.get_board_state()
            self.network_client.send_game_action(action_data)
            save_game(self)
            Logger.info("Game", "Sent network action to other player")

    def get_board_state(self):
        """
        fonction : récupère l'état du plateau
        retour : état du plateau
        """
        return {
            "board": [[cell[:] for cell in row] for row in self.board.board],
            "round_turn": self.round_turn,
            "first_turn": self.first_turn
        }

    def can_play(self) -> bool:
        """
        fonction : vérifie si le joueur peut jouer
        retour : True si le joueur peut jouer, False sinon
        """
        if not self.is_network_game:
            return True
        if not self.game_started:
            self.update_status_message("Waiting for game to start...", "blue")
            return False
        if not self.is_my_turn:
            other_player = 2 if self.player_number == 1 else 1
            self.update_status_message(f"Player {other_player}'s turn", "orange")
            return False
        return True

    def cleanup(self):
        """
        procédure : nettoie les ressources du jeu
        """
        if self.network_client:
            self.network_client.disconnect()
            self.game_started = False
            self.is_my_turn = False
            if self.render and hasattr(self.render, 'root') and self.render.root:
                try:
                    self.render.root.destroy()
                except:
                    pass 
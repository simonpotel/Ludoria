from tkinter import messagebox, Frame, Label
from src.network.client import NetworkClient
from src.utils.logger import Logger
from src.saves import save_game
import json

class GameBase:
    """
    classe : classe de base pour les jeux, gère le réseau et l'interface
    """
    def __init__(self, game_save, quadrants, game_mode="Solo"):
        """
        procédure : initialise une partie
        params :
            game_save - nom de la sauvegarde
            quadrants - quadrants du plateau
            game_mode - mode de jeu (Solo ou Network)
        """
        self.game_save = game_save
        self.game_mode = game_mode
        self.network_client = None
        self.is_network_game = game_mode == "Network"
        self.player_number = None
        self.is_my_turn = False
        self.game_started = not self.is_network_game
        self.render = None
        self.selected_piece = None
        self.status_frame = None
        self.status_label = None
        
        if self.is_network_game:
            self.setup_network()

    def setup_network(self):
        """
        procédure : configure la connexion réseau
        """
        self.network_client = NetworkClient()
        self._register_network_handlers()
        
        Logger.info("Game", f"Connecting to server with game name: {self.game_save}")
        if not self.network_client.connect(self.game_save):
            messagebox.showerror("Error", "Failed to connect to game server")
            return
            
        Logger.info("Game", "Connected to game server")

    def _register_network_handlers(self):
        """
        procédure : enregistre les gestionnaires d'événements réseau
        """
        handlers = {
            "turn_started": self.on_turn_started,
            "turn_ended": self.on_turn_ended,
            "game_action": self.on_network_action,
            "player_disconnected": self.on_player_disconnected,
            "player_assignment": self.on_player_assignment,
            "game_state": self.on_game_state
        }
        for event, handler in handlers.items():
            self.network_client.register_handler(event, handler)

    def setup_status_display(self, parent):
        """
        procédure : configure l'affichage du statut
        params :
            parent - widget parent pour l'affichage
        """
        if self.is_network_game:
            self.status_frame = Frame(parent)
            self.status_frame.pack(side="bottom", fill="x", padx=10, pady=5)
            self.status_label = Label(self.status_frame, text="Connecting to server...", fg="blue")
            self.status_label.pack()

    def update_status_message(self, message: str, color: str = "black"):
        """
        procédure : met à jour le message de statut
        params :
            message - message à afficher
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
        self.player_number = data["player_number"]
        self.game_id = data.get("game_id")
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

    def on_network_action(self, action_data):
        """
        procédure : gère une action réseau reçue
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

    def on_game_state(self, state_data):
        pass

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
        if self.render and self.render.root:
            self.render.root.destroy()

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
        fonction : récupère l'état actuel du plateau
        retour : dictionnaire contenant l'état du jeu
        """
        return {
            "board": [[cell[:] for cell in row] for row in self.board.board],
            "round_turn": self.round_turn,
            "first_turn": self.first_turn
        }

    def can_play(self) -> bool:
        """
        fonction : vérifie si le joueur peut jouer
        retour : bool indiquant si le joueur peut jouer
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
            if self.render and self.render.root:
                self.render.root.destroy() 
import pygame
from src.network.client.client import NetworkClient
from src.utils.logger import Logger
from src.saves import save_game
import json
import random
from typing import Optional, Dict, List

class GameBase:
    """
    classe : base commune pour tous les jeux réseau ou locaux
    gère la connexion réseau, l'état de base du jeu et les interactions communes.
    """
    def __init__(self, game_save, quadrants, game_mode="Solo", player_name=None):
        """
        constructeur : initialise un jeu, potentiellement en mode réseau.

        params:
            game_save: nom de la sauvegarde ou identifiant de la partie réseau.
            quadrants: configuration initiale des quadrants (peut être utilisé par les sous-classes).
            game_mode: mode de jeu ("Solo", "Bot", "Network").
            player_name: nom du joueur local (requis pour le mode réseau).
        """
        self.game_save = game_save
        self.quadrants = quadrants
        self.game_mode = game_mode
        self.is_network_game = game_mode == "Network"
        self.local_player_name = player_name
        self.game_started = False # indique si la partie réseau a démarré (deux joueurs connectés)
        self.player_number = None # 1 ou 2 en mode réseau
        self.is_my_turn = False # true si c'est le tour du joueur local en réseau
        self.network_client: Optional[NetworkClient] = None # client réseau
        self.render = None # référence à l'objet render (doit être défini par la sous-classe)
        self.selected_piece = None # pièce sélectionnée (utilisé par certaines sous-classes)
        self.status_message = "" # message affiché à l'utilisateur
        self.status_color = (0, 0, 0) # couleur du message
        self.game_id = None # id unique de la partie réseau
        self._bot_timer_set = False # flag pour le timer du bot
        self.chat_messages = [] # historique des messages du chat
        self.chat_input = "" # contenu actuel de l'input du chat
        self.chat_active = False # indique si l'input du chat est actuellement actif
        
        if self.is_network_game:
            if not self.local_player_name:
                # génère un nom par défaut si non fourni
                self.local_player_name = f"Player_{random.randint(100, 999)}"
                Logger.warning("GameBase", f"No player name provided for network game, using default: {self.local_player_name}")
            self.setup_network()

    def setup_network(self):
        """
        procédure : initialise et configure la connexion réseau.
        """
        if not self.local_player_name:
            Logger.error("GameBase", "Cannot setup network without a local player name.")
            return
        if not self.game_save:
            # en mode réseau, game_save est utilisé comme nom/id de la partie
            Logger.error("GameBase", "Cannot setup network without a game name (game_save).")
            return

        self.network_client = NetworkClient()
        self._register_network_handlers()
        
        game_name = self.game_save # utilise le nom de sauvegarde comme id de partie
        Logger.info("GameBase", f"Connecting to server for game '{game_name}' as player '{self.local_player_name}'")
        if not self.network_client.connect(self.local_player_name, game_name):
            Logger.error("GameBase", "Failed to connect to the game server")
            self.update_status_message("Connection failed!", "red")
            self.cleanup()
            # idéalement, informer l'utilisateur et revenir au menu principal ici
            return
            
        Logger.info("GameBase", "Connected to game server, waiting for assignment...")
        self.update_status_message("Connected, waiting for player assignment...", "blue")

    def _register_network_handlers(self):
        """
        procédure : enregistre les méthodes de cette classe pour gérer les messages du serveur.
        """
        if not self.network_client:
            return
        # association des types de messages aux méthodes correspondantes
        self.network_client.register_handler("player_assignment", self.on_player_assignment)
        self.network_client.register_handler("turn_started", self.on_turn_started)
        self.network_client.register_handler("turn_ended", self.on_turn_ended)
        self.network_client.register_handler("game_action", self.on_network_action)
        self.network_client.register_handler("player_disconnected", self.on_player_disconnected)
        self.network_client.register_handler("chat_message", self.on_chat_message)
        # ajouter d'autres handlers si nécessaire (ex: "game_over", "chat_message")

    def update_status_message(self, message: str, color=(0, 0, 0)):
        """
        procédure : met à jour le message d'état affiché à l'utilisateur et sa couleur.
        déclenche un rafraîchissement de l'affichage si le message ou la couleur change.

        params:
            message: le nouveau message à afficher.
            color: la couleur du texte (tuple RGB ou nom de couleur prédéfini).
        """
        needs_redraw = False
        if self.status_message != message:
            self.status_message = message
            needs_redraw = True
        
        # conversion des noms de couleur en RGB
        if isinstance(color, str):
            if color == "red": color = (255, 0, 0)
            elif color == "green": color = (0, 255, 0)
            elif color == "blue": color = (0, 0, 255)
            elif color == "orange": color = (255, 165, 0)
            else: color = (0, 0, 0) # noir par défaut
                
        if self.status_color != color:
            self.status_color = color
            needs_redraw = True
            
        # redessine le plateau si nécessaire et si le rendu est disponible
        if needs_redraw and self.render:
            self.render.needs_render = True

    def on_player_assignment(self, data: Dict):
        """
        procédure : gère la réception du message d'assignation du numéro de joueur.

        params:
            data: dictionnaire contenant les données d'assignation ('player_number', 'game_id').
        """
        try:
            self.player_number = data["player_number"]
            self.game_id = data.get("game_id", self.game_save)
            self.game_started = True # la partie peut commencer (même si on attend le 2eme joueur)
            # détermine si c'est notre tour initialement
            self.is_my_turn = (self.player_number == 1)
            
            status = f"You are Player {self.player_number}. "
            if self.is_my_turn:
                 status += "Your turn!"
                 color = "green"
            else:
                 status += "Waiting for Player 1..."
                 color = "orange"
                 
            self.update_status_message(status, color)
            Logger.info("GameBase", f"Assigned as Player {self.player_number} in game {self.game_id}. My turn: {self.is_my_turn}")
            if self.render: self.render.needs_render = True
        except KeyError as e:
            Logger.error("GameBase", f"Received invalid player assignment data: {data}. Missing key: {e}")
            self.update_status_message("Error receiving player assignment!", "red")
        except Exception as e:
            Logger.error("GameBase", f"Error in on_player_assignment: {e}")
            self.update_status_message("Error processing player assignment!", "red")

    def on_turn_started(self, data: Optional[Dict] = None):
        """
        procédure : gère le début du tour du joueur local.
        le paramètre 'data' est inclus pour la compatibilité future mais n'est pas utilisé.
        """
        self.game_started = True # confirme que le jeu est actif
        self.is_my_turn = True
        self.update_status_message(f"Your turn (Player {self.player_number})", "green")
        if self.render:
            self.render.needs_render = True # rafraîchit pour indiquer que c'est notre tour
        Logger.info("GameBase", f"Turn started for Player {self.player_number}")

    def on_turn_ended(self, data: Optional[Dict] = None):
        """
        procédure : gère la fin du tour du joueur local.
        le paramètre 'data' est inclus pour la compatibilité future mais n'est pas utilisé.
        """
        self.game_started = True
        self.is_my_turn = False
        other_player = 2 if self.player_number == 1 else 1
        self.update_status_message(f"Player {other_player}'s turn", "orange")
        if self.render:
            self.render.needs_render = True # rafraîchit pour indiquer l'attente
        Logger.info("GameBase", f"Turn ended for Player {self.player_number}")

    def on_network_action(self, action_data: Dict):
        """
        procédure : gère une action de jeu reçue du serveur (provenant de l'autre joueur).
        cette méthode doit être surchargée par les classes de jeu spécifiques.

        params:
            action_data: dictionnaire contenant les détails de l'action.
        """
        Logger.info("GameBase", f"Received network action: {action_data}")
        # cette méthode est une base, les sous-classes doivent l'implémenter
        # pour traiter les actions spécifiques à leur jeu.
        # exemple: mettre à jour self.board.board, self.round_turn, etc.
        
        # tentative de mise à jour générique si la sous-classe n'a pas traité l'action
        if "board_state" in action_data:
            processed = self.update_board_from_state(action_data["board_state"])
            if processed:
                Logger.info("GameBase", "Generic board update applied.")
                if self.render: self.render.needs_render = True
            else:
                 Logger.warning("GameBase", "Received action with board_state, but generic update failed or was skipped.")
        else:
            Logger.warning("GameBase", "Received network action was not processed by subclass and lacks 'board_state'.")

    def update_board_from_state(self, state: Dict) -> bool:
        """
        procédure : met à jour l'état interne du jeu (plateau, tour) à partir d'un état reçu.

        params:
            state: dictionnaire contenant l'état ('board', 'round_turn', optionnellement 'first_turn').
        
        retour:
            bool: True si la mise à jour a été effectuée, False sinon (état invalide).
        """
        if not state or "board" not in state or "round_turn" not in state:
             Logger.error("GameBase", f"Invalid board state received for update: {state}")
             return False
             
        try:
             # assure une copie profonde pour éviter les références partagées
             self.board.board = [[cell[:] for cell in row] for row in state["board"]]
             self.round_turn = state["round_turn"]
             
             # mise à jour conditionnelle des attributs spécifiques (ex: katerenga)
             if hasattr(self, 'first_turn') and "first_turn" in state:
                 self.first_turn = state["first_turn"]
                 
             if hasattr(self, 'locked_pieces') and "locked_pieces" in state:
                  old_locked = list(self.locked_pieces) if hasattr(self, 'locked_pieces') else []
                  
                  # Normalisation des locked_pieces en listes
                  normalized_locked = []
                  for pos in state["locked_pieces"]:
                      if isinstance(pos, list):
                          normalized_locked.append(pos)
                      elif isinstance(pos, tuple):
                          normalized_locked.append(list(pos))
                      else:
                          Logger.warning("GameBase", f"Unknown locked_pieces format: {pos}")
                          
                  self.locked_pieces = normalized_locked
                  
                  if old_locked != self.locked_pieces:
                      Logger.game("GameBase", f"Updated locked pieces from {old_locked} to {self.locked_pieces}")
                      
                      # Si jeu Katerenga, vérifier si cette mise à jour entraîne une victoire
                      if hasattr(self, 'check_win') and self.__class__.__name__ == "Game" and self.__module__ == "src.katerenga.game":
                          # Déterminer quel joueur vient de jouer (l'adversaire actuel)
                          player_who_moved = 1 - self.round_turn
                          Logger.game("GameBase", f"Checking victory after locked pieces update for Player {player_who_moved + 1}")
                          if self.check_win(player_who_moved):
                              Logger.success("GameBase", f"Victory detected during state update for Player {player_who_moved + 1}")
                  
             Logger.game("GameBase", f"Board state updated successfully. Turn: {self.round_turn}")
             save_game(self) # sauvegarde l'état reçu
             return True
        except Exception as e:
             Logger.error("GameBase", f"Error applying board state update: {e}. State: {state}")
             return False

    def on_player_disconnected(self, message: str):
        """
        procédure : gère l'annonce de la déconnexion de l'autre joueur.

        params:
            message: chaîne de caractères contenant le message de déconnexion.
        """
        # message is now directly the string passed by the handler
        Logger.warning("GameBase", f"Disconnection event: {message}")
        self.game_started = False
        self.is_my_turn = False
        self.update_status_message(f"Game ended: {message}", "red")
        
        if self.render is not None and hasattr(self.render, 'end_game_waiting_input') and self.render.end_game_waiting_input:
            pass
        elif self.render is not None:
            self.render.running = False

    def send_network_action(self, action_data: Dict):
        """
        procédure : envoie une action de jeu locale au serveur.
        ajoute automatiquement l'état actuel du plateau à l'action.

        params:
            action_data: dictionnaire contenant les détails spécifiques de l'action (ex: coup joué).
        """
        if self.is_network_game and self.network_client and self.is_my_turn:
            # ajoute l'état complet du jeu pour synchronisation
            action_data["board_state"] = self.get_board_state()
            
            # Log détaillé pour le débogage des problèmes de fin de partie
            Logger.game("GameBase", f"Sending network action with board state: player={self.player_number}, round_turn={self.round_turn}")
            
            self.network_client.send_game_action(action_data)
            # sauvegarde locale après avoir envoyé le coup
            save_game(self)
            Logger.info("GameBase", f"Sent network action: {action_data}")
            # la confirmation de fin de tour viendra du serveur via on_turn_ended
        elif not self.is_my_turn:
             Logger.warning("GameBase", "Attempted to send action when not my turn.")

    def get_board_state(self) -> Dict:
        """
        fonction : retourne l'état actuel complet du jeu, utilisé pour la sauvegarde et le réseau.
        les sous-classes peuvent surcharger pour ajouter des informations spécifiques.

        retour:
            dict: dictionnaire représentant l'état du jeu.
        """
        # état de base commun à tous les jeux
        state = {
            "board": [[cell[:] for cell in row] for row in self.board.board], # copie profonde
            "round_turn": self.round_turn
        }
        # ajoute des éléments spécifiques si présents dans la classe fille
        if hasattr(self, 'first_turn'):
            state["first_turn"] = self.first_turn
        if hasattr(self, 'locked_pieces'):
             state["locked_pieces"] = list(self.locked_pieces)
             
        return state

    def can_play(self) -> bool:
        """
        fonction : vérifie si le joueur local a le droit de jouer maintenant.
        utile pour bloquer les inputs en dehors de son tour en mode réseau.

        retour:
            bool: True si le joueur peut jouer, False sinon.
        """
        if not self.is_network_game:
            # en mode solo/bot, on peut toujours jouer (la logique de tour est gérée ailleurs)
            return True
            
        # vérifications pour le mode réseau
        if not self.game_started:
            self.update_status_message("Waiting for game to start...", "blue")
            return False
            
        if self.network_client and not self.network_client.opponent_connected:
            self.update_status_message("Waiting for another player to join...", "blue")
            return False
            
        if not self.is_my_turn:
            other_player = 2 if self.player_number == 1 else 1
            self.update_status_message(f"Waiting for Player {other_player}...", "orange")
            return False
            
        # si on arrive ici, c'est notre tour en réseau
        return True

    def cleanup(self):
        """
        procédure : nettoie les ressources, notamment la connexion réseau.
        appelée à la fin du jeu ou en cas d'erreur.
        """
        Logger.info("GameBase", "Cleaning up game resources.")
        if self.network_client:
            self.network_client.disconnect()
            self.network_client = None # libère la référence
        self.game_started = False
        self.is_my_turn = False
        
    def on_chat_message(self, data: Dict):
        """
        procédure : gère la réception d'un message de chat.
        
        params:
            data: dictionnaire contenant les données du message (sender_name, message, player_number).
        """
        try:
            sender_name = data.get("sender_name", "Inconnu")
            message = data.get("message", "")
            player_number = data.get("player_number", 0)
            
            # vérifie si le message est valide
            if not message:
                Logger.warning("GameBase", f"Received empty chat message from {sender_name}")
                return
                
            # ajoute le message à l'historique avec horodatage
            formatted_message = f"[Joueur {player_number}] {sender_name}: {message}"
            self.chat_messages.append(formatted_message)
            
            # limite la taille de l'historique (optionnel)
            if len(self.chat_messages) > 100:
                self.chat_messages = self.chat_messages[-100:]
                
            Logger.info("GameBase", f"Chat message received: {formatted_message}")
            
            # rafraîchit pour afficher le nouveau message
            if self.render:
                self.render.needs_render = True
                
        except Exception as e:
            Logger.error("GameBase", f"Error processing chat message: {e}")

    def send_chat_message(self, message: str):
        """
        procédure : envoie un message de chat au serveur.
        
        params:
            message: contenu du message à envoyer.
        """
        if not self.is_network_game or not self.network_client:
            Logger.warning("GameBase", "Cannot send chat: not a network game or client not initialized")
            return
            
        # vérifie si le message est valide
        if not message or message.isspace():
            return
            
        Logger.info("GameBase", f"Sending chat message: {message}")
        self.network_client.send_chat_message(message, self.local_player_name)
        
        # ajoute le message à l'historique local immédiatement
        # (il sera également reçu via le réseau comme confirmation)
        formatted_message = f"[Joueur {self.player_number}] {self.local_player_name}: {message}"
        self.chat_messages.append(formatted_message)
        
        # rafraîchit l'interface
        if self.render:
            self.render.needs_render = True
            
        # réinitialise l'input
        self.chat_input = ""

    def handle_events(self, event) -> bool:
        """
        procédure : gère les événements pygame communs, notamment le timer du bot.
        les sous-classes doivent appeler super().handle_events(event).

        params:
            event: l'événement pygame à traiter.

        retour:
            bool: True si l'événement n'a pas été traité par cette méthode (doit être traité par la sous-classe), False sinon.
        """
        # gestion du chat si en mode réseau
        if self.is_network_game:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.chat_active:
                        # envoi du message
                        self.send_chat_message(self.chat_input)
                        self.chat_input = ""
                        self.chat_active = False
                        return False
                    else:
                        # active le mode chat
                        self.chat_active = True
                        return False
                elif self.chat_active:
                    if event.key == pygame.K_ESCAPE:
                        # annule le mode chat
                        self.chat_active = False
                        return False
                    elif event.key == pygame.K_BACKSPACE:
                        # supprime le dernier caractère
                        self.chat_input = self.chat_input[:-1]
                        if self.render:
                            self.render.needs_render = True
                        return False
                    elif event.unicode and ord(event.unicode) >= 32:
                        # ajoute le caractère tapé
                        self.chat_input += event.unicode
                        if self.render:
                            self.render.needs_render = True
                        return False
        
        # gestion du timer pour déclencher le coup du bot
        if hasattr(self, '_bot_timer_set') and self._bot_timer_set:
            if event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0) # désactive le timer
                self._bot_timer_set = False
                if hasattr(self, '_bot_play'):
                    # exécute le coup du bot
                    if self._bot_play(): # si le bot a joué (et le jeu n'est pas fini)
                         if self.render: self.render.needs_render = True # rafraîchit après le coup du bot
                    return False # événement traité (timer du bot)
        return True # événement non traité par la classe de base 
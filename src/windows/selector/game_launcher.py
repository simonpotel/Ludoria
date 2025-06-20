from pathlib import Path
import json
from typing import Optional, List, Dict, Any, Union, Type
from src.utils.logger import Logger
from src.katerenga.game import Game as Katerenga
from src.isolation.game import Game as Isolation
from src.congress.game import Game as Congress
from src.saves import load_game

class GameLauncher:
    """
    classe : gestionnaire de lancement des jeux.
    responsable de la validation des paramètres, de la création d'instances de jeu,
    du chargement des sauvegardes et du démarrage de la boucle principale du jeu.
    """
    
    def __init__(self) -> None:
        """
        constructeur : procédure d'initialisation du lanceur de jeu.
        """
        pass
    
    def validate_game_params(self, game_save: str, selected_mode: str, game_modes: List[str]) -> bool:
        """
        fonction : valide les paramètres de jeu.
        vérifie que le nom de la partie n'est pas vide et que le mode de jeu sélectionné est valide.

        params:
            game_save (str): nom de la partie/sauvegarde.
            selected_mode (str): mode de jeu sélectionné.
            game_modes (list): liste des modes de jeu valides.

        retour:
            bool: `true` si les paramètres sont valides, `false` sinon.
        """
        if not game_save:
            Logger.warning("GameLauncher", "Game validation failed: the game name cannot be empty.")
            return False
        
        if selected_mode not in game_modes:
            Logger.warning("GameLauncher", f"Game validation failed: invalid game mode '{selected_mode}'.")
            return False
        
        return True

    def create_game_instance(self, selected_game: str, game_save: str, mode: str, selected_quadrants: List[List[List[List[Optional[int]]]]], player_name: Optional[str] = None) -> Union[Katerenga, Isolation, Congress]:
        """
        fonction : création d'une instance de jeu.
        crée et retourne une instance du jeu spécifié par `selected_game` avec les paramètres fournis.

        params:
            selected_game (str): type de jeu à créer (ex: "katerenga", "isolation").
            game_save (str): nom de la partie/sauvegarde.
            mode (str): mode de jeu (ex: "Solo", "Bot").
            selected_quadrants (list): configuration des quadrants sélectionnée pour le jeu.
            player_name (str, optional): nom du joueur pour les parties réseau.

        retour:
            object | none: instance du jeu créé, ou `none` si `selected_game` est inconnu.
        
        exceptions:
            valueerror: levée si `selected_game` n'est pas un type de jeu géré.
        """
        Logger.info("GameLauncher", f"Game instance creation: type={selected_game}, name={game_save}, mode={mode}")
        
        if selected_game == "katerenga":
            instance = Katerenga(game_save, selected_quadrants, mode)
        elif selected_game == "isolation":
            instance = Isolation(game_save, selected_quadrants, mode)
        elif selected_game == "congress":
            instance = Congress(game_save, selected_quadrants, mode)
        else:
            Logger.error("GameLauncher", f"Attempt to create an unknown game type: {selected_game}")
            raise ValueError(f"Game type not defined: {selected_game}")
            
        instance.game_type = selected_game
        return instance

    def start_game(self, game_save: str, selected_game: str, selected_mode: str, selected_quadrants: List[List[List[List[Optional[int]]]]], player_name: Optional[str] = None) -> bool:
        """
        procédure : démarrage d'une partie.
        crée l'instance du jeu, tente de charger une sauvegarde si elle existe, puis lance la boucle principale du jeu.
        
        params:
            game_save (str): nom de la partie/sauvegarde.
            selected_game (str): type de jeu sélectionné.
            selected_mode (str): mode de jeu sélectionné.
            selected_quadrants (list): configuration des quadrants sélectionnée.
            player_name (str, optional): nom du joueur pour les parties réseau.
            
        retour:
            bool: `true` si le jeu s'est terminé normalement, `false` en cas d'erreur critique pendant l'exécution.
        """
        game_instance = None
        
        try:
            save_file_path = Path(f'saves/{game_save}.json') # chemin vers le fichier de sauvegarde
            saved_game_type = None # type de jeu contenu dans le fichier de sauvegarde
            
            if save_file_path.is_file():
                try:
                    with open(save_file_path, 'r') as file:
                        game_state = json.load(file)
                        
                        # on extrait game de la save ("katerenga", "isolation", "congress")
                        # et on compare avec la selection de l'utilisateur
                        # si les deux ne correspondent pas, on utilise la valeur de la sauvegarde
                        # pour empecher l'utilisateur de charger une partie avec un jeu different
                        if 'game' in game_state:
                            saved_game_type = game_state['game']
                            if saved_game_type != selected_game:
                                Logger.warning("GameLauncher", f"Save file is for game type '{saved_game_type}', but '{selected_game}' was selected. Using '{saved_game_type}' from save file.")
                                selected_game = saved_game_type
                except Exception as e:
                    Logger.error("GameLauncher", f"Error reading save file: {e}")
            
            Logger.info("GameLauncher", f"Game screen initialization for {selected_game}...")
            game_instance = self.create_game_instance(selected_game, game_save, selected_mode, selected_quadrants)
            
            # stocker le nom du joueur dans l'instance du jeu si fourni pour le mode réseau
            if selected_mode == "Network" and player_name:
                game_instance.player_name = player_name
            
            if save_file_path.is_file():
                Logger.info("GameLauncher", f"Loading game state from saved file: {save_file_path}")
                success = load_game(game_instance) # module externe pour charger la sauvegarde
                
                if success:
                    Logger.success("GameLauncher", "Game state loaded successfully.")
                    if hasattr(game_instance, 'render') and game_instance.render:
                        game_instance.render.needs_render = True # force le premier rendu après chargement
                else:
                    Logger.error("GameLauncher", "Game state loading failed, starting a new game.")
            else:
                Logger.info("GameLauncher", f"No saved file found for '{game_save}'. Starting a new game.")
            
            if hasattr(game_instance, 'load_game'): # la méthode load_game est la boucle principale du jeu spécifique
                game_instance.load_game()
                Logger.success("GameLauncher", f"Game '{selected_game}' finished.")
                return True
            else:
                Logger.error("GameLauncher", f"Game instance has no load_game method: {type(game_instance)}")
                return False
                
        except Exception as e:
            Logger.error("GameLauncher", f"Critical error during game startup: {e}")
            if game_instance and hasattr(game_instance, 'cleanup'):
                game_instance.cleanup()
            return False
            

from typing import Dict, Any, List, Optional
import os
import json
from src.utils.logger import Logger


def save_game(game: Any) -> None:
    """
    procédure : sauvegarde l'état du jeu
    params :
        game - instance du jeu à sauvegarder
    """
    # skip la sauvegarde pour les fichiers de test de développement
    if game.game_save.startswith("dev_"):
        Logger.info("Saves", f"Skipping save for development test file: {game.game_save}")
        return
        
    Logger.info("Saves", f"Saving game state for {game.game_save}")
    try:
        # extraction du type de jeu depuis le nom du module de la classe
        game_type = game.__class__.__module__.split('.')[-2]  # katerenga, isolation, congress
        
        game_state: Dict[str, Any] = {
            'board': [[[cell[0], cell[1]] for cell in row] for row in game.board.board],
            'round_turn': game.round_turn,
            'game': game_type  # type de jeu (katerenga, isolation, congress)
        }

        os.makedirs("saves", exist_ok=True)
        save_path = f"saves/{game.game_save}.json"
        
        with open(save_path, 'w') as file:
            json.dump(game_state, file, indent=4)
        Logger.success("Saves", f"Game state saved to {save_path}")
    except Exception as e:
        Logger.error("Saves", f"Failed to save game state: {str(e)}")
        raise


def load_game(game: Any) -> bool:
    """
    fonction : charge l'état du jeu depuis une sauvegarde
    params :
        game - instance du jeu à charger
    retour : bool indiquant si le chargement a réussi
    """
    save_path = f"saves/{game.game_save}.json"
    Logger.info("Saves", f"Loading game state from {save_path}")
    
    try:
        with open(save_path, 'r') as file:
            game_state = json.load(file)
            _update_game_state(game, game_state)
            Logger.success("Saves", f"Game state loaded from {save_path}")
            return True
            
    except FileNotFoundError:
        Logger.warning("Saves", f"Save file not found: {save_path}")
        return False
    except json.JSONDecodeError:
        Logger.error("Saves", f"Invalid save file format: {save_path}")
        return False
    except Exception as e:
        Logger.error("Saves", f"Failed to load game state: {str(e)}")
        return False


def _update_game_state(game: Any, game_state: Dict[str, Any]) -> None:
    """
    procédure : met à jour l'état du jeu avec les données chargées
    params :
        game - instance du jeu à mettre à jour
        game_state - données de sauvegarde
    """
    Logger.board("Saves", "Updating board state from save file")
    
    # mise à jour du plateau avec vérification des dimensions
    saved_board = game_state['board']
    current_board = game.board.board
    
    for i in range(min(len(current_board), len(saved_board))):
        for j in range(min(len(current_board[i]), len(saved_board[i]))):
            current_board[i][j][0] = saved_board[i][j][0]
            current_board[i][j][1] = saved_board[i][j][1]
    
    game.round_turn = game_state['round_turn']

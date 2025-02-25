import os
import json
from src.utils.logger import Logger


def save_game(game):
    """
    méthode: sauvegarde l'état actuel du jeu dans un fichier JSON
    """
    Logger.info("Saves", f"Saving game state for {game.game_save}")
    try:
        game_state = {
            'board': [[[cell[0], cell[1]] for cell in row] for row in game.board.board],
            'game_number': game.board.game_number,
            'round_turn': game.round_turn,
        }

        os.makedirs("saves", exist_ok=True)
        with open(f"saves/{game.game_save}.json", 'w') as file:
            json.dump(game_state, file, indent=4)
        Logger.success("Saves", f"Game state saved successfully to saves/{game.game_save}.json")
    except Exception as e:
        Logger.error("Saves", f"Failed to save game state: {str(e)}")
        raise


def load_game(game):
    """
    méthode: charge l'état du jeu depuis un fichier JSON
    """
    Logger.info("Saves", f"Loading game state for {game.game_save}")
    try:
        with open(f"saves/{game.game_save}.json", 'r') as file:
            game_state = json.load(file)
            
            Logger.board("Saves", "Updating board state from save file")
            for i in range(len(game.board.board)):
                for j in range(len(game.board.board[i])):
                    game.board.board[i][j][0] = game_state['board'][i][j][0]
                    game.board.board[i][j][1] = game_state['board'][i][j][1]
            
            game.board.game_number = game_state['game_number']
            game.round_turn = game_state['round_turn']
            
            Logger.success("Saves", f"Game state loaded successfully from saves/{game.game_save}.json")
            return True
    except FileNotFoundError:
        Logger.warning("Saves", f"Save file not found: saves/{game.game_save}.json")
        return False
    except json.JSONDecodeError:
        Logger.error("Saves", f"Invalid save file format: saves/{game.game_save}.json")
        return False
    except Exception as e:
        Logger.error("Saves", f"Failed to load game state: {str(e)}")
        return False

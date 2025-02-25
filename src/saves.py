import os
import json
from src.utils.logger import Logger


def save_game(game):
    """
    procédure : sauvegarde l'état actuel du jeu dans un fichier JSON
    paramètres :
        game - instance du jeu à sauvegarder
    """
    Logger.info("Saves", f"Saving game state for {game.game_save}")
    try:
        # prépare les données à sauvegarder
        game_state = {
            'board': [[[cell[0], cell[1]] for cell in row] for row in game.board.board],
            'game_number': game.board.game_number,
            'round_turn': game.round_turn,
        }

        # crée le dossier de sauvegarde si nécessaire
        os.makedirs("saves", exist_ok=True)
        
        # écrit les données dans le fichier
        with open(f"saves/{game.game_save}.json", 'w') as file:
            json.dump(game_state, file, indent=4)
        Logger.success("Saves", f"Game state saved successfully to saves/{game.game_save}.json")
    except Exception as e:
        Logger.error("Saves", f"Failed to save game state: {str(e)}")
        raise


def load_game(game):
    """
    fonction : charge l'état du jeu depuis un fichier JSON
    paramètres :
        game - instance du jeu à charger
    retourne : True si le chargement réussit, False sinon
    """
    Logger.info("Saves", f"Loading game state for {game.game_save}")
    try:
        # lit le fichier de sauvegarde
        with open(f"saves/{game.game_save}.json", 'r') as file:
            game_state = json.load(file)
            
            # met à jour l'état du plateau
            Logger.board("Saves", "Updating board state from save file")
            for i in range(len(game.board.board)):
                for j in range(len(game.board.board[i])):
                    game.board.board[i][j][0] = game_state['board'][i][j][0]
                    game.board.board[i][j][1] = game_state['board'][i][j][1]
            
            # met à jour les autres attributs du jeu
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

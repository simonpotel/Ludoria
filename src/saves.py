import os
import json


def save_game(game):
    """
    méthode: sauvegarde l'état actuel du jeu dans un fichier JSON
    """
    game_state = {
        'board': [[[cell[0], cell[1]] for cell in row] for row in game.board.board],
        'game_number': game.board.game_number,
        'round_turn': game.round_turn,
    }

    os.makedirs("saves", exist_ok=True)
    with open(f"saves/{game.game_save}.json", 'w') as file:
        json.dump(game_state, file, indent=4)


def load_game(game):
    """
    méthode: charge l'état du jeu depuis un fichier JSON
    """
    try:
        with open(f"saves/{game.game_save}.json", 'r') as file:
            game_state = json.load(file)
            
            for i in range(len(game.board.board)):
                for j in range(len(game.board.board[i])):
                    game.board.board[i][j][0] = game_state['board'][i][j][0]
                    game.board.board[i][j][1] = game_state['board'][i][j][1]
            
            game.board.game_number = game_state['game_number']
            game.round_turn = game_state['round_turn']
            
            return True
    except FileNotFoundError:
        return False

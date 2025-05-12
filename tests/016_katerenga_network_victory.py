from test_base import TestBase
from unittest.mock import patch, MagicMock

from src.katerenga.game import Game as KaterengaGame
from src.windows.render.render import Render
from src.network.client.client import NetworkClient
from src.utils.logger import Logger
from src.saves import load_game
from src.windows.selector.config_loader import ConfigLoader
from src.moves import available_move


class TestKaterengaNetworkVictory(TestBase):
    """test pour vérifier l'envoi de paquets réseau lors d'une victoire dans katerenga"""
    
    def setUp(self):
        """initialise l'environnement de test avec les mocks nécessaires"""
        super().setUp()
        
        # configuration des quadrants
        self.config_loader = ConfigLoader()
        config_result = self.config_loader.load_quadrants()
        if not config_result:
            self.fail("échec du chargement de la configuration des quadrants")
        
        self.quadrants_config, self.quadrant_names, _ = config_result
        first_quadrant_name = self.quadrant_names[0]
        self.selected_quadrants = [self.quadrants_config[first_quadrant_name] for _ in range(4)]
        
        # création des mocks pour isoler le test
        self.client_mock = MagicMock(spec=NetworkClient)
        self.client_mock.opponent_connected = True
        self.render_mock = MagicMock(spec=Render)
        self.render_mock.running = True
        self.render_mock.needs_render = False
        
        # mock pour simuler le comportement de l'objet Render
        def mock_show_end_popup(winner_text):
            self.render_mock.end_popup_active = True
            self.render_mock.end_popup_text = winner_text
            self.render_mock.end_popup_buttons = []
            self.render_mock.needs_render = True
            # simule le comportement normal du jeu lorsque la popup est affichée
            self.render_mock.running = False
            
        self.render_mock.show_end_popup.side_effect = mock_show_end_popup
        
        # patch pour éviter la connexion réelle au serveur
        self.network_client_patch = patch('src.network.client.client.NetworkClient', return_value=self.client_mock)
        self.network_client_mock = self.network_client_patch.start()
        
        # patch pour éviter l'initialisation réelle du rendu
        self.render_patch = patch('src.windows.render.render.Render', return_value=self.render_mock)
        self.render_mock_class = self.render_patch.start()
        
        # patch pour éviter d'interagir avec pygame
        self.pygame_event_patch = patch('pygame.event.get', return_value=[])
        self.pygame_event_mock = self.pygame_event_patch.start()
        
        # patch pour les fonctions pygame d'affichage
        self.pygame_display_flip_patch = patch('pygame.display.flip')
        self.pygame_display_flip_mock = self.pygame_display_flip_patch.start()
        
        self.pygame_display_update_patch = patch('pygame.display.update')
        self.pygame_display_update_mock = self.pygame_display_update_patch.start()
        
    def tearDown(self):
        """nettoie les ressources utilisées par le test"""
        self.network_client_patch.stop()
        self.render_patch.stop()
        self.pygame_event_patch.stop()
        self.pygame_display_flip_patch.stop()
        self.pygame_display_update_patch.stop()
        super().tearDown()
    
    @patch('src.saves.save_game')
    def test_katerenga_network_victory_packet(self, mock_save_game):
        """vérifie qu'un paquet réseau est envoyé lors d'une victoire en occupant deux camps"""
        # crée le jeu en mode réseau
        game = KaterengaGame("dev_katerenga", self.selected_quadrants, "Network")
        
        # remplace le renderer par notre mock
        game.render = self.render_mock
        
        # configure le jeu pour le réseau
        game.is_network_game = True
        game.network_client = self.client_mock
        game.player_number = 1
        game.is_my_turn = True
        game.game_started = True
        game.local_player_name = "TestPlayer"
        
        # réinitialise le mock pour garantir un état propre pour les assertions
        self.client_mock.reset_mock()
        
        # force le client à un état de connexion correct pour l'envoi
        self.client_mock.is_connected = True
        self.client_mock.connected_to_game = True
        
        # charge le fichier de sauvegarde
        self.assertTrue(load_game(game), "échec du chargement du fichier de sauvegarde dev_katerenga.json")
        
        # vérifie que c'est le tour du joueur 1 (player 0 dans la représentation du code)
        self.assertEqual(game.round_turn, 0, "le test attend le tour du joueur 1 (round_turn=0)")
        
        # vérifie les positions des camps
        self.assertEqual(game.camps, [(0, 0), (0, 9), (9, 0), (9, 9)], "les camps doivent être aux coins")
        
        # vérifie qu'il y a déjà une pièce du joueur 1 à (9,0)
        self.assertEqual(game.board.board[9][0][0], 0, "il devrait y avoir une pièce du joueur 1 à la position (9,0)")
        
        # trouve une pièce du joueur 1 qui peut se déplacer vers (9,9) pour gagner
        valid_source_pos = None
        for r in range(10):
            for c in range(10):
                if game.board.board[r][c][0] == 0:  # pièce du joueur 1
                    if available_move(game.board.board, r, c, 9, 9):
                        valid_source_pos = (r, c)
                        break
            if valid_source_pos:
                break
        
        self.assertIsNotNone(valid_source_pos, "impossible de trouver une pièce du joueur 1 pouvant se déplacer vers le camp (9,9)")
        source_r, source_c = valid_source_pos
        Logger.info("Test", f"pièce valide trouvée en ({source_r}, {source_c}) pouvant se déplacer vers (9,9)")
        
        # effectue le coup gagnant
        game.on_click(source_r, source_c)  # sélection de la pièce
        game.on_click(9, 9)  # déplacement vers le camp adverse
        
        # vérifie que le client a tenté d'envoyer un paquet réseau
        self.client_mock.send_game_action.assert_called_once()
        
        # vérifie le contenu du paquet envoyé
        call_args = self.client_mock.send_game_action.call_args[0][0]
        self.assertEqual(call_args["from_row"], source_r)
        self.assertEqual(call_args["from_col"], source_c)
        self.assertEqual(call_args["to_row"], 9)
        self.assertEqual(call_args["to_col"], 9)
        self.assertIn("board_state", call_args)
        
        # vérifie que le jeu a détecté la victoire localement
        self.assertTrue(hasattr(game.render, 'end_popup_active') and game.render.end_popup_active, "Popup should be active after victory")
        
        # vérifie que la victoire est détectée correctement
        self.assertTrue(game.check_win(0), "check_win devrait retourner True pour le joueur 1 après le coup gagnant")


if __name__ == "__main__":
    import unittest
    unittest.main() 
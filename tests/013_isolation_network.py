from test_base import TestBase
from unittest.mock import patch, MagicMock

from src.isolation.game import Game as IsolationGame
from src.windows.render.render import Render
from src.network.client.client import NetworkClient
from src.network.client.game_base import GameBase
from src.board import Board


class TestIsolationNetwork(TestBase):
    """test pour vérifier l'envoi de paquets réseau dans isolation"""
    
    def setUp(self):
        """initialise l'environnement de test avec les mocks nécessaires
        
        note: un mock permet de simuler des objets complexes sans avoir besoin 
        de leurs dépendances réelles, idéal pour isoler les tests unitaires
        """
        super().setUp()
        # création des mocks pour isoler le test
        self.client_mock = MagicMock(spec=NetworkClient)
        self.render_mock = MagicMock(spec=Render)
        
        # mock pour le plateau
        self.board_mock = MagicMock(spec=Board)
        self.board_mock.board = [[[None, 0] for _ in range(8)] for _ in range(8)]
        self.board_mock.game_number = 1
        
        # patch pour éviter la connexion réelle au serveur
        self.network_client_patch = patch('src.network.client.client.NetworkClient', return_value=self.client_mock)
        self.network_client_mock = self.network_client_patch.start()
        
        # patch pour éviter l'initialisation réelle du rendu
        self.render_patch = patch('src.windows.render.render.Render', return_value=self.render_mock)
        self.render_mock_class = self.render_patch.start()
        
        # patch pour le plateau
        self.board_patch = patch('src.board.Board', return_value=self.board_mock)
        self.board_mock_class = self.board_patch.start()
        
        # patch pour éviter d'interagir avec pygame
        self.pygame_event_patch = patch('pygame.event.get', return_value=[])
        self.pygame_event_mock = self.pygame_event_patch.start()
        
    def tearDown(self):
        """nettoie les ressources utilisées par le test"""
        self.network_client_patch.stop()
        self.render_patch.stop()
        self.board_patch.stop()
        self.pygame_event_patch.stop()
        super().tearDown()
    
    def create_mocked_game(self, is_network=True):
        """crée une instance de jeu isolation avec des mocks pour les tests
        
        params:
            is_network: indique si le jeu doit être en mode réseau
        
        retour:
            une instance de jeu isolation configurée pour les tests
        """
        # ne pas vraiment créer l'instance de jeu, mais simuler une avec des mocks
        game = IsolationGame.__new__(IsolationGame)
        
        # paramètres de base
        game.game_save = "test_save"
        game.quadrants = None  # pas besoin de vrais quadrants
        game.game_mode = "Network" if is_network else "Solo"
        
        # configuration du réseau
        game.is_network_game = is_network
        game.local_player_name = "TestPlayer" if is_network else None
        game.network_client = self.client_mock
        game.player_number = 1
        game.is_my_turn = True
        game.game_started = True
        
        # autres attributs nécessaires
        game.board = self.board_mock
        game.render = self.render_mock
        game.round_turn = 0
        game.chat_messages = []
        game.chat_input = ""
        game.chat_active = False
        game.status_message = ""
        game.status_color = (0, 0, 0)
        
        return game
    
    @patch('src.saves.save_game')
    def test_connect_packet(self, mock_save_game):
        """vérifie que le paquet CONNECT est envoyé lors de la connexion"""
        # création d'une instance de jeu avec des mocks
        with patch.object(NetworkClient, 'connect', return_value=True) as connect_mock:
            # simuler la création d'un jeu qui va automatiquement se connecter
            game = self.create_mocked_game(is_network=True)
            
            # appeler manuellement setup_network pour déclencher la connexion
            GameBase.setup_network(game)
            
            # vérifier que connect a été appelé avec les bons arguments
            connect_mock.assert_called_once_with(game.local_player_name, game.game_save)
    
    @patch('src.saves.save_game')
    @patch('src.captures.has_valid_move', return_value=True)
    def test_game_action_packet(self, mock_has_valid_move, mock_save_game):
        """vérifie que le paquet GAME_ACTION est envoyé lors d'un placement de tour"""
        # création d'une instance de jeu
        game = self.create_mocked_game(is_network=True)
        game.is_my_turn = True
        
        # préparation du plateau pour simuler le placement d'une tour
        # s'assurer que la case cible est vide
        game.board.board[2][2][0] = None
        
        # simuler la validité du placement
        game.board.place_tower = MagicMock(return_value=True)
        game.get_board_state = MagicMock(return_value={"board": [], "round_turn": 0})
        
        # patch les méthodes nécessaires pour simuler un placement complet
        with patch('src.captures.is_threatened', return_value=False):
            # le jeu d'isolation place une tour directement au clic
            # c'est on_click qui doit naturellement déclencher l'envoi du paquet réseau
            IsolationGame.on_click(game, 2, 2)
        
        # vérifie que game_action a été appelé sur le client
        self.client_mock.send_game_action.assert_called_once()
        # vérifie le contenu de l'action envoyée
        call_args = self.client_mock.send_game_action.call_args[0][0]
        self.assertEqual(call_args["row"], 2)
        self.assertEqual(call_args["col"], 2)
        self.assertIn("board_state", call_args)
    
    def test_chat_send_packet(self):
        """vérifie que le paquet CHAT_SEND est envoyé lors de l'envoi d'un message"""
        # création d'une instance de jeu
        game = self.create_mocked_game(is_network=True)
        
        # message de test
        test_message = "Ceci est un message de test"
        
        # simuler l'envoi d'un message par le jeu
        game.chat_input = test_message
        game.chat_active = True
        
        # simuler l'appui sur la touche Entrée pour envoyer le message
        import pygame
        enter_event = MagicMock()
        enter_event.type = pygame.KEYDOWN
        enter_event.key = pygame.K_RETURN
        
        # c'est handle_events qui doit naturellement déclencher l'envoi du message
        IsolationGame.handle_events(game, enter_event)
        
        # vérifier que send_chat_message a été appelé avec le bon message
        self.client_mock.send_chat_message.assert_called_once_with(test_message, game.local_player_name)
    
    def test_disconnect_packet(self):
        """vérifie que le paquet DISCONNECT est envoyé lors de la déconnexion"""
        # création d'une instance de jeu
        game = self.create_mocked_game(is_network=True)
        
        # appel direct à cleanup, car c'est ainsi que se termine le jeu
        # dans un contexte normal, cela est appelé quand la fenêtre est fermée
        IsolationGame.cleanup(game)
        
        # vérifier que disconnect a été appelé
        self.client_mock.disconnect.assert_called_once()


if __name__ == "__main__":
    import unittest
    unittest.main() 
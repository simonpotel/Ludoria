from test_base import TestBase

from src.windows.selector.selector import Selector
from src.windows.selector.quadrant_handler import QuadrantHandler
from src.windows.selector.config_loader import ConfigLoader
from src.windows.selector.game_launcher import GameLauncher

class TestSelectorInit(TestBase):
    def setUp(self):
        super().setUp()
        self.original_main_loop = Selector.main_loop
        Selector.main_loop = lambda self: None
        
    def tearDown(self):
        Selector.main_loop = self.original_main_loop
        super().tearDown()
    
    def test_selector_initialization(self):
        selector = Selector()
        
        self.assertIsNotNone(selector.quadrant_handler)
        self.assertIsInstance(selector.quadrant_handler, QuadrantHandler)
        
        self.assertIsNotNone(selector.config_loader)
        self.assertIsInstance(selector.config_loader, ConfigLoader)
        
        self.assertIsNotNone(selector.game_launcher)
        self.assertIsInstance(selector.game_launcher, GameLauncher)
        
        self.assertIsNotNone(selector.screen)
        self.assertIsNotNone(selector.clock)
        
        self.assertFalse(selector.running)
        self.assertTrue(selector.outer_running)
        
        self.assertIsNotNone(selector.quadrants_config)
        self.assertIsNotNone(selector.quadrant_names)
        self.assertEqual(len(selector.selected_quadrants), 4)

if __name__ == "__main__":
    import unittest
    unittest.main() 
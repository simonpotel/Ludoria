import unittest
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBase(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.freetype.init()
        self.original_display_set_mode = pygame.display.set_mode
        pygame.display.set_mode = lambda size, flags=0, depth=0, display=0, vsync=0: pygame.Surface(size)
        
    def tearDown(self):
        pygame.display.set_mode = self.original_display_set_mode
        pygame.quit() 
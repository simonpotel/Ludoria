from test_base import TestBase

from src.windows.launcher import Launcher
from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen


class TestSelectorInit(TestBase):
    def setUp(self):
        super().setUp()

    def test_selector_initialization(self):
        launcher = Launcher()
        launcher.start()

        self.assertTrue(launcher.running)

if __name__ == "__main__":
    import unittest
    unittest.main()

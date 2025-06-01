from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
from src.utils.logger import Logger

class Selector:
    def __init__(self) -> None:
        try:
            selection_screen = ModeSelectionScreen()
            selection_screen.run()
        except Exception as e:
            Logger.error("Selector", f"Error during game selection: {e}") 
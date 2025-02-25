from datetime import datetime
from enum import Enum
from typing import Any
import colorama  

colorama.init(convert=True)

class LogLevel(Enum):
    INFO = ('\033[94m', 'INFO')         # Blue
    SUCCESS = ('\033[92m', 'SUCCESS')   # Green
    WARNING = ('\033[93m', 'WARNING')   # Yellow
    ERROR = ('\033[91m', 'ERROR')       # Red
    MOVE = ('\033[95m', 'MOVE')         # Magenta
    GAME = ('\033[96m', 'GAME')         # Cyan
    BOARD = ('\033[97m', 'BOARD')       # White
    AI = ('\033[38;5;208m', 'AI')       # Orange

class Logger:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    _instance = None

    def __init__(self):
        self.enable_colors = True

    @classmethod
    def initialize(cls):
        if cls._instance is None:
            cls._instance = Logger()

    @classmethod
    def _format_message(cls, level: LogLevel, component: str, message: Any) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        color_code, level_name = level.value
        
        base_message = f"[{timestamp}] [{level_name}] [{component}] {str(message)}"
        return f"{color_code}{base_message}{cls.RESET}"

    @classmethod
    def _log(cls, level: LogLevel, component: str, message: Any):
        if not cls._instance:
            cls.initialize()
        print(cls._format_message(level, component, message))

    @classmethod
    def info(cls, component: str, message: Any):
        cls._log(LogLevel.INFO, component, message)

    @classmethod
    def success(cls, component: str, message: Any):
        cls._log(LogLevel.SUCCESS, component, message)

    @classmethod
    def warning(cls, component: str, message: Any):
        cls._log(LogLevel.WARNING, component, message)

    @classmethod
    def error(cls, component: str, message: Any):
        cls._log(LogLevel.ERROR, component, message)

    @classmethod
    def move(cls, component: str, message: Any):
        cls._log(LogLevel.MOVE, component, message)

    @classmethod
    def game(cls, component: str, message: Any):
        cls._log(LogLevel.GAME, component, message)

    @classmethod
    def board(cls, component: str, message: Any):
        cls._log(LogLevel.BOARD, component, message)

    @classmethod
    def ai(cls, component: str, message: Any):
        cls._log(LogLevel.AI, component, message) 
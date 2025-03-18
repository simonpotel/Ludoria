from datetime import datetime
from enum import Enum
from typing import Any
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

class LogLevel(Enum):
    """
    énumération : niveaux de log avec leurs couleurs
    """
    INFO = (Fore.BLUE, 'INFO')
    SUCCESS = (Fore.GREEN, 'SUCCESS')
    WARNING = (Fore.YELLOW, 'WARNING')
    ERROR = (Fore.RED, 'ERROR')
    MOVE = (Fore.MAGENTA, 'MOVE')
    GAME = (Fore.CYAN, 'GAME')
    BOARD = (Fore.WHITE, 'BOARD')
    BOT = (Fore.LIGHTBLUE_EX, 'BOT')

class Logger:
    """
    classe : gestionnaire de logs avec différents niveaux et couleurs
    implémente le pattern singleton
    """
    _instance = None

    def __init__(self):
        """
        procédure : initialise le logger
        """
        self.enable_colors = True

    @classmethod
    def initialize(cls):
        """
        procédure : crée l'instance unique du logger
        """
        if cls._instance is None:
            cls._instance = Logger()

    @classmethod
    def _format_message(cls, level: LogLevel, component: str, message: Any) -> str:
        """
        fonction : formate un message de log
        params :
            level - niveau de log
            component - composant source
            message - contenu du message
        retour : message formaté avec couleurs
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        color_code, level_name = level.value
        base_message = f"[{timestamp}] [{level_name}] [{component}] {str(message)}"
        return f"{color_code}{Style.BRIGHT}{base_message}{Style.RESET_ALL}"

    @classmethod
    def _log(cls, level: LogLevel, component: str, message: Any):
        """
        procédure : affiche un message de log
        params :
            level - niveau de log
            component - composant source
            message - contenu du message
        """
        if not cls._instance:
            cls.initialize()
        print(cls._format_message(level, component, message))

    @classmethod
    def info(cls, component: str, message: Any):
        """
        procédure : log niveau info (bleu)
        params :
            component - composant source
            message - contenu du message
        """
        cls._log(LogLevel.INFO, component, message)

    @classmethod
    def success(cls, component: str, message: Any):
        """
        procédure : log niveau succès (vert)
        params :
            component - composant source
            message - contenu du message
        """
        cls._log(LogLevel.SUCCESS, component, message)

    @classmethod
    def warning(cls, component: str, message: Any):
        """
        procédure : log niveau avertissement (jaune)
        params :
            component - composant source
            message - contenu du message
        """
        cls._log(LogLevel.WARNING, component, message)

    @classmethod
    def error(cls, component: str, message: Any):
        """
        procédure : log niveau erreur (rouge)
        params :
            component - composant source
            message - contenu du message
        """
        cls._log(LogLevel.ERROR, component, message)

    @classmethod
    def move(cls, component: str, message: Any):
        """
        procédure : log niveau déplacement (magenta)
        params :
            component - composant source
            message - contenu du message
        """
        cls._log(LogLevel.MOVE, component, message)

    @classmethod
    def game(cls, component: str, message: Any):
        """
        procédure : log niveau jeu (cyan)
        params :
            component - composant source
            message - contenu du message
        """
        cls._log(LogLevel.GAME, component, message)

    @classmethod
    def board(cls, component: str, message: Any):
        """
        procédure : log niveau plateau (blanc)
        params :
            component - composant source
            message - contenu du message
        """
        cls._log(LogLevel.BOARD, component, message)

    @classmethod
    def bot(cls, component: str, message: Any):
        """
        procédure : log niveau bot (bleu clair)
        params :
            component - composant source
            message - contenu du message
        """
        cls._log(LogLevel.BOT, component, message)
from datetime import datetime
from enum import Enum
from typing import Any
import colorama  

colorama.init(convert=True)

class LogLevel(Enum):
    """
    énumération : définit les différents niveaux de log avec leurs couleurs associées
    """
    INFO = ('\033[94m', 'INFO')         # bleu
    SUCCESS = ('\033[92m', 'SUCCESS')   # vert
    WARNING = ('\033[93m', 'WARNING')   # jaune
    ERROR = ('\033[91m', 'ERROR')       # rouge
    MOVE = ('\033[95m', 'MOVE')         # magenta
    GAME = ('\033[96m', 'GAME')         # cyan
    BOARD = ('\033[97m', 'BOARD')       # blanc
    AI = ('\033[38;5;208m', 'AI')       # orange

class Logger:
    """
    class Logger : gère l'affichage des messages de log avec différents niveaux et couleurs
    utilise le pattern singleton pour assurer une instance unique
    """
    RESET = '\033[0m'
    BOLD = '\033[1m'
    _instance = None

    def __init__(self):
        """
        constructeur : initialise le logger avec les couleurs activées par défaut
        """
        self.enable_colors = True

    @classmethod
    def initialize(cls):
        """
        procédure : initialise l'instance unique du logger si elle n'existe pas déjà
        """
        if cls._instance is None:
            cls._instance = Logger()

    @classmethod
    def _format_message(cls, level: LogLevel, component: str, message: Any) -> str:
        """
        fonction : formate un message de log avec timestamp, niveau, composant et couleur
        paramètres :
            level - niveau de log (LogLevel)
            component - nom du composant source
            message - contenu du message
        retourne : message formaté avec les codes couleur
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        color_code, level_name = level.value
        
        base_message = f"[{timestamp}] [{level_name}] [{component}] {str(message)}"
        return f"{color_code}{base_message}{cls.RESET}"

    @classmethod
    def _log(cls, level: LogLevel, component: str, message: Any):
        """
        procédure : affiche un message de log avec le niveau spécifié
        paramètres :
            level - niveau de log (LogLevel)
            component - nom du composant source
            message - contenu du message
        """
        if not cls._instance:
            cls.initialize()
        print(cls._format_message(level, component, message))

    @classmethod
    def info(cls, component: str, message: Any):
        """
        procédure : affiche un message de niveau INFO (bleu)
        """
        cls._log(LogLevel.INFO, component, message)

    @classmethod
    def success(cls, component: str, message: Any):
        """
        procédure : affiche un message de niveau SUCCESS (vert)
        """
        cls._log(LogLevel.SUCCESS, component, message)

    @classmethod
    def warning(cls, component: str, message: Any):
        """
        procédure : affiche un message de niveau WARNING (jaune)
        """
        cls._log(LogLevel.WARNING, component, message)

    @classmethod
    def error(cls, component: str, message: Any):
        """
        procédure : affiche un message de niveau ERROR (rouge)
        """
        cls._log(LogLevel.ERROR, component, message)

    @classmethod
    def move(cls, component: str, message: Any):
        """
        procédure : affiche un message de niveau MOVE (magenta)
        """
        cls._log(LogLevel.MOVE, component, message)

    @classmethod
    def game(cls, component: str, message: Any):
        """
        procédure : affiche un message de niveau GAME (cyan)
        """
        cls._log(LogLevel.GAME, component, message)

    @classmethod
    def board(cls, component: str, message: Any):
        """
        procédure : affiche un message de niveau BOARD (blanc)
        """
        cls._log(LogLevel.BOARD, component, message)

    @classmethod
    def ai(cls, component: str, message: Any):
        """
        procédure : affiche un message de niveau AI (orange)
        """
        cls._log(LogLevel.AI, component, message) 
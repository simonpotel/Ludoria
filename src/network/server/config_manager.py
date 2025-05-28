import json
from pathlib import Path
from typing import Optional
from src.utils.logger import Logger

class ConfigManager:
    """
    classe : gère la configuration du serveur
    """
    def __init__(self):
        """
        procédure : initialise le gestionnaire de configuration avec les valeurs par défaut
        """
        self.host = "0.0.0.0" # peut être 127.0.0.1 / localhost / etc.
        self.port = 5000
        self.max_players = 2  # 2 joueurs par partie
        self.timeout = 60 # délai d'attente en secondes (si le client ne répond pas, il est déconnecté)

    def load_config(self) -> None:
        """
        procédure : charge la configuration depuis le fichier
        """
        try:
            config_path = Path('configs/server.json')
            if not config_path.is_file(): # on vérifie si le fichier de configuration existe
                raise FileNotFoundError(f"Config file not found at {config_path.resolve()}")

            with open(config_path, 'r') as f: # on charge le fichier de configuration
                config = json.load(f)
                self.host = config['host']
                self.port = config['port']
                self.max_players = config.get('max_players', 2)
                self.timeout = config.get('timeout', 60)
                Logger.server_internal("Server", f"Config loaded from {config_path.resolve()}")

        except Exception as e:
            Logger.server_error("Server", f"Failed to load config: {str(e)}")
            Logger.server_error("Server", f"Using default config: {self.host}:{self.port}")

    def get_host(self) -> str:
        """
        fonction : retourne l'hôte du serveur
        retour : l'adresse IP du serveur
        """
        return self.host

    def get_port(self) -> int:
        """
        fonction : retourne le port du serveur
        retour : le numéro de port
        """
        return self.port

    def get_max_players(self) -> int:
        """
        fonction : retourne le nombre maximum de joueurs
        retour : le nombre maximum de joueurs autorisés
        """
        return self.max_players

    def get_timeout(self) -> int:
        """
        fonction : retourne le délai d'attente
        retour : le délai d'attente en secondes
        """
        return self.timeout 
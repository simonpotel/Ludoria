import json
from pathlib import Path
from src.utils.logger import Logger

class ConfigManager:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 5000
        self.max_players = 10
        self.timeout = 60

    def load_config(self):
        try:
            config_path = Path('configs/server.json')
            if not config_path.is_file():
                raise FileNotFoundError(f"Config file not found at {config_path.resolve()}")

            with open(config_path, 'r') as f:
                config = json.load(f)
                self.host = config['host']
                self.port = config['port']
                self.max_players = config.get('max_players', 10)
                self.timeout = config.get('timeout', 60)
                Logger.info("Server", f"Config loaded from {config_path.resolve()}")

        except Exception as e:
            Logger.error("Server", f"Failed to load config: {str(e)}")
            Logger.warning("Server", f"Using default config: {self.host}:{self.port}")

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_max_players(self):
        return self.max_players

    def get_timeout(self):
        return self.timeout 
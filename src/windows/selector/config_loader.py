from pathlib import Path
import json
from typing import Optional, Dict, List, Tuple, Any
from src.utils.logger import Logger

class ConfigLoader:
    """
    classe : gestionnaire de chargement des configurations de jeu.
    responsable du chargement et de la validation initiale des fichiers de configuration, comme `quadrants.json`.
    """
    
    def __init__(self) -> None:
        """
        constructeur : procédure d'initialisation du chargeur de configuration.
        """
        pass
    
    def load_quadrants(self) -> Optional[Tuple[Dict[str, List[List[List[Optional[int]]]]], List[str], List[List[List[List[Optional[int]]]]]]]:
        """
        fonction : charge les configurations des quadrants depuis `configs/quadrants.json`.
        lit le fichier json, extrait les configurations, les noms des quadrants et les données associées.
        
        retour:
            tuple | none: un tuple `(quadrants_config, quadrant_names, quadrants_data)` en cas de succès, 
                          `none` si le fichier est introuvable, mal formaté, ou si une autre erreur survient.
        """
        config_path = Path('configs/quadrants.json')
        
        if not config_path.is_file():
            self.handle_config_error(f"Unable to find file at {config_path}")
            return None
             
        try:
            with config_path.open('r', encoding='utf-8') as file: # assure l'encodage utf-8 pour la lecture
                quadrants_config: Dict[str, List[List[List[Optional[int]]]]] = json.load(file)
                quadrant_names: List[str] = sorted(quadrants_config.keys()) # trie les noms pour un ordre constant
                quadrants_data: List[List[List[List[Optional[int]]]]] = [quadrants_config[key] for key in quadrant_names]
                
                Logger.info("ConfigLoader", f"Config of Quadrants loaded from {config_path.resolve()}")
                return quadrants_config, quadrant_names, quadrants_data
                
        except json.JSONDecodeError as e:
            self.handle_config_error(f"Invalid JSON format in {config_path}: {e}")
            return None
            
        except Exception as e: # capture toute autre exception potentielle
            self.handle_config_error(f"Unexpected error while loading quadrants: {e}")
            return None

    def handle_config_error(self, message: str) -> None:
        """
        procédure : gestion centralisée des erreurs de chargement de configuration.
        enregistre un message critique dans les logs.

        params:
            message (str): message d'erreur descriptif à enregistrer.
        """
        Logger.error("ConfigLoader", message)
        
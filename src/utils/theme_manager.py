class ThemeManager:
    """
    classe : singleton pour gérer le thème sélectionné par l'utilisateur.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._current_theme = "tropique"  # thème par défaut
        return cls._instance
    
    @property
    def current_theme(self):
        """
        fonction : accesseur pour le thème actuel.
        
        retour : le nom du thème actuel
        """
        return self._current_theme
    
    @current_theme.setter
    def current_theme(self, theme):
        """
        procédure : définit le thème actuel.
        
        params:
            theme - le nom du thème à définir
        """
        self._current_theme = theme
    
    def get_theme_path(self, asset_type=None):
        """
        fonction : obtenir le chemin du dossier du thème actuel.
        
        params:
            asset_type - type d'asset à récupérer (optionnel)
            
        retour : le chemin vers le dossier du thème ou vers un asset spécifique
        """
        base_path = f"assets/{self._current_theme}"
        
        if asset_type:
            return f"{base_path}/{asset_type}.png"
        
        return base_path
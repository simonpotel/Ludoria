class RenderConstants:
    """
    classe : constantes utilisées par le moteur de rendu.
    
    définit les constantes de style, dimensions et couleurs pour tous les composants du jeu.
    """
    # système temporaire de sélection de thème 
    THEME = "nordique"
    
    # constantes de configuration et de style
    INFO_BAR_HEIGHT = 50        # hauteur de la barre d'info en pixels
    BOARD_PADDING = 10          # marge autour du plateau de jeu
    SHADOW_OFFSET = (2, 2)      # décalage de l'ombre des pièces (x, y)
    SHADOW_ALPHA = 128          # transparence de l'ombre (0-255)
    SELECTION_COLOR = (255, 255, 255)  # couleur du cadre de sélection (blanc)
    SELECTION_WIDTH = 4         # épaisseur du cadre de sélection
    BOARD_BG_COLOR = (100, 100, 100)   # couleur de l'arrière-plan du plateau
    INFO_OVERLAY_COLOR = (0, 0, 0, 180) # couleur semi-transparente de la barre d'info
    
    # constantes pour le chat
    CHAT_WIDTH = 250            # largeur du panneau de chat en pixels
    CHAT_MARGIN = 10            # marge autour du chat en pixels
    CHAT_INPUT_HEIGHT = 30      # hauteur de la zone de saisie du chat
    CHAT_BG_COLOR = (30, 30, 30, 200)  # couleur semi-transparente du fond de chat
    CHAT_INPUT_COLOR = (50, 50, 50, 255)  # couleur de la zone de saisie
    CHAT_TEXT_COLOR = (255, 255, 255)  # couleur du texte du chat
    CHAT_INPUT_ACTIVE_COLOR = (70, 70, 70, 255)  # couleur de la zone de saisie active

    # mapping des types de terrain vers les noms de fichiers
    CELL_IMAGES = {
        0: "red.png",      # feu
        1: "green.png",    # plante
        2: "blue.png",     # eau
        3: "brown.png",    # terre
        # ici on pourra ajouter d'autres files si on a besoin pour les camps par exemple si on 
        # veut faire un asset spécial en .png et pas juste une couleur 
    }
    
    QUADRANT_COLORS = {
        0: (255, 0, 0),    # red
        1: (0, 255, 0),    # green
        2: (0, 0, 255),    # blue
        3: (165, 42, 42),  # brown (remplace yellow)
        4: (255, 255, 255),# white
        5: (0, 0, 0),      # black
        None: (128, 128, 128) # grey
    } 
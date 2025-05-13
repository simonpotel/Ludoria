import pygame

class ImageButton:
    def __init__(self, x, y, width, height, text, action=None, bg_image_path="assets/cta_background.png"):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text.upper()
        self.action = action
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        self.is_hover = False
        self.bg_image_path = bg_image_path
        self.bg_image = None
        self.load_image()
        
    def load_image(self):
        try:
            self.original_image = pygame.image.load(self.bg_image_path).convert_alpha()
            self.bg_image = self.scale_image_preserve_ratio(self.original_image, self.rect.width, self.rect.height)
        except pygame.error:
            self.bg_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            self.bg_image.fill((60, 60, 60, 230))
    
    def scale_image_preserve_ratio(self, image, target_width, target_height):
        img_width, img_height = image.get_size()
        scale_ratio = max(target_width / img_width, target_height / img_height)
        new_width = int(img_width * scale_ratio)
        new_height = int(img_height * scale_ratio)
        scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
        
        final_image = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        final_image.blit(scaled_image, (x_offset, y_offset))
        
        return final_image
    
    def draw(self, surface):
        hover_effect = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        hover_effect.fill((255, 255, 255, 30 if self.is_hover else 0))
        
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        button_surface.blit(self.bg_image, (0, 0))
        button_surface.blit(hover_effect, (0, 0))
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        button_surface.blit(text_surface, text_rect)
        
        surface.blit(button_surface, self.rect.topleft)
    
    def check_hover(self, pos):
        self.is_hover = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hover and self.action:
                self.action()
                return True
        return False 
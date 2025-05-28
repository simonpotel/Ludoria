import pygame
from src.utils.logger import Logger

class MusicManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MusicManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.current_music = None
        self.volume = 0.5
        self.is_muted = False
        self.music_files = {
            'menu': 'assets/audio/menu.mp3'
        }
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
        self._initialized = True
        Logger.info("MusicManager", "Music manager initialized")

    def play_music(self, music_type):
        if music_type in self.music_files:
            try:
                if self.current_music != music_type:
                    pygame.mixer.music.load(self.music_files[music_type])
                    pygame.mixer.music.play(-1)
                    self.current_music = music_type
                    Logger.info("MusicManager", f"Playing music: {music_type}")
                elif not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
                    Logger.info("MusicManager", f"Resuming music: {music_type}")
            except Exception as e:
                Logger.error("MusicManager", f"Error playing music: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None
        Logger.info("MusicManager", "Music stopped")

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        Logger.info("MusicManager", f"Volume set to: {self.volume}")

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.volume)
        Logger.info("MusicManager", f"Music {'muted' if self.is_muted else 'unmuted'}") 
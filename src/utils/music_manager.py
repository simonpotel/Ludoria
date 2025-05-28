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
        self.sfx_volume = 0.7
        self.is_muted = False
        self.music_files = {
            'menu': 'assets/audio/menu.mp3',
            'game': 'assets/audio/game.mp3',
            'victory': 'assets/audio/victory.mp3'
        }
        self.sfx_files = {
            'victory': 'assets/audio/victory_sfx.mp3'
        }
        self.sfx_sounds = {}
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
        self._load_sfx()
        self._initialized = True
        Logger.info("MusicManager", "Music manager initialized")

    def _load_sfx(self):
        for sfx_name, sfx_path in self.sfx_files.items():
            try:
                self.sfx_sounds[sfx_name] = pygame.mixer.Sound(sfx_path)
                self.sfx_sounds[sfx_name].set_volume(self.sfx_volume)
            except Exception as e:
                Logger.error("MusicManager", f"Error loading sound effect {sfx_name}: {e}")

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

    def play_sfx(self, sfx_name):
        if sfx_name in self.sfx_sounds and not self.is_muted:
            try:
                self.sfx_sounds[sfx_name].play()
                Logger.info("MusicManager", f"Playing sound effect: {sfx_name}")
            except Exception as e:
                Logger.error("MusicManager", f"Error playing sound effect: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None
        Logger.info("MusicManager", "Music stopped")

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        Logger.info("MusicManager", f"Volume set to: {self.volume}")

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sfx_sounds.values():
            sound.set_volume(self.sfx_volume)
        Logger.info("MusicManager", f"SFX volume set to: {self.sfx_volume}")

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            pygame.mixer.music.set_volume(0)
            for sound in self.sfx_sounds.values():
                sound.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.volume)
            for sound in self.sfx_sounds.values():
                sound.set_volume(self.sfx_volume)
        Logger.info("MusicManager", f"Music {'muted' if self.is_muted else 'unmuted'}") 
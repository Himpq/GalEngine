


_MEDIA_VOLUME = 1.0
_Channels = []

from .GalUtils import toAbsPath

def getMusicLength(path):
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from ffmpy3 import FFmpeg as ffmpeg
    import wave
    path = toAbsPath(path)
    if path[-3:].lower() == 'mp3':
        return MP3(path).info.length
    if path[-4:].lower() == 'flac':
        return FLAC(path).info.length
    if path[-3:].lower() == 'wav':
        with wave.open(path) as f:
            return f.getnframes()/int(f.getframerate())


import pygame
pygame.mixer.init()

class _Music:
    def __init__(self, path):
        self.path = toAbsPath(path)
        self.sound   = pygame.mixer.Sound(self.path)
        self.channel = pygame.mixer.find_channel()
        self.setVolume(100)
        _Channels.append(self.channel)

    def play(self, loops=0, maxTime=0, fadems=0):
        self.channel.play(self.sound, loops, maxTime, fadems)

    def getStatus(self):
        return self.channel.get_busy()
    
    def setVolume(self, v):
        self.channel.set_volume(v/100 * _MEDIA_VOLUME)

    def getVolume(self):
        return int(self.channel.get_volume()*100)

class _Music2:
    def __init__(self, path):
        self.path = toAbsPath(path)
        pygame.mixer.music.load(self.path)
        self.setVolume(100)

    def setPos(self, pos):
        pygame.mixer.music.set_pos(pos)

    def play(self, loops=0, start=0.0):
        pygame.mixer.music.play(loops, start)

    def getStatus(self):
        return pygame.mixer.music.get_busy()
    
    def setVolume(self, v):
        pygame.mixer.music.set_volume(v/100 * _MEDIA_VOLUME)

    def getVolume(self):
        return int(pygame.mixer.music.get_volume()*100)
    
    def fadeOut(self, t):
        pygame.mixer.music.fadeout(t)

    def stop(self):
        pygame.mixer.music.stop()

def setGlobalVolume(value: float):
    global _MEDIA_VOLUME

    _MEDIA_VOLUME = value
    for channel in _Channels:
        channel.set_volume(value)

    pygame.mixer.music.set_volume(value)

def playSound(file):
    return _Music(file)
def playMusic(file):
    return _Music2(file)




import GalEngine as galengine

def getMusicLength(path):
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from ffmpy3 import FFmpeg as ffmpeg
    import wave
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
        self.path = path
        self.sound   = pygame.mixer.Sound(path)
        self.channel = pygame.mixer.find_channel()
    def play(self, loops=0, maxTime=0, fadems=0):
        self.channel.play(self.sound, loops, maxTime, fadems)
    def getStatus(self):
        return self.channel.get_busy()
    def setVolume(self, v):
        self.channel.set_volume(v/100)
    def getVolume(self):
        return int(self.channel.get_volume()*100)

def playSound(file):
    return _Music(file)
def playMusic(file):
    return _Music(file)


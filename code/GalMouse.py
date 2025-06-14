
import GalEngine as galengine
import pygame

def getPos():
    return pygame.mouse.get_pos()

def getPressed():
    return pygame.mouse.get_pressed()

def leftClick():
    return getPressed()[0]
def midClick():
    return getPressed()[1]
def rightClick():
    return getPressed()[2]

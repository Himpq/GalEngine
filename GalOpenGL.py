# Using OpenGL with your gal project.

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *

except:
    print("You have to install 'pyOpenGL' to use opengl with your gal project!")
    exit()

import GalEngine as galengine
import pygame

LB = [-1, -1, -1]
RT = [1, 1, 1]
"""
               x
               |            RT [1, 1, 1]
---------------|-------------> y
LB[-1, -1, -1] |
"""

def toOpenGLFormat (rgb: list):
    return rgb[0] / 255, rgb[1] / 255, rgb[2] / 255

class Rect:
    def __init__(self, x, y, width, height):
        self.size = (x, y, width, height)

class Texture:
    def load_texture(surface: pygame.surface.Surface):
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        image = pygame.image.tostring(surface, 'RGBA', 1)
        width, height = surface.get_size()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        return texture_id
    
def init():
    glEnable(GL_TEXTURE_2D)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)  # 设置正交投影

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glEnable(GL_TEXTURE_2D)

def blitSurfaceOnScreen ():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    p = Texture.load_texture(pygame.display.get_surface())

    glBindTexture(GL_TEXTURE_2D, p)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-1.0, -1.0, 0.0)
    glTexCoord2f(1.0, 0.0); glVertex3f(1.0, -1.0, 0.0)
    glTexCoord2f(1.0, 1.0); glVertex3f(1.0, 1.0, 0.0)
    glTexCoord2f(0.0, 1.0); glVertex3f(-1.0, 1.0, 0.0)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)

    glDeleteTextures(1, [p])

class Surface:
    def __init__(self, width, height):
        self.size = [width, height]
        self.fbo  = glGenFramebuffers(1)

    def convert_alpha(self): ...

class draw:
    def rect(surface: Surface, color: list, rect: Rect):
        glBindFramebuffer(GL_FRAMEBUFFER, surface.fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, surface.fbo, 0)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, surface.rbo)

import os
import pygame
import GalEngine as galengine
ADD = 1
DEL = -1
transitionList = {}

def scale(gui, size):
    return pygame.transform.scale(gui.getSurface(), size)

class SmoothZoom:
    def __init__(self, gui, changeVar, from_, to, time):
        self.gui       = gui
        self.changeVar = changeVar
        self.from_     = from_
        self.to        = to
        self.time      = time
        self.nowVar    = from_
        galengine.GalLog.Print("[GalTrans]")

    def int(self, t):
        if not self.allowFloat:
            return int(t)
        else:
            return float(t)
        
    def init(self, allowFloat=False):
        self.allowFloat = allowFloat
        self.fps = galengine.fpsControl.get()
        self.dsize = self.from_ - self.to
        if self.dsize < 0:
            self.type = ADD
        else:
            self.type = DEL
        self.framecount = self.fps*self.time
        self.dperframe  = self.int((self.type)*self.int(self.dsize / self.framecount))
        
        if self.dperframe == 0:
            self.dperframe = 1*self.type

    def start(self):
        if not 'func' in str(type(self.changeVar)):
            def changeCallback(s):
                self.gui.__dict__[self.changeVar] += s
        else:
            changeCallback = self.changeVar

        self.changecb              = changeCallback
        self.start                 = True
        self.finish                = False
        transitionList[hash(self)] = self

    def update(self):
        if not self.start:
            return
        self.nowVar += self.dperframe
        self.changecb(self.nowVar)
        

        if self.nowVar <= self.to:
            self.start  = False
            self.finish = True
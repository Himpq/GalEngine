
import os
import pygame
import GalEngine as galengine
ADD = 1
DEL = -1
BEFORE_ASSEMBLY = 0
AFTER_ASSEMBLY = 1
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
        
        if self.dperframe <= 0:
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

        if self.nowVar >= self.to:
            self.start  = False
            self.finish = True


class Transition:
    """支持多种变化速率的过渡动画类"""
    
    EASE_LINEAR = 'linear'
    EASE_IN = 'ease-in'
    EASE_OUT = 'ease-out'
    EASE_IN_OUT = 'ease-in-out'

    DEFAULT_EASES = [EASE_IN, EASE_OUT, EASE_IN_OUT, EASE_LINEAR]
    
    def __init__(self, gui, changeVar, from_, to, time, ease_type=EASE_LINEAR, startCallback=None, finishCallback=None):
        self.gui = gui
        self.changeVar = changeVar
        self.startCallback = startCallback if startCallback else lambda: None
        self.finishCallback = finishCallback if finishCallback else lambda: None
        self.from_ = float(from_)
        self.to = float(to)
        self.time = time
        self.ease_type = ease_type
        self.nowVar = from_
        self.progress = 0.0  # 当前进度(0.0 - 1.0)
        self.formula = False

        if not ease_type in self.DEFAULT_EASES:
            self.formula = ease_type
        
    def init(self, allowFloat=True):
        """初始化过渡动画"""
        self.allowFloat = allowFloat
        self.fps = galengine.fpsControl.get()
        self.framecount = int(self.fps * self.time)
        # print("Init an animation with frame count:", self.framecount)
        
    def _ease_function(self, x):
        """根据不同的缓动类型返回对应的缓动值"""
        if self.formula:
            return self.formula(x)
        if self.ease_type == self.EASE_LINEAR:
            return x
        elif self.ease_type == self.EASE_IN:
            return x * x
        elif self.ease_type == self.EASE_OUT:
            return 1 - (1 - x) * (1 - x)
        elif self.ease_type == self.EASE_IN_OUT:
            if x < 0.5:
                return 2 * x * x
            else:
                return 1 - (-2 * x + 2) * (-2 * x + 2) / 2
        return x

    def start(self, moment=BEFORE_ASSEMBLY):
        """开始过渡动画"""
        if not 'func' in str(type(self.changeVar)):
            def changeCallback(s):
                self.gui.__dict__[self.changeVar] = s
        else:
            changeCallback = self.changeVar
            
        self.changecb = changeCallback
        self.started = True
        self.finish = False
        self.progress = 0.0
        self.firstFrame = True
        transitionList[hash(self)] = self, moment
        
    def update(self):
        """更新过渡动画"""
        if not self.started or self.finish:
            return
        
        if self.firstFrame:
            self.firstFrame = False
            self.startCallback()
            
        self.progress += 1.0 / self.framecount

        if self.progress >= 1.0:
            self.progress = 1.0
            self.finish = True
            self.started = False
            self.finishCallback()
            return
            
        # 使用缓动函数计算当前值
        eased_progress = self._ease_function(self.progress)
        current_value = self.from_ + (self.to - self.from_) * eased_progress
        
        if not self.allowFloat:
            current_value = int(current_value)
            
        self.nowVar = current_value
        self.changecb(self.nowVar)

    def stop(self):
        self.finish = True
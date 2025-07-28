"""
    GalEngine By Himpq
"""
# True False

from .GalRegistry import GalGlobals, Status
from .GalUtils import Assembly, stop_thread
from .GalUtils import Mouse as mouse
from .GalFPSControl import fpsControl, NO_LIMITED

import threading
import time
import sys
import os
import pygame
pygame.init()

from . import GalLog
from . import GalSDL2 as gsdl
from . import GalError
from . import GalTransition as gtran
from . import GalGUI as gui
from . import GalMedia as media
from . import GalTimer as timer
from . import GalRegistry
from . import GalConfig as galcfg


GalRegistry.GalGlobals._assemblies = []

def setWindowSize(width, height):
    """Set window size"""
    if not GalGlobals.usingSDL2:
        if not GalGlobals.isAndroid:
            pygame.display.set_mode(size=(width, height), flags=GalRegistry.GalGlobals.screen.get_flags())
        else:
            pygame.display.set_mode(size=(width, height))
    else:
        GalRegistry.GalGlobals.screen.set_mode(size=(width, height))


def setWindowType(type_=0):
    """Set window render mode"""
    if not GalGlobals.usingSDL2:
        pygame.display.set_mode(size=(GalRegistry.GalGlobals.screen.get_size()), flags=type_)
    else:
        GalRegistry.GalGlobals.screen.set_mode(flags=type_)

def getWindowSize():
    "Return window size"
    return pygame.display.get_window_size()

# Assemblies Manager

def setMainAssembly(asm: Assembly):
    """Set main assembly"""
    GalGlobals._mainAssembly = asm


def addAssembly(Class: Assembly, runStart = True):
    """Add Assembly to the engine"""

    if not Class.__class__.__base__ == Assembly:
        raise GalError.AssemblyExtendsError("组件必须继承 GalAPI.Assembly 类。")
    
    if not Status.isScreenInit and GalGlobals.usingSDL2:
        Status.isScreenInit = True
        GalRegistry.GalGlobals.screen.init()
    
    GalRegistry.GalGlobals._assemblies.append(Class)

    GalRegistry.GUIHandler.restoreGUIs(Class)
    GalRegistry.EventHandler.restoreEventHandlers(Class)

    if len(GalRegistry.GalGlobals._assemblies) == 1:
        setMainAssembly(Class)
        print("[AsmManager] Set main assembly to", Class.__class__.__name__)

    Class.Start() if runStart else None

def removeAssembly():
    """Remove the last added Assembly"""
    asm = GalRegistry.GalGlobals._assemblies.pop()
    asm.Destroy()

    GalRegistry.EventHandler.saveEventHandlers(asm)
    GalRegistry.GUIHandler.saveGUIs(asm)

def getAssemblies():
    """Get all Assemblies"""
    return GalRegistry.GalGlobals._assemblies

def removeAllAssemblies():
    """Remove all Assemblies"""
    for i in GalRegistry.GalGlobals._assemblies:
        i.Destroy()
    GalRegistry.GalGlobals._assemblies.clear()

def getMainAssembly():
    """Get the main Assembly"""
    return GalRegistry.GalGlobals.getMainAssembly()

# Update Functions

def update(rectangle):
    """Update the display with a specific rectangle."""
    pygame.display.update(rectangle)

def updateTranslations(type_=gtran.BEFORE_ASSEMBLY):
    """Update translations based on the moment."""
    dellist = []
    nowFrameTransitionList = gtran.transitionList.copy()
    for i in nowFrameTransitionList:
            item, moment = nowFrameTransitionList[i]
            if moment == type_:
                if item.finish:
                    dellist.append(i)
                else:
                    item.update()
    for d in dellist:
        del gtran.transitionList[d]

def updateAssemblies():
    """Update all Assemblies and return their GUI components."""
    refreshgui = []
    for i in GalRegistry.GalGlobals._assemblies:
        lsgui = i.Draw()
        refreshgui.append(lsgui)
    return refreshgui

def startAssemblies():
    """Start all Assemblies."""
    for i in GalRegistry.GalGlobals._assemblies:
        i.Start()




def init():
    if not GalGlobals.usingSDL2:
        GalRegistry.GalGlobals.screen = pygame.display.set_mode((640, 480), 0, 32)
        pygame.display.set_caption("GalEngine Window")
    else:
        GalRegistry.GalGlobals.screen = gsdl.screen()

    @GalRegistry.EventHandler.register(pygame.QUIT)
    def handle_quit(event):
        GalRegistry.GalGlobals.Done = True
        return True  # 终止事件传播

    @GalRegistry.EventHandler.register(pygame.VIDEORESIZE)
    def handle_resize(event):
        setWindowSize(*event.size)
        return True  # 终止事件传播
    

    


def show():
    """Start the main loop to show the window and handle events."""
    global __Repaint

    GalRegistry.GalGlobals.Done = False           # 结束绘制
    fCount    = 0                                 # 总帧数计数器
    startTime = time.time()                       # 起始时间
    averTime  = []                                # 每帧耗时列表
    eventList = []                                # 事件列表
    fontRdFPS = pygame.font.SysFont("Arial", 20)  # 默认字体

    GalLog.Print("Start drawing.")

    startAssemblies()

    while not GalRegistry.GalGlobals.Done:
        #帧数控制和页面刷新
        FPS = fpsControl.get()
        fpsControl.refresh()
        fpsControl.tick(FPS)

        o1 = time.time()

        #清屏
        GalRegistry.GalGlobals.screen.fill((0, 0, 0))

        #更新组件(per frame)
        for i in GalRegistry.GalGlobals._assemblies:
            i.Update()

        #更新计时器
        for i in timer.TIMERS:
            timer.TIMERS[i].check()

        if not GalGlobals.usingSDL2:
            eventList = pygame.event.get(pump=True)
            #将events传给各EventHandler
            for event in eventList:
                GalRegistry.EventHandler.handle(event)
            
            pygame.event.pump()

        else:
            event = gsdl.sdl2.SDL_Event()
            event = gsdl.sdl2.SDL_Event()
            while gsdl.sdl2.SDL_PollEvent(event):
                # 将SDL事件包装为SDLEvent对象
                pe = gsdl.SDLEvent(event)
                
                # 使用EventHandlerClass处理事件
                GalRegistry.EventHandler.handle(pe)
                    
        if Status.isRequestedRefresh or not len(eventList) == 0 or Status.isContinuousRefresh:
            #刷新动画
            updateTranslations()
            #重绘Assembly使用的GUI
            refreshgui = updateAssemblies()
            #刷新动画
            updateTranslations(gtran.AFTER_ASSEMBLY)
            
            # 是否全局刷新
            if not GalGlobals.usingSDL2:
                if not GalGlobals.isAndroid:
                    if fpsControl.getRefreshAll():
                        pygame.display.update()
                    else:
                        for ls in refreshgui:
                            for gui in ls:
                                pygame.display.update(pygame.Rect(*gui.getRect()))
                
                else:
                    if fpsControl.getRefreshAll():
                        # 帧数显示
                        fps_text = fontRdFPS.render(f"FPS: {fpsControl.getAverageFPS()}", True, (0, 0, 0), (255,255,255))
                        GalRegistry.GalGlobals.screen.blit(fps_text, (5, 5))
                        pygame.display.update()
            else:
                GalRegistry.GalGlobals.screen.update()

            Status.isRequestedRefresh = False
        
        
        fCount += 1
        o2 = time.time()
        averTime.append(o2-o1)

    t2 = time.time()

    GalLog._print = True
    GalLog.Print("Stop drawing.")
    GalLog.Print("在",t2-startTime,"秒内绘制了",fCount,"次,平均每帧耗时", sum(averTime)/len(averTime), "s")
    GalLog.Print("最低帧耗时", min(averTime), "，最高帧耗时", max(averTime), "; 平均帧率:", len(averTime)/sum(averTime))
    GalLog.saveLog()

    for i in threading.enumerate():
        if not i.name == 'MainThread':
            stop_thread(i)
    
    time.sleep(0.02)

    pygame.quit()

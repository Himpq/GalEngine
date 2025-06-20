"""
    GalEngine By Himpq
"""

NO_LIMITED = 0xff

isAndroid = True

import sys
import os
sys.path.append("./GalEngine")

from GalAPI import Assembly, EmptyObject
import GalConfig as galcfg

import threading
import time
import inspect
import ctypes

import pygame


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

EVENTS = {
    "MouseDown": pygame.MOUSEBUTTONDOWN, #鼠标左右键点击
    "MouseMotion": pygame.MOUSEMOTION,   #鼠标移动事件
    "MouseUp": pygame.MOUSEBUTTONUP,     #鼠标弹起事件
    "KeyDown": pygame.KEYDOWN,
    "KeyUp": pygame.KEYUP,
}

class WINDOWTYPE:
    FullScreen = pygame.FULLSCREEN   #全屏
    DoubleBuf  = pygame.DOUBLEBUF
    HWSurface  = pygame.HWSURFACE    #硬件加速
    OpenGL     = pygame.OPENGL       #可使用OpenGL
    Resizable  = pygame.RESIZABLE    #可改变大小
    NoFrame    = pygame.NOFRAME      #隐藏边框控制条

usingSDL2 = True

if usingSDL2:
    import GalSDL2 as gsdl


__Assemblies = []
__EventHandler = {}
__Repaint = False
RefreshRequest = False
StillRefresh = True
Showing = False

usingAbsPath = False

def useAbsolutePath():
    """Buildozer to Android Application, you should enable this."""
    global usingAbsPath
    usingAbsPath = True

def toAbsPath(path):
    return os.path.abspath(path) if usingAbsPath else path

import GalLog


GalLog.Print("Pygame init...")

pygame.init()

import GalError
import GalTransition as gtran
import GalFPSControl as gfps
import GalGUI as gui
import GalMedia as media
import GalTimer as timer
import GalMouse as mouse


clock  = pygame.time.Clock()

if not usingSDL2:
    screen = pygame.display.set_mode((640, 480), 0, 32)
    pygame.display.set_caption("GalEngine Window")
else:
    screen = gsdl.screen()



GalError.log = GalLog
fpsControl = gfps.fpsControlObject()

def blit(widget, at):
    screen.blit(widget, at)

def setWindowSize(width, height):
    """Set window size"""
    if not usingSDL2:
        if not isAndroid:
            pygame.display.set_mode(size=(width, height), flags=screen.get_flags())
        else:
            pygame.display.set_mode(size=(width, height))
    else:
        screen.set_mode(size=(width, height))


def setWindowType(type_=0):
    """Set window render mode"""
    if not usingSDL2:
        pygame.display.set_mode(size=(screen.get_size()), flags=type_)
        if type_ & pygame.OPENGL != 0:
            print("[GalEngine Warning] You are using OpenGL with your project! It will make your project unstable!")
            import GalOpenGL as opengl
            globals()['opengl'] = opengl
            opengl.init()
    else:
        screen.set_mode(flags=type_)

def getWindowSize():
    "Return window size"
    return pygame.display.get_window_size()


# Assembli Manager

def addAssembly(Class: Assembly):
    if not Class.__class__.__base__ == Assembly:
        raise GalError.AssemblyExtendsError("组件必须继承 GalAPI.Assembly 类。")
    __Assemblies.append(Class)

def removeAssembly():
    __Assemblies.pop().Destroy()

def getAssemblies():
    return __Assemblies


def EventHandler(EventType, assembly):
    f = lambda:None
    def h(func):
        nonlocal f
        f = func
        def w(*arg, **args):
            nonlocal f
            return f(*arg, **args)
        return w
    if __EventHandler.get(EventType) == None:
        __EventHandler[EventType] = []
    __EventHandler[EventType].append((h(f), assembly))
    return h

def removeEventHandler(EventType, assembly):
    if __EventHandler.get(EventType) == None:
        return
    for i in __EventHandler[EventType]:
        if i[1] == assembly:
            __EventHandler[EventType].remove(i)
            print(__EventHandler)
            break

def update(rectangle):
    pygame.display.update(rectangle)

def show():
    global __Repaint, RefreshRequest
    GalLog.Print("Start drawing.")
    for i in __Assemblies:
        i.Start()

    Done = False
    n = 0
    t = time.time()
    pjtime = []
    Showing = True
    x = []
    font = pygame.font.SysFont("Arial", 20)

    screen.init()


    while not Done:
        #帧数控制和页面刷新
        FPS = fpsControl.get()
        fpsControl.refresh()
        if not FPS == NO_LIMITED:
            clock.tick(FPS)
        if __Repaint == True:
            __Repaint = False
            continue
        o1 = time.time()
        screen.fill((255,255,255))
        
        #更新组件(per frame)
        for i in __Assemblies:
            i.Update()

        #更新计时器
        for i in timer.TIMERS:
            timer.TIMERS[i].check()

        if not usingSDL2:
            x = pygame.event.get(pump=True)
            #将events传给各EventHandler
            for event in x:
                if event.type == pygame.QUIT:
                    Done = True
                if event.type == pygame.VIDEORESIZE:
                    setWindowSize(*event.size)

                if event.type in __EventHandler.keys():
                    for i in __EventHandler[event.type]:
                        i[0](event)
            pygame.event.pump()
        else:
            event = gsdl.sdl2.SDL_Event()
            while gsdl.sdl2.SDL_PollEvent(event):
                if event.type == gsdl.sdl2.SDL_QUIT:
                    Done = True
                elif event.type == gsdl.sdl2.SDL_WINDOWEVENT and event.window.event == gsdl.sdl2.SDL_WINDOWEVENT_RESIZED:
                    setWindowSize(event.window.data1, event.window.data2)
                pe = gsdl.SDLEvent(event)
                if event.type in __EventHandler.keys():
                    for handler in __EventHandler[event.type]:
                        handler[0](pe)
        
        if RefreshRequest or not len(x) == 0 or StillRefresh:

            refreshgui = []
            refreshArea = []
            dellist = []

            #刷新动画
            nowFrameTransitionList = gtran.transitionList.copy()
            for i in nowFrameTransitionList:
                    item = nowFrameTransitionList[i]
                    if item.finish:
                        dellist.append(i)
                    else:
                        item.update()
            for d in dellist:
                    del gtran.transitionList[d]

            #重绘Assembly使用的GUI
            for i in __Assemblies:
                    lsgui = i.Draw()
                    refreshgui.append(lsgui)
            
            # 是否全局刷新
            if not usingSDL2:
                if not isAndroid:
                    if fpsControl.getRefreshAll():
                        pygame.display.update()
                    else:
                        for ls in refreshgui:
                            for gui in ls:
                                pygame.display.update(pygame.Rect(*gui.getRect()))
                
                else:
                    if fpsControl.getRefreshAll():
                        # 帧数显示
                        fps_text = font.render(f"FPS: {fpsControl.getAverageFPS()}", True, (0, 0, 0), (255,255,255))
                        screen.blit(fps_text, (5, 5))
                        pygame.display.update()
            else:
                screen.update()

            RefreshRequest = False
        
        
        n += 1
        o2 = time.time()
        #print(fpsControl.getAverageFPS())
        pjtime.append(o2-o1)

    t2 = time.time()

    
    GalLog.Print("Stop drawing.")
    GalLog.Print("在",t2-t,"秒内绘制了",n,"次,平均每帧耗时", sum(pjtime)/len(pjtime), "s")
    GalLog.Print("最低帧耗时", min(pjtime), "，最高帧耗时", max(pjtime), "; 平均帧率:", len(pjtime)/sum(pjtime))
    GalLog.saveLog()

    for i in threading.enumerate():
        if not i.name == 'MainThread':
            stop_thread(i)
    
    time.sleep(0.02)

    pygame.quit()

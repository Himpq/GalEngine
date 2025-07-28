
import ctypes, inspect, os
import pygame


class EmptyObject:
    def __init__(self): ...

class Assembly:
    def Start(self):   ...
    def Update(self):  ...
    def Draw(self):    ...
    def Destroy(self): ...

class Mouse:
    def getPos():
        return pygame.mouse.get_pos()

    def getPressed():
        return pygame.mouse.get_pressed()

    def leftClick():
        return Mouse.getPressed()[0]
    def midClick():
        return Mouse.getPressed()[1]
    def rightClick():
        return Mouse.getPressed()[2]

def in_rect(pos,rect):
    x,y =pos
    rx,ry,rw,rh = rect
    if (rx <= x <=rx+rw) and (ry <= y <= ry +rh):
        return True
    return False

def notNone(*arg):
    a = [(not i == None) for i in arg]
    return all(a)

def DictToList(x):
    p = []
    for k in x:
        v = x.get(k)
        p.append((k, v))
    return p

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

def toAbsPath(path):
    return os.path.abspath(path)


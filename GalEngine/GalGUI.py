

import threading
import os
import time
from encodings.punycode import T

import pygame
from pygame.color import THECOLORS

from . import GalError
from . import GalLog

from .GalSDL2 import Switcher
from .GalUtils import in_rect, notNone, toAbsPath, EVENTS, Mouse
from .GalRegistry import EventHandler, Status, GalGlobals
from .GalFPSControl import fpsControl



#事件优先级，并非绘制优先级，绘制优先级请于组件Update中调整顺序
GalGlobals._zIndex = {}        

def sendRefreshRequest():
    Status.isRequestedRefresh = True

def getCenterPos(widget_width: int) -> int:
    screen_width = GalGlobals.screen.get_width()
    return (screen_width - widget_width) // 2

def getRightPos(widget_width: int) -> int:
    screen_width = GalGlobals.screen.get_width()
    return screen_width - widget_width

DefaultFont = None

def getDefaultFont():
    global DefaultFont
    if not DefaultFont:
        DefaultFont = Switcher.Font(toAbsPath("./source/fonts/MSJH.TTC"), 40)
    return DefaultFont



class GalStyle:
    def __init__(self, color=None, backgroundColor=None, borderColor=None, borderWidth=None, width=None, height=None,
                 font=None, padding=None, maxWidth=None, onHoverColor=None, onPressColor=None, ):
        self.color = color
        self.backgroundColor = backgroundColor
        self.borderColor     = borderColor
        self.borderWidth     = borderWidth
        self.width           = width
        self.height          = height
        self.font            = font
        self.padding         = padding if padding else GalPadding(0, 0, 0, 0)
        self.maxWidth        = maxWidth
        self.onHoverColor    = onHoverColor
        self.onPressColor    = onPressColor

    def get(self, key, default=None):
        return getattr(self, key, default)
    
    def __repr__(self):
        return f"GalStyle(color={self.color}, backgroundColor={self.backgroundColor}, borderColor={self.borderColor}, borderWidth={self.borderWidth}, width={self.width}, height={self.height}, font={self.font}, padding={self.padding}, maxWidth={self.maxWidth}, onHoverColor={self.onHoverColor}, onPressColor={self.onPressColor})"

class GalFont:
    def __init__(self, font, size, bold=False, italic=False):
        font = toAbsPath(font)
        if os.path.isfile(font):
            self.font = Switcher.Font(font, size)
            self.font.set_bold(bold)
            self.font.set_italic(italic)
        else:
            self.font = Switcher.SysFont(font, size)
        self.render = self.font.render

class GalGUIParent:
    def __init__(self, x=1):
        GalGlobals._zIndex[self] = 1 #点击优先级，同级按照覆盖顺序
        self.padding        = GalPadding(0, 0, 0, 0)
        self.isHiding       = False
        self.isEnabledEvent = True
        self.parent         = None

        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    def setPriority(self, x=1):
        if not GalGlobals._zIndex.get(self):
            return
        GalGlobals._zIndex[self] = x

    def destroy(self):
        "Destroy Widget"
        if GalGlobals._zIndex.get(self):
            del GalGlobals._zIndex[self]
        self.put = lambda *arg: None

        galEvHdler = EventHandler.getEventHandlers()
        for ev in galEvHdler:
            for v in range(len(galEvHdler[ev])-1):
                if galEvHdler[ev][v][1] == self:
                    del galEvHdler[ev][v]

    def getRect(self):
        i = self
        i.padding = self.style.padding
        return (i.x,
                i.y,
                i.width + i.padding.left + i.padding.right,
                i.height + i.padding.top + i.padding.bottom
                )
    
    def hide(self):
        if self.isHiding:
            self.isHiding = False
            self._enableEvent(True) if self.isEnabledEvent == False else None
            GalGlobals._zIndex[self] = self.origZIndex if hasattr(self, 'origZIndex') else 1
        else:
            self.isHiding = True
            self.origZIndex = GalGlobals._zIndex.get(self, 1)
            GalGlobals._zIndex[self] = -999
            self._enableEvent(False)
        self.refresh()

    def setParent(self, parent):
        self.parent = parent
        parent.putChild(self, (self.x, self.y))
        self.setPriority(GalGlobals._zIndex[parent] + 1) if GalGlobals._zIndex.get(parent) else self.setPriority(1)

    def _BlitOnScreen(self, widget, pos):
        if self.parent and self.parent.isHiding:
            return
        
        if getattr(GalGlobals.getMainAssembly(), '_GUIS', None):
            if not getattr(self, 'preReassign', False):
                self.preReassign = True
            elif not GalGlobals.getMainAssembly()._GUIS.get(self, None) and getattr(self, 'preReassign', False):
                GalGlobals.getMainAssembly()._GUIS[self] = 1
                print("[zIndexManager] Reassign", self, "to", GalGlobals.getMainAssembly().__class__.__name__)

        if not self.isHiding:
            GalGlobals.screen.blit(widget, pos)

    def _enableEvent(self, ena=True):
        self.isEnabledEvent = ena
            
    def __getattribute__(self, name):
        if name == "__dict__":
            return super().__getattribute__(name)
        if name == "x":
            return super().__getattribute__("x") + (self.parent.x if self.parent else 0)
        if name == "y":
            return super().__getattribute__("y") + (self.parent.y if self.parent else 0)
        return super().__getattribute__(name)
    

class GalPadding:
    def __init__(self, t, b, l, r):
        self.top, self.bottom, self.left, self.right = t, b, l, r
    def __str__(self):
        c = "top="+str(self.top)+"; botton="+str(self.bottom)+"; left="+str(self.left)+"; right="+str(self.right)
        return (f"<GalGUI.GalPadding object {c}>")
    def isZero(self):
        return self.top == 0 and self.bottom == 0 and self.left == 0 and self.right == 0
    
class GalImage(GalGUIParent):
    def __init__(self, path, x=0, y=0, width=None, height=None, style=GalStyle()):
        assert os.path.isfile(path), GalError.PhotoNotFound("找不到图片 %s 。"%str(path))

        super().__init__()

        self.x = x
        self.y = y
        path = toAbsPath(path)

        self.img       = Switcher.image.load(path, True) if GalGlobals.usingSDL2 else Switcher.image.load(path)
        self.originImg = self.img

        self.pos       = Switcher.Rect(x, y, width, height) if width and height else (x, y)
        self.width     = self.img.get_width()
        self.height    = self.img.get_height()
        self.path      = path
        self.style     = style

        self.updateStyle()

    def updateStyle(self):
        if self.style.width or self.style.height:
            if self.style.width:
                self.width = self.style.width
            if self.style.height:
                self.height = self.style.height

            self.scale(self.width, self.height, True)
            print("scale", self.width, self.height)
        
        self.pos = Switcher.Rect(self.x, self.y, self.width, self.height)

    def getSurface(self):
        return self.img
        
    def put(self, x=None, y=None):
        if not notNone(x, y):
            x, y = self.x, self.y
        else:
            self.x, self.y = x, y

        self.pos = Switcher.Rect(self.padding.left + x, self.padding.top + y,
                                   self.padding.right + self.width, self.padding.bottom + self.height)
        self._BlitOnScreen(self.img, self.pos)

    def scale(self, width, height, useOriginalImage=True, useSmoothScale=False):
        if width == self.img.get_width() and height == self.img.get_height():
            return
        self.width = int(width)
        self.height = int(height)
        f =  Switcher.smoothscale if useSmoothScale else Switcher.scale
        self.img = f(self.img if not useOriginalImage else self.originImg, (int(width), int(height)))

    def flip(self, xb=False, yb=False):
        self.img = Switcher.flip(self.img, xb, yb)

    def rotate(self, angle):
        self.img = Switcher.rotate(self.img, angle)

    def __repr__(self):
        return "<GalImage from "+(self.path if getattr(self, 'path', None) else 'None')+">"
    def __str__(self):
        return self.__repr__()


class GalLabel(GalGUIParent):
    def __init__(self, font=None, text='', color=[0, 0, 0, 255], background=None, x=0,
                  y=0, max_width=None, line_spacing=5, bgwidth=None, bgheight=None, padding=None,
                  style=GalStyle()):
        super().__init__()
        if isinstance(font, GalFont):
            font = font.font
        self.font = font if font else getDefaultFont()
        self.text = text
        self.color = color
        self.bgcolor = background
        self.x = x
        self.y = y
        self.lineSpacing = line_spacing
        self.maxWidth = max_width if max_width else None
        self.bgwidth = bgwidth
        self.bgheight = bgheight
        self.padding = padding if padding else GalPadding(0, 0, 0, 0)
        self.label = self.font.render(self.text, 1, self.color)
        self.width = self.label.get_width()
        self.height = self.label.get_height()
        self.isTextCenter = False
        self.transparency = 255
        self.style = style
        self.updateStyle()

    def updateStyle(self):
        if self.style.color:
            self.color = self.style.color
        if self.style.backgroundColor:
            self.bgcolor = self.style.backgroundColor
        if self.style.font:
            self.font = self.style.font
        if not self.style.padding.isZero() and self.padding.isZero():
            self.padding = self.style.padding
        if self.style.maxWidth:
            self.maxWidth = self.style.maxWidth
        self.update()

    def getSurface(self):
        # 如果有背景色，渲染底层背景，支持padding
        if self.bgcolor:
            # label可能是Surface（自动换行），也可能是普通文本
            label_w = self.label.get_width() if hasattr(self.label, 'get_width') else self.width
            label_h = self.label.get_height() if hasattr(self.label, 'get_height') else self.height
            bg_w    = self.bgwidth if self.bgwidth else label_w + self.padding.left + self.padding.right
            bg_h    = self.bgheight if self.bgheight else label_h + self.padding.top + self.padding.bottom
            surface = Switcher.Surface((bg_w, bg_h), pygame.SRCALPHA)
            surface.fill(self.bgcolor)
            # 居中贴上label
            label_x = (bg_w - label_w) // 2 if self.isTextCenter else self.padding.left
            label_y = (bg_h - label_h) // 2 if self.isTextCenter else self.padding.top
            surface.blit(self.label, (label_x, label_y))
            return surface
        else:
            return self.label

    def put(self, x=None, y=None):
        if not notNone(x, y):
            x, y = self.x, self.y
        else:
            self.x, self.y = x, y
        surface = self.getSurface()
        self._BlitOnScreen(surface, (x, y))
        
    def setText(self, text):
        self.text = text
        self.update()

    def changeFont(self, font:GalFont):
        self.font = font
        self.update()

    def update(self):
        if len(self.text) == 0:
            self.label = Switcher.Surface((1, 1), pygame.SRCALPHA)
            self.width = 1
            self.height = 1
            return
        # 支持文本中的换行符（\n），每段都自动换行
        lines = []
        maxWidth = self.bgwidth - self.padding.left - self.padding.right if self.bgwidth else self.maxWidth
        for raw_line in str(self.text).split("\n"):
            if maxWidth:
                # 自动换行处理
                current_line = ""
                i = 0
                while i < len(raw_line):
                    char = raw_line[i]
                    # 英文单词处理
                    if ord(char) < 128:
                        word = char
                        j = i + 1
                        while j < len(raw_line) and ord(raw_line[j]) < 128 and raw_line[j] != ' ':
                            word += raw_line[j]
                            j += 1
                        i = j
                    else:
                        word = char
                        i += 1
                    testLine = current_line + word
                    testSurface = self.font.render(testLine, True, self.color) if self.font else None
                    if testSurface and testSurface.get_width() <= maxWidth:
                        current_line = testLine
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
            else:
                lines.append(raw_line)
        # 合并所有行渲染到一个 Surface
        surfaces = [self.font.render(line, True, self.color) for line in lines]
        width = max([surf.get_width() for surf in surfaces]) if surfaces else 1
        height = sum([surf.get_height() for surf in surfaces]) + self.lineSpacing * (len(surfaces)-1) if surfaces else 1
        label_surface = Switcher.Surface((width, height), pygame.SRCALPHA)
        y = 0
        for surf in surfaces:
            label_surface.blit(surf, (0, y))
            y += surf.get_height() + self.lineSpacing
        self.label = label_surface
        self.width = label_surface.get_width()
        self.height = label_surface.get_height()
    
    def __repr__(self):
        return "<GalLabel "+(self.text if getattr(self, 'text', None) else 'None')+">"
    def __str__(self):
        return self.__repr__()

class GalButton(GalGUIParent):
    def __init__(self, x=0, y=0, width=None, height=None, onclick=None,
                onhover=None, onhoveroff=None, text="", font=None, padding=None, 
                createAsm=None, onhovercolor=None):
        super().__init__()
        self.width = 100 if not width else width
        self.height = 40 if not height else height
        self.x = x
        self.y = y
        self.onclick = onclick
        self.onhover = onhover
        self.onhoveroff = onhoveroff
        self.text = text
        self.borderWidth = 3
        self.padding = GalPadding(5, 5, 0, 0) if not padding else padding
        self.font = font if font else getDefaultFont()
        self.transparency = 255
        self.borderColor = list(THECOLORS['black'])
        self.borderRadius = 0
        self.backgroundColor = [239, 240, 241, 255]
        self.onhovercolor = onhovercolor if onhovercolor else None
        self.color = [0, 0, 0, 255]
        self.enable = True
        self.surface = None
        self._destroy = False
        self.dosthOnSurface = None
        self.createAsm = createAsm

        GalLog.Print(self, ": 设置按钮文本名:["+self.text+"]")

        self.setTransparency(255)
        self._bindingFunction(onclick, onhover, onhoveroff)

    def destroy(self):
        self._enableEvent(False)
        self._destroy = True

    def _bindingFunction(self, onclick, onhover, onhoveroff):
        if not onclick == None:
            self.onclick = onclick

            @EventHandler.register(EVENTS['MouseDown'])
            def IfMouseInRect(event):
                # print("按钮点击！！！", self.text, event.pos, isTopInGUI(self, event.pos), z_index)
                if not self.onclick or not self.enable or not self.isEnabledEvent:
                    return
                if in_rect(event.pos, (self.x,
                                        self.y,
                                        self.width + self.padding.left + self.padding.right,
                                        self.height + self.padding.top + self.padding.bottom
                                        )) and isTopInGUI(self, event.pos):
                    self.onclick(self)
                    GalLog.Print(self, ": 被点击，执行函数'"+self.onclick.__name__+"'")
                    return True
                
        if not onhover == None:
            self.ishovering = False
            self.onhover = onhover
            self.onhoveroff = onhoveroff

            @EventHandler.register(EVENTS['MouseMotion'])
            def IfMouseMoveInRect(event):
                if not self.enable or not self.isEnabledEvent:
                    return

                if in_rect(event.pos, (self.x,
                                        self.y,
                                        self.width + self.padding.left + self.padding.right,
                                        self.height + self.padding.top + self.padding.bottom
                                        )) and isTopInGUI(self, event.pos):
                    if not self.ishovering:
                        self.onhover(self) if self.onhover else None
                        self.ishovering = True
                        GalLog.Print(self, ": 鼠标停留，执行函数'"+self.onhover.__name__+"'")

                else:
                    if self.onhoveroff:
                        if self.ishovering:
                            self.onhoveroff(self)
                            self.ishovering = False
                            GalLog.Print(self, ": 鼠标移走，执行函数'"+self.onhoveroff.__name__+"'")

    def setTransparency(self, int_):
        "设置透明度(0-255)"
        self.borderColor[3] = int_
        self.backgroundColor[3] = int_
        self.color[3] = int_
        self.transparency = int_

    def getSurface(self):
        return self.surface

    def setEnable(self, enable=True):
        GalLog.Print(self, ("启用" if enable else "禁用") + "了本按钮")
        self.enable = enable
        
    def put(self, x=None, y=None):
        global AllRefresh
        if self._destroy:
            return
        
        if notNone(x, y):
            self.x, self.y = x, y
        
        self.btn3 = self.font.render(self.text, 1, self.color)
        #绘制文本
        if self.text:
            if self.btn3.get_width() > self.width:
                self.width = self.btn3.get_width() + 3
            if self.btn3.get_height() > self.height:
                self.height = self.btn3.get_height()
        self.surface = Switcher.Surface((
            self.width + self.padding.left + self.padding.right,
            self.height + self.padding.top + self.padding.bottom
        ))
        #请注意，因为圆角会使得surface留白，所以如果使用圆角就不能使用白色
        #绘制边框
        self.surface.set_colorkey((255, 255, 255)) if self.borderRadius else None
        self.surface = self.surface.convert_alpha()
        self.btn = Switcher.draw.rect(self.surface,
                                    self.borderColor,
                                    [0,
                                     0,
                                     self.width + self.padding.left + self.padding.right,
                                     self.height + self.padding.top + self.padding.bottom
                                    ],
                                    0,
                                    border_radius=self.borderRadius)
        # 判断是否悬停，切换背景色
        mouseX, mouseY = Mouse.getPos()
        is_hover = in_rect((mouseX, mouseY), (self.x, self.y, self.width + self.padding.left + self.padding.right, self.height + self.padding.top + self.padding.bottom))
        bg_color = self.backgroundColor
        if self.onhovercolor and is_hover:
            bg_color = self.onhovercolor
        self.btn2 = Switcher.draw.rect(self.surface,
                                    bg_color,
                                    [0 + self.borderWidth,
                                     0 + self.borderWidth,
                                     self.width - self.borderWidth*2 + self.padding.left + self.padding.right,
                                     self.height - self.borderWidth*2 + self.padding.top + self.padding.bottom
                                     ],
                                     0,)
        #贴上文字
        self.textsurface = Switcher.Surface((
            self.btn3.get_width(),
            self.btn3.get_height()
        ))
        self.textsurface.fill((0,0,0,0)) 
        self.textsurface.set_colorkey((0, 0, 0))
        self.textsurface = self.textsurface.convert_alpha()
        self.textsurface.blit(self.btn3, (0, 0))
        self.textsurface.set_alpha(self.color[3] if self.enable else 100)
        self.surface.blit(self.textsurface, (
            self.borderWidth + self.padding.left,
            self.borderWidth + self.padding.top
            )
        )

        self.dosthOnSurface(self.surface) if self.dosthOnSurface else None
        self._BlitOnScreen(self.surface, (self.x, self.y))

    def __repr__(self):
        return "<GalButton "+(self.text if getattr(self, 'text', None) else 'None')+">"
    def __str__(self):
        return self.__repr__()

class GalVideo(GalGUIParent):
    def __init__(self, path: str, width:int = 800, height:int = 600, x:int = 0, y:int = 0):
        # from moviepy.editor import VideoFileClip
        from moviepy import VideoFileClip
        import numpy
        super().__init__()

        self.videoPath = toAbsPath(path)
        self.width = width
        self.height = height
        self.isHiding = False
        self.coverSurface = None #未开始播放视频时默认展示的图片
        self.isPlaying = False
        self.surface = None
        self.upframes = 0
        self.quit = False
        self.x = x
        self.y = y
        
        self.audioPlayPerVideoFrame = 0
        self.volume = 1.0
        

        if not os.path.isfile(path):
            raise GalError.PhotoNotFound("无法找到文件 '"+path+"'。")

        self.video = VideoFileClip(self.videoPath)
        self.audio = self.video.audio

        self.audioChannel = pygame.mixer.find_channel()

        GalLog.Print(self, ": 初始化视频：", path)
        GalLog.Print(self, f": 视频帧率：{self.video.fps}")

        self.videoSize       = self.video.size
        self.videoTotalFrame = self.video.reader.nframes
        self.videoFrameRate  = self.video.fps
        self.audioFrameRate  = self.audio.fps
        self.nowIndex        = 0
        self.tempSetIndex    = None
        self.frames          = numpy.arange(1.0 / self.videoFrameRate, self.video.duration-.001, 1.0 / self.videoFrameRate)
        self.playThr         = None

    def setVolume(self, volume):
        self.volume = volume/100
    def getVolume(self):
        return int(self.volume * 100)
    def _getVolume(self):
        return self.volume
    def getDuration(self) -> float:
        "Return the length of the whole video"
        return self.video.duration
    def getTime(self) -> float:
        "Return a time"
        return self.nowIndex / self.videoFrameRate
    def getPos(self):
        "Return the index of the frame id playing now"
        return self.nowIndex
    def setPos(self, frame: int):
        "Set the pos of the video by frame id"
        self.nowIndex = frame
        self.tempSetIndex = frame
    def setPosByTime(self, time: int):
        "Set the pos of the video by time"
        self.nowIndex = int(self.videoFrameRate * time)
    def getWholeFrame(self):
        return self.videoTotalFrame

    def play(self, buffersize = 4000, nbytes = 2):
        "Play the video, or pause it."

        self._nbytes = nbytes
        self._buffersize = buffersize

        if not self.isPlaying:
            self.starttime = time.time()
            self.isPlaying = True

            if not pygame.mixer.get_init() == (self.audioFrameRate, -8 * self._nbytes, self.audio.nchannels):
                pygame.mixer.quit()
                pygame.mixer.init(self.audioFrameRate, -8 * self._nbytes, self.audio.nchannels, 1024)

            self.audioPlayPerVideoFrame = int((1/self.videoFrameRate) / (1/self.audioFrameRate))

            print("aFpVf={0}, audioFPS={1}, startPos={2}/{3}".format(self.audioPlayPerVideoFrame, self.audioFrameRate, self.nowIndex, self.audio.reader.nframes))
            self.playThr = threading.Thread(target=self._playThread)
            self.playThr.start()

        else:
            self.isPlaying = False
            self.playThr.join()
            self.endtime = time.time()
            self._quit()
            
    def put(self, x=None, y=None):
        self.x, self.y = self.x if not x else x, self.y if not y else y
        self.durate(self.x, self.y)

    def _quit(self):
        GalLog.Print(self, ": 关闭视频")
        self.isPlaying = False
        self.durate(self.x, self.y)
        fpsControl.back()
    
    def durate(self, x=None, y=None):
        if not self.isPlaying:
            if self.surface:
                self._BlitOnScreen(self.surface, (x, y))
                return
            if self.coverSurface == None:
                self.coverPic = self.video.get_frame(0)
                self.coverSurface = pygame.surfarray.make_surface(self.coverPic.swapaxes(0, 1))
                self.coverSurface = pygame.transform.scale(self.coverSurface, (self.width, self.height))

            self._BlitOnScreen(self.coverSurface, (x, y))
            return
        
        if self.nowIndex >= self.videoTotalFrame:
            self.setPos(0)
            self.play()
            return
        
        frame      = self.video.get_frame(self.frames[self.nowIndex])
        surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        surface = pygame.transform.scale(surface, (self.width, self.height))
        self._BlitOnScreen(surface, (x, y))
        self.surface = surface

    def _playThread(self, _from=None, to=None):
        _from = _from if _from else self.nowIndex
        to    = to    if to    else self.videoTotalFrame

        while self.isPlaying:
            self._playAudioPerFrame()
            self.nowIndex += 1
            if self.nowIndex == to:
                return

    def _playAudioPerFrame(self, frameID=None):
        if not globals().get("numpy"):
            import numpy

        if frameID == None:
            frameID = self.nowIndex

        nowVideoFrame = self.audioPlayPerVideoFrame * frameID
        endVideoFrame  = nowVideoFrame + self.audioPlayPerVideoFrame

        pos    = numpy.array(range(nowVideoFrame, endVideoFrame))
        frames = self.audio.to_soundarray(1/self.audioFrameRate*pos, nbytes=self._nbytes, quantize=True)
        chunk  = pygame.sndarray.make_sound(frames)

        self.audioChannel.set_volume(self._getVolume()) if not self.audioChannel.get_volume() == self._getVolume() else 0

        n = 0
        while self.audioChannel.get_queue():
            time.sleep(0.003)
            n+=1
            if n >= 30 and self.audioChannel.get_busy():
                self.audioChannel.stop()
                print(f"restart channel. timeout={n*0.003*1000}ms")
                self.audioChannel = pygame.mixer.find_channel(True)
                self.audioChannel.set_volume(self._getVolume())
                self.audioChannel.play(chunk)
                return
            
        self.audioChannel.queue(chunk)


class GalSlider(GalGUIParent):
    _draggingInstance = None  # 只允许一个Slider处于拖动状态
    def __init__(self, width = 250, height = 50, _min = 0, _max = 100, default = 0, x = 0, y = 0, onValueChanged = None,
                 trackColor  = [105, 105, 105, 255], thumbColor = [192, 192, 192, 255],
                 thumbColorHovering = [55, 49, 47, 255], thumbColorDragging = [27, 27, 27, 255],
                 thumbSize = None, trackWidth = None, error=None):
        assert default >= _min and default <= _max, "Your default value is out of setting range: ["+str(_min)+", "+str(_max)+"]"
        super().__init__()
        self.x = x
        self.y = y
        self.isDragging = False
        self.width = width
        self.height = height
        self.range = [_min, _max]
        self.value = default
        self.onValueChanged = onValueChanged # Callback Function
        self.trackColor = trackColor
        self.thumbColor = thumbColor
        self.thumbColorHovering = thumbColorHovering
        self.thumbColorDragging = thumbColorDragging
        self.thumbSize = [10, height] if not thumbSize else thumbSize
        self.trackWidth = 3 if not trackWidth else trackWidth
        self.error = 3 if not error else error  # 点击误差
        # 修正：步数应为(_max - _min)，否则滑块无法到达最右边
        steps = self.range[1] - self.range[0]
        self.widthPerStep = self.width / steps if steps != 0 else 0

        self.surface = Switcher.Surface((self.width + self.thumbSize[0], self.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))  # 完全透明
        
        # 创建轨道surface - 这部分是静态的，不需要每帧重绘
        self.track_surface = Switcher.Surface((self.width + self.thumbSize[0], self.height), pygame.SRCALPHA)
        self.track_surface.fill((0, 0, 0, 0))  # 完全透明
        
        # 绘制轨道
        Switcher.draw.line(
            self.track_surface, 
            self.trackColor, 
            (0, int(self.height/2)), 
            (self.width + self.thumbSize[0], int(self.height/2)), 
            self.trackWidth
        )
        

    def setValue(self, value):
        """设置滑块值并触发onchange事件"""
        old_value = self.value
        self.value = min(max(value, self.range[0]), self.range[1])
        
        # 仅在值改变时触发事件
        if self.value != old_value and self.onValueChanged:
            self.onValueChanged(self.value)
        
        return self.value
    
    def put(self, x=None, y=None):
        """绘制滑块组件"""
        if notNone(x, y):
            self.x, self.y = x, y
        
        # 计算滑块位置
        thumbPos = int(self.widthPerStep * (self.value - self.range[0]))
        thumbRect = Switcher.Rect(thumbPos, 0, *self.thumbSize)
        
        # 碰撞检测区域
        realRect = [thumbPos + self.x, self.y, self.thumbSize[0], self.thumbSize[1]]
        mouseX, mouseY = Mouse.getPos()
        thumbEvent = False
        
        # 清理surface并重新绘制
        self.surface.fill((0, 0, 0, 0))  # 清空为透明
        
        # 绘制轨道（静态部分）
        self.surface.blit(self.track_surface, (0, 0))
        
        # 处理滑块状态和绘制
        # 拖动状态只允许一个实例
        mousePressed = Mouse.getPressed()[0]
        if self.isDragging:
            if GalSlider._draggingInstance is self and mousePressed:
                Switcher.draw.rect(self.surface, self.thumbColorDragging, thumbRect)
                self._handle_thumb_dragging(self.x)
                thumbEvent = True
            else:
                self.isDragging = False
                if in_rect((mouseX, mouseY), realRect):
                    Switcher.draw.rect(self.surface, self.thumbColorHovering, thumbRect)
                else:
                    Switcher.draw.rect(self.surface, self.thumbColor, thumbRect)
        elif in_rect((mouseX, mouseY), realRect):
            # 只有没有任何Slider处于拖动状态时才允许hover变色
            if mousePressed and GalSlider._draggingInstance is None:
                self.isDragging = True
                GalSlider._draggingInstance = self
                Switcher.draw.rect(self.surface, self.thumbColorDragging, thumbRect)
                thumbEvent = True
            elif GalSlider._draggingInstance is None:
                Switcher.draw.rect(self.surface, self.thumbColorHovering, thumbRect)
            else:
                Switcher.draw.rect(self.surface, self.thumbColor, thumbRect)
        else:
            Switcher.draw.rect(self.surface, self.thumbColor, thumbRect)
        # 鼠标松开时清除拖动实例
        if not mousePressed and GalSlider._draggingInstance is self:
            self.isDragging = False
            GalSlider._draggingInstance = None
        
        # 只有没有任何Slider处于拖动状态时才允许track点击
        if GalSlider._draggingInstance is None and not self.isDragging and not thumbEvent:
            if mouseX >= self.x and mouseX <= self.x + self.width:
                lineMidY = int(self.y + self.height/2)
                lineTopY = int(lineMidY - (self.trackWidth-1)/2) - self.error
                lineBtnY = int(lineMidY + (self.trackWidth-1)/2) + self.error
                if mouseY >= lineTopY and mouseY <= lineBtnY and Mouse.getPressed()[0]:
                    self._handle_track_clicked(self.x, mouseX)

        # 绘制到屏幕
        self._BlitOnScreen(self.surface, (self.x, self.y))


    def _handle_thumb_dragging(self, abs_x):
        """处理滑块拖动逻辑"""
        mouseX = Mouse.getPos()[0]
        if mouseX >= abs_x + self.width:
            self.setValue(self.range[1])
        elif mouseX <= abs_x:
            self.setValue(self.range[0])
        else:
            # 计算相对位置并转换为值
            relative_pos = mouseX - abs_x
            val = int(self.range[0] + relative_pos / self.widthPerStep)
            self.setValue(val)

    def _handle_track_clicked(self, abs_x, mouseX):
        """处理轨道点击逻辑"""
        relative_pos = mouseX - abs_x
        val = int(self.range[0] + relative_pos / self.widthPerStep)
        self.setValue(val)
    
    def onThumbDragging(self):
        """保留向后兼容的方法"""
        abs_x, _ = self._getAbsolutePos()
        self._handle_thumb_dragging(abs_x)
    
    def onTrackClicked(self):
        """保留向后兼容的方法"""
        abs_x, _ = self._getAbsolutePos()
        self._handle_track_clicked(abs_x, Mouse.getPos()[0])
    
    def resize(self, width, height):
        """重设大小并重新创建surface"""
        self.width = width
        self.height = height
        self.widthPerStep = self.width / (self.range[1] - self.range[0]) if self.range[1] != self.range[0] else 0
        self._create_surfaces()
    
    def setRange(self, min_val, max_val):
        """设置滑块范围"""
        if min_val >= max_val:
            return False
        
        self.range = (min_val, max_val)
        self.widthPerStep = self.width / (max_val - min_val)
        self.value = min(max(self.value, min_val), max_val)
        return True

class GalGradientMask(GalGUIParent):
    def __init__(self, startYRatio=0.6, color=(0, 0, 0), maxAlpha=180, x=0, y=0):
        super().__init__()

        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        
        self.startYRatio = startYRatio
        self.color = color
        self.maxAlpha = maxAlpha

    def put(self, screen):
        self.width = screen.get_width()
        self.height = screen.get_height()
        gradYStart = int(self.height * self.startYRatio)
        gradYEnd = self.height
        gradHeight = gradYEnd - gradYStart
        gradSurface = Switcher.Surface((self.width, gradHeight), pygame.SRCALPHA)
        for i in range(gradHeight):
            alpha = int(self.maxAlpha * (i / gradHeight))
            Switcher.draw.rect(
                gradSurface,
                (*self.color, alpha),
                Switcher.Rect(0, i, self.width, 1)
            )
        
        screen.blit(gradSurface, (0, gradYStart))


def galSceneTransition(screen, alpha):
    """全屏黑色渐变，alpha: 0~255"""
    alpha = int(alpha)
    width, height = screen.get_width(), screen.get_height()
    s = Switcher.Surface((width, height))
    s.fill((0, 0, 0, alpha))
    s.set_alpha(alpha)
    screen.blit(s, (0, 0))

def isTopInGUI(x, clickPos):
    p = []
    for i in GalGlobals._zIndex:
        v = GalGlobals._zIndex.get(i)
        isInRect = in_rect(clickPos, (
            i.x,
            i.y,
            i.width + i.padding.left + i.padding.right,
            i.height + i.padding.top + i.padding.bottom
        ))
        if isInRect:
            p.append((i, v))
    if len(p) == 0:
        return False
    p.sort(key=(lambda item: item[1]), reverse=False)
    if p[-1][0] == x:
         return True
    return False
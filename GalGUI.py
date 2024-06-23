# 请勿单独导入本模块（除非不使用控件的 put 方法）

import threading
import pygame
import os
import GalError
import time
import numpy
from GalAPI import in_rect, notNone
from pygame.color import THECOLORS
from moviepy.editor import VideoFileClip

np = numpy

import GalEngine as galengine


DefaultFont = pygame.font.Font(r"C:\WINDOWS\Fonts\STFANGSO.TTF", 40)
z_index     = {}        #事件优先级，并非绘制优先级，绘制优先级请于组件Update中调整顺序

def isTopInGUI(x, clickPos):
    p = []
    for i in z_index:
        v = z_index.get(i)
        inRe = in_rect(clickPos, (
                                i.x,
                                i.y,
                                i.width + i.padding.left + i.padding.right,
                                i.height + i.padding.top + i.padding.bottom
                                ))
        if inRe:
            p.append((i, v))
    if p[-1][0] == x:
         return True
    return False

def sendRefreshRequest():
    galengine.RefreshRequest = True

class GalFont:
    def __init__(self, font, size, bold=False, italic=False):
        if os.path.isfile(font):
            self.font = pygame.font.Font(font, size)
            self.font.set_bold(bold)
            self.font.set_italic(italic)
        else:
            self.font = pygame.font.SysFont(font, size, bold, italic)
        self.render = self.font.render

class GalGUIParent:
    def __init__(self, x=1):
        z_index[self] = 1 #点击优先级，同级按照覆盖顺序
        
        self.padding        = GalPadding(0, 0, 0, 0)
        self.isHiding       = False
        self.isEnabledEvent = True

        galengine.GalLog.Print(self, "-> 创建[",self.__class__.__name__,"]")

    def setX(self, x):
        self.x = x
    def setY(self, y):
        self.y = y     
    def setPriority(self, x=1):
        z_index[self] = x
    def destroy(self):
        "Destroy Widget"
        if z_index.get(self):
            del z_index[self]
        self.put = lambda *arg: None
        for ev in galengine.__EventHandler:
            for v in range(len(galengine.__EventHandler[ev])-1):
                if galengine.__EventHandler[ev][v][1] == self:
                    del galengine.__EventHandler[ev][v]
    def refresh(self):
        sendRefreshRequest()
    def getRect(self):
        i = self
        return (i.x,
                                   i.y,
                                   i.width + i.padding.left + i.padding.right,
                                   i.height + i.padding.top + i.padding.bottom
                                   )
    def hide(self):
        if self.isHiding:
            self.isHiding = False
            self._enableEvent(True) if self.isEnabledEvent == False else None
        else:
            self.isHiding = True
            self._enableEvent(False)
        self.refresh()
    def _BlitOnScreen(self, widget, pos):
        if not self.isHiding:
            galengine.screen.blit(widget, pos)
    def _enableEvent(self, ena=True):
        self.isEnabledEvent = ena
            

class GalPadding:
    def __init__(self, t, b, l, r):
        self.top, self.bottom, self.left, self.right = t, b, l, r
    def __str__(self):
        c = "top="+str(self.top)+"; botton="+str(self.bottom)+"; left="+str(self.left)+"; right="+str(self.right)
        return (f"<GalGUI.GalPadding object {c}>")
    
class GalImage(GalGUIParent):
    def __init__(self, path, x=0, y=0, width=None, height=None):
        if not os.path.isfile(path):
            raise GalError.PhotoNotFound("找不到图片 %s 。"%str(path))
        super().__init__()
        self.img = pygame.image.load(path)
        self.originImg = self.img
        self.pos = pygame.Rect(x, y, width, height) if width and height else (x, y)
        self.width = width if width else self.img.get_width()
        self.height = height if height else self.img.get_height()
        self.x = x
        self.y = y

    def getSurface(self):
        return self.img
        
    def put(self, x=None, y=None):
        if not notNone(x, y):
            x, y = self.x, self.y
        else:
            self.x, self.y = x, y

        self.pos = pygame.Rect(self.padding.left + x, self.padding.top + y,
                                   self.padding.right + self.width, self.padding.bottom + self.height)
        self._BlitOnScreen(self.img, self.pos)
    def scale(self, width, height, useOriginalImage=True, useSmoothScale=True):
        if width == self.img.get_width() and height == self.img.get_height():
            return
        f =  pygame.transform.smoothscale if useSmoothScale else pygame.transform.scale
        self.img = f(self.img if not useOriginalImage else self.originImg, (width, height))

    def flip(self, xb=False, yb=False):
        self.img = pygame.transform.flip(self.img, xb, yb)

    def rotate(self, angle):
        self.img = pygame.transform.rotate(self.img, angle)


class GalLabel(GalGUIParent):
    def __init__(self, font=None, text='', color=[0, 0, 0, 255], background=None, x=0, y=0):
        super().__init__()
        self.font = font if font else DefaultFont
        self.text = text
        self.color = color
        self.bgcolor = background
        self.label = self.font.render(self.text, 1, self.color, self.bgcolor)
        self.x = x
        self.y = y
        self.width = self.label.get_width()
        self.height = self.label.get_height()
        
        self.transparency = 255

    def getSurface(self):
        return self.label

    def put(self, x=None, y=None):
        if not notNone(x, y):
            x, y = self.x, self.y
        else:
            self.x, self.y = x, y
        self._BlitOnScreen(self.label, (x, y))
    def setText(self, text):
        self.text = text
        self.label = self.font.render(self.text, 1, self.color, self.bgcolor)
    def changeFont(self, font:GalFont):
        self.font = font
        self.label = self.font.render(self.text, 1, self.color, self.bgcolor)
        self.width, self.height = self.label.get_width(), self.label.get_height()


class GalButton(GalGUIParent):
    def __init__(self, x=0, y=0, width=None, height=None, onclick=None, onhover=None, onhoveroff=None, text="", font=None, padding=None):
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
        self.font = font if font else DefaultFont
        self.transparency = 255
        self.borderColor = list(THECOLORS['black'])
        self.borderRadius = 0
        self.backgroundColor = [239, 240, 241, 255]
        self.color = [0, 0, 0, 255]
        self.enable = True
        self.surface = None
        

        galengine.GalLog.Print(self, ": 设置按钮文本名:["+self.text+"]")

        self.setTransparency(255)

        if not onclick == None:
            @galengine.EventHandler(galengine.EVENTS['MouseDown'], self)
            def IfMouseInRect(event):
                if not self.onclick or not self.enable or not self.isEnabledEvent:
                    return
                if in_rect(event.pos, (self.x,
                                       self.y,
                                       self.width + self.padding.left + self.padding.right,
                                       self.height + self.padding.top + self.padding.bottom
                                       )) and isTopInGUI(self, event.pos):
                    self.onclick(self)
                    galengine.GalLog.Print(self, ": 被点击，执行函数'"+self.onclick.__name__+"'")
        if not onhover == None:
            self.ishovering = False
            @galengine.EventHandler(galengine.EVENTS['MouseMotion'], self)
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
                        galengine.GalLog.Print(self, ": 鼠标停留，执行函数'"+self.onhover.__name__+"'")

                else:
                    if self.onhoveroff:
                        if self.ishovering:
                            self.onhoveroff(self)
                            self.ishovering = False
                            galengine.GalLog.Print(self, ": 鼠标移走，执行函数'"+self.onhoveroff.__name__+"'")

    def setTransparency(self, int_):
        "设置透明度(0-255)"
        self.borderColor[3] = int_
        self.backgroundColor[3] = int_
        self.color[3] = int_
        self.transparency = int_
        self.refresh()

    def getSurface(self):
        return self.surface

    def setEnable(self, enable=True):
        galengine.GalLog.Print(self, ("启用" if enable else "禁用") + "了本按钮")
        self.enable = enable
        self.refresh()
        
    def put(self, x=None, y=None):
        global AllRefresh
        
        if notNone(x, y):
            self.x, self.y = x, y


        self.btn3 = self.font.render(self.text, 1, self.color)

        #绘制文本
        if self.text:
            if self.btn3.get_width() > self.width:
                self.width = self.btn3.get_width() + 3
            if self.btn3.get_height() > self.height:
                self.height = self.btn3.get_height()
        self.surface = pygame.Surface((
            self.width + self.padding.left + self.padding.right,
            self.height + self.padding.top + self.padding.bottom
        ))
        #请注意，因为圆角会使得surface留白，所以如果使用圆角就不能使用白色
        #绘制边框
        self.surface.set_colorkey((255, 255, 255)) if self.borderRadius else None
        self.surface = self.surface.convert_alpha()
        self.btn = pygame.draw.rect(self.surface,
                                    self.borderColor,
                                    [0,
                                     0,
                                     self.width + self.padding.left + self.padding.right,
                                     self.height + self.padding.top + self.padding.bottom
                                    ],
                                    0,
                                    border_radius=self.borderRadius)
        self.btn2 = pygame.draw.rect(self.surface,
                                    self.backgroundColor,
                                    [0 + self.borderWidth,
                                     0 + self.borderWidth,
                                     self.width - self.borderWidth*2 + self.padding.left + self.padding.right,
                                     self.height - self.borderWidth*2 + self.padding.top + self.padding.bottom
                                     ],
                                     0,)
        #贴上文字
        self.textsurface = pygame.Surface((
            self.btn3.get_width(),
            self.btn3.get_height()
        ))
        self.textsurface.set_colorkey((0, 0, 0))
        self.textsurface = self.textsurface.convert_alpha()
        self.textsurface.blit(self.btn3, (0, 0))
        self.textsurface.set_alpha(self.color[3] if self.enable else 100)
        self.surface.blit(self.textsurface, (
            self.borderWidth + self.padding.left,
            self.borderWidth + self.padding.top
            )
        )

            
        self._BlitOnScreen(self.surface, (self.x, self.y))

class GalVideo(GalGUIParent):
    def __init__(self, path: str, width:int = 800, height:int = 600, x:int = 0, y:int = 0):

        self.videoPath = path
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
        super().__init__()

        if not os.path.isfile(path):
            raise GalError.PhotoNotFound("无法找到文件 '"+path+"'。")

        self.video = VideoFileClip(path)
        self.audio = self.video.audio

        self.audioChannel = pygame.mixer.find_channel()

        galengine.GalLog.Print(self, ": 初始化视频：", path)
        galengine.GalLog.Print(self, f": 视频帧率：{self.video.fps}")

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
        galengine.GalLog.Print(self, ": 关闭视频")
        self.isPlaying = False
        self.durate(self.x, self.y)
        galengine.fpsControl.back()
    
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
        
        #Thread not sync!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! var: self.nowIndex
        
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
    def __init__(self, width = 250, height = 50, _min = 0, _max = 100, default = 0, x = 0, y = 0, onValueChanged = None,
                 trackColor  = [105, 105, 105, 255], thumbColor = [192, 192, 192, 255],
                 thumbColorHovering = [55, 49, 47, 255], thumbColorDragging = [27, 27, 27, 255]):
        assert default >= _min and default <= _max, "Your default value is out of setting range: ["+str(_min)+", "+str(_max)+"]"
        self.x = x
        self.y = y
        self.isDragging = False
        self.width = width
        self.height = height
        self.range = [_min, _max]
        self.value = default
        self.onValueChanged = onValueChanged
        self.trackColor = trackColor
        self.thumbColor = thumbColor
        self.thumbColorHovering = thumbColorHovering
        self.thumbColorDragging = thumbColorDragging
        self.thumbSize = [10, height]
        self.trackWidth = 3
        self.error = 3  # 点击误差
        if self.width < self.range[1]: #超出范围
            self.widthPerStep = (self.width / self.range[1])
        else:                          #小于范围
            self.widthPerStep =(self.width / self.range[1])

        self.surface = pygame.Surface((self.width + self.thumbSize[0], self.height))
        self.surface.fill([255, 255, 255])
        self.surface.set_colorkey((255, 255, 255))
        self.surface = self.surface.convert_alpha()

        pygame.draw.line(self.surface, self.trackColor, (0, int(self.height/2)), (self.width+self.thumbSize[0], int(self.height/2)), self.trackWidth)
        self.lineRect = 1
        super().__init__()

    def setValue(self, value):
        self.value = value
        self.onValueChanged(self) if not self.onValueChanged == None else 0
    
    def put(self, x=0, y=0):
        self.x, self.y = self.x if not x else x, self.y if not y else y
        surface        = self.surface.copy()
        thumbPos       = int(self.widthPerStep * self.value)
        thumbRect      = pygame.Rect(thumbPos, 0, *self.thumbSize)
        realRect       = [thumbPos + self.x, self.y, self.thumbSize[0], self.thumbSize[1]]
        mouseX, mouseY = galengine.mouse.getPos()
        thumbEvent     = False

        if self.isDragging and galengine.mouse.getPressed()[0]:    # Thumb is draggin'
            pygame.draw.rect(surface, self.thumbColorDragging, thumbRect)
            self.onThumbDragging()
            thumbEvent = True
        elif in_rect(galengine.mouse.getPos(), realRect):          # Thumb is hovering or already draggin'
            if galengine.mouse.getPressed()[0]:
                self.isDragging = True
                pygame.draw.rect(surface, self.thumbColorDragging, thumbRect)
                thumbEvent = True
            else:
                self.isDragging = False
                pygame.draw.rect(surface, self.thumbColorHovering, thumbRect)
        else:                                                      # Free status
            pygame.draw.rect(surface, self.thumbColor, thumbRect)

        if not self.isDragging and not thumbEvent:
            if mouseX >= self.x and mouseX <= self.x + self.width + self.thumbSize[0]:
                lineMidY = int(self.y + self.height/2)
                lineTopY = int(lineMidY - (self.trackWidth-1)/2) - self.error
                lineBtnY = int(lineMidY + (self.trackWidth-1)/2) + self.error
                if mouseY >= lineTopY and mouseY <= lineBtnY and galengine.mouse.getPressed()[0]:
                    self.onTrackClicked()

        self._BlitOnScreen(surface, (self.x, self.y))

    def onThumbDragging(self):
        mouseX = galengine.mouse.getPos()[0]
        if mouseX >= self.x + self.width:
            self.setValue(self.range[1])
        elif mouseX <= self.x:
            self.setValue(self.range[0])
        else:
            val = int((mouseX - self.x) / self.widthPerStep)
            self.setValue(val)

    def onTrackClicked(self):
        mouseX = galengine.mouse.getPos()[0]
        val = int((mouseX - self.x) / self.widthPerStep)
        self.setValue(val)
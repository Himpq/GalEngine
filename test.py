import GalEngine as ge
import time

class A(ge.Assembly):
    def Start(self):
        self.a = ge.gui.GalImage("./source/img/bg2.jpg")
        #self.b = ge.gui.GalImage("./source/img/bg2.jpg")
        self.putbg = 'a'

        def focus(intt, sound=False, FIR=False):
            if intt == self.focus:
                if FIR:
                    self.sound2.play()
                    self.focuses[intt].borderColor = list(ge.gui.THECOLORS['red'])
                return
            else:
                self.sound2.play() if sound else None
            self.focuses[self.focus].borderColor = list(ge.gui.THECOLORS['black'])
            self.focus = intt
            self.focuses[intt].borderColor = list(ge.gui.THECOLORS['red'])
            print("SET",intt,"!")
            
        self.focusFunc = focus
        self.focus = 1
        self.focuses={}
        self.focuses[1]=ge.gui.GalButton(onclick=lambda x:focus(1,1), text='Focus_1')
        self.focuses[2]=ge.gui.GalButton(onclick=lambda x:focus(2,1), text='Focus_2')
        self.focuses[3]=ge.gui.GalButton(onclick=lambda x:focus(3,1), text='Focus_3')

        self.focusGTA = ge.gui.GalLabel(font=ge.pygame.font.Font("C:/Windows/Fonts/MSJHL.TTC", 40),
                                        text="音效:")

        self.sound = ge.media.playSound("./source/sounds/GTA5Sound/Click_04.wav")
        self.sound2 = ge.media.playSound("./source/sounds/GTA5Sound/Click_03.wav")
        self.sound3 = ge.media.playSound("./source/sounds/GTA5Sound/GTA5_Email.wav")
        self.sound2.setVolume(20)

        self.focusFunc(1, 0, 1)
        
        def aaa(button):
            self.putbg='b' if self.putbg == 'a' else 'a'
        def bbb(button):
            self.sound.play()
            button.setTransparency(128)
        def ccc(btn):
            btn.setTransparency(255)

        def 淡入淡出(se):#0渐入，1渐弱，2显示，3隐藏
            if se.status == 2:
                se.status = 1
            elif se.status == 3:
                se.status = 0
            elif se.status == 0:
                se.status = 1
            else:
                se.status = 0

        def doreButton(*arg):
            print("SET BTN1 TO:", not self.btn.enable)
            self.btn.setEnable(True if not self.btn.enable else False)

        f=ge.media.playMusic(r".\source\sounds\Dawn's Greeting.mp3")
        f.setVolume(50)

        self.music = f

        self.btn = ge.gui.GalButton(onclick=aaa,
                                    onhover=bbb,
                                    onhoveroff=ccc,
                                    text='更换背景222')
        self.btn.padding = ge.gui.GalPadding(10, 10, 10, 10)
        self.btn2 = ge.gui.GalButton(onclick=淡入淡出,
                                     text='淡入淡出')
        self.btn2.status = 2
        self.btn3 = ge.gui.GalButton(onclick=lambda x:f.play(),
                                     text='播放',
                                     onhover=bbb,
                                     onhoveroff=ccc)
        self.btn3.padding = ge.gui.GalPadding(10, 10, 10, 0)

        self.btn4 = ge.gui.GalButton(onclick=lambda x:[print(1),
                                                       self.btn.hide()],
                                     onhover=bbb,
                                     onhoveroff=ccc,
                                     text='测试优先级')
        self.btn4.borderRadius = 1000
        def changeFPS(*arg):
            ge.fpsControl.set(120 if ge.fpsControl.get() == 60 else 60)
        self.v = ge.gui.GalVideo(r"C:\Users\Himpq\Videos\ASMR ReZero Rem.mp4", 640, 360, 500, 300)
        # self.v = ge.gui.GalVideo(r"C:\Users\Himpq\Music\MV\ODESZA - Late Night.mp4", 640, 360, 500, 300)
        self.v.setVolume(100)
        self.timeShow = ge.gui.GalLabel(None, str(int(self.v.getTime()))+"s / "+ str(int(self.v.getDuration()))+"s", background=[255, 255, 255, 255])
        
        # print("Video Rect:", self.v.getRect())
        self.btn5 = ge.gui.GalButton(onclick=doreButton,
                                     text='测试按钮关闭与启用',
                                     onhover=bbb,
                                     onhoveroff=ccc)
        
        self.btn6 = ge.gui.GalButton(onclick=lambda x:self.v.play(),
                                     text="播放",
                                     onhover=bbb,
                                     onhoveroff=ccc)
        self.btn7 = ge.gui.GalButton(onclick=changeFPS,
                                     text='60/120 fps',
                                     onhover=bbb,
                                     onhoveroff=ccc,
                                     padding=ge.gui.GalPadding(20, 20, 20, 20))
        self.uptime = 0
        
        self.fps = ge.gui.GalLabel(text='fps: %s')
        self.listgui = [self.focuses[1], self.focuses[2], self.focuses[3], self.a, self.fps, self.btn, self.btn2, self.btn3, self.btn4, self.btn5, self.btn6, self.btn7, self.v, self.focusGTA]
        self.bigtosmall = ge.gui.GalLabel(text='缩放动画测试', font=ge.gui.GalFont("Microsoft JhengHei", 100), color=[255, 255, 255, 100], x=600, y=200)
        def changee(s):
            self.bigtosmall.changeFont(ge.gui.GalFont("Microsoft JhengHei", s))

        self.timeShowEvent = ge.timer.GalTimer(lambda: self.timeShow.setText(str(int(self.v.getTime()))+"s / "+ str(int(self.v.getDuration()))+"s"), delay = 0.5, checkWithRealFPS=True)
        self.timeShowEvent.start()

        self.timeBar = ge.gui.GalSlider(x=600, y=120, default=self.v.getPos(), _min = 0, _max = self.v.getWholeFrame())
        self.timeBar.onValueChanged = lambda timeBar: self.v.setPos(timeBar.value)

        self.volumeBar = ge.gui.GalSlider(x=880, y=120, default=self.v.getVolume(), _min = 0, _max = 100)
        self.volumeBar.onValueChanged = lambda volumeBar: self.v.setVolume(volumeBar.value)

        self.gtr = ge.gtran.SmoothZoom(self.bigtosmall, changee, 100, 40, 5)
        self.gtr.init()
        self.gtr.start()

        self.tempData = 0

    def Update(self):
        if self.btn2.status == 1:
            if self.btn2.transparency-15 <= 0:
                self.btn2.status = 3
            self.btn2.setTransparency(self.btn2.transparency-15)
            
        if self.btn2.status == 0:
            if self.btn2.transparency+15 >= 255:
                self.btn2.status = 2
            self.btn2.setTransparency(self.btn2.transparency+15)

        self.timeBar.setValue(self.v.getPos()) if not self.timeBar.isDragging else 0
        self.volumeBar.setValue(self.v.getVolume()) if not self.volumeBar.isDragging else 0

        if self.timeBar.isDragging:
            if self.v.isPlaying:
                self.v.play()
                self.tempData = 1

        else:
            if self.tempData == 1:
                self.tempData = 0
                self.v.play()
            
    def Draw(self):
        self.a.put()
        self.bigtosmall.put()
        nowtime = time.time()

        #计算fps
        f = nowtime - self.uptime
        self.uptime = nowtime
        self.fps.setText( "fps: %s | (%s, %s)"%(int(1/(1 if f == 0 else f)), str(ge.mouse.getPos()[0]), str(ge.mouse.getPos()[1])) )

        #放置focuses按钮
        for i in self.focuses:
            self.focuses[i].put(450, 70*i)

        #放置其他组件
        self.bigtosmall.put()
        self.fps.put()
        self.btn.put(10, 80)
        self.btn2.put(10, 170)
        self.btn3.put(10, 260)
        self.btn4.put(203, 80)
        self.btn5.put(10, 370)
        self.btn6.put(10, 470)
        self.btn7.put(10, 540)
        self.v.put(550, 0)
        self.focusGTA.put(284, 4)
        self.timeShow.put(600, 0)
        self.timeBar.put()
        self.volumeBar.put()
        return self.listgui
        
            
g = A()

@ge.EventHandler(ge.EVENTS["KeyDown"], g)
def keydownplay(e):
    if e.key == ge.pygame.K_DOWN:
        g.sound2.play()
        g.focusFunc(g.focus + (1 if not g.focus in (3,0) else 0))
    elif e.key == ge.pygame.K_UP:
        g.sound2.play()
        g.focusFunc(g.focus - (1 if not g.focus in (1,0) else 0))
    elif e.key == ge.pygame.K_RETURN or e.key == ge.pygame.K_KP_ENTER:
        g.sound3.play()
        print("ENTER IN:", g.focus)

    elif e.key == ge.pygame.K_g:
        print("Mouse Pos:", ge.pygame.mouse.get_pos())
ge.StillRefresh = True
ge.fpsControl.set(60)

ge.addAssembly(g)
ge.setWindowSize(1200, 900)
#ge.setWindowType(ge.WINDOWTYPE['Resizable'])
ge.setWindowType(ge.WINDOWTYPE.Resizable)
ge.show()

# 一个简陋的文档

开始开发 GalEngine 并且具备可移植性（Windows & Android），需要下载源代码```git clone https://github.com/Himpq/GalEngine.git```。  

将GalEngine文件夹放置到项目路径下，使用```import GalEngine as ge``` 导入GalEngine模块。  

## Begin

GalEngine 使用 Assembly 对游戏画面的渲染与事件的绑定进行操作：  
```python
import GalEngine as ge

 # 对 GalEngine 进行初始化
ge.init() 

 # 创建一个Assembly
class Main (ge.Assembly):   
  def Start (self):
    # 创建显示的文本
    self.label = ge.gui.GalLabel(text="Hello world!")    

  def Draw (self):
    self.label.put(0, 0)

# 实例化Assembly并加载进渲染队列
ge.addAssembly(Main())
# 开始循环绘制, 程序会堵塞 
ge.show()    
```

上述代码创建了一个显示Hello world!的程序。  
可以看到一个具有内容显示的Assembly至少：
1. 继承自 GalEngine.Assembly
2. 拥有 Start、Draw等成员函数
3. 在逻辑代码中绘制
4. 被添加进渲染队列

Assembly 是 GalEngine 非常重要的一环，首个被添加进渲染队列的 Assembly 会被视为主组件，接下来绑定的所有GUI事件（如按钮点击、滑块滑动）都会以此 Assembly 为主，直到该实例化 Assembly 被移出渲染队列。  

Assembly 不一定要显示内容，它可以在逻辑循环中操控其他 Assembly，实现多组件结合显示。  

一个简单的多 Assembly 示例：
```python

import GalEngine as ge

ge.init()

class Main (ge.Assembly):
  def Start (self):
    self.label = ge.gui.GalLabel(text = 'Hello world!')
  def Draw (self):
      self.label.put (0, 0)

class Assembly2 (ge.Assembly):
  def Start (self):
    self.label = ge.gui.GalLabel(text = 'this is assembly2')
  def Draw (self):
    self.label.put (200, 0)
      
ge.addAssembly(Main())
ge.addAssembly(Assembly2())
ge.show()
```

请尽量让主组件和与其同时绘制的副组件一直在渲染队列中，因为副组件的事件会绑定在主组件上，当主组件被移除时副组件的事件将会失效。  

## GUI & Transition
GalEngine 基于 pygame 和 GalSDL2 (PySDL2)，并且提供了少量的 GUI 组件:
1. GalLabel  
   一个简单的 Label 组件，可以显示文本
2. GalButton  
   一个简单的 按钮 组件，可以实现简单的 onHover、 onHoverOff等效果与基础的style改变。
3. GalImage  
   一个显示 图片 的组件，可以通过成员函数进行scale、flip、rotate等图片操作。
4. GalSlider  
   一个非常简单的 滑块 组件，可以作为用户调节数值设置的组件。
5. GalGradientMask  
   一个简单的全局遮罩组件，配合Transition可以实现屏幕现实的渐入渐出。

上述具有用户交互效果的组件均可支持 GalStyle 进行属性设置。

例1:
```python

import GalEngine as ge

ge.init()

class Main (ge.Assembly):
  def Start (self):
    self.label = ge.gui.GalLabel(text = 'Hello world!',
                                 style=ge.gui.GalStyle(
                                     color='red',
                                     backgroundColor='white'
                                     )
                                 )
  def Draw (self):
      self.label.put (0, 0)


      
ge.addAssembly(Main())
ge.show()
```
上述代码实现了一个白底红字的Hello world!。  

例2：
```python

import GalEngine as ge

ge.init()

class Main (ge.Assembly):
  def Start (self):
    self.btn = ge.gui.GalButton (text='Press me!',
                                  style=ge.gui.GalStyle(
                                      color='blue',
                                      backgroundColor='white',
                                      padding=ge.gui.GalPadding(5,5,5,5)
                                  ),
                                  bind=ge.gui.GalBind(
                                      onClick=lambda *e: print("Btn!"),
                                  )
                                 )
    def c(*e):
        self.btn.style.color=[114,255,114,255]
    def g(*e):
        self.btn.style.color=ge.gui.color_to_rgba('blue')

    self.btn.bind.onHover=c
    self.btn.bind.onHoverOff=g
  def Draw (self):
      self.btn.put (0, 0)


      
ge.addAssembly(Main())
ge.show()
```
上述代码实现了一个鼠标hover和hoveroff时变色的按钮，并且当点击时控制台会输出Btn!。  

当使用对象实例化直接创建按钮时，可能一些直接操作按钮元素的事件无法直接绑定（因为按钮还未实例化），你可以延后定义，通过 widget.bind 对事件进行延后定义。  

## Media & Timer
你可以直接使用 pygame 内置的媒体库对音频进行播放，但是 GalEngine 也提供了更高层封装的简易 Media 对象：
```python
import GalEngine as ge

ge.init()

music = ge.media.playMusic(r"C:\Users\HimpqNotebook\Downloads\Ghostface Playa - Why Not.mp3")
music.setVolume(30)

class Main (ge.Assembly):
    def Start (self):
        self.musicTimer = ge.timer.GalTimer(music.fadeOut, 1, args=(1000, ))
        music.play(0)
        self.musicTimer.start()

ge.addAssembly(Main())
ge.show()
```

上述例子中使用了通过帧数计时的 GalTimer 对音乐的播放进行控制（音乐只会播放一秒就渐出）。

## ...


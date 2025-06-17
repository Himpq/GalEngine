# GalEngine 
一个可以在 Windows 和 Android 上，基于 pygame 和 pysdl2 的 GUI 界面渲染引擎。  

本来是想做一个Galgame的渲染引擎，但是因为种种原因演变成现在这个**dirty code**样。

## Requirements
Build for android:
```
requirements = python3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,hostpython3==3.10.12,pygame,pysdl2,numpy
```

# GalEngine.GalSDL2
一种 [Buildozer](https://github.com/kivy/buildozer) 的 Pygame 渲染解决方案。  
能够在安卓平台上调用GPU完成渲染，且这部分**接口和参数**基本和 pygame 提供的一致，这意味着你可以直接通过更改调用名达到使用 SDL2 渲染的效果。  

该模块并不依赖GalEngine，所以直接调用即可。

## What does it do
GalEngine 将部分 pygame 的接口替换为 SDL2 的接口，并做了 **Texture/Renderer** 渲染的实现，使其能够做简单的GPU渲染。

## How to use
### Use in project(GalEngine)

克隆本项目的源代码，使用`sys.path.append("./GalEngine")`引入路径，`import GalEngine as ge`导入总项目。  

### Use in project(GalEngine.GalSDL2)
同上。直接导入`import GalSDL2`，即可调用SDL2进行绘制。窗体、显示模式等更改参见 **GalEngine.py**。  

# Switch
GalGUI 里面存在：
```python
class Switcher:
    Surface = galengine.gsdl.SDLSurface if galengine.usingSDL2 else pygame.Surface
    Font    = galengine.gsdl.SDLFont if galengine.usingSDL2    else pygame.font.Font
    SysFont = galengine.gsdl.SysFont if galengine.usingSDL2    else pygame.font.SysFont
    def Rect(x, y, w, h):
        return [x, y, w, h]
    smoothscale = galengine.gsdl.scale if galengine.usingSDL2  else pygame.transform.scale
    scale       = galengine.gsdl.scale if galengine.usingSDL2  else pygame.transform.scale
    flip        = galengine.gsdl.flip if galengine.usingSDL2   else pygame.transform.flip
    rotate      = galengine.gsdl.rotate if galengine.usingSDL2 else pygame.transform.rotate
    
    class draw:
        rect = galengine.gsdl.draw.rect if galengine.usingSDL2  else pygame.draw.rect

    class image:
        load = galengine.gsdl.image.load if galengine.usingSDL2 else pygame.image.load

```
这意味着GalGUI会调用这里的基本绘画参数来完整GalGUI的全部功能，你可以将**GalEngine.py**中的**usingSDL2**更改，来达到在**pygame**与**SDL2**切换的目的。
```python
"""
    GalEngine By Himpq
"""

NO_LIMITED = 0xff

isAndroid = True
usingSDL2 = True   # <-- change here

import sys
import os
sys.path.append("./GalEngine")
```

# Build android apk
参见 [Buildozer & WSL 2 打包Python文件为APK](https://himpqblog.cn/index.php/archives/811) ，里面有我一路踩过的坑，以及后悔没早点转用 Unity。  

在打包的时候记得把 GalEngine 作为资源文件一样打包进去即可。  
你可以使用`adb logcat | grep python`在设备上调试，这样会在终端显示报错信息。

# Notice

## Loading
在 Python for android 上，程序入场时会呈现加载界面(loading screen)，会导致与SDL2渲染时间重合一部分，如果你有加载动画需要渲染，需要执行：
```python
from android import loadingscreen
loadingscreen.hide_loading_screen()
```
移除加载界面。**loadingscreen**是python for android提供的接口。

## Absolute path
在 Python for Android 中，程序的资源文件导入必须使用绝对路径，否则会出现找不到资源文件的错误。  

在 GalEngine.GalGUI 中，如果 `isAndroid` 被设置为**True**，那么 GalEngine 会自动将所有传入模块的路径转换为绝对路径。

# Change
Ver0.1: 
  1. 修复了 Font 重复绘制导致的内存溢出
  2. 引入了 Image 的缓存池机制，可以通过 `GalSDL2.image.load(path, cache=True)` 缓存该图片
  3. 加入了 SDLEvent 作为 pygame 转到 sdl2 的兼容层
  4. 修复了 Alpha 图层失效的问题

# Problems
1. 使用 `GalSDL2.image.load` 导入图片时，会莫名占用巨大的体积，一张图片接近20~200MB不等（样本范围：图片大小由1920x1080至6000x4000不等）
2. 图片缩放有问题，放大的大小与 `pygame.transform.scale` 不一致

# GalEngine 开发文档（标准架构与API说明）

## 1. 引擎入口与主流程

推荐入口结构如下，所有模块通过 `import galengine as ge` 导入，主流程建议如下：

```python
import galengine as ge
import pygame
import os

def main():
    ge.useAbsolutePath()
    ge.StillRefresh = True
    ge.fpsControl.set(60)
    # 注册初始 Assembly
    ge.addAssembly(YourAssembly())
    ge.show()

if __name__ == "__main__":
    main()
```

---

## 2. Assembly 组件机制

### 2.1 生命周期与注册

所有场景/窗口需继承 `ge.Assembly`，生命周期方法如下：

- `Start(self)`: 初始化，注册GUI/事件
- `Update(self)`: 每帧逻辑
- `Draw(self)`: 每帧绘制
- `Destroy(self)`: 资源回收

注册方式：

```python
class YourAssembly(ge.Assembly):
    def Start(self):
        # 初始化GUI、注册事件
        ...
    def Draw(self):
        ...
```

---

## 3. 事件系统

### 3.1 注册与分发

事件通过装饰器注册，自动归属 Assembly，主循环自动分发：

```python
@ge.EventHandler(ge.EVENTS["MouseDown"], self)
def onMouseDown(event):
    ...
```

- `EventHandler(EventType, assembly=None)` 参数：
  - `EventType`: 事件类型（如 ge.EVENTS["MouseDown"]）
  - `assembly`: 归属 Assembly，默认主窗口

### 3.2 事件分发与屏蔽机制

事件分发由主循环统一处理，所有事件会遍历 __EventHandler 字典，按 Assembly 归属分发。

- 屏蔽机制原理：
  - 事件被处理后可以通过`return True`使主循环中的事件分发程序跳出，拒接下一步事件的执行。
  - 事件执行先后顺序与事件注册的顺序相同。

---

## 4. GUI 组件与管理

### 4.1 组件参数与生命周期

所有 GUI 组件需指定归属 Assembly，支持 z-index 优先级。

- `GalButton(text, font, onclick, createAsm, ...)`
- `GalLabel(text, color, font, ...)`
- `GalSlider(width, height, onValueChanged, default, ...)`
- `GalImage(path)`

### 4.2 z-index 管理原理与 setPriority

所有 GUI 组件按 z-index 字典管理，决定事件响应优先级。

- z_index 字典：每个组件作为 key，优先级为 value。
- 组件创建时默认优先级为 1，可通过 setPriority(x) 方法提升或降低。
- 事件分发时，isTopInGUI(x, clickPos) 用于判定当前点击位置下最高优先级的组件：
  ```python
  def isTopInGUI(x, clickPos):
      p = []
      for i in z_index:
          v = z_index.get(i)
          if in_rect(clickPos, ...):
              p.append((i, v))
      if not p: return False
      p.sort(key=lambda item: item[1])
      return p[-1][0] == x
  ```
- setPriority(x) 用法：
  ```python
  btn.setPriority(10)  # 设置按钮优先级为10，响应事件时优先级更高
  ```
- 组件销毁时会自动从 z_index 移除。

---

## 5. Transition 动画机制

### 5.1 Transition 类参数与原理

`Transition` 支持多种缓动类型，自动驱动动画。

- `gui`: 目标组件或窗口
- `changeVar`: 变化回调函数
- `from_`, `to`: 起止值
- `time`: 动画时长（秒）
- `ease_type`: 缓动类型（如 'linear', 'ease-in', 'ease-out', 'ease-in-out' 或自定义函数）
- `finishCallback`: 动画结束回调

抽象用法：

```python
def change_callback(val):
    # 变化逻辑
    ...

trans = ge.gtran.Transition(
    gui=target,
    changeVar=change_callback,
    from_=0,
    to=100,
    time=2.0,
    ease_type=ge.gtran.Transition.EASE_IN_OUT,
    finishCallback=lambda: print("动画结束")
)
trans.start()
```

---

## 6. 配置与存档机制

### 6.1 GalConfig 用法

- `GalConfig(path)`: 指定存档路径
- `get(key)`: 获取配置项
- `set(key, value)`: 设置配置项

```python
cfg = ge.galcfg.GalConfig("./temp/Save.ini")
cfg.set("Volume", 0.9)
vol = cfg.get("Volume")
```

---

## 7. 日志与异常处理

### 7.1 GalLog 用法

```python
def Print(*String): ...
def saveLog(Path = "./Log"): ...
```

### 7.2 GalError 用法

```python
class AssemblyExtendsError(Exception): pass
class PhotoNotFound(Exception): pass
```

---

## 8. 主循环与窗口管理

### 8.1 主循环核心流程

```python
def show():
    while ge.Showing:
        # 事件分发
        # Assembly 更新
        # GUI 绘制
        ...
```

### 8.2 SDL2/PyGame 适配

```python
if ge.usingSDL2:
    import GalSDL2 as gsdl
```

---

## 9. 事件穿透防护原理（源码机制详解）

- GalEngine 的事件循环分发时，若某个 EventHandler 返回 True，则立即 break 本次事件分发，后续组件不再响应该事件。
- 这样可防止“穿透”或“连点”导致多个组件重复响应。
- 伪代码示例：
  ```python
  for event in pygame.event.get():
      for handler in __EventHandler[event.type]:
          if handler(event) is True:
              break  # 本次事件分发终止
  ```
- 推荐所有 GUI 组件的事件回调在成功处理后返回 True。

---

## 11. 核心模块 API 说明（标准类型与示例）

### 11.3 SDL2模块（GalEngine.sdl2）

#### GalEngine.sdl2.screen(width: int, height: int, title: str) -> ScreenObject
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| width    | int    | 窗口宽度       |
| height   | int    | 窗口高度       |
| title    | str    | 窗口标题       |

创建 SDL2 窗口，返回 ScreenObject。

#### ScreenObject.blit(surface, at: Tuple[int, int]) -> None
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| surface  | Surface| 渲染对象       |
| at       | Tuple[int, int] | 坐标     |

将 Surface 渲染到指定位置。

#### ScreenObject.blitPygame(what: pygame.Surface, at: Tuple[int, int]) -> None
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| what     | pygame.Surface | Pygame表面 |
| at       | Tuple[int, int] | 坐标     |

将 Pygame Surface 渲染到 SDL2。

#### ScreenObject.update() -> None
刷新窗口内容。

#### ScreenObject.get_width() -> int
获取窗口宽度。

#### ScreenObject.get_height() -> int
获取窗口高度。

#### ScreenObject.get_size() -> Tuple[int, int]
获取窗口尺寸。

#### ScreenObject.quit() -> None
销毁窗口。

#### ScreenObject.set_mode(size: Tuple[int, int] = None, flags: int = None) -> None
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| size     | Tuple[int, int] | 新窗口尺寸 |
| flags    | int    | 渲染标志       |

设置窗口模式。

---

### 11.4 帧率控制模块（GalEngine.fpsControl）

#### GalEngine.fpsControl.set(fps: int, record: bool = False) -> None
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| fps      | int    | 目标帧率       |
| record   | bool   | 是否记录上一次帧率（可选）|

设置目标帧率。

#### GalEngine.fpsControl.get() -> int
获取当前帧率。

#### GalEngine.fpsControl.getAverageFPS() -> float
获取平均帧率。

#### GalEngine.fpsControl.setRefresh(strategy: bool) -> None
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| strategy | bool   | 刷新策略（True:全量，False:增量）|

设置刷新策略。

#### GalEngine.fpsControl.refresh() -> None
刷新帧时间。

---

### 11.1 媒体模块（GalEngine.media）

#### GalEngine.media.playSound(path: str) -> SoundObject
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| path     | str    | 音效文件路径   |

播放音效，返回音效对象。

#### GalEngine.media.playMusic(path: str) -> MusicObject
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| path     | str    | 音乐文件路径   |

播放音乐，返回音乐对象。

#### GalEngine.media.setGlobalVolume(value: float) -> None
| 参数名         | 类型  | 说明          |
| -------------- | ----- | ------------- |
| value          | float | 全局音量(0~1) |

设置全局音量。

#### 音效/音乐对象方法

##### setVolume(v: int) -> None
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| v        | int    | 音量(0~100)    |

设置音量。

##### play(loops: int = 0, maxTime: int = 0, fadems: int = 0) -> None
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| loops    | int    | 循环次数       |
| maxTime  | int    | 最大播放时长(ms)|
| fadems   | int    | 淡入时长(ms)   |

播放音效/音乐。

##### stop() -> None
停止播放。

##### fadeOut(t: int) -> None
| 参数名   | 类型   | 说明           |
|----------|--------|----------------|
| t        | int    | 淡出时长(ms)   |

淡出音效/音乐。

##### getStatus() -> bool
获取播放状态。

**示例：**
```python
snd = GalEngine.media.playSound("./source/sounds/Click.wav")
snd.setVolume(80)
snd.play()

music = GalEngine.media.playMusic("./source/sounds/BGM.mp3")
music.setVolume(50)
music.play(loops=1)
music.fadeOut(2000)
music.stop()
```

---

### 11.2 鼠标模块（GalEngine.mouse）

#### GalEngine.mouse.getPos() -> Tuple[int, int]
获取鼠标坐标。

#### GalEngine.mouse.getPressed() -> Tuple[bool, bool, bool]
获取鼠标按键状态(左/中/右)。

#### GalEngine.mouse.leftClick() -> bool
检测左键是否按下。

#### GalEngine.mouse.midClick() -> bool
检测中键是否按下。

#### GalEngine.mouse.rightClick() -> bool
检测右键是否按下。

**示例：**
```python
if GalEngine.mouse.leftClick():
    print("左键按下")
x, y = GalEngine.mouse.getPos()
```

---

> 所有模块均需通过 `import galengine as GalEngine` 统一入口使用，除 SDL2 可独立调用外，其余均依赖 GalEngine.py。

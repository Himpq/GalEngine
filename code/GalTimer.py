
import GalEngine as ge
import threading
import typing
TIMERS = {}

class GalTimer:
    def __init__(self, callback:typing.Callable = None, delay: int = 1, checkWithRealFPS:bool = False,
                 args: typing.Tuple = tuple(), kvargs: typing.Dict = {}, useThread:bool = False):
        """根据帧数来计时执行函数
        :param callback: 计时执行的函数
        :param delay:    计时时间
        :param checkWithRealFPS: 与实际帧数确认（可能会导致初始化时期与理想秒数不同步）
        :param useThread: 在新线程中执行该函数
        """
        self.stop = False
        self.callback = callback
        self.delay = delay
        self.fc = 0
        self.args = args
        self.kvargs = kvargs
        self.checkWithRealFPS = checkWithRealFPS
        self.useThread = useThread
        self.threadPool = [] if self.useThread else None

    def start(self):
        self.stop = False
        TIMERS[self] = self
    
    def check(self):
        self.fc += 1
        aver = ge.fpsControl.getAverageFPS() if self.checkWithRealFPS else ge.fpsControl.get()
        if int(aver) * self.delay <= self.fc: #1 unit
            if self.useThread:
                self.threadPool.append(threading.Thread(target=self.callback, args=self.arg, kwargs=self.kvargs))
                self.threadPool[-1].start()
            self.callback(*self.args, **self.kvargs)
            self.fc = 0

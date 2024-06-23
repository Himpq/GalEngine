
import GalEngine as galengine

REFRESH_ALL_GUI = True
REFRESH_UPDATED_GUI_ONLY = False

import time

class fpsControlObject:
    def __init__(self):
        self.fps = 60
        self.upfps = 60
        self.refreshall = True
        self.drawTime = 1
    def getAverageFPS(self):
        g = time.time() - self.drawTime
        g = g if g else 1
        return 1/g
    def refresh(self):
        self.drawTime = time.time()

    def getRefreshAll(self):
        return self.refreshall
    def setRefresh(self, strategy):
        self.refreshall = strategy

    def set(self, fps, record=False):
        if record:
            self.upfps = self.fps
        self.fps = fps

    def back(self):
        self.fps = self.upfps

    def get(self):
        return self.fps
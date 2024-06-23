
#import GalEngine as ge
import os
import time
import json

class GalConfig:
    def __init__(self, path):
        self.path   = path
        self.isOpen = False
        if not os.path.isfile(self.path):
            self.initFile()

    def initFile(self):
        with open(self.path, 'w') as f:
            f.write("[GalConfig File]\n")
            f.write("_CreateDate: "+str(time.ctime())+"\n")
            f.write("_Index: "+json.dumps(
                {
                    "_CreateDate": 1,
                    "_Index": 2
                }
                )+"\n")
                
    def getTotalLine(self):
        with open(self.path, 'r') as f:
            return len(f.readlines())
        
    def set(self, key, val):
        self.on()
        t = 0
        with open(self.path, 'a') as f:
            index = self.getIndex()
            if not key in index:
                f.write(str(key)+": "+str(val)+"\n")
                index[key] = self.getTotalLine()
                t = 1
            else:
                t = 2
        if t == 1:
            self.changeIndex(index)
        elif t == 2:
            ctx = self.getAllContent()
            rl  = self.getLine(index[key])
            val = str(val)
            with open(self.path, 'w') as f:
                f.write(ctx.replace(rl, f"{key}: {val}\n"))
        self.off()

    def getIndex(self, origin = False):
        with open(self.path, 'r') as f:
            f.readline()
            f.readline()
            r = ": ".join(f.readline().split(": ")[1:])
            r = json.loads(r) if not origin else r
            return r
        
    def changeIndex(self, index):
        self.on()
        t = self.getIndex(True)
        c = self.getAllContent()
        with open(self.path, 'w') as f:
            f.write(c.replace("_Index: "+t, "_Index: "+json.dumps(index)+"\n", 1))
        self.off()
            
    def getAllContent(self):
        with open(self.path, 'r') as f:
            return f.read()

    def getLine(self, ln):
        with open(self.path, 'r') as f:
            return f.readlines()[ln]

    def get(self, key, turnToObj = True):
        self.on()
        with open(self.path, 'r') as f:
            r = self.getIndex()
            if not key in r:
                return
            for i in range(r[key]):
                f.readline()
            t = f.readline().split(": ")
        self.off()
        return ": ".join(t[1:])[0:-1]
    
    def on(self):
        self.isOpen = True
    def off(self):
        self.isOpen = False

    def __enter__(self):
        self.on()
        return self

    def __exit__(self, *arg):
        self.off()


def openCfg(path):
    return GalConfig(path)


testg = None

def init():
    global testg
    import os
    os.remove("./temp/test.txt") if os.path.isfile("./temp/test.txt") else None
    with openCfg("./temp/test.txt") as testg:
        testg = testg
        testg = GalConfig("./temp/test.txt")
        testg.set("Test1", "test")
        testg.set("Test2", "testg")
    
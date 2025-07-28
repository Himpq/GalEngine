#请勿单独导入该模块

import time
import os

from . import GalError

LOG = []
_print = False

def getTime():
    x=time.localtime()
    h=(x.tm_hour)
    m=(x.tm_min)
    s=(x.tm_sec)
    h=("0" if h < 10 else '')+str(h)
    m=("0" if m < 10 else '')+str(m)
    s=("0" if s < 10 else '')+str(s)
    s=h+":"+m+":"+s
    return s

def Print(*String):
    String = list(String)
    if str(String[0])[0:7] == "<GalGUI":
        objname = String[0].__class__.__name__
        String[0] = objname+"-"+str(String[0]).split("at")[-1].strip()[0:-1]
    s = "["+getTime()+"] "+(" ".join([str(i) for i in String]))
    LOG.append(s)
    print("[Event]", s) if _print else 0

def saveLog(Path = "./Log"):
    if not os.path.isdir(Path):
        os.mkdir(Path)
    with open(Path+"/Log_"+time.ctime().replace(" ","_").replace(":","_")+".log", 'w', encoding='UTF-8') as f:
        for i in LOG:
            f.write(i+"\n")
    


class EmptyObject:
    def __init__(self): ...

class Assembly:
    def Start(self):   ...
    def Update(self):  ...
    def Draw(self):    ...
    def Destroy(self): ...

def in_rect(pos,rect):
    x,y =pos
    rx,ry,rw,rh = rect
    if (rx <= x <=rx+rw) and (ry <= y <= ry +rh):
        return True
    return False

def notNone(*arg):
    a = [(not i == None) for i in arg]
    return all(a)

def DictToList(x):
    p = []
    for k in x:
        v = x.get(k)
        p.append((k, v))
    return p

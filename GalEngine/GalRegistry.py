
from .GalUtils import Assembly, EVENTS
from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    import GalSDL2 as gsdl
    import pygame

    """
    EventHandler.eventList -> {
        MouseDown : [
            Handler<Assembly, func, type>
            ....
        ]
    }"""

__all__ = ["Assembly", "EVENTS", "GalGlobals", "EventHandler"]

class GalGlobals:
    usingSDL2 = True
    isAndroid = False
    _zIndex: dict = None
    _mainAssembly: Assembly                    = None
    _assemblies: dict[Assembly]                = None
    screen: Optional[Union["gsdl.screen", "pygame.Surface"]] = None
    Done = False

    @staticmethod
    def getMainAssembly():
        return GalGlobals._mainAssembly
    
    @staticmethod
    def useAbsolutePath():
        Status.isUsingAbsPath = True

class Status:
    isRequestedRefresh  = False
    isContinuousRefresh = True
    isUsingAbsPath      = False
    isScreenInit        = False

class Handler:
    def __init__(self, func, bindAssembly, eventType):
        self.bindFunc = func
        self.bindAssembly = bindAssembly
        self.bindEventType = eventType

    def run(self, *arg, **kwargs):
        return self.bindFunc(*arg, **kwargs)
    
    def getBindAssembly(self):
        return self.bindAssembly
    
    def getBindEvent(self):
        return self.bindEventType
    
    def getBindFunc(self):
        return self.bindFunc

class EventHandlerClass:
    def __init__(self):
        self.eventList = {}

    def register(self, eventType, bindAssembly = None):
        bindAssembly = bindAssembly if bindAssembly else GalGlobals.getMainAssembly()

        if self.eventList.get(eventType) is None:
            self.eventList[eventType] = []
        
        def decorator(func):
            self.eventList[eventType].append(Handler(func, bindAssembly, eventType))
            return func
        
        return decorator
    
    def getEventHandlers(self):
        return self.eventList
    
    def handle(self, event):
        if event.type in self.eventList:
            for handle in self.eventList[event.type]:
                if not isinstance(handle, Handler):
                    print(handle, 'is not handle')
                    continue
                if handle.run(event): # set cancelled
                    break

    def saveEventHandlers(self, assembly = None):
        assembly = assembly if assembly else GalGlobals.getMainAssembly()
        if not getattr(assembly, "_EVTS", None):
            assembly._EVTS = {}

        for eventType, handlers in list(self.eventList.items()):
            bindHandlers = [h for h in handlers if h.getBindAssembly() == assembly]
            
            if bindHandlers:
                if eventType not in assembly._EVTS:
                    assembly._EVTS[eventType] = []
                assembly._EVTS[eventType].extend(bindHandlers)
                
                for handler in bindHandlers:
                    self.eventList[eventType].remove(handler)
                
                if not self.eventList[eventType]:
                    del self.eventList[eventType]

    def restoreEventHandlers(self, assembly = None):
        assembly = assembly if assembly else GalGlobals.getMainAssembly()
        if not hasattr(assembly, "_EVTS"):
            return
        for eventType, savedHandlers in assembly._EVTS.items():
            currentHandlers = self.eventList.get(eventType, [])
            
            for handler in savedHandlers:
                if handler not in currentHandlers:
                    if eventType not in self.eventList:
                        self.eventList[eventType] = []

                    self.eventList[eventType].append(handler)
    
class GUIHandlerClass:
    def __init__(self):
        ...

    def saveGUIs(self, assembly = None):
        assembly = assembly if assembly else GalGlobals.getMainAssembly()

        if not hasattr(assembly, "_GUIS"):
            assembly._GUIS = {}
        
        zIndexCopy =  GalGlobals._zIndex.copy()
        for widget, zIndex in zIndexCopy.items():
            assembly._GUIS[widget] = zIndex
            del GalGlobals._zIndex[widget]

            print("[AsmManager] Remove GUI", widget, "from z-index.")

    def restoreGUIs(self, assembly = None):
        assembly = assembly if assembly else GalGlobals.getMainAssembly()
        if not hasattr(assembly, "_GUIS"):
            return
        
        for widget, zIndex in assembly._GUIS.items():
            GalGlobals._zIndex[widget] = zIndex
            print("[AsmManager] Restore GUI", widget, "to z-index.")
        
        del assembly._GUIS

EventHandler = EventHandlerClass()
GUIHandler   = GUIHandlerClass()
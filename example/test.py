
import GalEngine as ge
from GalEngine.GalUtils import Assembly
from GalEngine.GalGUI import GalLabel

ge.init()

class MainAssembly(Assembly):
    def Start(self):
        self.label = GalLabel(
            None,
            "Hello world!",
            color=[255, 255, 255, 255] # white
        )

    def Draw(self):
        self.label.put(0, 0)

Main = MainAssembly()
ge.addAssembly(Main)
ge.show()
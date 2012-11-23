from org.json.simple import JsonObject, JsonSimple
import os.path
from java.io import File

class _FascinatorHome:
    root = "."

    def getPath(self):
        return self.root

    def getPath(self, pth):
        return os.path.join(self.root, pth)

    def setPath(self, path):
        self.__class__.__dict__['root'] = path

    def getPathFile(self, path):
        return File(path)

FascinatorHome = _FascinatorHome()




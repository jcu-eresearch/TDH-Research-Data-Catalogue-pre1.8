from java.io import PrintWriter

class log:
    def error(self, *args):
        print "[ERROR]", args

    def info(self, *args):
        print "[INFO ]", args

    def debug(self, *args):
        a = args[0]
        b = args[1:]
        print "[DEBUG]", a.format(*b)

class response:
    def setStatus(self, status): pass

    def getPrintWriter(self, mime): return PrintWriter()

class config:
    def __init__(self, home, data):
        self.data = data
        self.home = home
    def getString(self, *args):
        print args
        if args[1] == 'redbox.version.string':
            return "1.5.2.2"
        d = self.data
        for i in args[1]:
            d = d[i]
        if d is None:
            return None
        return d.replace("${fascinator.home}",self.home)
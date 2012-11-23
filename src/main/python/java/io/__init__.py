class FileInputStream:
    def __init__(self, _file):
        self.file = _file
        self.file.open()

    def close(self):
        self.file.close()

    def read(self, *args):
        return  self.file.read(*args)


class InputStreamReader:
    def __init__(self, stream, encoding):
        self.stream = stream
        self.encoding = encoding

    def read(self, *args):
        return self.stream.read(*args).encode(self.encoding)

    def close(self):
        self.stream.close()

class File:
    def __init__(self, path):
        self.path = path
    def open(self):
        self.f = open(self.path)

    def read(self, *args):
        return self.f.read(*args)

    def close(self):
        self.f.close()

class PrintWriter:
    def println(self, message):
        print message
    def close(self): pass
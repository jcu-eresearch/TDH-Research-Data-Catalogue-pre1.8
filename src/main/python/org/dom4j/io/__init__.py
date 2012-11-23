from lxml import etree
class SAXReader:
    def __init__(self, doc_fac):
        self.fac = doc_fac
    def read(self, obj):
        return etree.parse(obj.stream.file.path)

class DefaultNamespaceContext: pass

class NodeWrapper:
    def __init__(self, node):
        if isinstance(node, NodeWrapper):
            self.node = node.node
        else:
            self.node = node

    def getValue(self):
        if self.node.__class__.__dict__.has_key('text'):
            return self.node.text.encode("utf-8")
        return self.node

    def xpath(self, p, namespaces={}):
        return fix(self.node.xpath(p, namespaces=namespaces))

def fix(nodes):
    return [NodeWrapper(x) for x in nodes]

class DefaultXPath:
    def __init__(self, xpath):
        self.xpath = xpath
    def setNamespaceContext(self, namespace):
        self.namespace = namespace

    def selectNodes(self, root):
        p = self.xpath
        return fix(root.xpath(p, namespaces={"rif": "http://ands.org.au/standards/rif-cs/registryObjects"}))


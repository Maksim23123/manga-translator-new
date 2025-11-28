import uuid


class DummySignal:
    def __init__(self):
        self._callbacks = []

    def connect(self, fn, **_kwargs):
        self._callbacks.append(fn)

    def emit(self, *args, **kwargs):
        for fn in list(self._callbacks):
            fn(*args, **kwargs)


class DummyGraph:
    def __init__(self, uid=None, parent=None):
        self.uid = uid or uuid.uuid4()
        self.parentGraph = parent
        self._nodes = []

    def add_node(self, node):
        self._nodes.append(node)

    def getNodes(self):
        return {node.uid: node for node in self._nodes}


class DummyOutputNode:
    def __init__(self, graph):
        self._graph = graph
        self.uid = uuid.uuid4()
        self.killed = DummySignal()
        self.kill_called = False
        graph.add_node(self)

    def graph(self):
        return self._graph

    def kill(self):
        self.kill_called = True
        self.killed.emit()


class DummyGraphManager:
    def __init__(self, nodes=None):
        self._nodes = list(nodes or [])

    def getAllNodes(self, classNameFilters=None):
        return list(self._nodes)

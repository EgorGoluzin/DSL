class Node:
    def __init__(self, name, labels=None):
        self.name = name
        self.labels = labels or {}


class Edge:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst


class Digraph:
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def save(self, path):
        # Логика сохранения в файл
        pass
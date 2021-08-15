import networkx as nx
import pydot


def fold_constant(g: pydot.Dot):
    pass


class FoldConstant:
    def __init__(self, ast):
        self.ast: nx.DiGraph = nx.drawing.nx_pydot.from_pydot(ast)
        self.visit_set = {}

    def run(self):
        pass

    def __fold(self, n: pydot.Node):
        pass

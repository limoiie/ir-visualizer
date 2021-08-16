import networkx as nx
import pydot


class AnalysisManager:
    def __init__(self, passes):
        self.passes = passes

    def __call__(self, ast: pydot.Graph):
        nx_ast = nx.drawing.nx_pydot.from_pydot(ast)
        for p in self.passes:
            nx_ast = p.run(nx_ast)
        return nx.drawing.nx_pydot.to_pydot(nx_ast)

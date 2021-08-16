import networkx as nx


class CleanDropOff:
    def __init__(self):
        self.ast: nx.Graph = nx.Graph()

    def run(self, ast: nx.Graph):
        assert isinstance(ast, nx.Graph)
        self.ast = ast

        for drop_off in list(filter(self.__is_drop_off, self.ast.nodes)):
            self.ast.remove_node(drop_off)
        return self.ast

    def __is_drop_off(self, n: str):
        return self.ast.degree[n] == 0

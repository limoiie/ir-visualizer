import networkx as nx


class MarkEntries:
    def __init__(self, fill_color='black', font_color='white'):
        self.ast: nx.DiGraph = nx.DiGraph()
        self.fill_color = fill_color
        self.font_color = font_color

    def run(self, ast: nx.DiGraph):
        assert isinstance(ast, nx.DiGraph)
        self.ast = ast

        for n in self.ast.nodes:
            if self.__is_entry(n):
                node = self.ast.nodes[n]
                node['style'] = 'filled'
                node['fillcolor'] = self.fill_color
                node['fontcolor'] = self.font_color
        return self.ast

    def __is_entry(self, n: str):
        return self.ast.in_degree[n] == 0

import networkx as nx


class DiGraphAnalysisBase:
    def __init__(self):
        self.ast: nx.DiGraph = nx.DiGraph()

    def is_entry(self, n: str):
        return self.ast.in_degree[n] == 0

    def entries(self):
        return list(filter(self.is_entry, self.ast.nodes))

    def run(self, ast: nx.DiGraph):
        assert isinstance(ast, nx.DiGraph)
        self.ast = ast

    def node(self, n):
        return self.ast.nodes[n]

    def is_op(self, n: str):
        return self.ast.nodes[n]['ntyp'] == 'op'

    def is_const(self, n: str):
        return self.ast.nodes[n]['ntyp'] == 'c'

    def is_constexpr(self, n: str):
        return self.ast.nodes[n]['ntyp'] == 'ce'

    def is_var(self, n: str):
        return self.ast.nodes[n]['ntyp'] == 'v'

    def dfs(self, fn_visitor):
        for entry in self.entries():
            self.__dfs(entry, fn_visitor)

    def __dfs(self, n, fn_visitor):
        if not self.ast.has_node(n):
            return

        successors = list(self.ast.successors(n))
        if len(successors) == 0:
            return

        assert len(successors) == 1

        if self.is_op(successors[0]):
            op = successors[0]
            opr_list = list(self.ast.successors(op))

            for opr in opr_list:
                self.__dfs(opr, fn_visitor)

            fn_visitor(n, op)

        elif self.is_var(successors[0]):
            var = successors[0]
            self.__dfs(var, fn_visitor)
            fn_visitor(n, None)

    def merge_node(self, n, dead_n):
        in_edges = [(p, n) for p in self.ast.predecessors(dead_n)]
        out_edges = [(n, s) for s in self.ast.successors(dead_n)]

        self.ast.add_edges_from(in_edges + out_edges)
        self.ast.remove_edge(n, n)
        self.ast.remove_node(dead_n)

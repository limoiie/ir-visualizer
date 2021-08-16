import networkx as nx


class PruneBranches:
    def __init__(self):
        self.ast: nx.DiGraph = nx.DiGraph()

    def run(self, ast: nx.DiGraph):
        assert isinstance(ast, nx.DiGraph)
        self.ast = ast

        entries = set(filter(self.__is_entry, self.ast.nodes))
        main_entry = max(entries, key=self.__tree_size)
        entries.remove(main_entry)

        self.__clean(entries)
        return self.ast

    def __clean(self, worklist: set):
        while worklist:
            curr = worklist.pop()
            if not self.__is_entry(curr):
                continue

            succs = set(self.ast.successors(curr))
            out_edges_of_curr = [(curr, succ) for succ in succs]

            self.ast.remove_edges_from(out_edges_of_curr)
            self.ast.remove_node(curr)

            worklist |= succs

    def __is_entry(self, n: str):
        return self.ast.in_degree[n] == 0

    def __tree_size(self, n: str):
        return 1 + sum(map(self.__tree_size, self.ast.successors(n)))

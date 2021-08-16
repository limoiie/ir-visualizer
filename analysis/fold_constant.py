from functools import reduce

import networkx as nx


class FoldConstant:
    def __init__(self):
        self.ast: nx.DiGraph = nx.DiGraph()
        self.dead_edges = []
        self.dead_nodes = []

        self.op_fn_map = {
            '&': lambda x, y: x & y,
            '|': lambda x, y: x | y,
            '^': lambda x, y: x ^ y,
        }

    def run(self, ast: nx.DiGraph):
        assert isinstance(ast, nx.DiGraph)
        self.ast = ast

        for n in self.ast.nodes:
            self.__fold_constexpr(n)
        self.__clean_dead()
        return self.ast

    def __fold_constexpr(self, curr):
        node_curr = self.ast.nodes[curr]
        if node_curr['ntyp'] == 'c':
            return node_curr
        if node_curr['ntyp'] != 'ce':
            return None

        # collect operands
        op = list(self.ast.successors(curr))[0]
        opr_node_list = []
        for succ in self.ast.successors(op):
            folded_node = self.__fold_constexpr(succ)
            if not folded_node:
                return None
            opr_node_list.append(folded_node)
        const = self.__simulate_exp(op, opr_node_list)

        # clean expression relationships
        self.dead_edges.append((curr, op))
        for succ in self.ast.successors(op):
            self.dead_edges.append((op, succ))
        self.dead_nodes.append(op)

        # update node attributes
        node_curr = self.ast.nodes[curr]
        node_curr['ntyp'] = 'c'
        node_curr['label'] = hex(const)

        return node_curr

    def __clean_dead(self):
        self.ast.remove_edges_from(self.dead_edges)
        self.ast.remove_nodes_from(self.dead_nodes)

    def __simulate_exp(self, op, opr_node_list: list):
        l = map(lambda node: int(node['label'], 16), opr_node_list)
        return reduce(self.__fn_of(op), l)

    def __fn_of(self, op):
        op = self.ast.nodes[op]['label']
        if op not in self.op_fn_map:
            raise NotImplementedError(f'Op {op} is not supported yet!')
        return self.op_fn_map[op]

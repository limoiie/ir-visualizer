from functools import reduce

import networkx as nx
import pydot


def fold_constant(g: pydot.Dot):
    pass


class FoldConstant:
    def __init__(self, ast):
        self.ast: nx.DiGraph = nx.drawing.nx_pydot.from_pydot(ast)
        self.visit_set = {}

        self.op_fn_map = {
            '&': lambda x, y: x & y,
            '|': lambda x, y: x & y,
            '^': lambda x, y: x & y,
        }

    def run(self):
        for n in self.ast.nodes:
            if self.ast.has_node(n):
                self.__fold_constexpr(n)
        return nx.drawing.nx_pydot.to_pydot(self.ast)

    def __fold_constexpr(self, curr):
        op = self.ast.successors(curr)
        op = op[0] if op else None
        if not op:
            return None

        opr_node_list = []
        for succ in self.ast.successors(op):
            node_succ = self.ast.nodes[succ]
            if node_succ['ntyp'] is 'c':
                opr_node_list.append(node_succ)
            elif node_succ['ntyp'] is 'ce':
                folded_node = self.__fold_constexpr(node_succ)
                opr_node_list.append(folded_node)
            else:
                return None
        const = self.__simulate_exp(op, opr_node_list)

        self.ast.remove_edge(curr, op)
        for succ in self.ast.successors(op):
            self.ast.remove_edge(op, succ)
        self.ast.remove_node(op)

        node_curr = self.ast.nodes[curr]
        node_curr['ntyp'] = 'c'
        node_curr['label'] = const
        return node_curr

    def __simulate_exp(self, op, opr_node_list: list):
        l = map(lambda node: int(node['label'], 16), opr_node_list)
        return reduce(self.__fn_of(op), l)

    def __fn_of(self, op):
        if op not in self.op_fn_map:
            raise NotImplementedError(f'Op {op} is not supported yet!')
        return self.op_fn_map[op]

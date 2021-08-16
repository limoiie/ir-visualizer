from functools import reduce

import networkx as nx
import pydot

from analysis.AnalysisBase import DiGraphAnalysisBase


class Simplify(DiGraphAnalysisBase):
    def __init__(self):
        super().__init__()
        self.fn_reduce_map = {
            '^': self.__reduce_xor,
            '|': self.__reduce_or,
            '&': self.__reduce_and,
            '?': self.__reduce_default,
        }
        self.fn_reduce_map = {
            '^': lambda a, b: a ^ b,
            '|': lambda a, b: a | b,
            '&': lambda a, b: a & b,
        }

    def run(self, ast: nx.DiGraph):
        super().run(ast)

        self.dfs(self.__visit)
        return self.ast

    def __visit(self, n, op):
        opr_list = list(self.ast.successors(op))
        if all(map(self.is_const, opr_list)) and op in self.fn_reduce_map:
            op_symbol = self.node(op)['label']
            self.__reduce_const(n, op, opr_list, self.fn_reduce_map[op_symbol])
            return

        # noinspection PyArgumentList
        self.__dispatch(op)(n, op, opr_list)

    def __reduce_xor(self, n: str, op: str, opr_list):
        if len(opr_list) != 2:
            return

        op_out_edges = [(op, opr) for opr in opr_list]

        if self.is_const(opr_list[0]) and self.is_const(opr_list[1]):
            self.__reduce_const(n, op, opr_list, lambda a, b: a ^ b)
            return

        for i, k in [(0, 1), (1, 0)]:
            if self.is_const(opr_list[i]):
                val, var = opr_list[i], opr_list[k]
                c_val = int(self.node(opr_list[i])['label'], 16)
                if c_val == 0xFFFF_FFFF:
                    self.ast.remove_edge(op, val)
                    self.ast.remove_node(val)
                    self.node(op)['label'] = '~'
                elif c_val == 0:
                    self.ast.remove_edges_from(op_out_edges)
                    self.ast.remove_node(val)
                    self.ast.remove_edge(n, op)
                    self.ast.remove_node(op)
                    self.ast.add_edge(n, var)
                return

    def __reduce_and(self, n: pydot.Node, op, opr_list):
        op_out_edges = [(op, opr) for opr in opr_list]

        if self.is_const(opr_list[0]) and self.is_const(opr_list[1]):
            self.__reduce_const(n, op, opr_list, lambda a, b: a & b)
            return

        for i, k in [(0, 1), (1, 0)]:
            if self.is_const(opr_list[i]):
                val, var = opr_list[i], opr_list[k]
                val_node = self.node(opr_list[i])
                c_val = int(val_node['label'], 16)
                if c_val == 0xFFFF_FFFF:
                    self.ast.remove_edges_from(op_out_edges)
                    self.ast.remove_node(val)
                    self.ast.remove_edge(n, op)
                    self.ast.remove_node(op)
                    self.ast.add_edge(n, var)
                elif c_val == 0:
                    self.ast.remove_edges_from(op_out_edges)
                    self.ast.remove_nodes_from(opr_list)
                    self.ast.remove_edge(n, op)
                    self.ast.remove_node(op)

                    self.node(op)['ntyp'] = 'c'
                    self.node(op)['label'] = val_node['label']
                return

    def __reduce_or(self, n: pydot.Node, op, opr_list):
        op_out_edges = [(op, opr) for opr in opr_list]

        if self.is_const(opr_list[0]) and self.is_const(opr_list[1]):
            self.__reduce_const(n, op, opr_list, lambda a, b: a | b)
            return

        for i, k in [(0, 1), (1, 0)]:
            if self.is_const(opr_list[i]):
                val, var = opr_list[i], opr_list[k]
                val_node = self.node(opr_list[i])
                c_val = int(val_node['label'], 16)
                if c_val == 0xFFFF_FFFF:
                    self.ast.remove_edges_from(op_out_edges)
                    self.ast.remove_nodes_from(opr_list)
                    self.ast.remove_edge(n, op)
                    self.ast.remove_node(op)

                    self.node(op)['ntyp'] = 'c'
                    self.node(op)['label'] = val_node['label']
                elif c_val == 0:
                    self.ast.remove_edges_from(op_out_edges)
                    self.ast.remove_node(val)
                    self.ast.remove_edge(n, op)
                    self.ast.remove_node(op)
                    self.ast.add_edge(n, var)
                return

    def __reduce_default(self, n, op, opr_list):
        pass

    def __reduce_const(self, n, op, opr_list, fn_op):
        node = self.node(n)
        op_out_edges = [(op, opr) for opr in opr_list]

        opr_list_ = map(lambda x: self.node(x)['label'], opr_list)
        opr_list_ = map(lambda x: int(x, 16), opr_list_)
        result = reduce(fn_op, opr_list_)

        self.ast.remove_edges_from(op_out_edges)
        self.ast.remove_nodes_from(opr_list)
        self.ast.remove_edge(n, op)
        self.ast.remove_node(op)

        node['ntyp'] = 'c'
        node['label'] = hex(result)

    def __dispatch(self, op):
        op_symbol = self.node(op)['label']
        if op_symbol not in self.fn_reduce_map:
            op_symbol = '?'
        return self.fn_reduce_map[op_symbol]

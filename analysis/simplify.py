from functools import reduce

import networkx as nx

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
        self.fn_op_map = {
            '^': lambda a, b: a ^ b,
            '|': lambda a, b: a | b,
            '&': lambda a, b: a & b,
        }

    def run(self, ast: nx.DiGraph):
        super().run(ast)

        self.dfs(self.__visit)
        return self.ast

    def __visit(self, n, op):
        if op is None:
            copy_n = list(self.ast.successors(n))[0]
            self.__reduce_copy(n, copy_n)
            return

        opr_list = list(self.ast.successors(op))
        if all(map(self.is_const, opr_list)) and op in self.fn_op_map:
            op_symbol = self.node(op)['label']
            self.__reduce_const(n, op, opr_list, self.fn_op_map[op_symbol])
            return

        # noinspection PyArgumentList
        self.__dispatch(op)(n, op, opr_list)

    def __reduce_xor(self, n: str, op: str, opr_list):
        if len(opr_list) == 1:
            self.merge_node(n, op)
            self.merge_node(n, opr_list[0])
            return

        for i, k in [(0, 1), (1, 0)]:
            if self.is_const(opr_list[i]):
                val, var = opr_list[i], opr_list[k]
                c_val = int(self.node(opr_list[i])['label'], 16)
                if c_val == 0xFFFF_FFFF:
                    self.ast.remove_node(val)
                    self.node(op)['label'] = '~'
                elif c_val == 0:
                    self.merge_node(n, op)
                    self.merge_node(n, var)
                    self.ast.remove_node(val)
                return

    def __reduce_and(self, n: str, op: str, opr_list):
        if len(opr_list) == 1:
            self.merge_node(n, op)
            self.merge_node(n, opr_list[0])
            return

        for i, k in [(0, 1), (1, 0)]:
            if self.is_const(opr_list[i]):
                val, var = opr_list[i], opr_list[k]
                val_node = self.node(opr_list[i])
                c_val = int(val_node['label'], 16)
                if c_val == 0xFFFF_FFFF:
                    self.merge_node(n, op)
                    self.merge_node(n, var)
                    self.ast.remove_node(val)
                elif c_val == 0:
                    self.ast.remove_nodes_from(opr_list)
                    self.ast.remove_node(op)

                    self.node(op)['ntyp'] = 'c'
                    self.node(op)['label'] = val_node['label']
                return

    def __reduce_or(self, n: str, op: str, opr_list):
        if len(opr_list) == 1:
            self.merge_node(n, op)
            self.merge_node(n, opr_list[0])
            return

        for i, k in [(0, 1), (1, 0)]:
            if self.is_const(opr_list[i]):
                val, var = opr_list[i], opr_list[k]
                val_node = self.node(opr_list[i])
                c_val = int(val_node['label'], 16)
                if c_val == 0xFFFF_FFFF:
                    self.ast.remove_nodes_from(opr_list)
                    self.ast.remove_node(op)

                    self.node(op)['ntyp'] = 'c'
                    self.node(op)['label'] = val_node['label']
                elif c_val == 0:
                    self.merge_node(n, op)
                    self.merge_node(n, var)
                    self.ast.remove_node(val)
                return

    def __reduce_default(self, n, op, opr_list):
        pass

    def __reduce_const(self, n, op, opr_list, fn_op):
        node = self.node(n)

        opr_list_ = map(lambda x: self.node(x)['label'], opr_list)
        opr_list_ = map(lambda x: int(x, 16), opr_list_)
        result = reduce(fn_op, opr_list_)

        self.ast.remove_nodes_from(opr_list)
        self.ast.remove_node(op)

        node['ntyp'] = 'c'
        node['label'] = hex(result)

    def __reduce_copy(self, n, copy_n):
        self.merge_node(n, copy_n)

    def __dispatch(self, op):
        op_symbol = self.node(op)['label']
        if op_symbol not in self.fn_reduce_map:
            op_symbol = '?'
        return self.fn_reduce_map[op_symbol]

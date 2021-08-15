import re
import unittest

import pydot


class BlockParser:
    def __init__(self):
        self.ast = pydot.Dot()
        self.id_base = 0

    def block_parser(self, ir_block: str):
        for inst_line in ir_block.split(sep='\n'):
            inst_line = inst_line.strip()
            if len(inst_line) == 0:
                continue
            self.__handle_inst_line(inst_line)
            pass
        pass

    def __handle_inst_line(self, line):
        (var, op, typ, opr_list) = _parse_inst_line(line)

        var_node = self.__var_node(var, typ)
        op_node = self.__op_node(op)
        edge = pydot.Edge(var_node, op_node)
        self.ast.add_edge(edge)

        is_constexpr = var_node.get('ntyp') == 'v'
        for opr in opr_list:
            opr_node = self.__var_node(opr, typ)
            is_constexpr &= opr_node.get('ntyp') in ['c', 'ce']
            edge = pydot.Edge(op_node, opr_node)
            self.ast.add_edge(edge)

        if is_constexpr:
            var_node.set('ntyp', 'ce')

    def __id(self):
        self.id_base += 1
        return self.id_base

    def __op_node(self, op):
        op_name, ntyp = f'"{op}#{self.__id():02}"', 'op'
        label = op_map[op] if op in op_map else op
        n = pydot.Node(op_name, label=label, ntyp=ntyp)
        self.ast.add_node(n)
        return n

    def __var_node(self, var, typ):
        var_name, ntyp = f'"${var[1:]}"', 'v'
        if not var.startswith('%'):
            var_name, ntyp = f'"{var}#{self.__id()}"', 'c'
        n = self.ast.get_node(var_name)
        if n:
            return n[0]

        n = pydot.Node(var_name, label=var, typ=typ, ntyp=ntyp)
        self.ast.add_node(n)
        return n


op_map = {
    'and': '&', 'or': '|', 'xor': '^', 'shl': '<<', 'shr': '>>'
}


def _parse_inst_line(line):
    # match assignment
    r = re.match(r'(%[^\b]+) = (.+)', line)
    if not r:
        print(f'Failed to parse {line}')
        return
    var, exp = r.groups()

    r = re.match(r'(\w+) (\w+) (.+)', exp)
    operator, typ, operands = r.groups()
    operands = operands.split(', ')

    return var, operator, typ, operands


class Test(unittest.TestCase):
    def test_parse_inst_line(self):
        line = '%1898 = and i32 0x2E2882F, %1897'
        expect = ('%1898', 'and', 'i32', ['0x2E2882F', '%1897'])
        output = _parse_inst_line(line)
        self.assertTrue(expect == output,
                        f'output ({output}) does not equal to '
                        f'expect ({expect})')

import re
import unittest

import pydot


class BapIrBlockParser:
    def __init__(self):
        self.ast = pydot.Dot()
        self.__id_base = 0
        self.__id_ssa_base = {}

    def parser(self, ir_block: str):
        for inst_line in ir_block.split(sep='\n'):
            inst_line = inst_line.strip()
            if not inst_line:
                continue
            self.__parse_inst_line(inst_line)

    def __parse_inst_line(self, line):
        r = re.match(r'[0-9a-z]{8}: ([^\b]+) := (.+)', line)
        if not r:
            print(f'Failed to parse {line}')
            return

        var, exp = r.groups()
        node_op = self.__parse_exp(exp)
        node_var = self.__var_node(var, False)
        edge = pydot.Edge(node_var, node_op)
        self.ast.add_edge(edge)

    def __parse_exp(self, s: str):
        s = s.strip()
        op, opr_list = _break_exp(s)
        if op is None:
            if _is_cast(s):
                # unwrap the cast
                start, end = s.index('[') + 1, s.rindex(']')
                return self.__parse_exp(s[start:end])

            # is var
            return self.__var_node(s, True)

        node_op = self.__op_node(op)
        for opr in opr_list:
            node_opr = self.__parse_exp(opr)
            edge = pydot.Edge(node_op, node_opr)
            self.ast.add_edge(edge)

        return node_op

    def __op_node(self, op: str):
        op_name, ntyp = f'"{op}#{self.__id():02}"', 'op'
        n = pydot.Node(op_name, label=op, ntyp=ntyp)
        self.ast.add_node(n)
        return n

    def __var_node(self, var: str, is_use):
        if _is_const(var):
            var_name, ntyp = f'"{var}#{self.__id()}"', 'c'
        else:
            var_name, ntyp = self.__ssa_use_var_name(var) if is_use else \
                self.__ssa_def_var_name(var), 'v'
            var = var_name

        n = self.ast.get_node(var_name)
        if n:
            return n[0]

        n = pydot.Node(var_name, label=var, ntyp=ntyp)
        self.ast.add_node(n)
        return n

    def __ssa_def_var_name(self, var: str):
        self.__id_ssa_base[var] = 1 + (self.__id_ssa_base.get(var) or 0)
        ssa_num = self.__id_ssa_base[var]
        return f'{var}.{ssa_num}'

    def __ssa_use_var_name(self, var: str):
        ssa_num = self.__id_ssa_base.get(var) or 0
        return f'{var}.{ssa_num}'

    def __id(self):
        self.__id_base += 1
        return self.__id_base


unop_list = {
    '~', '-'
}


def _is_cast(exp: str):
    cast_prefix_list = [
        'extend:', 'pad:', 'low:', 'high:'
    ]
    return any(map(exp.startswith, cast_prefix_list))


def _is_const(exp: str):
    return exp.startswith('0x') or exp.isdigit()


def _break_exp(exp: str):
    sub_exps = []
    start = 0
    cnt = 0

    for i, c in enumerate(exp + ' '):
        if c == '[':
            cnt += 1
        elif c == ']':
            cnt -= 1

        if cnt == 0 and c in [' ', '~']:
            sub_exp = exp[start:i+1].strip()
            sub_exp and sub_exps.append(sub_exp)
            start = i + 1

    if len(sub_exps) == 1:
        if _is_cast(exp):
            # unwrap the cast
            start, end = exp.index('[') + 1, exp.rindex(']')
            return _break_exp(exp[start:end])

        return None, sub_exps

    if len(sub_exps) == 2:
        op = sub_exps[0]
        opr_list = [sub_exps[1]]
    elif len(sub_exps) == 3:
        op = sub_exps[1]
        opr_list = [sub_exps[0], sub_exps[2]]
    else:
        raise RuntimeError(f'Unknown sub_exp_list len: {len(sub_exps)}')

    assert op in ['~', '+', '-', '*', '/', '<<', '>>', '&', '|', '^']
    return op, opr_list


class Test(unittest.TestCase):
    def test_break_exp(self):
        cases = [
            ('low:32[RSI] & 0xD7D921C0', ('&', ['low:32[RSI]', '0xD7D921C0'])),
            ('pad:64[low:32[RSI] << 6]', ('<<', ['low:32[RSI]', '6'])),
            ('low:32[RSI] << 6', ('<<', ['low:32[RSI]', '6'])),
            ('~low:32[RDX]', ('~', ['low:32[RDX]']))
        ]
        for exp, expect in cases:
            output = _break_exp(exp)
            self.assertEqual(expect, output)

    def test_parse_inst_line(self):
        block = '0005b299: RBP := pad:64[low:32[RBP] ^ 0x8FB392AA]'
        parser = BapIrBlockParser()
        parser.parser(block)
        print(parser.ast)

    def test_parse_block(self):
        block = '''
0005af1f: RSI := pad:64[low:32[RDX]]
0005af28: RSI := pad:64[~low:32[RSI]]
0005af37: RSI := pad:64[low:32[RSI] & 0x5312623B]
0005af5e: RDX := pad:64[low:32[RDX] & 0xACED9DC4]
0005af85: RDX := pad:64[low:32[RDX] | low:32[RSI]]
0005afa6: RSI := pad:64[low:32[RDX]]
0005afb5: RSI := pad:64[low:32[RSI] ^ 0x1DC0]
0005afdc: RSI := pad:64[low:32[RSI] & 0x3FC0]
0005b003: RDX := pad:64[low:32[RDX] ^ 0xACEDA204]
0005b02a: RDX := pad:64[low:32[RDX] | low:32[RSI]]
'''
        parser = BapIrBlockParser()
        parser.parser(block)
        print(parser.ast)

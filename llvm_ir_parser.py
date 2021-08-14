import io
import re
import unittest
from locale import getpreferredencoding

import matplotlib.pyplot
import matplotlib.pyplot as plt
import matplotlib.image as pimg

import networkx as nx
from networkx.drawing.nx_pydot import to_pydot, unicode
from networkx.utils import make_str


def parse_inst_line(line):
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


class BlockParser:
    def __init__(self):
        self.ast = nx.DiGraph()
        self.id_base = 0

    def block_parser(self, ir_block: str):
        for inst_line in ir_block.split(sep='\n'):
            inst_line = inst_line.strip()
            if len(inst_line) == 0:
                continue
            self.__handle_inst_line(inst_line)
            pass
        pass

    def paint(self, **kwargs):
        q = nx.nx_pydot.to_pydot(self.ast)
        view_dot(q.create_png())

    def __handle_inst_line(self, line):
        (var, op, typ, opr_list) = parse_inst_line(line)

        op = f'"{op}#{self.__id():02}"'

        var = self.__get_or_insert_var(var, typ)
        self.ast.add_node(op, typ=typ, color='red')
        self.ast.add_edge(var, op)

        for opr in opr_list:
            opr = self.__get_or_insert_var(opr, typ)
            self.ast.add_edge(op, opr)

    def __id(self):
        self.id_base += 1
        return self.id_base

    def __get_or_insert_var(self, var, typ):
        if var.startswith('%'):
            var = f'"${var[1:]}"'
            self.ast.add_node(f'{var}', typ=typ)
        else:
            val = var
            var = f'"{val}#{self.__id()}"'
            self.ast.add_node(f'{var}', typ=typ, val=val)
        return var


class Test(unittest.TestCase):
    def test_parse_inst_line(self):
        line = '%1898 = and i32 0x2E2882F, %1897'
        expect = ('%1898', 'and', 'i32', ['0x2E2882F', '%1897'])
        output = parse_inst_line(line)
        self.assertTrue(expect == output,
                        f'output ({output}) does not equal to '
                        f'expect ({expect})')

    def test_print_graph(self):
        block = '''
%shl1.i90 = shl i32 %reg, 0x6, !dbg !807
%shl2.i92 = shl i32 %1877, 0x17, !dbg !807
%1878 = xor i32 %shl2.i92, 0xFFFFFFFF
%1879 = and i32 0x2E2882F, %1878
%1880 = xor i32 0x2E2882F, 0xFFFFFFFF
%1881 = and i32 %shl2.i92, %1880
%1882 = xor i32 0xFFFFFFFF, 0xFFFFFFFF
%1883 = and i32 %1882, 0x2E2882F
%1884 = and i32 0xFFFFFFFF, %1880
%1885 = or i32 %1879, %1881
%1886 = or i32 %1883, %1884
%1887 = xor i32 %1885, %1886
%1888 = xor i32 %shl2.i92, 0xFFFFFFFF
%1889 = xor i32 %shl1.i90, 0xFFFFFFFF
%1890 = and i32 0xFFFFFFFF, %1889
%1891 = xor i32 0xFFFFFFFF, 0xFFFFFFFF
%1892 = and i32 %shl1.i90, %1891
%1893 = or i32 %1890, %1892
%1894 = xor i32 %shl1.i90, 0xFFFFFFFF
%1895 = xor i32 0x2E2882F, 0xFFFFFFFF
%1896 = and i32 0x41F9C030, %1895
%1897 = xor i32 0x41F9C030, 0xFFFFFFFF
%1898 = and i32 0x2E2882F, %1897
%1899 = xor i32 0xFFFFFFFF, 0xFFFFFFFF
%1900 = and i32 %1899, 0x41F9C030
%1901 = and i32 0xFFFFFFFF, %1897
'''
        parser = BlockParser()
        parser.block_parser(block)
        parser.paint(node_shape='s', font_family='monaco')


def view_dot(p):
    sio = io.BytesIO()
    sio.write(p)
    sio.seek(0)
    img = pimg.imread(sio)

    with open('plot.png', 'wb+') as f:
        f.write(p)

    plt.figure(figsize=(50, 10), dpi=200)
    plt.imshow(img)
    plt.show()

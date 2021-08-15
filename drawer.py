import io
import unittest

import pydot
from matplotlib import image as pimg, pyplot as plt

from llvm_ir_parser import BlockParser


class ASTDrawer:
    def __init__(self, g, font_name='"Fira Code"'):
        self.g: pydot.Dot = g

        self.font_name = font_name
        self.style_map = {
            'v': self.__style_var_node,
            'c': self.__style_const_node,
            'ce': self.__style_constexpr_node,
            'op': self.__style_op_node,
            '?': self.__style_default_node
        }

    def draw(self, save_file='', fmt='png'):
        self.__adjust_style()
        p = self.g.create(format=fmt)

        sio = io.BytesIO()
        sio.write(p)
        sio.seek(0)
        img = pimg.imread(sio)

        if save_file:
            with open(f'{save_file}.{fmt}', 'wb+') as f:
                f.write(p)

        plt.figure(figsize=(24, 24), dpi=200)
        plt.imshow(img)
        plt.show()

    def __adjust_style(self):
        for n in self.g.get_node_list():
            t = ASTDrawer.__node_type(n)
            # noinspection PyArgumentList
            self.style_map[t](n)
        return

    def __style_op_node(self, node: pydot.Node):
        node.set('fontname', self.font_name)
        node.set('shape', 'circle')
        node.set('color', 'red')

    def __style_var_node(self, node: pydot.Node):
        node.set('fontname', self.font_name)

    def __style_const_node(self, node: pydot.Node):
        node.set('fontname', self.font_name)
        node.set('shape', 'box')
        node.set('color', 'blue')

    def __style_constexpr_node(self, node: pydot.Node):
        node.set('fontname', self.font_name)
        node.set('color', 'blue')

    def __style_default_node(self, node: pydot.Node):
        node.set('fontname', self.font_name)

    @staticmethod
    def __node_type(node: pydot.Node):
        ntyp = node.get('ntyp')
        return ntyp if ntyp else 'default'


class Test(unittest.TestCase):
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

        drawer = ASTDrawer(parser.ast)
        drawer.draw()

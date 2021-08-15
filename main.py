import fire

from drawer import ASTDrawer
from llvm_ir_parser import BlockParser


def paint(ir_file='sample.bc'):
    with open(ir_file, 'r') as f:
        block = f.read()

    parser = BlockParser()
    parser.block_parser(block)

    drawer = ASTDrawer(parser.ast)
    drawer.draw(save_file='plot')


if __name__ == '__main__':
    fire.Fire(paint)

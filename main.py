import os
import fire

from analysis.analysis_manager import AnalysisManager
from analysis.clean_drop_off import CleanDropOff
from analysis.fold_constant import FoldConstant
from analysis.mark_entries import MarkEntries
from analysis.prune_branches import PruneBranches
from analysis.simplify import Simplify
from bap_ir_parser import BapIrBlockParser
from drawer import ASTDrawer
from llvm_ir_parser import LlvmIrBlockParser


def parser_factory(ir_file):
    _, ext = os.path.splitext(ir_file)
    return {
        '.bc': LlvmIrBlockParser(),
        '.bir': BapIrBlockParser()
    }[ext]


def paint(ir_file='sample.bc', tag='ana-new'):
    tag = f'-{tag}' if tag else tag
    with open(ir_file, 'r') as f:
        block = f.read()

    parser = parser_factory(ir_file)
    parser.parser(block)

    ast = AnalysisManager([
        FoldConstant(),
        CleanDropOff(),
        MarkEntries(fill_color='black'),
        PruneBranches(),
        Simplify()
    ])(parser.ast)

    drawer = ASTDrawer(ast)
    drawer.draw(save_file=f'{ir_file}{tag}')


if __name__ == '__main__':
    fire.Fire(paint)

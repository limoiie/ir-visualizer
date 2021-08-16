import fire

from analysis.analysis_manager import AnalysisManager
from analysis.clean_drop_off import CleanDropOff
from analysis.fold_constant import FoldConstant
from analysis.mark_entries import MarkEntries
from analysis.prune_branches import PruneBranches
from drawer import ASTDrawer
from llvm_ir_parser import BlockParser


def paint(ir_file='sample.bc'):
    with open(ir_file, 'r') as f:
        block = f.read()

    parser = BlockParser()
    parser.block_parser(block)

    ast = AnalysisManager([
        FoldConstant(),
        CleanDropOff(),
        MarkEntries(fill_color='black'),
        PruneBranches()
    ])(parser.ast)

    drawer = ASTDrawer(ast)
    drawer.draw(save_file='plot')


if __name__ == '__main__':
    fire.Fire(paint)

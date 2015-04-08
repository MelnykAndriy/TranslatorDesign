__author__ = 'mandriy'

import argparse
import sys
from code_gen.semantic_checker import SemanticChecker
from code_gen.generator import SignalAsmGenerator
from signal_parser.parser import SignalParser
from signal_parser.term import term_to_dot
from utils.errors import dump_errors
from utils.common_utils import gen_asm_filename
from sys import stderr

args_parser = argparse.ArgumentParser(
    version='1.0',
    add_help=True,
    prog='signalc',
    epilog='Made by Andriy Melnyk.'
)

args_parser.add_argument('source_file',
                         metavar='source',
                         type=str,
                         help='Source file to be compiled.')

args_parser.add_argument('-o',
                         metavar='filename',
                         action='store',
                         dest='output_file',
                         help='Compiler output file.',
                         default=None)

args_parser.add_argument('-td',
                         metavar='dot filename',
                         action='store',
                         dest='tree_dot_filename',
                         default=None,
                         help='Store parser result to file in dot format.')

compiler_arguments = args_parser.parse_args(sys.argv[1:])


def say_goodbye():
    print >> stderr, 'Compilation is interrupted.'
    exit()

parser = SignalParser()
checker = SemanticChecker()
generator = SignalAsmGenerator()

term = parser.parse_file(compiler_arguments.source_file)
dump_errors(parser.errors())
if term is not None:

    if compiler_arguments.tree_dot_filename:
        term_to_dot(term).write_dot(compiler_arguments.tree_dot_filename)

    if not checker.check(term):
        dump_errors(checker.errors())
        say_goodbye()

    generated_asm_content = generator.generate(term, parser.identifiers(), parser.literals())

    if compiler_arguments.output_file is None:
        compiler_arguments.output_file = gen_asm_filename(compiler_arguments.source_file)

    with open(compiler_arguments.output_file, 'w') as output_file:
        output_file.write(generated_asm_content)

else:
    say_goodbye()




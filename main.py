__author__ = 'mandriy'

import argparse
import sys
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

args_parser.add_argument('-td',
                         metavar='dot filename',
                         action='store',
                         dest='tree',
                         default='tree',
                         help='Tree image.')

compiler_arguments = args_parser.parse_args(sys.argv[1:])


def say_goodbye():
    print >> stderr, 'Compilation is interrupted.'
    exit()

parser = SignalParser()

term = parser.parse_file(compiler_arguments.source_file)
dump_errors(parser.errors())
if term is not None:

    term_to_dot(term).write_jpg(compiler_arguments.tree + '.jpg')

else:
    say_goodbye()




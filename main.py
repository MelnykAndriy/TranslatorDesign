__author__ = 'mandriy'

import argparse
import sys

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

args_parser.add_argument('-ld',
                         action='store_true',
                         dest='is_lexer_dump_needed',
                         help='Display lexer result.')

args_parser.add_argument('-td',
                         metavar='dot filename',
                         action='store',
                         dest='tree_dot_filename',
                         default=None,
                         help='Store parser result to file in dot format.')

compiler_arguments = args_parser.parse_args(sys.argv[1:])
print compiler_arguments

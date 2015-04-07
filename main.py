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
#
#
# from signal_parser.parser import SignalParser
# from signal_parser.term import *
#
# parser = SignalParser()
# term = parser.parse(',1,2', 'labels-list')
# program = parser.parse('PROGRAM p1; LABEL 1,2; BEGIN IN 1; END.')
# res = term._root.match(',', 'unsigned-integer', ',', 'unsigned-integer')
# res = term._root.match(',', 'unsigned-integer', ',', 'unsigned-integer', 'labels-list')
#
# def print_res():
#     for i in xrange(len(res)):
#         if isinstance(res[i], LeafNode):
#             print res[i].get_label()
#         else:
#             term_to_dot(Term(res[i])).write_svg('test%d.svg' % i)
#
#
#
# term._root.match('LABEL', 'unsigned-integer', 'labels-list', ';')
# res = program._root.match('PROGRAM', 'identifier', ';', 'declarations', 'BEGIN', 'statements-list' ,'END' ,'.')
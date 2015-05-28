__author__ = 'mandriy'

from StringIO import StringIO
from signal_parser.rules import Rule, TreePattern
from generator_utils import *


class SignalAsmGenerator(object):

    def __init__(self, instruction_indent=4):
        self._instruction_indent = instruction_indent
        self._labels_table = None
        self._identifiers = None
        self._literals = None
        self._asm = None

    def generate(self, term, idents, literals):
        self._labels_table = {}
        self._identifiers = idents
        self._literals = literals
        self._asm = StringIO()

        term.sort_traversal(
            down_match_dict={'constant-declarations': lambda x: self._gen_constants(collect_constants(x))}
        )

        term.foreach(
            pre_rules=(
                Rule(TreePattern(pattern=('PROGRAM', 'identifier', ';', 'block', '.'), parent='program'),
                     lambda matched_program:
                     self._asm.write(self._gen_program_header(get_identifier_leaf_token(matched_program[1]).label()))),
                Rule(TreePattern(pattern=('statements-list',), parent='statements-list'),
                     lambda stmts_list: self._asm.write(self._gen_emty_stmt_list_nop(stmts_list[0])))
            ),
            post_rules=(
                Rule(TreePattern(pattern=('PROGRAM', 'identifier', ';', 'block', '.'), parent='program'),
                     lambda matched_program:
                     self._asm.write(self._gen_program_footer(get_identifier_leaf_token(matched_program[1]).label()))),
            )
        )

        self._asm.flush()
        return self._asm.getvalue()

    def _create_labels_names(self, labels):
        for label in labels:
            asm_label_name = generate_random_string(6) + label.label()
            while self._identifiers.contain_item(asm_label_name):
                asm_label_name = generate_random_string(6) + label.label()
            self._labels_table[label.code()] = asm_label_name

    def _gen_constants(self, constants):
        self._asm.write('_DATA SEGMENT\n')
        for identifier, constant_init in constants.items():
            init_value = evaluate_constant(constant_init)
            self._asm.write('%s%s %s %s\n' % (gen_indent(self._instruction_indent), identifier, constant_type(init_value),
                                            init_value))
        self._asm.write('_DATA ENDS\n')


    @staticmethod
    def _gen_program_header(proc_name):
        return '%s PROC\n' % proc_name

    def _gen_emty_stmt_list_nop(self, stmt_list):
        if is_empty_stmt_list(stmt_list):
            return '%sNOP\n' % gen_indent(self._instruction_indent)
        else:
            return ''

    def _gen_program_footer(self, proc_name):
        return '%sRET\n%s ENDP\n' % (gen_indent(self._instruction_indent), proc_name)

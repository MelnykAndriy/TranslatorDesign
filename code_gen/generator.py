__author__ = 'mandriy'

from StringIO import StringIO
from signal_parser.rules import Rule, TreePattern
from generator_utils import *


class SignalAsmGenerator(object):

    def __init__(self, instruction_indent=4, labels_indent=2):
        self._instruction_indent = instruction_indent
        self._labels_indent = labels_indent
        self._labels_table = None
        self._identifiers = None
        self._literals = None

    def generate(self, term, idents, literals):
        self._labels_table = {}
        self._identifiers = idents
        self._literals = literals
        asm = StringIO()
        term.foreach(
            pre_rules=(
                Rule(TreePattern(pattern=('label-declarations',), parent='declarations'),
                     lambda decl: self._create_labels_names(collect_declared_labels(decl))),
                Rule(TreePattern(pattern=('PROGRAM', 'identifier', ';', 'block', '.'), parent='program'),
                     lambda matched_program:
                     asm.write(self._gen_program_header(get_identifier_leaf_token(matched_program[1]).label()))),
                Rule(TreePattern(pattern=('unsigned-integer', ':', 'statement'), parent='statement'),
                     lambda labeled_stmt: asm.write(
                         self._gen_label(
                             self._labels_table[get_unsigned_integer_leaf_token(labeled_stmt[0]).code()]))),
                Rule(TreePattern(pattern=('GOTO', 'unsigned-integer', ';'), parent='statement'),
                     lambda goto_stmt: asm.write(
                         self._gen_goto(self._labels_table[get_unsigned_integer_leaf_token(goto_stmt[1]).code()]))),
                Rule(TreePattern(pattern=('statements-list',), parent='statements-list'),
                     lambda stmts_list: asm.write(self._gen_emty_stmt_list_nop(stmts_list[0])))
            ),
            post_rules=(
                Rule(TreePattern(pattern=('PROGRAM', 'identifier', ';', 'block', '.'), parent='program'),
                     lambda matched_program:
                     asm.write(self._gen_program_footer(get_identifier_leaf_token(matched_program[1]).label()))),
            )
        )

        asm.flush()
        return asm.getvalue()

    def _create_labels_names(self, labels):
        for label in labels:
            asm_label_name = generate_random_string(6) + label.label()
            while self._identifiers.contain_item(asm_label_name):
                asm_label_name = generate_random_string(6) + label.label()
            self._labels_table[label.code()] = asm_label_name

    def _gen_goto(self, label_name):
        return '%sJMP %s\n' % (gen_indent(self._instruction_indent), label_name)

    def _gen_label(self, label_name):
        return '%s%s:\n' % (gen_indent(self._labels_indent), label_name)

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

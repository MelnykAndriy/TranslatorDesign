__author__ = 'mandriy'

from errors import *
from generator_utils import *
from signal_parser.rules import Rule, TreePattern


class SemanticChecker(object):

    def __init__(self):
        self._semantic_errors = None

    def errors(self):
        return self._semantic_errors

    def check(self, term):
        self._semantic_errors = []
        self.check_duplicated_constants(term)
        return not self._semantic_errors

    def check_duplicated_constants(self, term):
        error_before_check = len(self._semantic_errors)
        constants_stack = []
        program_code = []

        def _constants_check(constant_declaration):
            identifier = get_identifier_leaf_token(constant_declaration[0])
            if identifier.code() == program_code[0]:
                self._semantic_errors.append(CollisionWithProgramName(identifier.position()))
            else:
                if identifier.code() in constants_stack:
                    self._semantic_errors.append(DuplicateConstantName(identifier.position()))
                else:
                    constants_stack.append(identifier.code())

        def _save_program_code(program):
            program_code.append(get_identifier_leaf_token(program[1]).code())

        term.foreach(
            pre_rules=(
                Rule(TreePattern(pattern=('identifier', '=', 'constant', ';'), parent='constant-declaration'),
                     _constants_check),
                Rule(TreePattern(pattern=('PROGRAM', 'identifier', ';', 'block', '.'),
                                 parent='program'),
                     _save_program_code)
            )
        )

        return error_before_check == len(self._semantic_errors)

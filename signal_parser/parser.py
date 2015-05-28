__author__ = 'mandriy'

from parser_utils import TokensIterator
import lexer.keywords as kw
import lexer.delimiters as dm
import lexer.lexer_utils as lu
from lexer.lexer import SignalLexicalAnalysis
from functools import partial
from errors import *
from term import StandardTreeBuilder


class UnknownSort(Exception):
    pass


class SignalParser(object):

    def __init__(self):
        self._tree_builder = None
        self._tokens = None
        self._errors_stack = None
        self._positions_stack = None
        self._lexer = None

    def errors(self):
        return self._errors_stack

    def identifiers(self):
        return self._lexer.identifiers()

    def literals(self):
        return self._lexer.constants()

    def parse_file(self, filename, tree_builder=StandardTreeBuilder):
        with open(filename, "r") as source_file:
            return self.parse(source_file.read(), tree_builder=tree_builder)

    def parse(self, source_text, sort='signal-program', tree_builder=StandardTreeBuilder):
        self._lexer = SignalLexicalAnalysis()
        self._tokens = TokensIterator(self._lexer(source_text))
        self._errors_stack = [] + self._lexer.errors()
        self._positions_stack = []
        self._tree_builder = tree_builder()
        tree = None
        if sort not in SignalParser.productions:
            raise UnknownSort('Sort %s is unknown.' % sort)
        sort_production = SignalParser.productions[sort]
        if sort_production(self, self._tree_builder.build_tree()):
            tree = self._tree_builder.get_tree()
        if not self._tokens.only_terminate_token_left() and not self._errors_stack:
            self._errors_stack.append(ExtraTokens(self._tokens.next_token().position()))
        return tree

    def _signal_program(self, prev_node):
        return self._unique_by_and_production('signal-program',
                                              prev_node,
                                              self._program)

    def _program(self, prev_node):
        return self._unique_by_and_production(
            'program',
            prev_node,
            ErrorCase(self._leaf_production(self._exact_code_leaf(kw.PROGRAM)),
                      StandardErrorHandler(make_error_case(ExpectedToken, 'PROGRAM keyword'))),
            ErrorCase(self._procedure_identifier, StandardErrorHandler(make_error_case(MissedToken, 'Program name'))),
            ErrorCase(self._leaf_production(self._exact_code_leaf(dm.SEMICOLON)),
                      StandardErrorHandler(make_error_case(MissedToken, 'Semicolon'))),
            self._block,
            ErrorCase(self._leaf_production(self._exact_code_leaf(dm.DOT)),
                      StandardErrorHandler(make_error_case(MissedToken, 'Dot'))))

    def _procedure_identifier(self, prev_node):
        return self._unique_by_and_production('procedure-identifier',
                                              prev_node,
                                              self._identifier)

    def _block(self, prev_node):
        return self._unique_by_and_production(
            'block',
            prev_node,
            self._declarations,
            ErrorCase(self._leaf_production(self._exact_code_leaf(kw.BEGIN)),
                      StandardErrorHandler(make_error_case(ExpectedToken, 'BEGIN keyword'))),
            self._statements_list,
            ErrorCase(self._leaf_production(self._exact_code_leaf(kw.END)),
                      StandardErrorHandler(make_error_case(ExpectedToken, 'END keyword')))
        )

    def _declarations(self, prev_node):
        return self._unique_by_and_production('declarations',
                                              prev_node,
                                              self._constant_declarations)

    def _constant_declarations(self, prev_node):
        return self._unique_by_or(
            'constant-declarations',
            prev_node,
            self._create_raw_and(self._leaf_production(self._exact_code_leaf(kw.CONST)),
                                 self._constant_declarations_list),
            self._empty_leaf)

    def _constant_declarations_list(self, prev_node):
        return self._unique_by_or(
            'constants-declarations-list',
            prev_node,
            self._create_raw_and(self._constant_declaration,
                                 self._constant_declarations_list),
            self._empty_leaf
        )

    def _constant_declaration(self, prev_node):
        return self._unique_by_and_production(
            'constant-declaration',
            prev_node,
            self._constant_identifier,
            ErrorCase(self._leaf_production(self._exact_code_leaf(dm.EQUAL)),
                      StandardErrorHandler(make_error_case(ExpectedToken, '='))),
            ErrorCase(self._constant, StandardErrorHandler(make_error_case(MissedToken, 'Constant value'))),
            ErrorCase(self._leaf_production(self._exact_code_leaf(dm.SEMICOLON)),
                      StandardErrorHandler(make_error_case(MissedToken, 'Semicolon')))
        )

    def _constant(self, prev_node):
        return self._unique_by_and_production(
            'constant',
            prev_node,
            self._sign,
            self._unsigned_constant
        )

    def _sign(self, prev_node):
        return self._unique_by_or(
            'sign',
            prev_node,
            self._leaf_production(self._exact_code_leaf(dm.MINUS)),
            self._leaf_production(self._exact_code_leaf(dm.PLUS)),
            self._empty_leaf
        )

    def _unsigned_constant(self, prev_node):
        return self._unique_by_and_production(
            'unsigned-constant',
            prev_node,
            self._integer_part,
            self._fractional_part
        )

    def _integer_part(self, prev_node):
        return self._unique_by_and_production(
            'integer-part',
            prev_node,
            self._unsigned_integer
        )

    def _fractional_part(self, prev_node):
        return self._unique_by_or(
            'fractional-part',
            prev_node,
            self._create_raw_and(
                self._leaf_production(self._exact_code_leaf(dm.SHARP)),
                self._sign,
                ErrorCase(self._unsigned_integer,
                          StandardErrorHandler(make_error_case(ExpectedToken, 'Number')))
            ),
            self._empty_leaf
        )

    def _statements_list(self, prev_node):
        return self._unique_by_or('statements-list',
                                  prev_node,
                                  self._empty_leaf)

    def _constant_identifier(self, prev_node):
        return self._unique_by_and_production('constant-identifier',
                                              prev_node,
                                              self._identifier)

    def _identifier(self, prev_node):
        return self._unique_by_and_production('identifier',
                                              prev_node,
                                              self._leaf_production(lu.is_identifier_code))

    def _unsigned_integer(self, prev_node):
        return self._unique_by_and_production('unsigned-integer',
                                              prev_node,
                                              self._leaf_production(lu.is_constant_code))

    def _with_error(self, handle_case, *args):
        try:
            handle_case_result = handle_case(*args)
            if not handle_case_result:
                self._positions_stack.append(self._tokens.current_token().position())
            else:
                self._positions_stack = []
            return handle_case_result
        except SyntaxErrorFound, e:
            self._positions_stack.append(self._tokens.current_token().position())
            self._errors_stack.append(e.make_error_report(self._positions_stack[0]))
            self._positions_stack = []

    def _with_checkpoint(self, func, *args):
        self._tokens.save_checkpoint()
        func_result = self._with_error(func, *args)
        if func_result:
            self._tokens.confirm_last_checkpoint()
        else:
            self._tokens.back_to_last_checkpoint()
        return func_result

    def _unique_by_and_production(self, production, prev_node, *handle_cases):
        node = self._tree_builder.build_interior_node(production)
        if self._raw_unique_by_and(node, *handle_cases):
            self._tree_builder.build_dependency(prev_node, node)
            return True
        return False

    def _raw_unique_by_and(self, prev_node, *handle_cases):
        successfully = self._with_checkpoint(reduce,
                                             lambda res, handle_case: res and self._with_checkpoint(handle_case,
                                                                                                    prev_node),
                                             handle_cases,
                                             True)
        return successfully

    def _create_raw_and(self, *handle_cases):
        def raw_and(prev_node):
            return self._raw_unique_by_and(prev_node, *handle_cases)
        return raw_and

    def _leaf_production(self, leaf_p):
        return partial(self._leaf_node, leaf_p)

    def _leaf_node(self, leaf_p, prev_node):
        token = self._tokens.next_token()
        if leaf_p(token.code()):
            self._tree_builder.build_leaf_node(prev_node, token)
            return True
        return False

    def _empty_leaf(self, prev_node):
        self._tree_builder.build_empty_node(prev_node)
        return True
    
    @staticmethod
    def _exact_code_leaf(code):
        return lambda token_code: code == token_code

    def _unique_by_or(self, production, prev_node, *handle_cases):
        nodes = []
        
        def try_parse(handle_case):
            nodes.append(self._tree_builder.build_interior_node(production))
            return self._with_checkpoint(handle_case, nodes[len(nodes) - 1])

        successfully = self._with_checkpoint(reduce,
                                             lambda res, handle_case: res or try_parse(handle_case),
                                             handle_cases,
                                             False)
        if successfully:
            self._tree_builder.build_dependency(prev_node, nodes.pop())
            return True
        return False

    productions = {'signal-program': _signal_program,
                   'program': _program,
                   'procedure-identifier': _procedure_identifier,
                   'block': _block,
                   'declarations': _declarations,
                   'constant-declarations': _constant_declarations,
                   'constant-declarations-list': _constant_declarations_list,
                   'constant-declaration': _constant_declaration,
                   'constant': _constant,
                   'sign': _sign,
                   'unsigned-constant': _unsigned_constant,
                   'integer-part': _integer_part,
                   'fractional-part': _fractional_part,
                   'constant-identifier': _constant_identifier,
                   'statements-list': _statements_list,
                   'identifier': _identifier,
                   'unsigned-integer': _unsigned_integer}
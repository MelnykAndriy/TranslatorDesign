__author__ = 'mandriy'

from parser_utils import TokensIterator, TokensExhausted
from term import *
import lexer.keywords as kw
import lexer.delimiters as dm
import lexer.lexer_utils as lu
from lexer.lexer import SignalLexicalAnalysis
from functools import partial
from errors import *


class UnknownSort(Exception):
    pass


class SignalParser(object):

    def __init__(self):
        self._tokens = None
        self._term = None
        self._errors_stack = None
        self._positions_stack = None
        self._lexer = None

    def errors(self):
        return self._errors_stack

    def identifiers(self):
        return self._lexer.identifiers()

    def literals(self):
        return self._lexer.constants()

    def parse_file(self, filename):
        with open(filename, "r") as source_file:
            return self.parse(source_file.read())

    def parse(self, source_text, sort='signal-program'):
        self._lexer = SignalLexicalAnalysis()
        self._tokens = TokensIterator(self._lexer(source_text))
        self._errors_stack = [] + self._lexer.errors()
        self._positions_stack = []
        if sort not in SignalParser.productions:
            raise UnknownSort('Sort %s is unknown.' % sort)
        sort_production = SignalParser.productions[sort]
        imagine_root = InteriorNode('')
        if sort_production(self, imagine_root):
            self._term = Term(imagine_root.get_child_by_sort(sort))
        if not self._tokens.only_terminate_token_left() and not self._errors_stack:
            self._errors_stack.append(ExtraTokens(self._tokens.next_token().position()))
        return self._term

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
                                              self._label_declarations)

    def _statement(self, prev_node):
        return self._unique_by_or(
            'statement',
            prev_node,
            self._create_raw_and(
                self._unsigned_integer,
                ErrorCase(self._leaf_production(self._exact_code_leaf(dm.COLON)),
                          StandardErrorHandler(make_error_case(MissedToken, 'Colon'))),
                ErrorCase(self._statement,
                          StandardErrorHandler(make_error_case(EmptyLabeledStatement)))
            ),
            self._create_raw_and(
                self._leaf_production(self._exact_code_leaf(kw.GOTO)),
                ErrorCase(self._unsigned_integer, StandardErrorHandler(make_error_case(GotoStatementArgument))),
                ErrorCase(self._leaf_production(self._exact_code_leaf(dm.SEMICOLON)),
                          StandardErrorHandler(make_error_case(MissedToken, 'Goto statement semicolon')))
            ),
            self._create_raw_and(
                self._leaf_production(self._exact_code_leaf(kw.IN)),
                ErrorCase(self._unsigned_integer, StandardErrorHandler(make_error_case(InStatementArgument))),
                ErrorCase(self._leaf_production(self._exact_code_leaf(dm.SEMICOLON)),
                          StandardErrorHandler(make_error_case(MissedToken, 'In statement semicolon')))
            ),
            self._create_raw_and(
                self._leaf_production(self._exact_code_leaf(kw.OUT)),
                ErrorCase(self._unsigned_integer, StandardErrorHandler(make_error_case(OutStatementArgument))),
                ErrorCase(self._leaf_production(self._exact_code_leaf(dm.SEMICOLON)),
                          StandardErrorHandler(make_error_case(MissedToken, 'Out statement semicolon')))
            ),
            self._create_raw_and(
                self._leaf_production(self._exact_code_leaf(kw.LINK)),
                ErrorCase(self._variable_identifier, StandardErrorHandler(make_error_case(LinkStatementArguments))),
                ErrorCase(self._leaf_production(self._exact_code_leaf(dm.COMMA)),
                          StandardErrorHandler(make_error_case(MissedToken, 'Coma'))),
                ErrorCase(self._unsigned_integer, StandardErrorHandler(make_error_case(LinkStatementArguments))),
                ErrorCase(self._leaf_production(self._exact_code_leaf(dm.SEMICOLON)),
                          StandardErrorHandler(make_error_case(MissedToken, 'Link statement semicolon')))
            )
        )

    def _statements_list(self, prev_node):
        return self._unique_by_or('statements-list',
                                  prev_node,
                                  self._create_raw_and(self._statement,
                                                       self._statements_list),
                                  self._empty_leaf)

    def _label_declarations(self, prev_node):
        return self._unique_by_or(
            'label-declarations',
            prev_node,
            self._create_raw_and(
                self._leaf_production(self._exact_code_leaf(kw.LABEL)),
                ErrorCase(self._unsigned_integer, StandardErrorHandler(make_error_case(InvalidLabelDefinition))),
                self._labels_list,
                ErrorCase(self._leaf_production(self._exact_code_leaf(dm.SEMICOLON)),
                          StandardErrorHandler(make_error_case(MissedToken, 'Semicolon')))
            ),
            self._empty_leaf)

    def _labels_list(self, prev_node):
        return self._unique_by_or(
            'labels-list',
            prev_node,
            self._create_raw_and(
                self._leaf_production(self._exact_code_leaf(dm.COMMA)),
                ErrorCase(self._unsigned_integer, StandardErrorHandler(make_error_case(InvalidLabelDefinition))),
                self._labels_list
            ),
            self._empty_leaf
        )

    def _variable_identifier(self, prev_node):
        return self._unique_by_and_production('variable-identifier',
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
        node = InteriorNode(production)
        if self._raw_unique_by_and(node, *handle_cases):
            prev_node.add_child(node)
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
            prev_node.add_child(LeafNode(token))
            return True
        return False

    @staticmethod
    def _empty_leaf(prev_node):
        prev_node.add_child(EmptyNode())
        return True
    
    @staticmethod
    def _exact_code_leaf(code):
        return lambda token_code: code == token_code

    def _unique_by_or(self, production, prev_node, *handle_cases):
        nodes = []
        
        def try_parse(handle_case):
            nodes.append(InteriorNode(production))
            return self._with_checkpoint(handle_case, nodes[len(nodes) - 1])

        successfully = self._with_checkpoint(reduce,
                                             lambda res, handle_case: res or try_parse(handle_case),
                                             handle_cases,
                                             False)
        if successfully:
            prev_node.add_child(nodes.pop())
            return True
        return False

    productions = {'signal-program': _signal_program,
                   'program': _program,
                   'procedure-identifier': _procedure_identifier,
                   'block': _block,
                   'declarations': _declarations,
                   'statement': _statement,
                   'statements-list': _statements_list,
                   'label-declarations': _label_declarations,
                   'labels-list': _labels_list,
                   'variable-identifier': _variable_identifier,
                   'identifier': _identifier,
                   'unsigned-integer': _unsigned_integer}
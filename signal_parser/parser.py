__author__ = 'mandriy'

from parser_utils import TokensIterator, TokensExhausted
from term import *
import lexer.keywords as kw
import lexer.delimiters as dm
import lexer.lexer_utils as lu
from lexer.lexer import SignalLexicalAnalysis
from functools import partial


class UnknownSort(Exception):
    pass


class SignalParser(object):

    def __init__(self):
        self._tokens = None
        self._idents_table = None
        self._constants_table = None
        self._term = None

    def parse_file(self, filename):
        with open(filename, "r") as source_file:
            return self.parse(source_file.read())

    def parse(self, source_text, sort='signal-program'):
        lexer = SignalLexicalAnalysis()
        self._tokens = TokensIterator(lexer(source_text))
        self._idents_table = lexer.identifiers()
        self._constants_table = lexer.constants()
        if sort not in SignalParser.productions:
            raise UnknownSort('Sort %s is unknown.' % sort)
        sort_production = SignalParser.productions[sort]
        imagine_root = InteriorNode('')
        if sort_production(self, imagine_root):
            self._term = Term(imagine_root.get_child_by_sort(sort))
            # TODO seems everything is alright
        else:
            pass  # TODO find error reason in stack
        if not self._tokens.only_terminate_token_left():
            raise Exception('something wrong')
            pass  # TODO report an error
        return self._term

    def _signal_program(self, prev_node):
        return self._unique_by_and_production('signal-program',
                                              prev_node,
                                              self._program)

    def _program(self, prev_node):
        return self._unique_by_and_production('program',
                                              prev_node,
                                              self._leaf_production(self._exact_code_leaf(kw.PROGRAM)),
                                              self._procedure_identifier,
                                              self._leaf_production(self._exact_code_leaf(dm.SEMICOLON)),
                                              self._block,
                                              self._leaf_production(self._exact_code_leaf(dm.DOT)))

    def _procedure_identifier(self, prev_node):
        return self._unique_by_and_production('procedure-identifier',
                                              prev_node,
                                              self._identifier)

    def _block(self, prev_node):
        return self._unique_by_and_production('block',
                                              prev_node,
                                              self._declarations,
                                              self._leaf_production(self._exact_code_leaf(kw.BEGIN)),
                                              self._statements_list,
                                              self._leaf_production(self._exact_code_leaf(kw.END)))

    def _declarations(self, prev_node):
        return self._unique_by_and_production('declarations',
                                              prev_node,
                                              self._label_declarations)

    def _statement(self, prev_node):
        return self._unique_by_or(
            'statement',
            prev_node,
            self._create_raw_and(self._unsigned_integer,
                                 self._leaf_production(self._exact_code_leaf(dm.COLON)),
                                 self._statement),
            self._create_raw_and(self._leaf_production(self._exact_code_leaf(kw.GOTO)),
                                 self._unsigned_integer,
                                 self._leaf_production(self._exact_code_leaf(dm.SEMICOLON))),
            self._create_raw_and(self._leaf_production(self._exact_code_leaf(kw.IN)),
                                 self._unsigned_integer,
                                 self._leaf_production(self._exact_code_leaf(dm.SEMICOLON))),
            self._create_raw_and(self._leaf_production(self._exact_code_leaf(kw.OUT)),
                                 self._unsigned_integer,
                                 self._leaf_production(self._exact_code_leaf(dm.SEMICOLON))),
            self._create_raw_and(self._leaf_production(self._exact_code_leaf(kw.LINK)),
                                 self._variable_identifier,
                                 self._leaf_production(self._exact_code_leaf(dm.COMMA)),
                                 self._unsigned_integer,
                                 self._leaf_production(self._exact_code_leaf(dm.SEMICOLON)))
        )

    def _statements_list(self, prev_node):
        return self._unique_by_or('statements-list',
                                  prev_node,
                                  self._create_raw_and(self._statement,
                                                       self._statements_list),
                                  self._empty_leaf)

    def _label_declarations(self, prev_node):
        return self._unique_by_or('label-declarations',
                                  prev_node,
                                  self._create_raw_and(self._leaf_production(self._exact_code_leaf(kw.LABEL)),
                                                       self._unsigned_integer,
                                                       self._labels_list,
                                                       self._leaf_production(self._exact_code_leaf(dm.SEMICOLON))),
                                  self._empty_leaf)

    def _labels_list(self, prev_node):
        return self._unique_by_or('labels-list',
                                  prev_node,
                                  self._create_raw_and(self._leaf_production(self._exact_code_leaf(dm.COMMA)),
                                                       self._unsigned_integer,
                                                       self._labels_list),
                                  self._empty_leaf)

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

    def _with_checkpoint(self, func, *args):
        self._tokens.save_checkpoint()
        func_result = func(*args)
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
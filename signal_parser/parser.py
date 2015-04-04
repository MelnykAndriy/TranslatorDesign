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


def _exact_code_leaf(code):
    return lambda token_code: code == token_code


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
        return self._unique_by_and('signal-program',
                                   prev_node,
                                   self._program)

    def _program(self, prev_node):
        return self._unique_by_and('program',
                                   prev_node,
                                   self._leaf_production(_exact_code_leaf(kw.PROGRAM)),
                                   self._procedure_identifier,
                                   self._leaf_production(_exact_code_leaf(dm.SEMICOLON)),
                                   self._block,
                                   self._leaf_production(_exact_code_leaf(dm.DOT)))

    def _procedure_identifier(self, prev_node):
        return self._unique_by_and('procedure-identifier',
                                   prev_node,
                                   self._identifier)

    def _block(self, prev_node):
        return self._unique_by_and('block',
                                   prev_node,
                                   self._declarations,
                                   self._leaf_production(_exact_code_leaf(kw.BEGIN)),
                                   self._statements_list,
                                   self._leaf_production(_exact_code_leaf(kw.END)))

    def _declarations(self, prev_node):
        return self._unique_by_and('declarations',
                                   prev_node,
                                   self._label_declarations)

    def _statement(self, prev_node):
        statement = InteriorNode('statement')
        next_production = False
        self._tokens.save_checkpoint()
        if not self._with_checkpoint(self._unsigned_integer, statement):
            next_production = True
        if not next_production and not dm.COLON == self._tokens.next_token().code():
            next_production = True
        else:
            statement.add_child(LeafNode(':'))
        if not next_production and self._with_checkpoint(self._statement, statement):
            self._tokens.confirm_last_checkpoint()
            prev_node.add_child(statement)
            return True
        else:
            self._tokens.back_to_last_checkpoint()
            statement = InteriorNode('statement')
            next_production = False
# GOTO ------------
        self._tokens.save_checkpoint()
        if kw.GOTO == self._tokens.next_token().code():
            statement.add_child(LeafNode('GOTO'))
        else:
            next_production = True
        if not next_production and not self._with_checkpoint(self._unsigned_integer, statement):
            next_production = True
        if not next_production and dm.SEMICOLON == self._tokens.next_token().code():
            self._tokens.confirm_last_checkpoint()
            statement.add_child(LeafNode(';'))
            prev_node.add_child(statement)
            return True
        else:
            self._tokens.back_to_last_checkpoint()
            statement = InteriorNode('statement')
            next_production = False
# LINK ---------------
        self._tokens.save_checkpoint()

        if kw.LINK == self._tokens.next_token().code():
            statement.add_child(LeafNode('LINK'))
        else:
            next_production = True

        if not next_production and not self._with_checkpoint(self._variable_identifier, statement):
            next_production = True

        if not next_production:
            if not dm.COMMA == self._tokens.next_token().code():
                next_production = True
            else:
                statement.add_child(LeafNode(','))

        if not next_production and not self._with_checkpoint(self._unsigned_integer, statement):
            next_production = True

        if not next_production and dm.SEMICOLON == self._tokens.next_token().code():
            self._tokens.confirm_last_checkpoint()
            statement.add_child(LeafNode(';'))
            prev_node.add_child(statement)
            return True
        else:
            self._tokens.back_to_last_checkpoint()
            statement = InteriorNode('statement')
            next_production = False
# IN --------------------
        self._tokens.save_checkpoint()

        if kw.IN == self._tokens.next_token().code():
            statement.add_child(LeafNode('IN'))
        else:
            next_production = True

        if not next_production and not self._with_checkpoint(self._unsigned_integer, statement):
            next_production = True

        if not next_production and dm.SEMICOLON == self._tokens.next_token().code():
            self._tokens.confirm_last_checkpoint()
            statement.add_child(LeafNode(';'))
            prev_node.add_child(statement)
            return True
        else:
            self._tokens.back_to_last_checkpoint()
            statement = InteriorNode('statement')
            next_production = False

# OUT -------------------
        self._tokens.save_checkpoint()

        if kw.OUT == self._tokens.next_token().code():
            statement.add_child(LeafNode('OUT'))
        else:
            next_production = True

        if not next_production and not self._with_checkpoint(self._unsigned_integer, statement):
            next_production = True

        if not next_production and dm.SEMICOLON == self._tokens.next_token().code():
            self._tokens.confirm_last_checkpoint()
            statement.add_child(LeafNode(';'))
            prev_node.add_child(statement)
            return True
        else:
            self._tokens.back_to_last_checkpoint()
            # TODO error stack push
            return False

    def _statements_list(self, prev_node):
        statements_list = InteriorNode('statements-list')
        self._tokens.save_checkpoint()
        cant_be_parsed_as_statements_list = False
        if not self._with_checkpoint(self._statement, statements_list):
            cant_be_parsed_as_statements_list = True
        if not cant_be_parsed_as_statements_list and not self._with_checkpoint(self._statements_list, statements_list):
            cant_be_parsed_as_statements_list = True
        if cant_be_parsed_as_statements_list:
            self._tokens.back_to_last_checkpoint()
            empty_statements_list = InteriorNode('statements-list')
            empty_statements_list.add_child(EmptyNode())
            prev_node.add_child(empty_statements_list)
        else:
            self._tokens.confirm_last_checkpoint()
            prev_node.add_child(statements_list)
        return True

    def _label_declarations(self, prev_node):
        self._tokens.save_checkpoint()
        label_declarations = InteriorNode('label-declarations')
        cant_be_parsed_as_labels_decl = False
        if kw.LABEL == self._tokens.next_token().code():
            label_declarations.add_child(LeafNode('LABEL'))
        else:
            cant_be_parsed_as_labels_decl = True

        if not cant_be_parsed_as_labels_decl and \
                not self._with_checkpoint(self._unsigned_integer, label_declarations):
            cant_be_parsed_as_labels_decl = True

        if not cant_be_parsed_as_labels_decl and \
                not self._with_checkpoint(self._labels_list, label_declarations):
            cant_be_parsed_as_labels_decl = True

        if not cant_be_parsed_as_labels_decl and dm.SEMICOLON == self._tokens.next_token().code():
            label_declarations.add_child(LeafNode(';'))
        else:
            cant_be_parsed_as_labels_decl = True

        if cant_be_parsed_as_labels_decl:
            self._tokens.back_to_last_checkpoint()
            empty_label_declarations = InteriorNode('label-declarations')
            empty_label_declarations.add_child(EmptyNode())
            prev_node.add_child(empty_label_declarations)
        else:
            self._tokens.confirm_last_checkpoint()
            prev_node.add_child(label_declarations)
        return True

    def _labels_list(self, prev_node):
        labels_list = InteriorNode('labels-list')
        cant_be_parsed_as_labels_list = False
        self._tokens.save_checkpoint()
        if dm.COMMA == self._tokens.next_token().code():
            labels_list.add_child(LeafNode(','))
        else:
            cant_be_parsed_as_labels_list = True
        if not cant_be_parsed_as_labels_list and not self._with_checkpoint(self._unsigned_integer, labels_list):
            cant_be_parsed_as_labels_list = True
        if not cant_be_parsed_as_labels_list and not self._with_checkpoint(self._labels_list, labels_list):
            cant_be_parsed_as_labels_list = True

        if cant_be_parsed_as_labels_list:
            self._tokens.back_to_last_checkpoint()
            empty_labels_list = InteriorNode('labels-list')
            empty_labels_list.add_child(EmptyNode())
            prev_node.add_child(empty_labels_list)
        else:
            self._tokens.confirm_last_checkpoint()
            prev_node.add_child(labels_list)
        return True

    def _variable_identifier(self, prev_node):
        return self._unique_by_and('variable-identifier',
                                   prev_node,
                                   self._identifier)

    def _identifier(self, prev_node):
        return self._unique_by_and('identifier',
                                   prev_node,
                                   self._leaf_production(lu.is_identifier_code))

    def _unsigned_integer(self, prev_node):
        return self._unique_by_and('unsigned-integer',
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

    def _unique_by_and(self, production, prev_node, *handle_cases):
        node = InteriorNode(production)
        successfully = self._with_checkpoint(reduce,
                                             lambda res, handle_case: res and self._with_checkpoint(handle_case, node),
                                             handle_cases,
                                             True)
        if successfully:
            prev_node.add_child(node)
            return True
        return False

    def _leaf_production(self, leaf_p):
        return partial(self._leaf_node, leaf_p)

    def _leaf_node(self, leaf_p, prev_node):
        token = self._tokens.next_token()
        if leaf_p(token.code()):
            prev_node.add_child(LeafNode(token.label()))
            return True
        return False

    def _unique_by_or(self, *handle_funcs):
        pass

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
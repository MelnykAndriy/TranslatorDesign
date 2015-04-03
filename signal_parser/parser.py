__author__ = 'mandriy'

from parser_utils import TokensIterator, TokensExhausted
from term import *
import lexer.keywords as kw
import lexer.delimiters as dm
import lexer.lexer_utils as lu
from lexer.lexer import SignalLexicalAnalysis


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
        if not self._tokens.next_token().label() == TokensIterator.teminate_token().label():
            print self._tokens.current_token().label()
            print self._tokens.current_token().code()
            raise Exception('something wrong')
            pass  # TODO report an error
        return self._term

    def _signal_program(self, prev_node):
        signal_program = InteriorNode('signal-program')
        if not self._with_checkpoint(self._program, signal_program):
            return False
        prev_node.add_child(signal_program)
        return True

    def _program(self, prev_node):
        program_node = InteriorNode('program')

        if kw.PROGRAM == self._tokens.next_token().code():
            program_node.add_child(LeafNode('PROGRAM'))
        else:
            return False

        if not self._with_checkpoint(self._procedure_identifier, program_node):
            return False

        if dm.SEMICOLON == self._tokens.next_token().code():
            program_node.add_child(LeafNode(';'))
        else:
            return False

        if not self._with_checkpoint(self._block, program_node):
            return False

        if dm.DOT == self._tokens.next_token().code():
            program_node.add_child(LeafNode('.'))
        else:
            return False
        prev_node.add_child(program_node)
        return True

    def _procedure_identifier(self, prev_node):
        procedure_identifier = InteriorNode('procedure-identifier')
        if not self._with_checkpoint(self._identifier, procedure_identifier):
            return False
        prev_node.add_child(procedure_identifier)
        return True

    def _block(self, prev_node):
        block = InteriorNode('block')
        if not self._with_checkpoint(self._declarations, block):
            return False
        if kw.BEGIN == self._tokens.next_token().code():
            block.add_child(LeafNode('BEGIN'))
        else:
            return False
        if not self._with_checkpoint(self._statements_list, block):
            return False
        if kw.END == self._tokens.next_token().code():
            block.add_child(LeafNode('END'))
        else:
            return False
        prev_node.add_child(block)
        return True

    def _declarations(self, prev_node):
        declarations = InteriorNode('declarations')
        if not self._with_checkpoint(self._label_declarations, declarations):
            return False
        prev_node.add_child(declarations)
        return True

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
        variable_identifier = InteriorNode('variable-identifier')
        if not self._with_checkpoint(self._identifier, variable_identifier):
            return False
        prev_node.add_child(variable_identifier)
        return True

    def _identifier(self, prev_node):
        ident_code = self._tokens.next_token().code()
        if lu.is_identifier_code(ident_code):
            identifier = InteriorNode('identifier')
            identifier.add_child(LeafNode(self._idents_table.get_item_by_code(ident_code)))
            prev_node.add_child(identifier)
            return True
        return False

    def _unsigned_integer(self, prev_node):
        constant_code = self._tokens.next_token().code()
        if lu.is_constant_code(constant_code):
            unsigned_integer = InteriorNode('unsigned-integer')
            unsigned_integer.add_child(LeafNode(self._constants_table.get_item_by_code(constant_code)))
            prev_node.add_child(unsigned_integer)
            return True
        return False

    def _with_checkpoint(self, func, *args):
        self._tokens.save_checkpoint()
        func_result = func(*args)
        if func_result:
            self._tokens.confirm_last_checkpoint()
        else:
            self._tokens.back_to_last_checkpoint()
        return func_result

    def _unique_by_and(self, *handle_funcs):
        pass

    def _unique_by_or(self, *handle_funcs):
        pass

    def _match_leaf(self):
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
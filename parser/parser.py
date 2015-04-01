__author__ = 'mandriy'

from parser_utils import TokensIterator
from term import *
import lexer.keywords as kw
import lexer.delimiters as dm
import lexer.lexer_utils as lu
from lexer.lexer import SignalLexicalAnalysis
import os.path

class SignalParser:

    def __init__(self):
        self.__tokens__ = None
        self.__idents_table__ = None
        self.__constants_table__ = None
        self.__term__ = None

    def parse_file(self, filename):
        with open(filename, "r") as source_file:
            return self.parse(source_file.read())

    def parse(self, source_text):
        lexer = SignalLexicalAnalysis()
        self.__tokens__ = TokensIterator(lexer(source_text))
        self.__idents_table__ = lexer.identifiers()
        self.__constants_table__ = lexer.constants()
        try:
            if self.__signal_program__():
                pass
                # TODO seems everything is alright
            else:
                pass  # TODO find error reason in stack

        except TokensExhausted:
            pass  # TODO report an error
        try:
            self.__tokens__.next_token()
            # TODO report an error
        except TokensExhausted:
            pass  # TODO seems everything is alright
        return self.__term__

    def __signal_program__(self):
        signal_program = InteriorNode('signal-program')
        if not self.__with_checkpoint__(self.__program__, signal_program):
            return False
        self.__term__ = Term(signal_program)
        return True

    def __program__(self, prev_node):
        program_node = InteriorNode('program')

        if kw.PROGRAM == self.__tokens__.next_token().get_code():
            program_node.add_child(LeafNode('PROGRAM'))
        else:
            return False

        if not self.__with_checkpoint__(self.__procedure_identifier__, program_node):
            return False

        if dm.SEMICOLON == self.__tokens__.next_token().get_code():
            program_node.add_child(LeafNode(';'))
        else:
            return False

        if not self.__with_checkpoint__(self.__block__, program_node):
            return False

        if dm.DOT == self.__tokens__.next_token().get_code():
            program_node.add_child(LeafNode('.'))
        else:
            return False
        prev_node.add_child(program_node)
        return True

    def __procedure_identifier__(self, prev_node):
        procedure_identifier = InteriorNode('procedure-identifier')
        if not self.__with_checkpoint__(self.__identifier__, procedure_identifier):
            return False
        prev_node.add_child(procedure_identifier)
        return True

    def __block__(self, prev_node):
        block = InteriorNode('block')
        if not self.__with_checkpoint__(self.__declarations__, block):
            return False
        if kw.BEGIN == self.__tokens__.next_token():
            block.add_child(LeafNode('BEGIN'))
        else:
            return False
        if not self.__with_checkpoint__(self.__statements_list__, block):
            return False
        if kw.END == self.__tokens__.next_token():
            block.add_child(LeafNode('END'))
        else:
            return False
        if dm.SEMICOLON == self.__tokens__.next_token():
            block.add_child(LeafNode(';'))
        else:
            return False
        prev_node.add_child(block)
        return True

    def __declarations__(self, prev_node):
        declarations = InteriorNode('declarations')
        if not self.__with_checkpoint__(self.__label_declarations__, declarations):
            return False
        prev_node.add_child(declarations)
        return True

    def __statement__(self, prev_node):
        statement = InteriorNode('statement')
        next_production = False
        self.__tokens__.save_checkpoint()
        if not self.__with_checkpoint__(self.__unsigned_integer__, statement):
            next_production = True
        if not next_production and not dm.COLON == self.__tokens__.next_token():
            next_production = True
        else:
            statement.add_child(':')
        if not next_production and self.__with_checkpoint__(self.__statement__, statement):
            self.__tokens__.confirm_last_checkpoint()
            prev_node.add_child(statement)
            return True
        else:
            self.__tokens__.back_to_last_checkpoint()
            statement = InteriorNode('statement')
            next_production = False
# GOTO ------------
        self.__tokens__.save_checkpoint()
        if kw.GOTO == self.__tokens__.next_token():
            statement.add_child('GOTO')
        else:
            next_production = True
        if not next_production and not self.__with_checkpoint__(self.__unsigned_integer__, statement):
            next_production = True
        if not next_production and dm.SEMICOLON == self.__tokens__.next_token():
            self.__tokens__.confirm_last_checkpoint()
            statement.add_child(';')
            prev_node.add_child(statement)
            return True
        else:
            self.__tokens__.back_to_last_checkpoint()
            statement = InteriorNode('statement')
            next_production = False
# LINK ---------------
        self.__tokens__.save_checkpoint()

        if kw.LINK == self.__tokens__.next_token():
            statement.add_child('LINK')
        else:
            next_production = True

        if not next_production and not self.__with_checkpoint__(self.__variable_identifier__, statement):
            next_production = True

        if not next_production:
            if not dm.COMMA == self.__tokens__.next_token():
                next_production = True
            else:
                statement.add_child(',')

        if not next_production and not self.__with_checkpoint__(self.__unsigned_integer__, statement):
            next_production = True

        if not next_production and dm.SEMICOLON == self.__tokens__.next_token():
            self.__tokens__.confirm_last_checkpoint()
            statement.add_child(';')
            prev_node.add_child(statement)
            return True
        else:
            self.__tokens__.back_to_last_checkpoint()
            statement = InteriorNode('statement')
            next_production = False
# IN --------------------
        self.__tokens__.save_checkpoint()

        if kw.IN == self.__tokens__.next_token():
            statement.add_child('IN')
        else:
            next_production = True

        if not next_production and not self.__with_checkpoint__(self.__unsigned_integer__, statement):
            next_production = True

        if not next_production and dm.SEMICOLON == self.__tokens__.next_token():
            self.__tokens__.confirm_last_checkpoint()
            statement.add_child(';')
            prev_node.add_child(statement)
            return True
        else:
            self.__tokens__.back_to_last_checkpoint()
            statement = InteriorNode('statement')
            next_production = False

# OUT -------------------
        self.__tokens__.save_checkpoint()

        if kw.OUT == self.__tokens__.next_token():
            statement.add_child('OUT')
        else:
            next_production = True

        if not next_production and not self.__with_checkpoint__(self.__unsigned_integer__, statement):
            next_production = True

        if not next_production and dm.SEMICOLON == self.__tokens__.next_token():
            self.__tokens__.confirm_last_checkpoint()
            statement.add_child(';')
            prev_node.add_child(statement)
            return True
        else:
            self.__tokens__.back_to_last_checkpoint()
            # TODO error stack push
            return False

    def __statements_list__(self, prev_node):
        statements_list = InteriorNode('statements-list')
        self.__tokens__.save_checkpoint()
        cant_be_parsed_as_statements_list = False
        if not self.__with_checkpoint__(self.__statement__, statements_list):
            cant_be_parsed_as_statements_list = True
        if not self.__with_checkpoint__(self.__statements_list__, statements_list):
            cant_be_parsed_as_statements_list = True
        if cant_be_parsed_as_statements_list:
            self.__tokens__.back_to_last_checkpoint()
            empty_statements_list = InteriorNode('statements-list')
            empty_statements_list.add_child(EmptyNode())
            prev_node.add_child(empty_statements_list)
        else:
            self.__tokens__.confirm_last_checkpoint()
            prev_node.add_child(statements_list)
        return True

    def __label_declarations__(self, prev_node):
        self.__tokens__.save_checkpoint()
        label_declarations = InteriorNode('label-declarations')
        cant_be_parsed_as_labels_decl = False
        if kw.LABEL == self.__tokens__.next_token():
            label_declarations.add_child(LeafNode('LABEL'))
        else:
            self.__tokens__.confirm_last_checkpoint()
            cant_be_parsed_as_labels_decl = True

        if not cant_be_parsed_as_labels_decl and \
                not self.__with_checkpoint__(self.__unsigned_integer__, label_declarations):
            cant_be_parsed_as_labels_decl = True

        if not cant_be_parsed_as_labels_decl and \
                not self.__with_checkpoint__(self.__labels_list__, label_declarations):
            cant_be_parsed_as_labels_decl = True

        if not cant_be_parsed_as_labels_decl and dm.SEMICOLON == self.__tokens__.next_token():
            label_declarations.add_child(LeafNode(';'))
        else:
            cant_be_parsed_as_labels_decl = True

        if cant_be_parsed_as_labels_decl:
            self.__tokens__.back_to_last_checkpoint()
            empty_label_declarations = InteriorNode('label-declarations')
            empty_label_declarations.add_child(EmptyNode())
            prev_node.add_child(empty_label_declarations)
        else:
            self.__tokens__.confirm_last_checkpoint()
            prev_node.add_child(label_declarations)
        return True

    def __labels_list__(self, prev_node):
        labels_list = InteriorNode('labels-list')
        cant_be_parsed_as_labels_list = False
        if dm.COMMA == self.__tokens__.next_token():
            labels_list.add_child(LeafNode(','))
        else:
            cant_be_parsed_as_labels_list = True
        if not self.__with_checkpoint__(self.__unsigned_integer__, labels_list):
            cant_be_parsed_as_labels_list = True
        if not self.__with_checkpoint__(self.__labels_list__, labels_list):
            cant_be_parsed_as_labels_list = True

        if cant_be_parsed_as_labels_list:
            self.__tokens__.back_to_last_checkpoint()
            empty_labels_list = InteriorNode('labels-list')
            empty_labels_list.add_child(EmptyNode())
            prev_node.add_child(empty_labels_list)
        else:
            prev_node.add_child(labels_list)
        return True

    def __variable_identifier__(self):
        variable_identifier = InteriorNode('variable-identifier')
        if not self.__with_checkpoint__(self.__identifier__, variable_identifier):
            return False
        prev_node.add_child(variable_identifier)
        return True

    def __identifier__(self, prev_node):
        ident_code = self.__tokens__.next_token().get_token()
        if lu.is_identifier_code(ident_code):
            identifier = InteriorNode('identifier')
            identifier.add_child(LeafNode(self.__idents_table__.get_item_by_code(constant_code)))
            prev_node.add_child(identifier)
            return True
        return False

    def __unsigned_integer__(self):
        constant_code = self.__tokens__.next_token().get_token()
        if lu.is_constant_code(constant_code):
            unsigned_integer = InteriorNode('unsigned-integer')
            unsigned_integer.add_child(LeafNode(self.__constants_table__.get_item_by_code(constant_code)))
            prev_node.add_child(unsigned_integer)
            return True
        return False

    def __with_checkpoint__(self, func, *args):
        self.__tokens__.save_checkpoint()
        func_result = func(*args)
        if func_result:
            self.__tokens__.confirm_last_checkpoint()
        else:
            self.__tokens__.back_to_last_checkpoint()
        return func_result

    def __unique_by_and__(self, *handle_funcs):
        pass

    def __unique_by_or__(self, *handle_funcs):
        pass

    def __match_leaf__(self):
        pass

from _curses import error

__author__ = 'mandriy'

import unittest
from signal_parser.parser import SignalParser
from signal_parser.term import EmptyNode
from signal_parser.tree_construction import StandardTreeBuilder
from lexer.lexer_utils import Token
from signal_parser.errors import *


def term_from_test_rep(term_rep, tree_builder_class=StandardTreeBuilder):
    """
    :param lst: it has to be tuple of form (interior-node-sort, childs)
    childs is a list of form [leaf-node-sort or (interior-node-sort, childs) * ]
    :return: term
    """
    tree_builder = tree_builder_class()
    root = tree_builder.build_tree()

    def term_from_test_rep_inner(term_rep_inner, prev_node):
        if isinstance(term_rep_inner, tuple):
            node = tree_builder.build_interior_node(term_rep_inner[0])
            tree_builder.build_dependency(prev_node, node)
            children = term_rep_inner[1]
            for child in children:
                term_from_test_rep_inner(child, node)
            return node
        elif isinstance(term_rep_inner, EmptyNode):
            return term_rep_inner
        else:
            return tree_builder.build_leaf_node(prev_node, Token(term_rep_inner, -1, (0, 0)))
    term_from_test_rep_inner(term_rep, root)
    return tree_builder.get_tree()


def get_identifier(ident):
    return 'identifier', [ident]


def get_unsigned_integer(i):
    return 'unsigned-integer', [str(i)]


class ParsingTest(unittest.TestCase):

    def setUp(self):
        self._parser = SignalParser()

        self._id_text = 'someIdentifierHere12'
        self._var_id_text = self._id_text
        self._proc_id_text = self._id_text
        self._unsigned_int_text = '12512'
        self._labels_list_text = ',5,4'
        self._label_declarations_text = 'LABEL 3 ' + self._labels_list_text + ';'
        self._goto_text = 'GOTO 215;'
        self._in_text = 'IN 1;'
        self._out_text = 'OUT 100500;'
        self._link_text = 'LINK lol, 100;'
        self._labeled_stmt_text = '215: ' + self._goto_text
        self._declarations_text = self._label_declarations_text
        self._stmt_lst_text = self._in_text + self._out_text + self._link_text
        self._empty_block_text = 'BEGIN ' + 'END'
        self._block_text = self._declarations_text + 'BEGIN ' + self._stmt_lst_text + 'END'
        self._program_text = 'PROGRAM program1; ' + self._block_text + '.'

        self._id_rep = get_identifier('someIdentifierHere12')
        self._var_id_rep = ('variable-identifier', [self._id_rep])
        self._proc_id_rep = ('procedure-identifier', [self._id_rep])
        self._unsigned_int_rep = get_unsigned_integer(12512)
        self._labels_list_rep = ('labels-list',
                                 [',', get_unsigned_integer(5),
                                  ('labels-list',
                                   [',', get_unsigned_integer(4),
                                    ('labels-list', [EmptyNode()])])])
        self._label_declarations_rep = ('label-declarations',
                                        ['LABEL', get_unsigned_integer(3), self._labels_list_rep, ';'])
        self._empty_declarations_rep = ('declarations', [('label-declarations', [EmptyNode()])])
        self._goto_rep = ('statement', ['GOTO', get_unsigned_integer(215), ';'])
        self._in_rep = ('statement', ['IN', get_unsigned_integer(1), ';'])
        self._out_rep = ('statement', ['OUT', get_unsigned_integer(100500), ';'])
        self._link_rep = ('statement', ['LINK',
                                        ('variable-identifier', [get_identifier('lol')]),
                                        ',',
                                        get_unsigned_integer(100),
                                        ';'])
        self._labeled_stmt_rep = ('statement', [get_unsigned_integer(215), ':', self._goto_rep])
        self._declarations_rep = ('declarations', [self._label_declarations_rep])
        self._empty_stmt_list_rep = ('statements-list', [EmptyNode()])
        self._stmt_lst_rep = ('statements-list', [self._in_rep,
                                                  ('statements-list', [self._out_rep,
                                                                       ('statements-list',
                                                                        [self._link_rep,
                                                                         ('statements-list', [EmptyNode()])])])])
        self._empty_block_rep = ('block', [self._empty_declarations_rep, 'BEGIN', self._empty_stmt_list_rep, 'END'])
        self._block_rep = ('block', [self._declarations_rep, 'BEGIN', self._stmt_lst_rep, 'END'])
        self._program_rep = ('program', ['PROGRAM',
                                         ('procedure-identifier', [get_identifier('program1')]),
                                         ';',
                                         self._block_rep,
                                         '.'])

    def tearDown(self):
        pass

    def test_program_parsing(self):
        self.assertEqual(self._parser.parse(self._program_text, sort='program'),
                         term_from_test_rep(self._program_rep))

    def test_block_parsing(self):
        self.assertEqual(self._parser.parse(self._block_text, sort='block'),
                         term_from_test_rep(self._block_rep))

    def test_block_without_stmts_and_decls_parsing(self):
        self.assertEqual(self._parser.parse(self._empty_block_text, sort='block'),
                         term_from_test_rep(self._empty_block_rep))

    def test_declarations_parsing(self):
        self.assertEqual(self._parser.parse(self._declarations_text, sort='declarations'),
                         term_from_test_rep(self._declarations_rep))

    def test_empty_decl_parsing(self):
        self.assertEqual(self._parser.parse(' ', sort='declarations'),
                         term_from_test_rep(self._empty_declarations_rep))

    def test_labeled_statement_parsing(self):
        self.assertEqual(self._parser.parse(self._labeled_stmt_text, sort='statement'),
                         term_from_test_rep(self._labeled_stmt_rep))

    def test_link_statement_parsing(self):
        self.assertEqual(self._parser.parse(self._link_text, sort='statement'),
                         term_from_test_rep(self._link_rep))

    def test_in_statement_parsing(self):
        self.assertEqual(self._parser.parse(self._in_text, sort='statement'),
                         term_from_test_rep(self._in_rep))

    def test_out_statement_parsing(self):
        self.assertEqual(self._parser.parse(self._out_text, sort='statement'),
                         term_from_test_rep(self._out_rep))

    def test_goto_statement_parsing(self):
        self.assertEqual(self._parser.parse(self._goto_text, sort='statement'),
                         term_from_test_rep(self._goto_rep))

    def test_statements_list_parsing(self):
        self.assertEqual(self._parser.parse(self._stmt_lst_text, sort='statements-list'),
                         term_from_test_rep(self._stmt_lst_rep))

    def test_empty_statements_list_parsing(self):
        self.assertEqual(self._parser.parse(' ', sort='statements-list'),
                         term_from_test_rep(self._empty_stmt_list_rep))

    def test_label_declarations_parsing(self):
        self.assertEqual(self._parser.parse(self._label_declarations_text, sort='label-declarations'),
                         term_from_test_rep(self._label_declarations_rep))

    def test_labels_list_parsing(self):
        self.assertEqual(self._parser.parse(self._labels_list_text, sort='labels-list'),
                         term_from_test_rep(self._labels_list_rep))

    def test_procedure_identifier_parsing(self):
        self.assertEqual(self._parser.parse(self._proc_id_text, sort='procedure-identifier'),
                         term_from_test_rep(self._proc_id_rep))

    def test_variable_identifier_parsing(self):
        self.assertEqual(self._parser.parse(self._var_id_text, sort='variable-identifier'),
                         term_from_test_rep(self._var_id_rep))

    def test_unsigned_integer_parsing(self):
        self.assertEqual(self._parser.parse(self._unsigned_int_text, sort='unsigned-integer'),
                         term_from_test_rep(self._unsigned_int_rep))

    def test_identifier_parsing(self):
        self.assertEqual(self._parser.parse(self._id_text, sort='identifier'),
                         term_from_test_rep(self._id_rep))


# noinspection PyShadowingNames
class ErrorsCollectingTest(unittest.TestCase):

    def setUp(self):
        self._parser = SignalParser()

    def tearDown(self):
        pass

    def test_expected_program_keyword(self):
        invalid_source = ' program1; BEGIN END.'
        self._parser.parse(invalid_source, 'signal-program')
        error = self._parser.errors().pop()
        self.assertIsInstance(error, ExpectedToken, 'Extected program keyword error reporting.')
        self.assertEqual(error.position(), (2, 1), 'Extected program keyword error position.')

    def test_missed_program_name(self):
        invalid_source = 'PROGRAM   ; BEGIN END.'
        self._parser.parse(invalid_source, 'signal-program')
        error = self._parser.errors().pop()
        self.assertIsInstance(error, MissedToken, 'Missed program name error reporting.')
        self.assertEqual(error.position(), (11, 1), 'Missed program name error position.')

    def test_extra_tokens(self):
        invalid_source = 'PROGRAM program1; BEGIN END. LABEL id, 2;'
        self._parser.parse(invalid_source, 'signal-program')
        error = self._parser.errors().pop()
        self.assertIsInstance(error, ExtraTokens, 'ExtraTokens error reporting.')
        self.assertEqual(error.position(), (30, 1), 'ExtraTokens error position.')

    def test_missed_semicolon(self):
        invalid_source = 'PROGRAM program1 BEGIN END.'
        self._parser.parse(invalid_source, 'signal-program')
        error = self._parser.errors().pop()
        self.assertIsInstance(error, MissedToken, 'Missed semicolon after program name error reporting.')
        self.assertEqual(error.position(), (18, 1), 'Missed semicolon after program name error position.')

    def test_missed_dot(self):
        invalid_source = 'PROGRAM program1; BEGIN END'
        self._parser.parse(invalid_source, 'signal-program')
        error = self._parser.errors().pop()
        self.assertIsInstance(error, MissedToken, 'Missed dot after program block  error reporting.')
        self.assertEqual(error.position(), (28, 1), 'Missed dot after program block error position.')

    def test_begin_expected(self):
        invalid_source = ' LABEL 1, 2,3;\n 1: LINK var, 2; GOTO 1; END.'
        self._parser.parse(invalid_source, 'block')
        error = self._parser.errors().pop()
        self.assertIsInstance(error, ExpectedToken, 'Expected block begin error reporting.')
        self.assertEqual(error.position(), (2, 2), 'Expected block begin error position.')

    def test_end_expected(self):
        invalid_source = ' LABEL 1, 2,3;\n BEGIN 1: LINK var, 2;\n GOTO 1;\n IN 1; '
        self._parser.parse(invalid_source, 'block')
        error = self._parser.errors().pop()
        self.assertIsInstance(error, ExpectedToken, 'Expected block end error reporting.')
        self.assertEqual(error.position(), (7, 4), 'Expected block end error position.')

    def test_label_declaration(self):
        invalid_source = ' LABEL invalid1, 2,3; '
        self._parser.parse(invalid_source, 'declarations')
        error = self._parser.errors().pop()
        self.assertIsInstance(error, InvalidLabelDefinition, 'Invalid label definition error reporting.')
        self.assertEqual(error.position(), (8, 1), 'Invalid label definition error position.')

    def test_missed_semicolon_after_label_declarations(self):
        invalid_source = ' LABEL 1, 2,3  '
        self._parser.parse(invalid_source, 'declarations')
        error = self._parser.errors().pop()
        self.assertIsInstance(error, MissedToken,
                              'Missed semicolon after label declarations error reporting.')
        self.assertEqual(error.position(), (14, 1),
                         'Missed semicolon after label declarations error position.')

    def test_label_declaration_in_labels_list(self):
        invalid_source = ' LABEL 1,\n 2,\n 3,\n    lol; '
        self._parser.parse(invalid_source, 'declarations')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, InvalidLabelDefinition, 'Labels list invalid label error reporting.')
        self.assertEqual(error.position(), (5, 4), 'Labels list invalid label error position.')

    def test_labeleld_statement_semicolon(self):
        invalid_source = ' 1 GOTO 1;'
        self._parser.parse(invalid_source, 'statement')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, MissedToken, 'Missed colon inside labeled statement error reporting.')
        self.assertEqual(error.position(), (4, 1), 'Missed colon inside labeled statement error position.')

    def test_empty_labeled_statement(self):
        invalid_source = 'BEGIN LINK var, 1;\n 5: END'
        self._parser.parse(invalid_source, 'block')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, EmptyLabeledStatement, 'EmptyLabeledStatement error reporting.')
        self.assertEqual(error.position(), (5, 2), 'EmptyLabeledStatement error position.')

    def test_goto_semicolon(self):
        invalid_source = 'BEGIN\n\tIN 1;\n\tOUT 2;\n\tGOTO 15 END'
        self._parser.parse(invalid_source, 'block')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, MissedToken, 'Missed GOTO semicolon error reporting.')
        self.assertEqual(error.position(), (13, 4), 'Missed GOTO semicolon error position.')

    def test_goto_label(self):
        invalid_source = 'GOTO label15;'
        self._parser.parse(invalid_source, 'statement')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, GotoStatementArgument, 'GOTO argument error reporting.')
        self.assertEqual(error.position(), (6, 1), 'GOTO argument error position.')

    def test_in_argument(self):
        invalid_source = 'IN 1;\n IN 2;\nIN badInARG;'
        self._parser.parse(invalid_source, 'statements-list')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, InStatementArgument, 'IN argument error reporting.')
        self.assertEqual(error.position(), (4, 3), 'IN argument error position.')

    def test_in_semicolon(self):
        invalid_source = 'BEGIN\n15: IN 1\nOUT 2;\nGOTO 15; END'
        self._parser.parse(invalid_source, 'block')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, MissedToken, 'Missed IN semicolon error reporting.')
        self.assertEqual(error.position(), (1, 3), 'Missed IN semicolon error position.')

    def test_out_argument(self):
        invalid_source = 'OUT 5;\n OUT badInARG;\n OUT 7;'
        self._parser.parse(invalid_source, 'statements-list')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, OutStatementArgument, 'OUT argument error reporting.')
        self.assertEqual(error.position(), (6, 2), 'OUT argument error position.')

    def test_out_semicolon(self):
        invalid_source = 'BEGIN\n15: IN 1;\nOUT 2\nGOTO 15; END'
        self._parser.parse(invalid_source, 'block')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, MissedToken, 'Missed OUT semicolon error reporting.')
        self.assertEqual(error.position(), (1, 4), 'Missed OUT semicolon error position.')

    def test_link_semicolon(self):
        invalid_source = 'GOTO 1; \n1:\n LINK id2, 5'
        self._parser.parse(invalid_source, 'statements-list')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, MissedToken, 'Missed LINK semicolon error reporting.')
        self.assertEqual(error.position(), (13, 3), 'Missed LINK semicolon error position.')

    def test_link_args(self):
        invalid_source = 'GOTO 1; \n1:\n LINK id2, id5; '
        self._parser.parse(invalid_source, 'statements-list')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, LinkStatementArguments, 'LINK arguments error reporting.')
        self.assertEqual(error.position(), (12, 3), 'LINK arguments error position.')

    def test_link_args2(self):
        invalid_source = 'GOTO 1; \n1:\n LINK 2, 5; '
        self._parser.parse(invalid_source, 'statements-list')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, LinkStatementArguments, 'LINK arguments error reporting.')
        self.assertEqual(error.position(), (7, 3), 'LINK arguments error position.')

    def test_link_missed_comma(self):
        invalid_source = 'LINK id 7; '
        self._parser.parse(invalid_source, 'statements-list')
        error = self._parser.errors().pop(0)
        self.assertIsInstance(error, MissedToken, 'LINK statement missed comma error reporting.')
        self.assertEqual(error.position(), (9, 1), 'LINK statement missed comma error position.')


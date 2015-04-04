__author__ = 'mandriy'

import unittest
from signal_parser.parser import InteriorNode, LeafNode, EmptyNode, SignalParser
from signal_parser.term import Term, term_to_dot
from lexer.lexer_utils import Token


def term_from_test_rep(term_rep):
    """
    :param lst: it has to be tuple of form (interior-node-sort, childs)
    childs is a list of form [leaf-node-sort or (interior-node-sort, childs) * ]
    :return: term
    """
    def term_from_test_rep_inner(term_rep_inner):
        if isinstance(term_rep_inner, tuple):
            node = InteriorNode(term_rep_inner[0])
            children = term_rep_inner[1]
            for child in children:
                node.add_child(term_from_test_rep_inner(child))
            return node
        elif isinstance(term_rep_inner, EmptyNode):
            return term_rep_inner
        else:
            return LeafNode(Token(term_rep_inner, -1, (0, 0)))
    return Term(term_from_test_rep_inner(term_rep))


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


class ErrorsCollectingTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
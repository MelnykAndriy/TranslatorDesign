__author__ = 'mandriy'

import unittest
from lexer.lexer import SignalLexicalAnalysis
from lexer.keywords import is_keyword_code, keyword_code
from lexer.delimiters import is_delimiter_code, delimiter_code
from lexer.lexer_utils import is_constant_code, is_identifier_code, InvalidToken, UnclosedComment, PositionMixin


class LexerTest(unittest.TestCase):

    def setUp(self):
        self.__count_tests_source__ = '''PROGRAM test1;
                                            LABEL 100,200, 300, 400;
                                            BEGIN
                                                GOTO 300;
                                            END.'''

    def getErrors(self, source):
        lexer = SignalLexicalAnalysis()
        lexer(source)
        return lexer.errors()

    def getTokens(self, source):
        lexer = SignalLexicalAnalysis()
        return lexer(source)

    def getCountTokens(self):
        return self.getTokens(self.__count_tests_source__)

    def checkNoErrors(self, lexer):
        errors = lexer.errors()
        self.assertFalse(len(errors), 'Some errors are reported by mistake.')

    def test_tokens_count(self):
        self.assertEqual(len(self.getCountTokens()), 18, 'Tokens count is failed.')

    def test_keywords_count(self):
        self.assertEqual(map(lambda token: is_keyword_code(token.code()),
                             self.getCountTokens()).count(True),
                         5,
                         'Keywords count is failed.')

    def test_delims_count(self):
        self.assertEqual(map(lambda token: is_delimiter_code(token.code()),
                             self.getCountTokens()).count(True),
                         7,
                         'Delimiters count is failed.')

    def test_constants_count(self):
        self.assertEqual(map(lambda token: is_constant_code(token.code()),
                             self.getCountTokens()).count(True),
                         5,
                         'Constants count is failed.')

    def test_idents_count(self):
        self.assertEqual(map(lambda token: is_identifier_code(token.code()),
                             self.getCountTokens()).count(True),
                         1,
                         'Identifiers count is failed.')

    def test_identfiers_table_filling(self):
        source = 'LINK var2, 0; LINK var1, 0; '
        lexer = SignalLexicalAnalysis()
        tokens = lexer(source)
        ident_tab = lexer.identifiers()
        idents = filter(lambda token: is_identifier_code(token.code()), tokens)
        self.checkNoErrors(lexer)
        self.assertNotIn(False, map(lambda ident_token, ident_value:
                                    ident_tab.get_item_by_code(ident_token.code()) == ident_value,
                                    idents,
                                    ('var2', 'var1')),
                         'Identifiers filling is broken.')

    def test_constants_table_filling(self):
        source = 'LABEL 100,200, 300, 400;'
        lexer = SignalLexicalAnalysis()
        tokens = lexer(source)
        constant_table = lexer.constants()
        self.checkNoErrors(lexer)
        self.assertListEqual([True, False, True, False, True, False, True, False],
                             map(lambda token, constant:
                                 is_constant_code(token.code()) and
                                 constant_table.get_item_by_code(token.code()) == constant,
                                 tokens[1:],
                                 (100, None, 200, None, 300, None, 400)),
                             'Constants filling is broken.')

    def test_invalid_token_errors_collecting(self):
        errors = self.getErrors('LINK some_var, 0; PROGRAM 14badIdent;')
        self.assertEqual(len(errors), 2, 'Errors count.')
        self.assertNotIn(False, map(lambda error: isinstance(error, InvalidToken), errors), 'Errors type.')

    def test_unclosed_comment_errors_collecting(self):
        errors = self.getErrors("GOTO *< GOTO 400; >* 200; *< don't forget to close comments ")
        self.assertEqual(len(errors), 1, 'Errors count.')
        self.assertNotIn(False, map(lambda error: isinstance(error, UnclosedComment), errors), 'Errors type.')

    def test_errors_positions(self):
        invalid_token_errors = self.getErrors('LINK some_var, 0; PROGRAM 14badIdent;')
        unclosed_comment_error = self.getErrors("GOTO *< GOTO 400; >* 200; *< don't forget to close comments ")
        self.assertListEqual([(6, 1), (27, 1)], map(PositionMixin.position, invalid_token_errors),
                             'Checks whether InvalidToken errors positions are correct.')
        self.assertListEqual([(27, 1)],  map(PositionMixin.position, unclosed_comment_error),
                             'Checks whether UnclosedComment error position is correct.')

    def test_comments_skiping(self):
        source_with_comment = 'GOTO *< GOTO 400; >* 200;'
        tokens = self.getTokens(source_with_comment)
        self.assertListEqual(map(lambda token: token.code(), tokens),
                             [keyword_code('GOTO'), 501, delimiter_code(';')],
                             'Comments skiping is failed.')

    def test_file_positions(self):
        source = 'GOTO *< GOTO 400; >* 200;\n\tOUT 3;'
        lexer = SignalLexicalAnalysis()
        tokens = lexer(source)
        self.checkNoErrors(lexer)
        self.assertListEqual([(1, 1), (22, 1), (25, 1), (5, 2), (9, 2), (10, 2)],
                             map(PositionMixin.position, tokens),
                             'Tokens positions are incorrect.')

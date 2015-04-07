__author__ = 'mandriy'

import unittest
import signal_parser.parser
import code_gen.semantic_checker
from code_gen.errors import *


class SemanticErrors(unittest.TestCase):

    def setUp(self):
        self._parser = signal_parser.parser.SignalParser()
        self._checker = code_gen.semantic_checker.SemanticChecker()

    def _check_error_reporting(self, term, expected_error_type, expected_error_pos):
        self.assertFalse(self._checker.check(term))
        self.assertEqual(len(self._checker.errors()), 1)
        self.assertIsInstance(self._checker.errors()[0], expected_error_type,
                              '%s error reporting.' % str(expected_error_type))
        self.assertEqual(self._checker.errors()[0].position(), expected_error_pos,
                         '%s error position.' % str(expected_error_type))

    def test_duplicated_labels_error(self):
        term = self._parser.parse('PROGRAM test1;\n LABEL 1, 2 ,3 , 4, 3; \n'
                                  'BEGIN\n 2: GOTO 2; LINK port1, 1; LINK port2, 2; LINK port3, 3; '
                                  'IN 1; IN 2; OUT 3;\n END.',
                                  sort='signal-program')
        self._check_error_reporting(term, DuplicateLabelName, (21, 2))

    def test_label_link_ambiguity(self):
        term = self._parser.parse('PROGRAM test1;\n LABEL 1, 2; \nBEGIN\n'
                                  ' 2: LINK var, 3; GOTO 2; LINK var1, 2; IN 2;\n2: OUT 3;\n END.',
                                  sort='signal-program')
        self._check_error_reporting(term, LabelLinkAmbiguity, (1, 5))

    def test_goto_unresolved_label(self):
        term = self._parser.parse(
            'PROGRAM test1;\n LABEL 1, 2;\nBEGIN\nGOTO 1; LINK var, 2; \nGOTO 2; 1: IN 2; GOTO 1; END.',
            sort='signal-program'
        )
        self._check_error_reporting(term, GotoUnresolvedLabel, (6, 5))

    def test_undeclared_label(self):
        term = self._parser.parse(
            'PROGRAM test1;\n LABEL 1;\nBEGIN\n 3: LINK var, 2; \n IN 2;  END.',
            sort='signal-program'
        )
        self._check_error_reporting(term, UndeclaredLabel, (2, 4))

    def test_unresolved_port(self):
        term = self._parser.parse(
            'PROGRAM test1;\n BEGIN\n LINK port1, 1;\n LINK port2, 2;\n IN 1;\n OUT 2;\n IN 3;\n END.'
        )
        self._check_error_reporting(term, UnresolvedPort, (5, 7))

    def test_port_directions(self):
        term = self._parser.parse(
            'PROGRAM test1;\n BEGIN\n LINK port1, 1;\n LINK port2, 2;\n IN 1;\n OUT 2;\n OUT 2;\nOUT 1;\n END.'
        )
        self._check_error_reporting(term, PortDirectionConfilct, (5, 8))

    def test_already_linked_port(self):
        term = self._parser.parse(
            'PROGRAM test1;\n BEGIN\n LINK port1, 1;\n LINK port2, 1;\n END.'
        )
        self._check_error_reporting(term, AlreadyLinkedPort, (14, 4))

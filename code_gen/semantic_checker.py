__author__ = 'mandriy'

from signal_parser.term import Term
from errors import *
from generator_utils import *
from signal_parser.rules import Rule, TreePattern


class SemanticChecker(object):

    def __init__(self):
        self._semantic_errors = None

    def errors(self):
        return self._semantic_errors

    def check(self, term):
        self._semantic_errors = []
        self.check_duplicated_labels(term)
        self.check_port_usage(term)
        self.check_goto_unresolved_labels(term)
        self.check_label_ambiguity(term)
        self.check_undeclared_labels(term)
        return not self._semantic_errors

    def check_duplicated_labels(self, term):
        labels_stack = []
        error_before_check = len(self._semantic_errors)

        def check_if_label_is_already_defined(unsigned_label):
            token = get_unsigned_integer_leaf_token(unsigned_label)
            if token.code() in labels_stack:
                self._semantic_errors.append(DuplicateLabelName(token.position()))
            else:
                labels_stack.append(token.code())

        def find_duplicated_labels(labels_declarations):
            labels_declarations_term = Term(labels_declarations)
            labels_declarations_term.sort_traversal(
                up_match_dict={'unsigned-integer': check_if_label_is_already_defined}
            )

        term.sort_traversal(down_match_dict={'label-declarations': find_duplicated_labels})
        return error_before_check == len(self._semantic_errors)

    def check_label_ambiguity(self, term):
        error_before_check = len(self._semantic_errors)
        labels_stack = []

        def check_if_labels_is_already_used_somewere(labeled_statement):
            label = get_unsigned_integer_leaf_token(labeled_statement[0])
            if label.code() in labels_stack:
                self._semantic_errors.append(LabelLinkAmbiguity(label.position()))
            else:
                labels_stack.append(label.code())

        term.foreach(
            pre_rules=(
                Rule(TreePattern(pattern=('unsigned-integer', ':', 'statement'), parent='statement'),
                     check_if_labels_is_already_used_somewere),
            )
        )
        return error_before_check == len(self._semantic_errors)

    def check_port_usage(self, term):
        error_before_check = len(self._semantic_errors)
        linked_ports = {}

        def collect_link_statement_ports(link_stmt):
            port = get_unsigned_integer_leaf_token(link_stmt[3])
            if port.code() in linked_ports:
                self._semantic_errors.append(AlreadyLinkedPort(port.position()))
            else:
                linked_ports[port.code()] = 'linked'

        def check_direction(port, direction):
            if port.code() not in linked_ports:
                self._semantic_errors.append(UnresolvedPort(port.position()))
            else:
                port_state = linked_ports[port.code()]
                if port_state == direction or port_state == 'linked':
                    linked_ports[port.code()] = direction
                else:
                    self._semantic_errors.append(PortDirectionConfilct(port.position()))

        term.foreach(
            pre_rules=(
                Rule(TreePattern(pattern=('IN', 'unsigned-integer', ';'), parent='statement'),
                     lambda in_stmt: check_direction(get_unsigned_integer_leaf_token(in_stmt[1]), 'in')),
                Rule(TreePattern(pattern=('OUT', 'unsigned-integer', ';'), parent='statement'),
                     lambda out_stmt: check_direction(get_unsigned_integer_leaf_token(out_stmt[1]), 'out')),
                Rule(TreePattern(pattern=('LINK', 'identifier', ',', 'unsigned-integer', ';'), parent='statement'),
                     collect_link_statement_ports)
            )
        )
        return error_before_check == len(self._semantic_errors)

    def check_undeclared_labels(self, term):
        error_before_check = len(self._semantic_errors)
        declared_labels = []

        def check_if_label_is_declared(labeled_statement):
            label = get_unsigned_integer_leaf_token(labeled_statement[0])
            if label not in declared_labels:
                self._semantic_errors.append(UndeclaredLabel(label.position()))

        term.foreach(
            pre_rules=(
                Rule(TreePattern(pattern=('label-declarations',), parent='declarations'),
                     lambda decls: declared_labels.extend(collect_declared_labels(decls))),
                Rule(TreePattern(pattern=('unsigned-integer', ':', 'statement'), parent='statement'),
                     check_if_label_is_declared)
            )
        )

        return error_before_check == len(self._semantic_errors)

    def check_goto_unresolved_labels(self, term):
        error_before_check = len(self._semantic_errors)
        used_in_goto_labels = []
        declared_labels = []
        linked_labels = []

        term.foreach(
            pre_rules=(
                Rule(TreePattern(pattern=('label-declarations',), parent='declarations'),
                     lambda decls: declared_labels.extend(collect_declared_labels(decls))),
                Rule(TreePattern(pattern=('unsigned-integer', ':', 'statement'), parent='statement'),
                     lambda l_stmt: linked_labels.append(get_unsigned_integer_leaf_token(l_stmt[0]))),
                Rule(TreePattern(pattern=('GOTO', 'unsigned-integer', ';'), parent='statement'),
                     lambda goto_stmt: used_in_goto_labels.append(get_unsigned_integer_leaf_token(goto_stmt[1])))
            )
        )

        for label in used_in_goto_labels:
            if label not in linked_labels or label not in declared_labels:
                self._semantic_errors.append(GotoUnresolvedLabel(label.position()))

        return error_before_check == len(self._semantic_errors)
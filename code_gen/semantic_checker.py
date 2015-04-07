__author__ = 'mandriy'

from signal_parser.term import Term
from errors import *
from generator_utils import *


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
            labels_declarations_term.sort_traversal(up_match_dict={'unsigned-integer': check_if_label_is_already_defined})

        term.sort_traversal(down_match_dict={'label-declarations': find_duplicated_labels})
        return error_before_check == len(self._semantic_errors)

    def check_label_ambiguity(self, term):
        error_before_check = len(self._semantic_errors)
        labels_stack = []

        def check_if_labels_is_already_used_somewere(statement_node):
            labeled_statement = statement_node.match('unsigned-integer', ':', 'statement')
            if labeled_statement:
                label = get_unsigned_integer_leaf_token(labeled_statement[0])
                if label.code() in labels_stack:
                    self._semantic_errors.append(LabelLinkAmbiguity(label.position()))
                else:
                    labels_stack.append(label.code())

        term.sort_traversal(down_match_dict={'statement': check_if_labels_is_already_used_somewere})
        return error_before_check == len(self._semantic_errors)

    def check_port_usage(self, term):
        error_before_check = len(self._semantic_errors)
        linked_ports = {}

        def collect_link_statement_ports(stmt):
            link_stmt = stmt.match('LINK', 'identifier', ',', 'unsigned-integer', ';')
            if link_stmt:
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

        def check_in_direction(stmt):
            in_stmt = stmt.match('IN', 'unsigned-integer', ';')
            if in_stmt:
                check_direction(get_unsigned_integer_leaf_token(in_stmt[1]), 'in')

        def check_out_direction(stmt):
            out_stmt = stmt.match('OUT', 'unsigned-integer', ';')
            if out_stmt:
                check_direction(get_unsigned_integer_leaf_token(out_stmt[1]), 'out')

        term.sort_traversal(
            up_match_dict={
                'statement': lambda node: map(lambda stmt_func: stmt_func(node),
                                              (collect_link_statement_ports, check_out_direction, check_in_direction))})
        return error_before_check == len(self._semantic_errors)

    @staticmethod
    def _collect_labels(label_declaration):
        declared_labels = []
        label_declaration_term = Term(label_declaration)

        label_declaration_term.sort_traversal(
            up_match_dict={'unsigned-integer':
                           lambda label: declared_labels.append(get_unsigned_integer_leaf_token(label))}
        )
        return declared_labels

    def check_undeclared_labels(self, term):
        error_before_check = len(self._semantic_errors)
        declared_labels = []

        def check_if_label_is_declared(statement):
            labeled_statement = statement.match('unsigned-integer', ':', 'statement')
            if labeled_statement:
                label = get_unsigned_integer_leaf_token(labeled_statement[0])
                if label not in declared_labels:
                    self._semantic_errors.append(UndeclaredLabel(label.position()))

        term.sort_traversal(down_match_dict={
            'label-declarations': lambda decls: declared_labels.extend(self._collect_labels(decls)),
            'statement': check_if_label_is_declared}
        )
        return error_before_check == len(self._semantic_errors)

    def check_goto_unresolved_labels(self, term):
        error_before_check = len(self._semantic_errors)
        used_in_goto_labels = []
        declared_labels = []
        linked_labels = []

        def collect_linked_labels(statement):
            labeled_statement = statement.match('unsigned-integer', ':', 'statement')
            if labeled_statement:
                linked_labels.append(get_unsigned_integer_leaf_token(labeled_statement[0]))

        def collect_used_in_goto(statement):
            goto_statement = statement.match('GOTO', 'unsigned-integer', ';')
            if goto_statement:
                used_in_goto_labels.append(get_unsigned_integer_leaf_token(goto_statement[1]))

        term.sort_traversal(down_match_dict={
            'label-declarations': lambda decls: declared_labels.extend(self._collect_labels(decls)),
            'statement': lambda node: map(lambda stmt_func: stmt_func(node),
                                          (collect_linked_labels, collect_used_in_goto))})
        for label in used_in_goto_labels:
            if label not in linked_labels or label not in declared_labels:
                self._semantic_errors.append(GotoUnresolvedLabel(label.position()))

        return error_before_check == len(self._semantic_errors)
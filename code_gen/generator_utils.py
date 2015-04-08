__author__ = 'mandriy'

from signal_parser.term import Term, EmptyNode
import random
import string


def get_unsigned_integer_leaf_token(unsigned_integer_node):
    if unsigned_integer_node.label() == 'unsigned-integer':
        return unsigned_integer_node.children()[0].token()


def get_identifier_leaf_token(identifier_node):
    if identifier_node.label() == 'identifier':
        return identifier_node.children()[0].token()


def generate_random_string(n):
    return ''.join(random.choice(string.ascii_lowercase+string.uppercase) for _ in xrange(n))


def gen_indent(n):
    return ''.join(' ' for _ in xrange(n))


def is_empty_stmt_list(stmt_list):
    return stmt_list.label() == 'statements-list' and len(stmt_list.children()) == 1 and\
        isinstance(stmt_list.children()[0], EmptyNode)


def collect_declared_labels(label_declaration):
    declared_labels = []
    label_declaration_term = Term(label_declaration[0])

    label_declaration_term.sort_traversal(
        up_match_dict={'unsigned-integer':
                       lambda label: declared_labels.append(get_unsigned_integer_leaf_token(label))}
    )
    return declared_labels
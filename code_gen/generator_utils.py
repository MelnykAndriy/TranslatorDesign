from signal_parser import Rule, TreePattern

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


def evaluate_constant(constant):
    value = 1

    return value


def constant_type(constant_value):

    return 'dd'


def collect_constants(constants_declaration):
    constants = {}
    constants_declaration_term = Term(constants_declaration)

    def save_constant(constant_decl):
        constants[get_identifier_leaf_token(constant_decl[0]).label()] = constant_decl[2]

    constants_declaration_term.foreach(
        pre_rules=(
            Rule(TreePattern(pattern=('identifier', '=', 'constant', ';'), parent='constant-declaration'),
                 save_constant),
        )
    )
    return constants
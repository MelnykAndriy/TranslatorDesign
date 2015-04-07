__author__ = 'mandriy'


def get_unsigned_integer_leaf_token(unsigned_integer_node):
    if unsigned_integer_node.label() == 'unsigned-integer':
        return unsigned_integer_node.children()[0].token()
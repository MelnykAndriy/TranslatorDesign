__author__ = 'mandriy'

from lexer.lexer_utils import PositionMixin


class Term:

    def __init__(self, root):
        self.__root__ = root
        self.__root__.mark_as_root()

    def traversal(self, up_func=lambda node, parent_node: None, down_func=lambda node, parent_node: None):

        def traversal_inner():
            pass



        if order == 'pre':
            pass
        elif order == 'post':
            pass
        else:
            Exception('Order is not supported.')



# TODO add position mixin
class Node:

    def __init__(self, label):
        self.__label__ = label

    def get_label(self):
        return self.__label__


class LeafNode(Node):

    def __init__(self, token):
        Node.__init__(self, token.label())


class EmptyNode(Node):

    def __init__(self):
        Node.__init__(self, '')


class IsNotANode(Exception):
    pass


class InteriorNode(Node):

    def __init__(self, sort):
        Node.__init__(self, sort)
        self.__childred__ = []
        self.__is_root__ = False

    def add_child(self, child_node):
        if isinstance(child_node, Node):
            self.__childred__.append(child_node)
        else:
            raise IsNotANode(child_node)

    def is_root(self):
        return self.__is_root__

    def mark_as_root(self):
        self.__is_root__ = True




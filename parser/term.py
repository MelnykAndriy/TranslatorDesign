__author__ = 'mandriy'

from lexer.lexer_utils import PositionMixin


class Term(PositionMixin):

    def __init__(self):
        pass


class Node:

    def __init__(self, label):
        self.__label__ = label

    def get_label(self):
        return self.__label__


class LeafNode(Node):

    def __init__(self, label):
        Node.__init__(self, label)


class IsNotANode(Exception):
    pass


class InteriorNode(Node):

    def __init__(self, sort):
        Node.__init__(self, sort)
        self.childred = []

    def add_child(self, child_node):
        if isinstance(child_node, Node):
            self.childred.append(child_node)
        else:
            raise IsNotANode(child_node)



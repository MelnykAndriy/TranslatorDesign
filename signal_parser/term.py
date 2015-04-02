__author__ = 'mandriy'

from lexer.lexer_utils import PositionMixin


class Term(object):

    def __init__(self, root):
        self._root = root
        self._root.mark_as_root()

    def traversal(self, up_func=lambda node, parent_node: None, down_func=lambda node, parent_node: None):
        def traversal_inner(node, parent_node):
            down_func(node, parent_node)
            if isinstance(node, InteriorNode):
                node.iterate_children(traversal_inner)
            up_func(node, parent_node)
        self._root.iterate_children(traversal_inner)


# TODO add position mixin
class Node(object):

    def __init__(self, label):
        self._label = label
    # TODO add token

    def get_label(self):
        return self._label


class LeafNode(Node):

    def __init__(self, token):
        super(LeafNode, self).__init__(token)


class EmptyNode(LeafNode):

    def __init__(self):
        super(EmptyNode, self).__init__('')


class IsNotANode(Exception):
    pass


class InteriorNode(Node):

    def __init__(self, sort):
        super(InteriorNode, self).__init__(sort)
        self._childred = []
        self._is_root = False

    def add_child(self, child_node):
        if isinstance(child_node, Node):
            self._childred.append(child_node)
        else:
            raise IsNotANode(child_node)

    def is_root(self):
        return self._is_root

    def mark_as_root(self):
        self._is_root = True

    def iterate_children(self, func):
        for child in self._childred:
            func(child, self)





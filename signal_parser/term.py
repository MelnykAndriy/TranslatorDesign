__author__ = 'mandriy'

from lexer.lexer_utils import PositionMixin
from utils.common_utils import interval
import pydot


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


def term_to_dot(term, node_style=(), edge_style=()):
    graph = pydot.Dot(graph_type='graph')
    ids = interval(0, infinite=True)
    indexes = [ids.next()]

    def link_edges(node, parent_node):
        parent_vertex = pydot.Node(indexes[len(indexes) - 1], label=str(parent_node.get_label()), *node_style)
        indx = ids.next()
        child_vertex = pydot.Node(indx, label=str(node.get_label()), *node_style)
        indexes.append(indx)
        graph.add_node(parent_vertex)
        graph.add_node(child_vertex)
        edge = pydot.Edge(parent_vertex, child_vertex, *edge_style)
        graph.add_edge(edge)

    term.traversal(down_func=link_edges,
                   up_func=lambda node, parent_node: indexes.pop())
    return graph


def print_term(term):
    pass



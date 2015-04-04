__author__ = 'mandriy'

from lexer.lexer_utils import Position, Token
from utils.common_utils import interval
import pydot


class Term(object):

    def __init__(self, root):
        self._root = root
        self._root.mark_as_root()

    def match(self, up_match_dict=(), down_match_dict=()):
        pass

    def traversal(self, up_func=lambda node, parent_node: None, down_func=lambda node, parent_node: None):
        def traversal_inner(node, parent_node):
            down_func(node, parent_node)
            if isinstance(node, InteriorNode):
                node.iterate_children(traversal_inner)
            up_func(node, parent_node)
        self._root.iterate_children(traversal_inner)

    def nodes_traversal(self, up_func=lambda node: None, down_func=lambda node: None):
        def traversal_inner(node):
            down_func(node)
            if isinstance(node, InteriorNode):
                node.iterate_children(lambda child_node, parent: traversal_inner(child_node))
            up_func(node)
        traversal_inner(self._root)

    def __eq__(self, other):
        def term_equal(node1, node2):
            def node_equal():
                return node1.get_label() == node2.get_label() and type(node1) == type(node2)

            def children_equal():
                return isinstance(node1, LeafNode) or reduce(lambda prev_subterm_res, tree_subterms:
                                                             prev_subterm_res and term_equal(tree_subterms[0],
                                                                                             tree_subterms[1]),
                                                             zip(node1.children(), node2.children()),
                                                             True)
            return node_equal() and children_equal()
        return term_equal(self._root, other._root)


# TODO add position mixin
class Node(object):

    def __init__(self, label):
        self._label = label

    def get_label(self):
        return self._label


class LeafNode(Node):

    def __init__(self, token):
        super(LeafNode, self).__init__(token.label())
        self._token = token

    def token(self):
        return self._token


class EmptyNode(LeafNode):

    def __init__(self):
        super(EmptyNode, self).__init__(Token('', -1, (0, 0)))


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

    def get_child_by_sort(self, sort):
        for child in self._childred:
            if isinstance(child, InteriorNode) and child.get_label() == sort:
                return child

    def children(self):
        return self._childred


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



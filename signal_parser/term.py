__author__ = 'mandriy'

from lexer.lexer_utils import Position, Token
from utils.common_utils import interval
from functools import partial
import pydot


class Term(object):

    def __init__(self, root):
        self._root = root

    def sort_traversal(self, up_match_dict=(), down_match_dict=()):
        def _match(match_dict, node):
            if node.label() in match_dict:
                match_dict[node.label()](node)
        self.nodes_traversal(partial(_match, up_match_dict), partial(_match, down_match_dict))

    def foreach(self, post_rules=(), pre_rules=()):
        def rules_chain(rules, node):
            for rule in rules:
                rule(node)
        self.nodes_traversal(
            pre_func=partial(rules_chain, pre_rules),
            post_func=partial(rules_chain, post_rules)
        )

    def traverse_nodes_dependencies(self, post_func=lambda node, parent_node: None, pre_func=lambda node, parent_node: None):
        def traversal_inner(node, parent_node):
            pre_func(node, parent_node)
            if isinstance(node, InteriorNode):
                node.iterate_children(traversal_inner)
            post_func(node, parent_node)
        self._root.iterate_children(traversal_inner)

    def nodes_traversal(self, post_func=lambda node: None, pre_func=lambda node: None):
        def traversal_inner(node):
            pre_func(node)
            if isinstance(node, InteriorNode):
                node.iterate_children(lambda child_node, parent: traversal_inner(child_node))
            post_func(node)
        traversal_inner(self._root)

    def __eq__(self, other):
        def term_equal(node1, node2):
            def node_equal():
                return node1.label() == node2.label() and type(node1) == type(node2)

            def children_equal():
                return isinstance(node1, LeafNode) or reduce(lambda prev_subterm_res, tree_subterms:
                                                             prev_subterm_res and term_equal(tree_subterms[0],
                                                                                             tree_subterms[1]),
                                                             zip(node1.children(), node2.children()),
                                                             True)
            return node_equal() and children_equal()
        return term_equal(self._root, other._root)


class Node(object):

    def __init__(self, label):
        self._label = label

    def label(self):
        return self._label


class LeafNode(Node):

    def __init__(self, token):
        super(LeafNode, self).__init__(token.label())
        self._token = token

    def token(self):
        return self._token

    def position(self):
        return self._token.position()


class EmptyNode(LeafNode):

    def __init__(self):
        super(EmptyNode, self).__init__(Token('', -1, (0, 0)))


class IsNotANode(Exception):
    pass


class InteriorNode(Node):

    def __init__(self, sort):
        super(InteriorNode, self).__init__(sort)
        self._children = []

    def add_child(self, child_node):
        if isinstance(child_node, Node):
            self._children.append(child_node)
        else:
            raise IsNotANode(child_node)

    def is_root(self):
        return self._is_root

    def iterate_children(self, func):
        for child in self._children:
            func(child, self)

    def get_child_by_sort(self, sort):
        for child in self._children:
            if isinstance(child, InteriorNode) and child.label() == sort:
                return child

    def children(self):
        return self._children

    def position(self):
        def lookup_position(node):
            if isinstance(node, LeafNode):
                return node.position()
            else:
                lookup_position(node.children[0])
        return lookup_position(self)

    def match(self, *sorts):
        if not sorts:
            if len(self._children) == 1:
                if isinstance(self._children[0], InteriorNode):
                    return self._children[0].match(*sorts)
                elif isinstance(self._children[0], EmptyNode):
                    return []
            return None

        if len(sorts) == 1 and self.label() == sorts[0]:
            return [self]

        sorts_stack = list(sorts)

        def match_child(matching_child):
            if isinstance(matching_child, LeafNode):
                if sorts_stack and matching_child.label() == sorts_stack[0]:
                    sorts_stack.pop(0)
                    return [matching_child]
                else:
                    return None

            sorts_selections = [[]] + [sorts_stack[0:i+1] for i in xrange(len(sorts_stack))]
            sorts_selections.reverse()

            for sorts_selection in sorts_selections:
                child_match_result = matching_child.match(*sorts_selection)
                if child_match_result is not None:
                    for i in xrange(len(sorts_selection)):
                        sorts_stack.pop(0)
                    return child_match_result

            return None

        ret_nodes = []
        for child in self._children:
            child_matching_result = match_child(child)
            if child_matching_result is not None:
                ret_nodes.extend(child_matching_result)
            else:
                return None

        if not sorts_stack:
            return ret_nodes


def term_to_dot(term, node_style=(), edge_style=()):
    graph = pydot.Dot(graph_type='graph')
    ids = interval(0, infinite=True)
    indexes = [ids.next()]

    def link_edges(node, parent_node):
        parent_vertex = pydot.Node(indexes[len(indexes) - 1], label=str(parent_node.label()), *node_style)
        indx = ids.next()
        child_vertex = pydot.Node(indx, label=str(node.label()), *node_style)
        indexes.append(indx)
        graph.add_node(parent_vertex)
        graph.add_node(child_vertex)
        edge = pydot.Edge(parent_vertex, child_vertex, *edge_style)
        graph.add_edge(edge)

    term.traverse_nodes_dependencies(
        pre_func=link_edges,
        post_func=lambda node, parent_node: indexes.pop()
    )
    return graph




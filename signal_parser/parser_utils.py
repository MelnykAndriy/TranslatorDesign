__author__ = 'mandriy'

import pydot


class TokensExhausted(Exception):

    def __init__(self, last_token):
        self._last_token = last_token

    def last_token(self):
        return self._last_token


class TokensIterator(object):

    def __init__(self, tokens):
        self._tokens = tuple(tokens)
        self._current_token = 0
        self._checkpoint_stack = []

    def save_checkpoint(self):
        self._checkpoint_stack.append(self._current_token)

    def back_to_last_checkpoint(self):
        self._current_token = self._checkpoint_stack.pop()

    def confirm_last_checkpoint(self):
        self._checkpoint_stack.pop()

    def current_token(self):
        return self._tokens[self._current_token - 1]

    def next_token(self):
        if self._current_token != len(self._tokens):
            self._current_token += 1
            return self._tokens[self._current_token - 1]
        else:
            raise TokensExhausted(self._tokens[self._current_token - 1])


def term_to_dot(term, node_style=(), edge_style=()):
    graph = pydot.Dot(graph_type='graph')

    def link_edges(node, parent_node):
        edge = pydot.Edge(pydot.Node(parent_node.get_label(), *node_style),
                          pydot.Node(node.get_label(), *node_style),
                          *edge_style)
        graph.add_edge(edge)

    term.traversal(down_func=link_edges)
    return graph


def print_term(term):
    pass

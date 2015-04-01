__author__ = 'mandriy'

import pydot


class TokensExhausted(Exception):

    def __init__(self, last_token):
        self.__last_token__ = last_token

    def last_token(self):
        return self.__last_token__


class TokensIterator:

    def __init__(self, tokens):
        self.__tokens__ = tuple(tokens)
        self.__current_token__ = 0
        self.__checkpoint_stack__ = []

    def save_checkpoint(self):
        self.append(self.__current_token__)

    def back_to_last_checkpoint(self):
        self.__current_token__ = self.__checkpoint_stack__.pop()

    def confirm_last_checkpoint(self):
        self.__checkpoint_stack__.pop()

    def next_token(self):
        if self.__current_token__ != len(self.__tokens__):
            self.__current_token__ += 1
            return self.__tokens__[self.__current_token__ - 1]
        else:
            raise TokensExhausted(self.__tokens__[self.__current_token__ - 1])


def term_to_dot(term, node_style=(), edge_style=()):
    graph = pydot.Dot(graph_type='graph')

    def link_edges(node, parent_node):
        edge = pydot.Edge(Node(parent_node.get_label(), *node_style),
                          Node(node.get_label(), *node_style),
                          *edge_style)
        graph.add_edge(edge)

    term.traversal(down_func=link_edges)
    return graph


def print_term(term):
    pass

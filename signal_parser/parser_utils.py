__author__ = 'mandriy'

import lexer.lexer_utils


class TokensExhausted(Exception):

    def __init__(self, last_token):
        self._last_token = last_token

    def last_token(self):
        return self._last_token


class TokensIterator(object):

    def __init__(self, tokens):
        if tokens:
            token = tokens[len(tokens) - 1]
            pos = token.position()
            terminate_token_pos = (pos.column() + len(token.label()), pos.line())
        else:
            terminate_token_pos = (0, 0)
        self._terminate_token = lexer.lexer_utils.Token('$', ord('$'), terminate_token_pos)
        self._tokens = tuple(list(tokens) + [self._terminate_token])
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

    def has_next_token(self):
        return self._current_token != len(self._tokens)

    def only_terminate_token_left(self):
        return self._tokens[self._current_token].code() == self._terminate_token.code()

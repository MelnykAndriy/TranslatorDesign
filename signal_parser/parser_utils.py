__author__ = 'mandriy'


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

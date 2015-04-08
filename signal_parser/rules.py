__author__ = 'mandriy'

from term import InteriorNode


class TreePattern(object):

    def __init__(self, parent, pattern):
        self._pattern = pattern
        self._base = parent

    def pattern(self):
        return self._pattern

    def base(self):
        return self._base


class Rule(object):

    def __init__(self, mask, match_func):
        self._mask = mask
        self._match_func = match_func

    def __call__(self, node):
        if isinstance(node, InteriorNode) and node.label() == self._mask.base():
            match_res = node.match(*self._mask.pattern())
            if match_res:
                self._match_func(match_res)

__author__ = 'mandriy'


class Position(object):

    def __init__(self, position):
        self._line, self._column = tuple(position)

    def line(self):
        return self._line

    def column(self):
        return self._column

    def position(self):
        return self._line, self._column

    def __eq__(self, other):
        if isinstance(other, Position):
            return self._line == other.line() and self._column == other.column()
        elif isinstance(other, tuple) and len(other) == 2:
            return self._line == other[0] and self._column == other[1]
        else:
            return False


def interval(begin, end=0, infinite=False):
    num = begin
    while infinite or num <= end:
        yield num
        num += 1
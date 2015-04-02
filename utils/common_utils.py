__author__ = 'mandriy'


class PositionMixin(object):

    def __init__(self, position):
        self._line, self._position = tuple(position)

    def position(self):
        return self._line, self._position


def interval(begin, end=0, infinite=False):
    num = begin
    while infinite or num <= end:
        yield num
        num += 1
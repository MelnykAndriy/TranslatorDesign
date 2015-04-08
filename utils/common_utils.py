__author__ = 'mandriy'


class Position(object):

    def __init__(self, position):
        if isinstance(position, Position):
            self._column, self._line = position.position()
        else:
            self._column, self._line, = tuple(position)

    def line(self):
        return self._line

    def column(self):
        return self._column

    def position(self):
        return self._column, self._line,

    def __eq__(self, other):
        if isinstance(other, Position):
            return self._line == other.line() and self._column == other.column()
        elif isinstance(other, tuple) and len(other) == 2:
            return self._line == other[1] and self._column == other[0]
        else:
            return False


def gen_asm_filename(base_name):
    if base_name.endswith('.signal'):
        return base_name.replace('.signal', '.asm')

    return base_name + '.asm'


def interval(begin, end=0, infinite=False):
    num = begin
    while infinite or num <= end:
        yield num
        num += 1
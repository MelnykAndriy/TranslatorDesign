__author__ = 'mandriy'


from common_utils import Position
from sys import stderr


class CompilingError(object):

    def __init__(self, msg, file_coordinates):
        self._msg = msg
        self._pos = Position(file_coordinates)

    def position(self):
        return self._pos

    def what(self):
        col, line = self._pos.position()
        return "%s. Line %d, column %d." % (self._msg, line, col)


def dump_errors(errors, stream=stderr):
    for error in errors:
        print >> stream, error.what()

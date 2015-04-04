__author__ = 'mandriy'


from common_utils import Position


class CompilingError(object):

    def __init__(self, msg, file_coordinates):
        self._msg = msg
        self._pos = Position(file_coordinates)

    def position(self):
        return self._pos

    def what(self):
        pos, line = self.position()
        return "%s. Line %d, position %d." % (self._msg, line, self._pos.position())
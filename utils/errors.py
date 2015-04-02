__author__ = 'mandriy'


from common_utils import PositionMixin


class CompilingError(PositionMixin):

    def __init__(self, msg, file_coordinates):
        super(CompilingError, self).__init__(file_coordinates)
        self._msg = msg

    def what(self):
        pos, line = self.position()
        return "%s. Line %d, position %d." % (self._msg, line, pos)
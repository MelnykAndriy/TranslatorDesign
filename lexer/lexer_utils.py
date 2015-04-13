__author__ = 'mandriy'

from utils.common_utils import interval, Position
from utils.errors import CompilingError


class Token(object):

    def __init__(self, label, code, file_coords):
        self._token__code = code
        self._label = label
        self._pos = Position(file_coords)

    def code(self):
        return self._token__code

    def label(self):
        return self._label

    def position(self):
        return self._pos

    def __eq__(self, other):
        return self._token__code == other.code()

    def __str__(self):
        return self._label


class SignalLexicalError(CompilingError):

    def __init__(self, msg, file_coords):
        super(SignalLexicalError, self).__init__(msg, file_coords)

    def what(self):
        return 'Lexical Error : %s' % super(SignalLexicalError, self).what()


class InvalidToken(SignalLexicalError):

    def __init__(self, file_coords):
        super(InvalidToken, self).__init__("Invalid token", file_coords)


class UnclosedComment(SignalLexicalError):

    def __init__(self, file_coords):
        super(UnclosedComment, self).__init__("Commet's end was not found", file_coords)


class CodeTable(object):

    def __init__(self, code_interval_start, code_interval_finish=None):
        self._rep = dict()
        if code_interval_finish is None:
            self._identifier_code_generator = interval(code_interval_start, infinite=True)
        else:
            self._identifier_code_generator = interval(code_interval_start, code_interval_finish)

    def insert(self, item):
        if item not in self._rep.values():
            item_code = self._identifier_code_generator.next()
            self._rep[item_code] = item
            return item_code
        else:
            return [item_code for item_code in self._rep.keys() if self._rep[item_code] == item][0]

    def extend(self, items):
        return tuple(map(lambda item: self.insert(item), items))

    def get_item_by_code(self, code):
        if code in self._rep.keys():
            return self._rep[code]

    def get_code_by_item(self, item):
        if item in self._rep.values():
            return [code for code, sitem in self._rep.items() if sitem == item][0]

    def contain_code(self, code):
        return code in self._rep.keys()

    def contain_item(self, item):
        return item in self._rep.values()


_identifiers_interval = (1001, None)
_constants_interval = (501, 1000)


def is_identifier_code(code):
    a = _identifiers_interval[0]
    return a <= code


def is_constant_code(code):
    a, b = _constants_interval
    return a <= code <= b


class ConstantsTable(CodeTable):

    def __init__(self):
        super(ConstantsTable, self).__init__(*_constants_interval)


class IdentifiersTable(CodeTable):

    def __init__(self):
        super(IdentifiersTable, self).__init__(*_identifiers_interval)

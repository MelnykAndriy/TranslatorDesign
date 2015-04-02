__author__ = 'mandriy'


class PositionMixin(object):

    def __init__(self, position):
        self._line, self._position = tuple(position)

    def position(self):
        return self._line, self._position


class Token(PositionMixin):

    def __init__(self, label, code, file_coords):
        super(Token, self).__init__(file_coords)
        self._token__code = code
        self._label = label

    def code(self):
        return self._token__code

    def label(self):
        return self._label


class LexicalError(PositionMixin):

    def __init__(self, msg, file_coordinates):
        super(LexicalError, self).__init__(file_coordinates)
        self._msg = msg

    def what(self):
        pos, line = self.position()
        return "%s. Line %d, position %d." % (self._msg, line, pos)


class InvalidToken(LexicalError):

    def __init__(self, file_coords):
        super(InvalidToken, self).__init__("Invalid token.", file_coords)


class UnclosedComment(LexicalError):

    def __init__(self, file_coords):
        super(UnclosedComment, self).__init__("Commet's end was not found.", file_coords)


def interval(begin, end=0, infinite=False):
    num = begin
    while infinite or num <= end:
        yield num
        num += 1


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

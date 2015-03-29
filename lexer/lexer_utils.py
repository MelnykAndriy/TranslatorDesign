__author__ = 'mandriy'


class PositionMixin:

    def __init__(self, position):
        self.__line__, self.__position__ = tuple(position)

    def position(self):
        return self.__line__, self.__position__


class Token(PositionMixin):

    def __init__(self, code, file_coords):
        PositionMixin.__init__(self, file_coords)
        self.__token__code__ = code

    def code(self):
        return self.__token__code__


class LexicalError(PositionMixin):

    def __init__(self, msg, file_coordinates):
        PositionMixin.__init__(self, file_coordinates)
        self.__msg__ = msg

    def what(self):
        pos, line = self.position()
        return "%s. Line %d, position %d." % (self.__msg__, line, pos)


class InvalidToken(LexicalError):

    def __init__(self, file_coords):
        LexicalError.__init__(self, "Invalid token.", file_coords)


class UnclosedComment(LexicalError):

    def __init__(self, file_coords):
        LexicalError.__init__(self, "Commet end was not found.", file_coords)


def interval(begin, end=0, infinite=False):
    num = begin
    while infinite or num <= end:
        yield num
        num += 1


class CodeTable:

    def __init__(self, code_interval_start, code_interval_finish=None):
        self.__rep__ = dict()
        if code_interval_finish is None:
            self.__identifier_code_generator = interval(code_interval_start, infinite=True)
        else:
            self.__identifier_code_generator = interval(code_interval_start, code_interval_finish)

    def insert(self, item):
        if item not in self.__rep__.values():
            item_code = self.__identifier_code_generator.next()
            self.__rep__[item_code] = item
            return item_code
        else:
            return [item_code for item_code in self.__rep__.keys() if self.__rep__[item_code] == item][0]

    def extend(self, items):
        return tuple(map(lambda item: self.insert(item), items))

    def get_item_by_code(self, code):
        if code in self.__rep__.keys():
            return self.__rep__[code]

    def get_code_by_item(self, item):
        if item in self.__rep__.values():
            return [code for code, sitem in self.__rep__.items() if sitem == item][0]

    def contain_code(self, code):
        return code in self.__rep__.keys()

    def contain_item(self, item):
        return item in self.__rep__.values()

__identifiers_interval__ = (1001, None)
__constants_interval__ = (501, 1000)


def is_identifier_code(code):
    a = __identifiers_interval__[0]
    return a <= code


def is_constant_code(code):
    a, b = __constants_interval__
    return a <= code <= b


class ConstantsTable(CodeTable):

    def __init__(self):
        CodeTable.__init__(self, *__constants_interval__)


class IdentifiersTable(CodeTable):

    def __init__(self):
        CodeTable.__init__(self, *__identifiers_interval__)

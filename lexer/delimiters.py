__author__ = 'mandriy'

SEMICOLON = ord(';')
COLON = ord(':')
COMMA = ord(',')
OPEN_PARENTHESIS = ord('(')
CLOSE_PARENTHESIS = ord(')')
ASSEMBLY_INSERT_BEGIN = 301
ASSEMBLY_INSERT_END = 302

_delimiters = {
    ';': SEMICOLON,
    ':': COLON,
    ',': COMMA,
    '(': OPEN_PARENTHESIS,
    ')': CLOSE_PARENTHESIS,
    '($': ASSEMBLY_INSERT_BEGIN,
    '$)': ASSEMBLY_INSERT_END
}


def is_delimiter_code(code):
    return code in _delimiters.values()


class BadDelimiter(Exception):
    pass


def is_delimiter(s):
    return s in _delimiters


def delimiter_code(s):
    try:
        return _delimiters[s]
    except KeyError:
        raise BadDelimiter()


def delimiter_by_code(code):
    dm = [dm for dm in _delimiters if _delimiters[dm] == code]
    if dm:
        return dm[0]
    else:
        raise Exception('There is no known delimiter for provided code.')
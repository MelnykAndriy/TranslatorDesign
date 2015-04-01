__author__ = 'mandriy'

COMMA = ord(',')
SEMICOLON = ord(';')
DOT = ord('.')
COLON = ord(':')

__single_character_delimiters__ = {
    ',': COMMA,
    ';': SEMICOLON,
    '.': DOT,
    ':': COLON
}


def is_delimiter_code(code):
    return code in __single_character_delimiters__.values()


class BadDelimiter(Exception):
    pass


def is_delimiter(s):
    return s in __single_character_delimiters__.keys()


def delimiter_code(s):
    try:
        return __single_character_delimiters__[s]
    except KeyError:
        raise BadDelimiter()
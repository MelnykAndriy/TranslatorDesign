__author__ = 'mandriy'

SEMICOLON = ord(';')
DOT = ord('.')
PLUS = ord('+')
MINUS = ord('-')
EQUAL = ord('=')
SHARP = ord('#')


_single_character_delimiters = {
    ';': SEMICOLON,
    '.': DOT,
    '+': PLUS,
    '-': MINUS,
    '=': EQUAL,
    '#': SHARP
}


def is_delimiter_code(code):
    return code in _single_character_delimiters.values()


class BadDelimiter(Exception):
    pass


def is_delimiter(s):
    return s in _single_character_delimiters


def delimiter_code(s):
    try:
        return _single_character_delimiters[s]
    except KeyError:
        raise BadDelimiter()


def delimiter_by_code(code):
    dm = [dm for dm in _single_character_delimiters if _single_character_delimiters[dm] == code]
    if dm:
        return dm[0]
    else:
        raise Exception('There is no known delimiter for provided code.')
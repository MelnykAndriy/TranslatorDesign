__author__ = 'mandriy'


PROGRAM = 401
BEGIN = 402
END = 403
LABEL = 404
GOTO = 405
LINK = 406
IN = 407
OUT = 408

__keywords__ = {
    'PROGRAM': PROGRAM,
    'BEGIN': BEGIN,
    'END': END,
    'LABEL': LABEL,
    'GOTO': GOTO,
    'LINK': LINK,
    'IN': IN,
    'OUT': OUT
}


def is_keyword_code(code):
    return code in __keywords__.values()


class BadKeyword(Exception):
    pass


def is_keyword(s):
    return s.upper() in __keywords__.keys()


def keyword_code(s):
    try:
        return __keywords__[s.upper()]
    except KeyError:
        raise BadKeyword()


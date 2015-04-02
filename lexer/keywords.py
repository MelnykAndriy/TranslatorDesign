__author__ = 'mandriy'


PROGRAM = 401
BEGIN = 402
END = 403
LABEL = 404
GOTO = 405
LINK = 406
IN = 407
OUT = 408

_keywords = {
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
    return code in _keywords.values()


class BadKeyword(Exception):
    pass


def is_keyword(s):
    return s in _keywords


def keyword_code(s):
    try:
        return _keywords[s]
    except KeyError:
        raise BadKeyword()


def keyword_by_code(code):
    keyword = [keyword for keyword in _keywords if _keywords[keyword] == code]
    if keyword:
        return keyword[0]
    else:
        raise Exception('There is no known keyword for provided code.')


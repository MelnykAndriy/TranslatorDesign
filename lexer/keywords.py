__author__ = 'mandriy'


BEGIN = 402
END = 403
GOTO = 404
PROCEDURE = 405
LABEL = 406
RETURN = 407

_keywords = {
    'PROCEDURE': PROCEDURE,
    'BEGIN': BEGIN,
    'END': END,
    'GOTO': GOTO,
    'LABEL': LABEL,
    'RETURN': RETURN,
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


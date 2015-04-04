__author__ = 'mandriy'

import utils.errors
import lexer.lexer_utils
import functools


def make_error_case(error_type, *args):
    return functools.partial(error_type, *args)


class SyntaxErrorFound(Exception):

    def __init__(self, error_case):
        self._error_case = error_case

    def make_error_report(self, pos):
        return self._error_case(pos)


class StandardErrorHandler(object):

    def __init__(self, error_case):
        self._error_case = error_case

    def __call__(self):
        raise SyntaxErrorFound(self._error_case)


class ErrorCase(object):

    def __init__(self, case_handler, error_handler=lambda: None):
        self._func = case_handler
        self._error_handler = error_handler

    def __call__(self, *args):
        func_result = self._func(*args)
        if not func_result:
            self._error_handler()
        return func_result


class SignalSyntaxError(utils.errors.CompilingError):

    def __init__(self, msg, file_coords):
        super(SignalSyntaxError, self).__init__(msg, file_coords)

    def what(self):
        return 'Syntax Error : %s' % super(SignalSyntaxError, self).what()


class ExpectedToken(SignalSyntaxError):

    def __init__(self, token_label, file_coords):
        super(ExpectedToken, self).__init__('%s is expected' % token_label, file_coords)


class MissedToken(SignalSyntaxError):

    def __init__(self, token_label, file_coords):
        super(MissedToken, self).__init__('%s is missed' % token_label, file_coords)


class ExtraTokens(SignalSyntaxError):

    def __init__(self, file_coords):
        super(ExtraTokens, self).__init__('Extra tokens', file_coords)


class InvalidLabelDefinition(SignalSyntaxError):

    def __init__(self, file_coords):
        super(InvalidLabelDefinition, self).__init__('Label should be defined as unsigned integer', file_coords)


class EmptyLabeledStatement(SignalSyntaxError):

    def __init__(self, file_coords):
        super(EmptyLabeledStatement, self).__init__('Statement is neccessary after label', file_coords)


class GotoStatementArgument(SignalSyntaxError):

    def __init__(self, file_coords):
        super(GotoStatementArgument, self).__init__('GOTO argument have to be an unsigned integer number', file_coords)


class InStatementArgument(SignalSyntaxError):

    def __init__(self, file_coords):
        super(InStatementArgument, self).__init__('IN argument have to be an unsigned integer number', file_coords)


class OutStatementArgument(SignalSyntaxError):

    def __init__(self, file_coords):
        super(OutStatementArgument, self).__init__('OUT argument have to be an unsigned integer number', file_coords)


class LinkStatementArguments(SignalSyntaxError):

    def __init__(self, file_coords):
        super(LinkStatementArguments, self).__init__('Link statement arguments are incorrect', file_coords)

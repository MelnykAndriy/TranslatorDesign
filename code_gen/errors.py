__author__ = 'mandriy'

import utils.errors


class SemanticError(utils.errors.CompilingError):

    def __init__(self, msg, file_coords):
        super(SemanticError, self).__init__(msg, file_coords)

    def what(self):
        return 'Semantic Error : %s' % super(SemanticError, self).what()


class DuplicateLabelName(SemanticError):

    def __init__(self, file_coords):
        super(DuplicateLabelName, self).__init__('Label with such name is already defined', file_coords)


class GotoUnresolvedLabel(SemanticError):

    def __init__(self, file_coords):
        super(GotoUnresolvedLabel, self).__init__('Goto label is unresolved', file_coords)


class UndeclaredLabel(SemanticError):

    def __init__(self, file_coords):
        super(UndeclaredLabel, self).__init__('Label is undeclared', file_coords)


class LabelLinkAmbiguity(SemanticError):

    def __init__(self, file_coords):
        super(LabelLinkAmbiguity, self).__init__('Label link is already defined', file_coords)


class PortDirectionConfilct(SemanticError):

    def __init__(self, file_coords):
        super(PortDirectionConfilct, self).__init__('Oposite port direction was already specified', file_coords)


class UnresolvedPort(SemanticError):

    def __init__(self, file_coords):
        super(UnresolvedPort, self).__init__('Port number is not resolved', file_coords)


class AlreadyLinkedPort(SemanticError):

    def __init__(self, file_coords):
        super(AlreadyLinkedPort, self).__init__('Port with such number is already linked', file_coords)

__author__ = 'mandriy'

import keywords
import delimiters
from lexer_utils import *


class SignalLexicalAnalysis(object):

    def __init__(self, predefined_constants=(), predefined_identifiers=()):
        self._tokens = []
        self._constant_table = ConstantsTable()
        self._identifiers_table = IdentifiersTable()
        self._errors = []
        self._constant_table.extend(predefined_constants)
        self._identifiers_table.extend(predefined_identifiers)

    def constants(self):
        return self._constant_table

    def identifiers(self):
        return self._identifiers_table

    def errors(self):
        return self._errors
    
    def tokens(self):
        return self._tokens

    def __call__(self, program_text):
        file_coordinates = [0, 1]
        self._errors = []

        def pos_inc(c):
            if c == '\t':
                return 4
            else:
                return 1

        def with_file_position(c, prev=[' '], coords=file_coordinates):
            if prev[0] == '\n':
                coords[0] = 0
                coords[1] += 1
            coords[0] += pos_inc(c)
            prev[0] = c
            return c

        program = (with_file_position(ch) for ch in program_text + ' ')
        tokens = []
        inside_comment = False
        try:
            current_character = program.next()

            def canon_file_pos(token):
                pos, line = file_coordinates
                return pos - len(token), line

            def report_invalid_token(token):
                self._errors.append(InvalidToken(canon_file_pos(token)))

            def iterate_to_the_token_end_and_report_error(invalid_token_begin, start_ch):
                invalid_token = invalid_token_begin
                iter_ch = start_ch
                while not (delimiters.is_delimiter(iter_ch) or iter_ch.isspace()):
                    invalid_token += iter_ch
                    iter_ch = program.next()
                report_invalid_token(invalid_token)
                return iter_ch

            while True:
                while current_character.isspace():
                    current_character = program.next()

                if delimiters.is_delimiter(current_character):
                    tokens.append(Token(current_character,
                                        ord(current_character),
                                        file_coordinates))
                    current_character = program.next()
                    continue

                if current_character.isalpha():
                    identifier = ''
                    while current_character.isalnum():
                        identifier += current_character
                        current_character = program.next()
                    if delimiters.is_delimiter(current_character) or current_character.isspace():
                        if keywords.is_keyword(identifier):
                            tokens.append(Token(identifier,
                                                keywords.keyword_code(identifier),
                                                canon_file_pos(identifier)))
                        else:
                            tokens.append(Token(identifier,
                                                self._identifiers_table.insert(identifier),
                                                canon_file_pos(identifier)))
                    else:
                        current_character = iterate_to_the_token_end_and_report_error(identifier, current_character)
                    continue

                if current_character.isdigit():
                    unsiged_integer = ''
                    while current_character.isdigit():
                        unsiged_integer += current_character
                        current_character = program.next()
                    if delimiters.is_delimiter(current_character) or current_character.isspace():
                        tokens.append(Token(unsiged_integer,
                                            self._constant_table.insert(int(unsiged_integer)),
                                            canon_file_pos(unsiged_integer)))
                    else:
                        current_character = iterate_to_the_token_end_and_report_error(unsiged_integer,
                                                                                      current_character)
                    continue

                if current_character == '*':
                    current_character = program.next()
                    if current_character == '<':
                        inside_comment = canon_file_pos('*')
                        prev_char = ' '
                        while not (prev_char == '>' and current_character == '*'):
                            prev_char = current_character
                            current_character = program.next()
                        inside_comment = False
                        current_character = program.next()
                    else:
                        report_invalid_token('*')
                    continue

                report_invalid_token(current_character)
                current_character = program.next()

        except StopIteration:
            if inside_comment:
                self._errors.append(UnclosedComment(inside_comment))
            self._tokens = tuple(tokens)
            return self._tokens

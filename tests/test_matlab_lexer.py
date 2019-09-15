import unittest

import pymatlabparser.matlab_lexer

class Test_matlab_lexer(unittest.TestCase):
    def setUp(self):
        self.matlab_lexer = pymatlabparser.matlab_lexer.MatlabLexer()

    def _check_token_type_and_value(self, string, token_type):
        tokens = [token for token in self.matlab_lexer.tokenize(string)]
        self.assertEqual(len(tokens), 1, 'Lexer produced wrong number of tokens')
        token = tokens[0]
        self.assertTrue(token.type == token_type and (token_type == 'ERROR' or token.value == string),
                        'Lexer produced wrong token type and/or value')

    def test_token_types(self):

        # Testing for single number tokens
        self._check_token_type_and_value('1', 'NUMBER')
        self._check_token_type_and_value('1.', 'NUMBER')
        self._check_token_type_and_value('1.1', 'NUMBER')
        self._check_token_type_and_value('.1', 'NUMBER')
        self._check_token_type_and_value('111.111', 'NUMBER')
        self._check_token_type_and_value('1e1', 'NUMBER')
        self._check_token_type_and_value('1e0', 'NUMBER')
        self._check_token_type_and_value('1e-1', 'NUMBER')
        self._check_token_type_and_value('.1e-1', 'NUMBER')
        self._check_token_type_and_value('1.e-1', 'NUMBER')
        self._check_token_type_and_value('1.e+1', 'NUMBER')
        self._check_token_type_and_value('123.456e+00789', 'NUMBER')


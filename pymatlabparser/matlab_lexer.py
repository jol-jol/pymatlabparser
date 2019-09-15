import sly

tokens_dict = dict((
    # Reserved keywords in Matlab
    # check this by typing "edit iskeywords" in Matlab command
    ('BREAK', 'break(?=\\W)'),                              ('CASE', 'case(?=\\W)'),
    ('CATCH', 'catch(?=\\W)'),                              ('OTHERWISE', 'otherwise(?=\\W)'),
    ('CONTINUE', 'continue(?=\\W)'),                        ('ELSE', 'else(?=\\W)'),
    ('ELSEIF', 'elseif(?=\\W)'),                            ('END', 'end(?=\\W)'),
    ('FOR', 'for(?=\\W)'),                                  ('FUNCTION', 'function(?=\\W)'),
    # ('GLOBAL', 'global(?=\\W)'),  ## treated as a command (see below comments on "command")
    ('IF', 'if(?=\\W)'),                                    ('RETURN', 'return(?=\\W)'),
    ('SWITCH', 'switch(?=\\W)'),                            ('TRY', 'try(?=\\W)'),
    ('WHILE', 'while(?=\\W)'),
    # Following are not supported yet
    # ('CLASSDEF', 'classdef(?=\\W)'),                      ('PARFOR', 'parfor(?=\\W)'),
    # ('PERSISTENT', 'persistent(?=\\W)'),                  ('SPMD', 'spmd(?=\\W)'),

    # Special syntax in Matlab that is better handled using lexer here - that is the command syntax
    # ... The command syntax is "COMMAND arg1 arg2 arg3 ...", which is special because args can be any characters
    # ... For example, "X .Y" is considered a command while "X.Y" is considered an expression in Matlab
    # ... This inevitably mis-classifies expressions, but it also happens in Matlab
    # ... For example, if a = 3, then "a + 4" gives 7 while "a +4" gives an error
    # ... These are hard to be distinguished at parser level, so handling here at lexer level
    # ... However, currently it's a bit inconsistent with Matlab - "a +4" is equivalent to "a + 4" here
    ('COMMAND', r'[a-zA-Z_][a-zA-Z0-9_]*[ \t]+?[a-zA-Z_][a-zA-Z0-9_]*?(;|\n)'),

    # General tokens
    ('NAME', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUMBER', r'((\d+\.?\d*)|(\.\d+))(e[\+\-]*\d+)*'),
    ('STRING', r'(".*?")|((?<=\W)\'.*?\')|(^\'.*?\')'),   # need to avoid single quote being used as transpose
    ('ignore_COMMENT', r'(%{(.|\s)*?%})|(%.*?\n)'),
    ('NEWLINE', r'\n'),

    # Special symbols
    # https://www.mathworks.com/help/matlab/matlab_prog/matlab-operators-and-special-characters.html

    # Arithmetic operators (all operators except uplus and uminus are implemented)
    ('MTIMES', r'\.\*'),        ('MRDIVIDE', r'\./'),       ('MLDIVIDE', r'\.\\'),          ('MPOWER', r'\.\^'),
    ('TRANSPOSE', r'\.\''),     ('PLUS', r'\+'),            ('MINUS', r'-'),                ('TIMES', r'\*'),
    ('RDIVIDE', r'/'),          ('LDIVIDE', r'\\'),         ('POWER', r'\^'),               ('CTRANSPOSE', r'\''),

    # Relational operators
    ('EQ', '=='),               ('GE', '>='),               ('LE', '<='),                   ('NE', '~='),
    ('GT', '>'),                ('LT', '<'),

    # Logical operators
    ('ANDAND', '&&'),           ('OROR', r'\|\|'),          ('AND', '&'),                   ('OR', r'\|'),
    ('NOT', '~'),

    # # Non-operator special characters (all are implemented except TILDE which is NOT)
    ('AT', '@'),                ('DOT', r'\.'),             ('ELLIPSIS', r'\.\.\.'),        ('COMMA', ','),
    ('COLON', ':'),             ('SEMICOLON', ';'),         ('LPAREN', r'\('),              ('RPAREN', r'\)'),
    ('LSQR', r'\['),            ('RSQR', r'\]'),            ('LCURL', '{'),                 ('RCURL', '}'),
    # ('EXCLAIM', '!'),            ('QUES', r'\?'),     # EXCLAIM AND QUES are not supported yet
    ('ASSIGN', '='),
))

class MatlabLexer(sly.Lexer):

    tokens = list(tokens_dict.keys())

    vars().update(tokens_dict)

    ignore = ' \t'
    #ignore_COMMENT = r'(%{(.|\s)*?%})|(%.*?\n)'

    # Extra action for newlines
    @_(r'\n+')
    def NEWLINE(self, t):
        self.lineno += t.value.count('\n')
        return t

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1
        return t

    def tokenize(self, text, lineno=1, index=0):
        return super().tokenize(text + '\n', lineno, index)

if __name__ == '__main__':
    lexer = MatlabLexer()
    while True:
        data = input('enter input (nothing to exit): ')
        if data == '': break
        tokens = [tok for tok in lexer.tokenize(data)]
        for tok in tokens:
            print(tok)

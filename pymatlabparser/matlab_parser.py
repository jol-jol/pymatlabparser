import sys
import sly
from matlab_lexer import MatlabLexer

class MatlabParser(sly.Parser):

    debugfile = 'parser.out'

    # Get the token list from the lexer (required)
    tokens = MatlabLexer.tokens

    # The official operator precedence for MATLAB is found at
    # https://www.mathworks.com/help/matlab/matlab_prog/operator-precedence.html
    precedence = (
        ('left', ASSIGN),
        ('left', COMMA),
        ('left', OROR),
        ('left', ANDAND),
        ('left', OR),
        ('left', AND),
        ('left', LT, LE, GT, GE, EQ, NE),
        ('left', COLON),
        ('left', PLUS, MINUS),
        ('left', MTIMES, MRDIVIDE, MLDIVIDE, TIMES, RDIVIDE, LDIVIDE),
        ('left', NOT),
        ('left', TRANSPOSE, POWER, CTRANSPOSE, MPOWER),
        ('left', DOT),
    )

   # -------------- dealing with code_blocks -------------------
    @_('code_block statement')
    def code_block(self, p):
        return ('code_block', p[0][1] + (p[1],))

    @_('statement code_block')
    def code_block(self, p):
        return ('code_block', (p[0],) + p[1][1])

    @_('statement')
    def code_block(self, p):
        return ('code_block', (p[0],))

    # -------------- dealing with reserved keywords -------------
    @_('FUNCTION statement code_block END NEWLINE')
    def statement(self, p):
        return ('func_def', (('function', p[1][1]),
                             ('body', p[2][1]),
                             ))

    @_('RETURN expr NEWLINE', 'RETURN expr SEMICOLON')
    def statement(self, p):
        return ('return', (p[1],
                           ))

    @_('FOR statement code_block END NEWLINE',
       'FOR statement code_block END SEMICOLON')
    def statement(self, p):
        return ('for_loop', (('for', p[1][1]),
                             ('body', p[2][1]),
                             ))

    @_('CONTINUE NEWLINE', 'BREAK NEWLINE', 'CONTINUE SEMICOLON', 'BREAK SEMICOLON')
    def statement(self, p):
        return (p[0],)

    @_('if_block END NEWLINE', 'if_block END SEMICOLON')
    def statement(self, p):
        return p[0]

    @_('if_block ELSE NEWLINE code_block')
    def if_block(self, p):
        return ('if_block', p[0][1] + (('else_body', p[3][1]),
                                       ))

    @_('if_block ELSE SEMICOLON code_block')
    def if_block(self, p):
        return ('if_block', p[0][1] + (('else_body', p[3][1]),
                                       ))

    @_('if_block ELSEIF statement code_block')
    def if_block(self, p):
        return ('if_block', p[0][1] + (('elseif', p[2][1]),
                                       ('body', p[3][1]),
                                       ))

    @_('IF statement code_block')
    def if_block(self, p):
        return ('if_block', (('if', p[1][1]),
                             ('body', p[2][1]),
                             ))

    @_('WHILE statement code_block END NEWLINE')
    def statement(self, p):
        return ('while', (('while', p[1][1]),
                          ('body', p[2][1]),
                          ))

    @_('TRY code_block CATCH statement code_block END NEWLINE')
    def statement(self, p):
        return ('try_catch', (('try', p[1][1]),
                              ('catch', p[3][1]),
                              ('body', p[4][1]),
                              ))

    @_('switch_block END NEWLINE')
    def statement(self, p):
        return p[0]

    @_('switch_block OTHERWISE SEMICOLON code_block END NEWLINE',
       'switch_block OTHERWISE NEWLINE code_block END NEWLINE',
       'switch_block OTHERWISE SEMICOLON code_block END SEMICOLON',
       'switch_block OTHERWISE NEWLINE code_block END SEMICOLON'
       )
    def statement(self, p):
        return ('switch_block', p[0][1] + (('otherwise', p[3][1]),
                                           ))

    @_('switch_block CASE statement code_block')
    def switch_block(self, p):
        return ('switch_block', p[0][1] + (('case', p[2][1]),
                                           ('body', p[3][1]),
                                           ))

    @_('SWITCH statement CASE statement code_block')
    def switch_block(self, p):
        return ('switch_block', (('switch', p[1][1]),
                                 ('case', p[3][1]),
                                 ('body', p[4][1]),
                                 ))

    # -------------- dealing with statements --------------------
    @_('SEMICOLON', 'NEWLINE')                      # empty lines with only semicolon/newline, e.g. ;;;;
    def statement(self, p):
        return ('statement', (p[0],))

    @_('expr SEMICOLON')                            # semicolon termination tells Matlab not to display the results
    def statement(self, p):                         # (will distinguish this in later versions)
        return ('statement', (p[0],))

    @_('expr NEWLINE')                              # a newline without semicolon tells Matlab to display the results
    def statement(self, p):                         # (will distinguish this in later versions)
        return ('statement', (p[0],))

    @_('COMMAND')                                   # e.g. clear var1 var2
    def statement(self, p):
        return ('command', (p[0],))

    # -------------- dealing with function call/array indexing syntax --------------
    @_('expr LPAREN args RPAREN')                   # e.g. my_function(pi, 2)
    def expr(self, p):
        called = ('expr', (p[0],))                  # creates a new node for the called expression
        return ('func_call/array_idxing', (called,  # the called expression
                                           p[2]))   # the arguments

    @_('expr LCURL args RCURL')                     # e.g. my_function{pi, 2}
    def expr(self, p):
        called = ('expr', (p[0],))                  # creates a new node for the called expression
        return ('cell_array_idxing', (called,       # the called expression
                                      p[2]))        # the arguments

    @_('args COMMA expr')                           # e.g. pi, 2, new_variable
    def args(self, p):
        return ('args', p[0][1] + (p[2],))          # concatenating the existing args tuple with the new expr

    @_('expr COMMA expr')                           # e.g. pi, 2
    def args(self, p):
        return ('args', (p[0],                      # expression before the comma
                         p[2]))                     # expression after the comma

    @_('expr')                                      # any expression could be elevated to arguments
    def args(self, p):
        return ('args', (p[0],))

    # -------------- dealing with matrx/cell array expression syntax ----------------
    @_('LCURL matrx_rows RCURL')                    # e.g. {3 5 a 2^3; 3 5 a 2^3;} (no semicolon in the last row)
    def expr(self, p):
        return ('cell_array', (p[1],))

    @_('LCURL matrx_elements RCURL')                # e.g. {3 5 a 2^3} (no semicolon in the last row)
    def expr(self, p):
        return ('cell_array', (p[1],))

    # the following permits the last row to not end with a semicolon
    @_('LCURL matrx_rows matrx_elements RCURL')     # e.g. {3 5 a 2^3; 3 5 a 2^3} (no semicolon in the last row)
    def expr(self, p):
        existing_matrx_rows = p[1][1]
        new_matrx_row = (p[2],)
        return ('cell_array', (('matrix rows',
                                existing_matrx_rows + new_matrx_row  # concatenating the two tuples
                                ),)
                )

    @_('LSQR matrx_rows RSQR')                      # e.g. [3 5 a 2^3; 3 5 a 2^3;]
    def expr(self, p):
        return ('matrx', (p[1],))

    @_('LSQR matrx_elements RSQR')                  # e.g. [3 5 a 2^3] (no semicolon in the last row)
    def expr(self, p):
        return ('matrx', (p[1],))

    # the following permits the last row to not end with a semicolon
    @_('LSQR matrx_rows matrx_elements RSQR')       # e.g. [3 5 a 2^3; 3 5 a 2^3] (no semicolon in the last row)
    def expr(self, p):
        existing_matrx_rows = p[1][1]
        new_matrx_row = (p[2],)
        return ('matrx', (('matrix rows',
                           existing_matrx_rows + new_matrx_row  # concatenating the two tuples
                           ),)
                )

    @_('matrx_rows matrx_elements SEMICOLON')       # e.g. 3 5 a 2^3; 3 5 a 2^3;
    def matrx_rows(self, p):
        return ('matrx_rows', p[0][1] + (p[1],))    # elevating the matrx_elements to a new matrx_rows using tuple

    @_('matrx_elements SEMICOLON')                  # e.g. 3 5 a 2^3;
    def matrx_rows(self, p):
        return ('matrx_rows', (p[0],))

    @_('matrx_elements matrx_elements')             # e.g. 3 5 a 2^3
    def matrx_elements(self, p):
        return ('matrx_elements', p[0][1] + p[1][1])

    @_('matrx_elements COMMA matrx_elements')       # e.g. 3, 5, a, 2^3  (COMMA makes no difference than space)
    def matrx_elements(self, p):
        return ('matrx_elements', p[0][1] + p[2][1])

    @_('expr')                                      # any expression could be elevated to matrx_elements
    def matrx_elements(self, p):
        return ('matrx_elements', (p[0],))


    # -------------- dealing with syntax-related expressions ------------
    @_('expr ASSIGN expr')                          # e.g. x(5, 6) = 100/5 + 3
    def expr(self, p):
        return ('assign', (p[0],                    # expression of the variable be assigned to (left-hand side)
                           p[2]))                   # expression of the value to assign (right-hand side)

    @_('LPAREN expr RPAREN')                        # e.g. (x + y + z)
    def expr(self, p):
        return ('bracket', (p[1],))

    @_('expr ELLIPSIS NEWLINE')                     # e.g. length = sqrt(x ^ 2 + y ^ 2 + ...
    def expr(self, p):
        return p[0]                                 # just ignores the ellipsis and newline and returns expr intact

    @_('expr DOT NAME')                             # e.g. my_variable.property
    def expr(self, p):
        return ('dot', (p[0],                       # the expression before the dot
                        (p[2],)))                   # the NAME after the dot (need tuple b/c it's NAME, not expr)

    @_('AT LPAREN args RPAREN expr')                # e.g. @(x, y) x + y^2
    def expr(self, p):
        return ('anonym_func', (p[2],               # arguments inside the parentheses
                                ('expr', (p[4],))   # expression for the anonymous function
                                ))

    # -------------- dealing with arithmetic expressions -------------------
    @_('PLUS expr', 'MINUS expr', 'NOT expr')       # e.g. - 5 (for unary plus and minus)
    def expr(self, p):
        return ('unary %s oper'%p[0], (p[1],))

    @_('expr COLON expr')                           # e.g. 5 : 25
    def expr(self, p):
        return ('range ', (p[0],                    # expression before the colon
                           p[2]))                   # expression after the colon

    @_('expr OROR expr',    'expr ANDAND expr',     'expr OR expr',     'expr AND expr',
       'expr LT expr',      'expr LE expr',         'expr GT expr',     'expr GE expr',
       'expr EQ expr',      'expr NE expr',         'expr PLUS expr',   'expr MINUS expr',
       'expr MTIMES expr',  'expr MRDIVIDE expr',   'expr MLDIVIDE expr',   'expr TIMES expr',
       'expr RDIVIDE expr', 'expr LDIVIDE expr',    'expr POWER expr',  'expr MPOWER expr',)         # e.g. x * y
    def expr(self, p):
        return ('"%s" oper'%p[1], (p[0],            # expression before the binary_operator
                                   p[2]))           # expression after the binary_operator

    @_('expr TRANSPOSE',    'expr CTRANSPOSE')
    def expr(self, p):
        return ('"%s" oper'%p[1], (p[0],))

    @_('NAME', 'NUMBER', 'STRING')                  # e.g. x, 56, 3e-2, "example"
    def expr(self, p):
        return (p[0],)      # creates a tuple for the token to avoid strings getting concatenated later on

if __name__ == '__main__':
    lexer = MatlabLexer()
    parser = MatlabParser()

    from matlab_ast_visualization import display_tree
    while True:
        try:
            text = input('enter input (nothing to exit): ')
            if text == '':
                break
            result = parser.parse(lexer.tokenize(text))
            print(display_tree(result))
        except EOFError:
            break
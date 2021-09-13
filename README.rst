===============
pymatlabparser
===============

Disclaimer: This is a side project of mine and has not been rigorously tested.

**pymatlabparser** is a parser for Matlab/Octave language, a popular language
in engineering and engineering education. This parser can handle many of the
unique syntax rules of Matlab, such as:


- Apostrophe's dual role for quotation (`'strings'`) and matrix transpose (`matrix'`)
    Input: `{'ABC' ABC'}`

.. code::

    code_block ──── statement ──── cell_array ──── matrx_elements ─┬── 'ABC'
                                                                   └── "'" oper ──── ABC

- Dot's dual role for accessing a struct's field (`a.b`) and matrix operations (`a.^b`)
    Input: `a.b + a.^2`

.. code::

    code_block ──── statement ──── "+" oper ─┬── dot ─┬── a
                                             │        └── b
                                             └── ".^" oper ─┬── a
                                                            └── 2

- Anonymous functions
    Input: `@(x, y, z) x.^2 + y.^2 + z.^2`

.. code::

    code_block ──── statement ──── anonym_func ─┬── args ─┬── x
                                                │         ├── y
                                                │         └── z
                                                └── expr ──── "+" oper ─┬── "+" oper ─┬── ".^" oper ─┬── x
                                                                        │             │              └── 2
                                                                        │             └── ".^" oper ─┬── y
                                                                        │                            └── 2
                                                                        └── ".^" oper ─┬── z
                                                                                       └── 2

- Matlab's for-loops, while blocks, if blocks, etc.
    Input: `for i = 1 : 10; disp(i); if i == 5; break; end; end`

.. code::

    code_block ──── for_loop ─┬── for ──── assign ─┬── i
                              │                    └── range  ─┬── 1
                              │                                └── 10
                              └── body ─┬── statement ──── func_call/array_idxing ─┬── expr ──── disp
                                        │                                          └── args ──── i
                                        └── if_block ─┬── if ──── "==" oper ─┬── i
                                                      │                      └── 5
                                                      └── body ──── statement ──── func_call/array_idxing ─┬── expr ──── disp
                                                                                                           └── args ──── i


Among other features.

Why this project?
--------------------

For possible future projects on alternative Matlab/Octave interpreters, IDE plugins,
education, etc.

Currently this project is experimental; Unexpected problems can occur from time to
time, and the author strives to improve it continuously.

How to use it?
------------------------------------------
This project uses the lexer-parser framework, implemented using `sly` Python package.
This is the only dependency you'd need to install, which is available using pip.

To generate the tree views like the ones shown above, simply execute the
`matlab_parser.py` file. To use it in code, create a `MatlabParser` object and call its
`parse()` function (just like how it works in `sly` or `ply` package). This will
generate an abstract syntax tree (AST) node.

Every AST node is a tuple that has two elements: the first element is a string name
that describes this node (e.g. for_loop, * operation, function call, etc.), and the
second element is a tuple of children node(s) which follow the same format of AST node.

To keep the code simple, there is no dedicated class for AST node; only these tuples
are used.

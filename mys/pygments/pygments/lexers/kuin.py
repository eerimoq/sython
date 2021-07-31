# -*- coding: utf-8 -*-
"""
    pygments.lexers.kuin
    ~~~~~~~~~~~~~~~~~~~~

    Lexers for the Kuin language.
"""

from pygments.lexer import RegexLexer
from pygments.lexer import bygroups
from pygments.lexer import include
from pygments.lexer import inherit
from pygments.lexer import this
from pygments.lexer import using
from pygments.lexer import words
from pygments.token import Comment
from pygments.token import Keyword
from pygments.token import Name
from pygments.token import Number
from pygments.token import Operator
from pygments.token import Punctuation
from pygments.token import String
from pygments.token import Text

__all__ = ['KuinLexer']

class KuinLexer(RegexLexer):
    """
    For `Kuin <https://github.com/kuina/Kuin>`_ source code

    .. versionadded:: 2.9
    """
    name = 'Kuin'
    aliases = ['kuin']
    filenames = ['*.kn']

    tokens = {
        'root': [
            include('statement'),
        ],
        'statement': [
            # Whitespace / Comment
            include('whitespace'),

            # Block-statement
            (r'(\+?[ \t]*\*?[ \t]*\bfunc)([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*)', bygroups(Keyword, using(this), Name.Function), 'func_'),
            (r'\b(class)([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*)', bygroups(Keyword, using(this), Name.Class), 'class_'),
            (r'\b(enum)([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*)', bygroups(Keyword, using(this), Name.Constant), 'enum_'),
            (r'\b(block)\b(?:([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*))?', bygroups(Keyword, using(this), Name.Other), 'block_'),
            (r'\b(ifdef)\b(?:([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*))?', bygroups(Keyword, using(this), Name.Other), 'ifdef_'),
            (r'\b(if)\b(?:([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*))?', bygroups(Keyword, using(this), Name.Other), 'if_'),
            (r'\b(switch)\b(?:([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*))?', bygroups(Keyword, using(this), Name.Other), 'switch_'),
            (r'\b(while)\b(?:([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*))?', bygroups(Keyword, using(this), Name.Other), 'while_'),
            (r'\b(for)\b(?:([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*))?', bygroups(Keyword, using(this), Name.Other), 'for_'),
            (r'\b(foreach)\b(?:([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*))?', bygroups(Keyword, using(this), Name.Other), 'foreach_'),
            (r'\b(try)\b(?:([ \t]+(?:\n\s*\|)*[ \t]*)([a-zA-Z_][0-9a-zA-Z_]*))?', bygroups(Keyword, using(this), Name.Other), 'try_'),

            # Line-statement
            (r'\b(do)\b', Keyword, 'do'),
            (r'(\+?[ \t]*\bvar)\b', Keyword, 'var'),
            (r'\b(const)\b', Keyword, 'const'),
            (r'\b(ret)\b', Keyword, 'ret'),
            (r'\b(throw)\b', Keyword, 'throw'),
            (r'\b(alias)\b', Keyword, 'alias'),
            (r'\b(assert)\b', Keyword, 'assert'),
            (r'\|', Text, 'continued_line'),
            (r'[ \t]*\n', Text),
        ],

        # Whitespace / Comment
        'whitespace': [
            (r'^[ \t]*;.*', Comment.Single),
            (r'[ \t]+(?![; \t])', Text),
            (r'\{', Comment.Multiline, 'multiline_comment'),
        ],
        'multiline_comment': [
            (r'\{', Comment.Multiline, 'multiline_comment'),
            (r'(?:\s*;.*|[^{}\n]+)', Comment.Multiline),
            (r'\n', Comment.Multiline),
            (r'\}', Comment.Multiline, '#pop'),
        ],

        # Block-statement
        'func_': [
            include('expr'),
            (r'\n', Text, 'func'),
        ],
        'func': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(func)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            include('statement'),
        ],
        'class_': [
            include('expr'),
            (r'\n', Text, 'class'),
        ],
        'class': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(class)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            include('statement'),
        ],
        'enum_': [
            include('expr'),
            (r'\n', Text, 'enum'),
        ],
        'enum': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(enum)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            include('expr'),
            (r'\n', Text),
        ],
        'block_': [
            include('expr'),
            (r'\n', Text, 'block'),
        ],
        'block': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(block)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            include('statement'),
            include('break'),
            include('skip'),
        ],
        'ifdef_': [
            include('expr'),
            (r'\n', Text, 'ifdef'),
        ],
        'ifdef': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(ifdef)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            (words(('rls', 'dbg'), prefix=r'\b', suffix=r'\b'), Keyword.Constant, 'ifdef_sp'),
            include('statement'),
            include('break'),
            include('skip'),
        ],
        'ifdef_sp': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'if_': [
            include('expr'),
            (r'\n', Text, 'if'),
        ],
        'if': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(if)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            (words(('elif', 'else'), prefix=r'\b', suffix=r'\b'), Keyword, 'if_sp'),
            include('statement'),
            include('break'),
            include('skip'),
        ],
        'if_sp': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'switch_': [
            include('expr'),
            (r'\n', Text, 'switch'),
        ],
        'switch': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(switch)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            (words(('case', 'default', 'to'), prefix=r'\b', suffix=r'\b'), Keyword, 'switch_sp'),
            include('statement'),
            include('break'),
            include('skip'),
        ],
        'switch_sp': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'while_': [
            include('expr'),
            (r'\n', Text, 'while'),
        ],
        'while': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(while)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            include('statement'),
            include('break'),
            include('skip'),
        ],
        'for_': [
            include('expr'),
            (r'\n', Text, 'for'),
        ],
        'for': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(for)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            include('statement'),
            include('break'),
            include('skip'),
        ],
        'foreach_': [
            include('expr'),
            (r'\n', Text, 'foreach'),
        ],
        'foreach': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(foreach)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            include('statement'),
            include('break'),
            include('skip'),
        ],
        'try_': [
            include('expr'),
            (r'\n', Text, 'try'),
        ],
        'try': [
            (r'\b(end)([ \t]+(?:\n\s*\|)*[ \t]*)(try)\b', bygroups(Keyword, using(this), Keyword), '#pop:2'),
            (words(('catch', 'finally', 'to'), prefix=r'\b', suffix=r'\b'), Keyword, 'try_sp'),
            include('statement'),
            include('break'),
            include('skip'),
        ],
        'try_sp': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],

        # Line-statement
        'break': [
            (r'\b(break)\b([ \t]+)([a-zA-Z_][0-9a-zA-Z_]*)', bygroups(Keyword, using(this), Name.Other)),
        ],
        'skip': [
            (r'\b(skip)\b([ \t]+)([a-zA-Z_][0-9a-zA-Z_]*)', bygroups(Keyword, using(this), Name.Other)),
        ],
        'alias': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'assert': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'const': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'do': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'ret': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'throw': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'var': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],
        'continued_line': [
            include('expr'),
            (r'\n', Text, '#pop'),
        ],

        'expr': [
            # Whitespace / Comment
            include('whitespace'),

            # Punctuation
            (r'\(', Punctuation,),
            (r'\)', Punctuation,),
            (r'\[', Punctuation,),
            (r'\]', Punctuation,),
            (r',', Punctuation),

            # Keyword
            (words((
                'true', 'false', 'null', 'inf'
                ), prefix=r'\b', suffix=r'\b'), Keyword.Constant),
            (words((
                'me'
                ), prefix=r'\b', suffix=r'\b'), Keyword),
            (words((
                'bit16', 'bit32', 'bit64', 'bit8', 'bool',
                'char', 'class', 'dict', 'enum', 'float', 'func',
                'int', 'list', 'queue', 'stack'
                ), prefix=r'\b', suffix=r'\b'), Keyword.Type),

            # Number
            (r'\b[0-9]\.[0-9]+(?!\.)(:?e[\+-][0-9]+)?\b', Number.Float),
            (r'\b2#[01]+(?:b(?:8|16|32|64))?\b', Number.Bin),
            (r'\b8#[0-7]+(?:b(?:8|16|32|64))?\b', Number.Oct),
            (r'\b16#[0-9A-F]+(?:b(?:8|16|32|64))?\b', Number.Hex),
            (r'\b[0-9]+(?:b(?:8|16|32|64))?\b', Number.Decimal),

            # String / Char
            (r'"', String.Double, 'string'),
            (r"'(?:\\.|.)+?'", String.Char),

            # Operator
            (r'(?:\.|\$(?:>|<)?)', Operator),
            (r'(?:\^)', Operator),
            (r'(?:\+|-|!|##?)', Operator),
            (r'(?:\*|/|%)', Operator),
            (r'(?:~)', Operator),
            (r'(?:(?:=|<>)(?:&|\$)?|<=?|>=?)', Operator),
            (r'(?:&)', Operator),
            (r'(?:\|)', Operator),
            (r'(?:\?)', Operator),
            (r'(?::(?::|\+|-|\*|/|%|\^|~)?)', Operator),

            # Identifier
            (r"\b([a-zA-Z_][0-9a-zA-Z_]*)(?=@)\b", Name),
            (r"(@)?\b([a-zA-Z_][0-9a-zA-Z_]*)\b", bygroups(Name.Other, Name.Variable)),
        ],

        # String
        'string': [
            (r'(?:\\[^{\n]|[^"\\])+', String.Double),
            (r'\\\{', String.Double, 'toStrInString'),
            (r'"', String.Double, '#pop'),
        ],
        'toStrInString': [
            include('expr'),
            (r'\}', String.Double, '#pop'),
        ],
    }
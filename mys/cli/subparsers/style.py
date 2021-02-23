import glob

from ...parser import ast
from ..utils import Spinner
from ..utils import read_package_configuration


class CommentsReader:

    def __init__(self, comments):
        self.comments = []

        for lineno, lines in comments:
            for i, line in enumerate(lines):
                self.comments.append((lineno + i, line))

        self.pos = 0

    def get_at(self, wanted_lineno):
        if self.pos == len(self.comments):
            return ''

        lineno, line = self.comments[self.pos]

        if lineno != wanted_lineno:
            return ''

        self.pos += 1

        return line

    def get_before(self, wanted_lineno, prev_line):
        """Get any lines found directly before given line number.

        """

        if self.pos == len(self.comments):
            return []

        lineno, line = self.comments[self.pos]
        lines = []
        blank_lines_count = 0

        while lineno < wanted_lineno:
            if line == '':
                blank_lines_count += 1
            else:
                if not lines:
                    if prev_line == '':
                        blank_lines_count = 0
                    else:
                        blank_lines_count = min(blank_lines_count, 1)

                lines += [''] * blank_lines_count
                blank_lines_count = 0
                lines.append(line)

            self.pos += 1

            if self.pos == len(self.comments):
                break

            lineno, line = self.comments[self.pos]

        if blank_lines_count > 0 and (lines or prev_line != ''):
            lines.append('')

        return lines

    def get_remaining(self, prev_line):
        if self.pos == len(self.comments):
            return []
        print(self.comments[self.pos:], len(prev_line))
        return self.get_before(self.comments[-1][0] + 1, prev_line)


def get_source(source_lines, lineno, col_offset, end_lineno, end_col_offset):
    source = []
    number_of_lines = end_lineno - lineno + 1
    new_lineno = lineno

    if number_of_lines == 1:
        line = source_lines[lineno - 1]
        line = line[col_offset:end_col_offset]

        if line:
            source.append(line)
    else:
        for i in range(number_of_lines):
            line = source_lines[lineno + i - 1]

            if i == 0:
                line = line[col_offset:]

                if not line:
                    new_lineno += 1
                    continue
            elif i == number_of_lines - 1:
                line = line[:end_col_offset]

                if not line:
                    continue

            source.append(line)

    return new_lineno, source


def get_function_or_class_node_start(node):
    if node.decorator_list:
        node = node.decorator_list[0]

    return node.lineno, 0


class CommentsFinder(ast.NodeVisitor):
    """Look for comments and blank lines in source code not spanned by AST
    nodes.

    """

    def __init__(self, source_lines):
        self.comments = []
        self.source_lines = source_lines
        self.prev_end_lineno = 1
        self.prev_end_col_offset = 0

    def get_source(self, end_lineno, end_col_offset):
        return get_source(self.source_lines,
                          self.prev_end_lineno,
                          self.prev_end_col_offset,
                          end_lineno,
                          end_col_offset)

    def add_comments(self, lineno, col_offset):
        lineno, source_lines = self.get_source(lineno, col_offset)

        if source_lines:
            self.comments.append((lineno, source_lines))

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        if self.source_lines:
            self.add_comments(len(self.source_lines), len(self.source_lines[-1]))

    def visit_FunctionDef(self, node):
        lineno, col_offset = get_function_or_class_node_start(node)
        self.add_comments(lineno, col_offset)
        self.prev_end_lineno = node.end_lineno
        self.prev_end_col_offset = node.end_col_offset

    def visit_ClassDef(self, node):
        lineno, col_offset = get_function_or_class_node_start(node)
        self.add_comments(lineno, col_offset)
        self.prev_end_lineno = node.end_lineno
        self.prev_end_col_offset = node.end_col_offset

    def visit_AnnAssign(self, node):
        self.add_comments(node.lineno, node.col_offset)
        self.prev_end_lineno = node.end_lineno
        self.prev_end_col_offset = node.end_col_offset

    def visit_ImportFrom(self, node):
        self.add_comments(node.lineno, node.col_offset)
        self.prev_end_lineno = node.end_lineno
        self.prev_end_col_offset = node.end_col_offset

    def visit_Constant(self, node):
        self.add_comments(node.lineno, node.col_offset)
        self.prev_end_lineno = node.end_lineno
        self.prev_end_col_offset = node.end_col_offset

class SourceStyler:

    def __init__(self):
        self.source_lines = None
        self.tree = None
        self.comments_reader = None
        self.local_imports = None
        self.other_imports = None
        self.code = None

    def style(self, source_lines, tree, comments):
        """Returns the styled source code from given source code, AST and
        extracted comments and blank lines.

        """

        self.source_lines = source_lines
        self.tree = tree
        self.comments_reader = CommentsReader(comments)
        self.local_imports = []
        self.other_imports = []
        self.code = []

        for node in self.tree.body:
            if isinstance(node, ast.ImportFrom):
                self._style_import_from(node)
            elif isinstance(node, ast.FunctionDef):
                self._style_function(node)
            elif isinstance(node, ast.ClassDef):
                self._style_class(node)
            else:
                self._style_other(node)

        imports = []

        if self.other_imports:
            imports += sorted(self.other_imports)

        if self.local_imports:
            imports += sorted(self.local_imports)

        if imports:
            imports.append('')

        self.code = imports + self.code
        self.code += self.comments_reader.get_remaining(self.get_prev_line())

        if len(self.code) == 0 or self.code[-1] != '':
            self.code.append('')

        return '\n'.join(self.code)

    def get_prev_line(self):
        if len(self.code) == 0:
            return ''
        else:
            return self.code[-1]

    def get_comments_before(self, lineno):
        prev_line = self.get_prev_line()
        comments = self.comments_reader.get_before(lineno, prev_line)

        return comments

    def get_inline_comment(self, lineno):
        comment = self.comments_reader.get_at(lineno)

        if comment:
            comment = '  ' + comment.strip()

        return comment

    def ensure_blank_line(self):
        if len(self.code) > 0:
            if self.get_prev_line() != '':
                self.code.append('')

    def _style_import_from(self, node):
        if node.module is None:
            module = ''
        else:
            module = node.module

        module = '.' * node.level + module
        names = []

        for item in node.names:
            if item.asname is None:
                name = item.name
            else:
                name = f'{item.name} as {item.asname}'

            names.append(name)

        comment = self.get_inline_comment(node.end_lineno)
        names = ', '.join(names)
        styled_code = f'from {module} import {names}{comment}'

        if module[0] == '.':
            self.local_imports.append(styled_code)
        else:
            self.other_imports.append(styled_code)

    def _style_function(self, node):
        # Just get everything the node spans for now.
        lineno, col_offset = get_function_or_class_node_start(node)
        comments = self.get_comments_before(lineno)

        if not comments:
            self.ensure_blank_line()

        self.code += comments
        self.code += get_source(self.source_lines,
                                lineno,
                                col_offset,
                                node.end_lineno,
                                node.end_col_offset)[1]
        self.code[-1] += self.get_inline_comment(node.end_lineno)

    def _style_class(self, node):
        # Just get everything the node spans for now.
        lineno, col_offset = get_function_or_class_node_start(node)
        comments = self.get_comments_before(lineno)

        if not comments:
            self.ensure_blank_line()

        self.code += comments
        self.code += get_source(self.source_lines,
                                lineno,
                                col_offset,
                                node.end_lineno,
                                node.end_col_offset)[1]

    def _style_other(self, node):
        # Just get everything the node spans for now.
        self.code += self.get_comments_before(node.lineno)
        self.code += get_source(self.source_lines,
                                node.lineno,
                                node.col_offset,
                                node.end_lineno,
                                node.end_col_offset)[1]


def style_files():
    source_styler = SourceStyler()

    for src_path in glob.glob('src/**/*.mys', recursive=True):
        with open(src_path, 'r') as fin:
            source = fin.read()

        tree = ast.parse(source)
        source_lines = source.split('\n')
        finder = CommentsFinder(source_lines)
        finder.visit(tree)
        styled_source = source_styler.style(source_lines, tree, finder.comments)

        if styled_source != source:
            with open(src_path, 'w') as fout:
                fout.write(styled_source)


def do_style(_parser, _args, _mys_config):
    read_package_configuration()

    with Spinner(text="Styling source code"):
        style_files()


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'style',
        description=(
            'Modify all source code files in the package follow the Mys style '
            'guidelines.'))
    subparser.set_defaults(func=do_style)

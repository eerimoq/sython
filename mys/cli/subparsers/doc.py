import os
import sys

from ..utils import add_verbose_argument
from ..utils import run


def do_doc(_parser, args, _mys_config):
    command = [
        sys.executable, '-m', 'sphinx',
        '-T', '-E',
        '-b', 'html',
        '-d', 'build/doc/doctrees',
        '-D', 'language=en',
        'doc', 'build/doc/html'
    ]
    run(command, 'Building documentation', args.verbose)

    path = os.path.abspath('build/doc/html/index.html')
    print(f'Documentation: {path}')


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'doc',
        description='Build the documentation.')
    add_verbose_argument(subparser)
    subparser.set_defaults(func=do_doc)
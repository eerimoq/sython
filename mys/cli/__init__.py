import argparse
import os
import shutil
import sys
from tempfile import TemporaryDirectory
from traceback import print_exc

import toml
from colors import cyan
from colors import yellow

from ..parser import ast
from ..version import __version__
from .subparsers import build
from .subparsers import clean
from .subparsers import delete
from .subparsers import deps
from .subparsers import doc
from .subparsers import fetch
from .subparsers import help as help_
from .subparsers import install
from .subparsers import new
from .subparsers import publish
from .subparsers import run
from .subparsers import style
from .subparsers import test
from .subparsers import transpile
from .subparsers.new import create_package
from .subparsers.run import run_app
from .utils import BuildConfig
from .utils import DependenciesVisitor
from .utils import build_app
from .utils import build_prepare
from .utils import create_file

DESCRIPTION = f'''\
The Mys programming language command line tool.

Run as {yellow('mys <subcommand>')} or {yellow('mys <mys-file>')}.

Available subcommands are:

    {cyan('new')}      Create a new package.
    {cyan('build')}    Build the appliaction.
    {cyan('run')}      Build and run the application.
    {cyan('test')}     Build and run tests
    {cyan('clean')}    Remove build output.
    {cyan('deps')}     Show dependencies.
    {cyan('publish')}  Publish a release to the registry.
    {cyan('delete')}   Delete a package from the registry.
    {cyan('install')}  Install an application from local package or registry.
    {cyan('doc')}      Build the documentation.
    {cyan('fetch')}    Download and extract all dependencies.
    {cyan('style')}    Code styling.
'''


def find_config_file():
    path = os.getenv('MYS_CONFIG')
    config_dir = os.path.expanduser('~/.config/mys')
    config_path = os.path.join(config_dir, 'config.toml')

    if path is not None:
        return path

    if not os.path.exists(config_path):
        os.makedirs(config_dir, exist_ok=True)
        create_file(config_path, '')

    return config_path


def load_mys_config():
    """Mys tool configuration.

    Add validation when needed.

    """

    path = find_config_file()

    try:
        with open(path) as fin:
            return toml.loads(fin.read())
    except toml.decoder.TomlDecodeError:
        raise Exception(f"failed to load Mys configuration file '{path}'")


def create_parser():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument(
        '-C', '--directory',
        help='Change directory to given directory before doing anything.')
    parser.add_argument('--config', help='Configuration file to use.')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    subparsers = parser.add_subparsers(dest='subcommand',
                                       help='Subcommand to execute.',
                                       metavar='subcommand')

    new.add_subparser(subparsers)
    build.add_subparser(subparsers)
    run.add_subparser(subparsers)
    test.add_subparser(subparsers)
    clean.add_subparser(subparsers)
    transpile.add_subparser(subparsers)
    deps.add_subparser(subparsers)
    publish.add_subparser(subparsers)
    delete.add_subparser(subparsers)
    install.add_subparser(subparsers)
    style.add_subparser(subparsers)
    doc.add_subparser(subparsers)
    fetch.add_subparser(subparsers)
    help_.add_subparser(subparsers)

    return parser


def do_run_file(args):
    with TemporaryDirectory() as tmp_dir:
        package_root = f'{tmp_dir}/app'
        create_package(package_root, [])
        dependency_visitor = DependenciesVisitor()
        shutil.copyfile(sys.argv[1], f'{package_root}/src/main.mys')
        os.chdir(package_root)

        with open('src/main.mys') as fin:
            dependency_visitor.visit(ast.parse(fin.read()))

        with open('package.toml', 'a') as fout:
            for dependency in dependency_visitor.dependencies:
                print(f'{dependency} = "latest"', file=fout)

        build_config = BuildConfig(False,
                                   False,
                                   'speed',
                                   False,
                                   False,
                                   False,
                                   False,
                                   1,
                                   'https://mys-lang.org')
        is_application, build_dir, _ = build_prepare(build_config)
        build_app(build_config, is_application, build_dir)
        run_app(args, False, build_dir)


def main():
    if len(sys.argv) >= 2:
        if sys.argv[1].endswith('.mys'):
            try:
                do_run_file(sys.argv[2:])
                return
            except Exception as e:
                sys.exit(str(e))

    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    if args.directory is not None:
        os.chdir(args.directory)

    try:
        args.func(parser, args, load_mys_config())
    except Exception as e:
        if args.debug:
            print_exc()

        sys.exit(str(e))
    except KeyboardInterrupt:
        print()

        if args.debug:
            raise

        sys.exit(1)

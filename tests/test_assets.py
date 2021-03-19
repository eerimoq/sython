import shutil
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory


class Test(TestCase):

    def test_assets(self):
        name = 'test_assets'
        remove_build_directory(name)
        shutil.copytree('tests/files/assets', f'tests/build/{name}')

        with Path(f'tests/build/{name}/mypkg'):
            with patch('sys.argv', ['mys', '-d', 'test', '-v']):
                mys.cli.main()

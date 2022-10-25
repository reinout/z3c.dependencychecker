import os
import tempfile

import pytest

from z3c.dependencychecker.modules import BaseModule
from z3c.dependencychecker.tests.utils import write_source_file_at


def test_module_path():
    obj = BaseModule('/some/path', '/some/path/random/bla')
    assert obj.path == '/some/path/random/bla'


def test_scan_raises():
    obj = BaseModule('/some/path', '/some/path/random/bla')
    with pytest.raises(NotImplementedError):
        obj.scan()


def test_create_from_files_raises():
    with pytest.raises(NotImplementedError):
        BaseModule.create_from_files('/some/path')


def test_has_test_with_prefix_in_path():
    folder = tempfile.mkdtemp()
    temporal_file = write_source_file_at((folder, 'blatest'))
    python_module = BaseModule(folder, temporal_file)
    assert python_module.testing


def test_has_test_in_path():
    folder = tempfile.mkdtemp()
    temporal_file = write_source_file_at((folder, 'test'))
    python_module = BaseModule(folder, temporal_file)
    assert python_module.testing


def test_has_tests_in_path():
    folder = tempfile.mkdtemp()
    temporal_file = write_source_file_at((folder, 'tests'))
    python_module = BaseModule(folder, temporal_file)
    assert python_module.testing


def test_has_test_in_filename():
    folder = tempfile.mkdtemp()
    temporal_file = write_source_file_at((folder, 'bla'), filename='test.py')
    python_module = BaseModule(folder, temporal_file)
    assert python_module.testing


def test_has_tests_in_filename():
    folder = tempfile.mkdtemp()
    temporal_file = write_source_file_at((folder, 'bla'), filename='tests.py')
    python_module = BaseModule(folder, temporal_file)
    assert python_module.testing


def test_has_tests_with_suffix_in_filename():
    folder = tempfile.mkdtemp()
    temporal_file = write_source_file_at((folder, 'bla'), filename='testsohlala.py')
    python_module = BaseModule(folder, temporal_file)
    assert python_module.testing


def test_is_not_a_test_module():
    folder = tempfile.mkdtemp()
    temporal_file = write_source_file_at((folder, 'bla'), filename='bla.py')
    python_module = BaseModule(folder, temporal_file)
    assert python_module.testing is False


def test_parent_folder_is_test_but_module_not():
    """Be sure to ignore the filesystem part and take into account the
    package part

    This means that if I have a package in a folder like:
    /home/gil/testing/my.package
    And a file within it like:
    /home/gil/testing/my.package/src/my/package/configure.zcml
    Despite having 'test' in the path, as it is not part of the package,
    it should be ignored.
    """
    folder = tempfile.mkdtemp()
    temporal_file = write_source_file_at((folder, 'test', 'bla'), filename='bla.py')
    python_module = BaseModule(os.path.join(folder, 'test'), temporal_file)
    assert python_module.testing is False

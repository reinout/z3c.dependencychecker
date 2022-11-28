"""Standard tests configuration module automatically scanned by pytest.

This module is used to add generic fixtures and other boilerplate needed by
our test suite.

Keeping it here ensures that pytest finds it without extra setup and eases
reusability.
"""
import os
import random
import shutil
import string
import tempfile

import pkg_resources
import pytest

from z3c.dependencychecker.dotted_name import DottedName
from z3c.dependencychecker.package import ImportsDatabase


@pytest.fixture
def fake_project():
    temp_folder = tempfile.mkdtemp(prefix='depcheck')
    fake_package_files = pkg_resources.resource_filename(
        'z3c.dependencychecker.tests',
        'sample1',
    )
    package_folder = os.path.join(temp_folder, 'sample1')
    shutil.copytree(fake_package_files, package_folder)
    # To prevent the sample .py files to be picked up by ourselves or other
    # tools, I'm postfixing them with ``_in``, now we get to rename them.
    # Same for zcml files.
    for (dirpath, dirnames, filenames) in os.walk(package_folder):
        for filename in filenames + dirnames:
            if not filename.endswith('_in'):
                continue
            new_filename = filename.replace('_in', '')
            if new_filename == '_it__.py':
                # Oopsie :-) The replace works too well...
                new_filename = '__init__.py'
            source = os.path.join(dirpath, filename)
            target = os.path.join(dirpath, new_filename)
            os.rename(source, target)

    yield package_folder
    shutil.rmtree(temp_folder)


@pytest.fixture
def minimal_structure():
    """Creates a folder structure that contains the minimal files needed
    to make Package class be able to initialize without errors
    """
    folder = tempfile.mkdtemp()
    _add_setup_py(folder)
    package_name = _add_egg_info(folder)

    src_folder = os.path.join(folder, 'src')
    os.makedirs(src_folder)

    yield folder, package_name

    shutil.rmtree(folder)


def _add_setup_py(folder):
    with open(os.path.join(folder, 'setup.py'), 'w') as setup_py_file:
        setup_py_file.write('hi')


def _add_egg_info(folder):
    package_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))

    egg_info_folder_path = os.path.join(
        folder,
        f'{package_name}.egg-info',
    )
    os.makedirs(egg_info_folder_path)

    _write_pkg_info_file(egg_info_folder_path)
    _write_requires_file(egg_info_folder_path)
    _write_top_level_file(egg_info_folder_path, package_name)

    return package_name


def _write_pkg_info_file(folder):
    with open(os.path.join(folder, 'PKG-INFO'), 'w') as pkg_info:
        lines = '\n'.join(
            ['Metadata-Version: 1.0', 'Name: testpackage', 'Version: 1.0.dev0']
        )
        pkg_info.write(lines)


def _write_requires_file(folder):
    with open(os.path.join(folder, 'requires.txt'), 'w') as requires_file:
        lines = '\n'.join(['one', 'two'])
        requires_file.write(lines)


def _write_top_level_file(folder_path, package_name):
    file_path = os.path.join(folder_path, 'top_level.txt')
    with open(file_path, 'w') as top_level_file:
        lines = '\n'.join([package_name])
        top_level_file.write(lines)

    sources_top_folder = os.path.join(
        folder_path,
        '..',
        package_name,
    )
    os.makedirs(sources_top_folder)


@pytest.fixture
def minimal_database():
    database = ImportsDatabase()
    database.own_dotted_name = DottedName('fake')
    return database

# -*- coding: utf-8 -*-
"""Standard tests configuration module automatically scanned by pytest.

This module is used to add generic fixtures and other boilerplate needed by
our test suite.

Keeping it here ensures that pytest finds it without extra setup and eases
reusability.
"""
import os
import pkg_resources
import pytest
import shutil
import tempfile


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
        for filename in (filenames + dirnames):
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

# -*- coding: utf-8 -*-
from z3c.dependencychecker.package import PackageMetadata
import os
import tempfile


def test_no_setup_py_file_found():
    folder = tempfile.mkdtemp()
    sys_exit = False
    try:
        PackageMetadata(folder)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_distribution_root(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.distribution_root == path


def test_setup_py_path(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.setup_py_path == os.path.join(path, 'setup.py')

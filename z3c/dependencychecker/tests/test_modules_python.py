# -*- coding: utf-8 -*-
from z3c.dependencychecker.modules import PythonModule
from z3c.dependencychecker.tests.utils import write_source_file_at
import os
import tempfile


def test_create_from_files_nothing(minimal_structure):
    path, package_name = minimal_structure
    modules_found = [x for x in PythonModule.create_from_files(path)]
    assert len(modules_found) == 0


def test_create_from_files_single_file():
    _, tmp_file = tempfile.mkstemp('.py')
    modules_found = [x for x in PythonModule.create_from_files(tmp_file)]
    assert len(modules_found) == 1
    assert modules_found[0].path == tmp_file


def test_create_from_files_no_init(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    assert len(os.listdir(src_path)) == 0

    write_source_file_at([src_path, ])
    assert len(os.listdir(src_path)) == 1

    modules_found = [x for x in PythonModule.create_from_files(src_path)]
    assert len(modules_found) == 0


def test_create_from_files_ignore_no_python(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at([src_path, ], filename='__init__.py')
    tempfile.mkstemp('.pt', 'bla', src_path)

    modules_found = [x for x in PythonModule.create_from_files(src_path)]
    assert len(modules_found) == 1


def test_create_from_files_found_python(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at([src_path, ], filename='__init__.py')
    write_source_file_at([src_path, ], filename='bla.py')

    modules_found = [x for x in PythonModule.create_from_files(src_path)]
    assert len(modules_found) == 2


def test_create_from_files_deep_nested(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at([src_path, ], filename='__init__.py')
    write_source_file_at([src_path, ], filename='bla.py')
    write_source_file_at([src_path, 'a', ], filename='__init__.py')
    write_source_file_at([src_path, 'a', ], filename='bla.py')
    write_source_file_at([src_path, 'a', 'b', ], filename='__init__.py')
    write_source_file_at([src_path, 'a', 'b', ], filename='bla.py')

    modules_found = [x for x in PythonModule.create_from_files(src_path)]
    assert len(modules_found) == 6

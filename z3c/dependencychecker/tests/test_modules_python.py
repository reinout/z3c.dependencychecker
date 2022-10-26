import os
import tempfile

import pytest

from z3c.dependencychecker.modules import PythonModule
from z3c.dependencychecker.tests.utils import write_source_file_at

IMPORT = 'import foo'
IMPORT_MULTIPLE = 'import foo, bar'
IMPORT_AS = 'import foo as bar'
IMPORT_AS_MULTIPLE = 'import foo as bar, boo as bla'

FROM_IMPORT = 'from foo import bar'
FROM_IMPORT_MULTIPLE = 'from foo import bar, ber'
FROM_IMPORT_AS = 'from foo import bar as ber'
FROM_IMPORT_AS_MULTIPLE = 'from foo import bar as ber, boo as bla'
FROM_IMPORT_ASTERISK = 'from os import *'
FROM_IMPORT_DOT = 'from . import something'
FROM_IMPORT_DOT_DOT = 'from .. import something'
FROM_IMPORT_DOT_RELATIVE = 'from .local import something'


def _get_imports_of_python_module(folder, source):
    temporal_file = write_source_file_at(
        (folder.strpath,),
        source_code=source,
    )

    python_module = PythonModule(folder.strpath, temporal_file)
    dotted_names = [x.name for x in python_module.scan()]
    return dotted_names


def test_create_from_files_nothing(minimal_structure):
    path, package_name = minimal_structure
    modules_found = list(PythonModule.create_from_files(path))
    assert len(modules_found) == 0


def test_create_from_files_single_file():
    _, tmp_file = tempfile.mkstemp('.py')
    modules_found = list(PythonModule.create_from_files(tmp_file))
    assert len(modules_found) == 1
    assert modules_found[0].path == tmp_file


def test_create_from_files_no_init(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    assert len(os.listdir(src_path)) == 0

    write_source_file_at([src_path])
    assert len(os.listdir(src_path)) == 1

    modules_found = list(PythonModule.create_from_files(src_path))
    assert len(modules_found) == 0


def test_create_from_files_ignore_no_python(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at([src_path], filename='__init__.py')
    tempfile.mkstemp('.pt', 'bla', src_path)

    modules_found = list(PythonModule.create_from_files(src_path))
    assert len(modules_found) == 1


def test_create_from_files_found_python(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at([src_path], filename='__init__.py')
    write_source_file_at([src_path], filename='bla.py')

    modules_found = list(PythonModule.create_from_files(src_path))
    assert len(modules_found) == 2


def test_create_from_files_deep_nested(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at([src_path], filename='__init__.py')
    write_source_file_at([src_path], filename='bla.py')
    write_source_file_at([src_path, 'a'], filename='__init__.py')
    write_source_file_at([src_path, 'a'], filename='bla.py')
    write_source_file_at([src_path, 'a', 'b'], filename='__init__.py')
    write_source_file_at([src_path, 'a', 'b'], filename='bla.py')

    modules_found = list(PythonModule.create_from_files(src_path))
    assert len(modules_found) == 6


def test_import(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, IMPORT)
    assert len(dotted_names) == 1


def test_import_details(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, IMPORT)
    assert dotted_names == ['foo']


def test_import_multiple(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, IMPORT_MULTIPLE)
    assert len(dotted_names) == 2


def test_import_multiple_details(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, IMPORT_MULTIPLE)
    assert sorted(dotted_names) == ['bar', 'foo']


def test_import_as(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, IMPORT_AS)
    assert len(dotted_names) == 1


def test_import_as_details(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, IMPORT_AS)
    assert dotted_names == ['foo']


def test_import_as_multiple(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, IMPORT_AS_MULTIPLE)
    assert len(dotted_names) == 2


def test_import_as_multiple_details(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, IMPORT_AS_MULTIPLE)
    assert sorted(dotted_names) == ['boo', 'foo']


def test_from_import(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, FROM_IMPORT)
    assert len(dotted_names) == 1


def test_from_import_details(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, FROM_IMPORT)
    assert dotted_names == ['foo.bar']


def test_from_import_multiple(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, FROM_IMPORT_MULTIPLE)
    assert len(dotted_names) == 2


def test_from_import_multiple_details(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, FROM_IMPORT_MULTIPLE)
    assert sorted(dotted_names) == ['foo.bar', 'foo.ber']


def test_from_import_as(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, FROM_IMPORT_AS)
    assert len(dotted_names) == 1


def test_from_import_as_details(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, FROM_IMPORT_AS)
    assert dotted_names == ['foo.bar']


def test_import_asterisk(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, FROM_IMPORT_ASTERISK)
    assert len(dotted_names) == 1


def test_import_asterisk_details(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, FROM_IMPORT_ASTERISK)
    assert dotted_names == ['os']


@pytest.mark.parametrize(
    'statement',
    [
        FROM_IMPORT_DOT,
        FROM_IMPORT_DOT_DOT,
        FROM_IMPORT_DOT_RELATIVE,
    ],
)
def test_ignore_local_imports(statement, tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, statement)
    assert len(dotted_names) == 0


def test_from_import_as_multiple(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        FROM_IMPORT_AS_MULTIPLE,
    )
    assert len(dotted_names) == 2


def test_from_import_as_multiple_details(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        FROM_IMPORT_AS_MULTIPLE,
    )
    assert sorted(dotted_names) == ['foo.bar', 'foo.boo']


def test_imports_multiple_lines(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        'import foo\nimport bar',
    )
    assert sorted(dotted_names) == ['bar', 'foo']

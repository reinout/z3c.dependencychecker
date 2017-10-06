# -*- coding: utf-8 -*-
from z3c.dependencychecker.modules import DocFiles
from z3c.dependencychecker.tests.utils import write_source_file_at

import os


NO_DOC = '\n'.join([
    'Random title',
    '============',
    '',
    'Random paragraph',
])
INVALID_PYTHON = '\n'.join([
    'Random title',
    '============',
    '',
    'Random paragraph',
    '>>> and some text here that breaks the parser'
])
SINGLE_IMPORT = '\n'.join([
    'Random title',
    '============',
    '',
    'Random paragraph',
    '>>> import zope.annotation'
])
MULTIPLE_IMPORTS_SAME_LINE = '\n'.join([
    'Random title',
    '============',
    '',
    'Random paragraph',
    '>>> from zope.interface import Interface, Attribute',
])
MULTIPLE_IMPORTS_DIFFERENT_LINES = '\n'.join([
    'class MyClass(object):',
    '    def test(self):',
    '        """Docstring with code to be evaluated.',
    '',
    '        >>> from zope.component import adapter',
    '        >>> from zope.component import utility',
    '        """',
])


def _get_dependencies_on_file(folder, source):
    temporal_file = write_source_file_at(
        (folder.strpath, ),
        source_code=source,
    )

    doc_file = DocFiles(folder.strpath, temporal_file)
    dotted_names = [x.name for x in doc_file.scan()]
    return dotted_names


def test_create_from_files_nothing(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    modules_found = [x for x in DocFiles.create_from_files(src_path)]
    assert len(modules_found) == 0


def test_create_from_files_deep_nested_txt(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at(
        [src_path, 'a', 'b', 'c', ],
        filename='bla.txt',
    )

    modules_found = [x for x in DocFiles.create_from_files(src_path)]
    assert len(modules_found) == 1


def test_create_from_files_deep_nested_rst(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at(
        [src_path, 'a', 'b', 'c', ],
        filename='bla.rst',
    )

    modules_found = [x for x in DocFiles.create_from_files(src_path)]
    assert len(modules_found) == 1


def test_no_code(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, NO_DOC)
    assert len(dotted_names) == 0


def test_invalid_code_ignored(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, INVALID_PYTHON)
    assert len(dotted_names) == 0


def test_code_found(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, SINGLE_IMPORT)
    assert len(dotted_names) == 1


def test_code_found_details(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, SINGLE_IMPORT)
    assert dotted_names == ['zope.annotation', ]


def test_multiple_imports_same_line(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_SAME_LINE,
    )
    assert len(dotted_names) == 2


def test_multiple_imports_same_line_details(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_SAME_LINE,
    )
    assert 'zope.interface.Interface' in dotted_names
    assert 'zope.interface.Attribute' in dotted_names


def test_multiple_imports_different_lines(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_DIFFERENT_LINES,
    )
    assert len(dotted_names) == 2


def test_multiple_imports_different_lines_details(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_DIFFERENT_LINES,
    )

    assert 'zope.component.adapter' in dotted_names
    assert 'zope.component.utility' in dotted_names
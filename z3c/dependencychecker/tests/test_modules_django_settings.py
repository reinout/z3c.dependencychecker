import os
import tempfile

from z3c.dependencychecker.modules import DjangoSettings
from z3c.dependencychecker.tests.utils import write_source_file_at

RANDOM_CODE = 'from zope.component import adapter'
RANDOM_ASSIGNMENT = 'a = 3'
APPS_ASSIGNMENT_TO_STRING = 'INSTALLED_APPS = "random"'
APPS_ASSIGNMENT_TO_TUPLE = 'INSTALLED_APPS = ("random1", "random2", )'
APPS_ASSIGNMENT_TO_LIST = 'INSTALLED_APPS = ["random3", "random4", ]'
APPS_ASSIGNMENT_TO_LIST_MIXED = 'INSTALLED_APPS = ["random5", 3, ]'
TEST_RUNNER_ASSIGNMENT_TO_LIST = 'TEST_RUNNER = ["random6", "random7", ]'
TEST_RUNNER_ASSIGNMENT_TO_STRING = 'TEST_RUNNER = "random8"'


def _get_imports_of_python_module(folder, source):
    temporal_file = write_source_file_at(
        (folder.strpath,),
        source_code=source,
    )

    django_settings = DjangoSettings(folder.strpath, temporal_file)
    dotted_names = [x.name for x in django_settings.scan()]
    return dotted_names


def test_create_from_files_nothing(minimal_structure):
    path, package_name = minimal_structure
    modules_found = list(DjangoSettings.create_from_files(path))
    assert len(modules_found) == 0


def test_create_from_files_single_file_random_name():
    _, tmp_file = tempfile.mkstemp('.py')
    modules_found = list(DjangoSettings.create_from_files(tmp_file))
    assert len(modules_found) == 0


def test_create_from_files_single_file_settings_name(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at([src_path], filename='some_settings.py')
    modules_found = list(DjangoSettings.create_from_files(src_path))
    assert len(modules_found) == 1


def test_create_from_files_deep_nested(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at(
        [src_path, 'a', 'b', 'c'],
        filename='anothersettings.py',
    )
    modules_found = list(DjangoSettings.create_from_files(src_path))
    assert len(modules_found) == 1


def test_random_code(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, RANDOM_CODE)
    assert len(dotted_names) == 0


def test_random_assignment(tmpdir):
    dotted_names = _get_imports_of_python_module(tmpdir, RANDOM_ASSIGNMENT)
    assert len(dotted_names) == 0


def test_apps_assignment_to_string(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        APPS_ASSIGNMENT_TO_STRING,
    )
    assert len(dotted_names) == 0


def test_apps_assignment_to_tuple(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        APPS_ASSIGNMENT_TO_TUPLE,
    )
    assert len(dotted_names) == 2


def test_apps_assignment_to_tuple_details(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        APPS_ASSIGNMENT_TO_TUPLE,
    )
    assert 'random1' in dotted_names
    assert 'random2' in dotted_names


def test_apps_assignment_to_list(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        APPS_ASSIGNMENT_TO_LIST,
    )
    assert len(dotted_names) == 2


def test_apps_assignment_to_list_details(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        APPS_ASSIGNMENT_TO_LIST,
    )
    assert 'random3' in dotted_names
    assert 'random4' in dotted_names


def test_apps_assignment_to_list_mixed(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        APPS_ASSIGNMENT_TO_LIST_MIXED,
    )
    assert len(dotted_names) == 1


def test_apps_assignment_to_list_mixed_details(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        APPS_ASSIGNMENT_TO_LIST_MIXED,
    )
    assert dotted_names[0] == 'random5'


def test_runner_assignment_to_list(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        TEST_RUNNER_ASSIGNMENT_TO_LIST,
    )
    assert len(dotted_names) == 0


def test_runner_assignment_to_string(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        TEST_RUNNER_ASSIGNMENT_TO_STRING,
    )
    assert len(dotted_names) == 1


def test_apps_assignment_to_string_mixed_details(tmpdir):
    dotted_names = _get_imports_of_python_module(
        tmpdir,
        TEST_RUNNER_ASSIGNMENT_TO_STRING,
    )
    assert dotted_names[0] == 'random8'

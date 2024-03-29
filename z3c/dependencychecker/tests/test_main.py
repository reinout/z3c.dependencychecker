from pathlib import Path
from unittest import mock
from z3c.dependencychecker.main import _version
from z3c.dependencychecker.main import get_path
from z3c.dependencychecker.main import main
from z3c.dependencychecker.main import parse_command_line
from z3c.dependencychecker.main import set_log_level
from z3c.dependencychecker.utils import change_dir

import logging
import os
import pytest
import sys
import tempfile


def test_usage_non_existing_option():
    arguments = ["dependencychecker", "--non-existing"]
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, "argv", arguments):
            parse_command_line()


def test_usage_set_verbose():
    arguments = ["dependencychecker", "--verbose"]
    with mock.patch.object(sys, "argv", arguments):
        options, args = parse_command_line()

    assert options.verbose


def test_version():
    assert _version().endswith(".dev0")


def test_set_debug_logging():
    _cleanup_logging_handlers()
    set_log_level(True)
    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG


def test_set_info_logging():
    _cleanup_logging_handlers()
    set_log_level(False)
    assert logging.getLogger().getEffectiveLevel() == logging.INFO


def _cleanup_logging_handlers():
    """The first iteration of this code was done as a pytest fixture,
    but introducing the pytest-catchlog plugin made it fail.

    On top of that, the loop inside a loop in this function is due to some
    sort of stickiness from pytest-catchlog handler that fails to be removed on
    a first iteration...
    """
    root_logger = logging.getLogger()
    while len(root_logger.handlers) > 0:
        handlers = root_logger.handlers
        for handler in handlers:
            root_logger.removeHandler(handler)


def test_get_path_no_path_given():
    """If no path is given as an argument the cwd is used"""
    folder = tempfile.mkdtemp()
    arguments = []
    with change_dir(folder):
        path = get_path(arguments)

    # realpath() below is used to work around a small mac tempdir naming
    # issue. /var/folders/xyz is the tempdir, but after cd'ing you're in
    # /private/var/folders/xyz...
    assert os.path.realpath(path) == os.path.realpath(folder)


def test_get_path_path_given():
    """If a path is given, that's the path being returned"""
    folder = Path(tempfile.mkdtemp())
    arguments = [folder]
    path = get_path(arguments)
    # .resolve() below makes it absolute: osx has /private/var/... !=
    # /var/... otherwise...
    assert path.resolve() == folder.resolve()


def test_get_path_given_path_not_a_folder():
    """If the path given is not a folder, get_path exits right away"""
    temporary_file = tempfile.NamedTemporaryFile()
    arguments = [temporary_file.name]
    sys_exit = False
    try:
        get_path(arguments)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_exit_zero_not_set(minimal_structure):
    path, _ = minimal_structure

    arguments = ["dependencychecker", str(path)]
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, "argv", arguments):
            main()


def test_exit_zero_set(minimal_structure):
    path, _ = minimal_structure

    arguments = ["dependencychecker", "--exit-zero", str(path)]
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, "argv", arguments):
            main()

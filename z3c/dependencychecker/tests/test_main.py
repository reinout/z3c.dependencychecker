# -*- coding: utf-8 -*-
from z3c.dependencychecker.main import get_path
from z3c.dependencychecker.main import parse_command_line
from z3c.dependencychecker.main import set_log_level
from z3c.dependencychecker.main import _version
from z3c.dependencychecker.utils import change_dir
import logging
import mock
import sys
import tempfile


def test_usage_non_existing_option():
    arguments = ['dependencychecker', '--non-existing']
    sys_exit = False
    try:
        with mock.patch.object(sys, 'argv', arguments):
            parse_command_line()
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_usage_set_verbose():
    arguments = ['dependencychecker', '--verbose']
    with mock.patch.object(sys, 'argv', arguments):
        options, args = parse_command_line()

    assert options.verbose


def test_version():
    assert _version().endswith('.dev0')


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
    sort of stickyness from pytest-catchlog handler that fails to be removed on
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

    assert path == folder


def test_get_path_path_given():
    """If a path is given, that's the path being returned"""
    folder = tempfile.mkdtemp()
    arguments = [folder, ]
    path = get_path(arguments)

    assert path == folder


def test_get_path_given_path_not_a_folder():
    """If the path given is not a folder, get_path exits right away"""
    temporary_file = tempfile.NamedTemporaryFile()
    arguments = [temporary_file.name, ]
    sys_exit = False
    try:
        get_path(arguments)
    except SystemExit:
        sys_exit = True

    assert sys_exit

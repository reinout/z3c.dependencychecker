# -*- coding: utf-8 -*-
from z3c.dependencychecker.main import parse_command_line
from z3c.dependencychecker.main import set_log_level
from z3c.dependencychecker.main import _version
import logging
import mock
import sys


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

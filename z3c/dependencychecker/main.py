# -*- coding: utf-8 -*-
import logging
import optparse
import pkg_resources
import sys


def main():
    options, args = parse_command_line()
    set_log_level(options.verbose)

    from z3c.dependencychecker.dependencychecker import main as old_main
    old_main(args)


def parse_command_line():
    usage = (
        'Usage: %prog [path]'
        '\n'
        '(path defaults to package name, fallback is "src/")'
    )
    parser = optparse.OptionParser(usage=usage, version=_version())
    parser.add_option(
        '-v',
        '--verbose',
        action='store_true',
        dest='verbose',
        default=False,
        help='Show debug output',
    )
    options, args = parser.parse_args()
    return options, args


def _version():
    ourselves = pkg_resources.require('z3c.dependencychecker')[0]
    return ourselves.version


def set_log_level(verbose):
    level = logging.INFO
    if verbose:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        stream=sys.stdout,
    )

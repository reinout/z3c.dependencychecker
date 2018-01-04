# -*- coding: utf-8 -*-
from z3c.dependencychecker.package import Package
from z3c.dependencychecker.report import Report
import logging
import optparse
import os
import pkg_resources
import sys


logger = logging.getLogger(__name__)


def main():
    options, args = parse_command_line()
    set_log_level(options.verbose)
    path = get_path(args)

    package_analyzed = Package(path)
    package_analyzed.inspect()

    report = Report(package_analyzed)
    report.print_report()


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
        format="%(levelname)s: %(message)s"
    )


def get_path(args):
    """Get path to the python source distribution that will be checked for
    dependencies

    If no path is given on the command line arguments, the current working
    directory is used instead.
    """
    path = os.getcwd()

    if len(args) < 1:
        logger.debug('path used: %s', path)
        return path

    path = os.path.abspath(args[0])
    if os.path.isdir(path):
        logger.debug('path used: %s', path)
        return path

    logger.error('Given path is not a folder: %s', args[0])
    sys.exit(1)

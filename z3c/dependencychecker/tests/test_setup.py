# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
import re
import shutil
import sys
import tempfile

from zope.testing import renormalizing
import pkg_resources
import z3c.testsetup


checker = renormalizing.RENormalizing([
    # Temp directory from setup() (including /private OSX madness).
    (re.compile(
        '/private%s/dependencychecker[^/]+' % re.escape(
            tempfile.gettempdir())),
     '/TESTTEMP'),
    (re.compile(
        '%s/dependencychecker[^/]+' % re.escape(tempfile.gettempdir())),
     '/TESTTEMP'),
    # Just the default /tmp directory.
    (re.compile(re.escape(tempfile.gettempdir())),
     '/TMPDIR'),
    ])


def ls(directory):
    for item in sorted(os.listdir(directory)):
        if item.startswith('.'):
            continue
        print item


class MockExitException(Exception):
    pass


def mock_exit(code=None):
    # Mock for sys.exit
    raise MockExitException(code)


def setup(test):
    """Set up tempdir with sample project"""
    test.orig_sysargv = sys.argv[:]
    test.orig_exit = sys.exit
    test.orig_dir = os.getcwd()
    sys.argv[1:] = []
    sys.exit = mock_exit
    test.tempdir = tempfile.mkdtemp(prefix='dependencychecker')
    sample1_source = pkg_resources.resource_filename(
        'z3c.dependencychecker.tests', 'sample1')
    sample1_dir = os.path.join(test.tempdir, 'sample1')
    test.globs['sample1_dir'] = sample1_dir
    test.globs['ls'] = ls
    shutil.copytree(sample1_source, sample1_dir)
    # To prevent the sample .py files to be picked up by ourselves or other
    # tools, I'm postfixing them with ``_in``, now we get to rename them.
    # Same for zcml files.
    for (dirpath, dirnames, filenames) in os.walk(sample1_dir):
        for filename in (filenames + dirnames):
            if not filename.endswith('_in'):
                continue
            new_filename = filename.replace('_in', '')
            if new_filename == '_it__.py':
                # Oopsie :-) The replace works too well...
                new_filename = '__init__.py'
            source = os.path.join(dirpath, filename)
            target = os.path.join(dirpath, new_filename)
            os.rename(source, target)


def teardown(test):
    """Clean up"""
    shutil.rmtree(test.tempdir)
    sys.exit = test.orig_exit
    sys.argv[:] = test.orig_sysargv
    os.chdir(test.orig_dir)


test_suite = z3c.testsetup.register_all_tests(
    'z3c.dependencychecker',
    checker=checker,
    setup=setup,
    teardown=teardown)

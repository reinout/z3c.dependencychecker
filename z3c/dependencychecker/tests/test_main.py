# -*- coding: utf-8 -*-
from z3c.dependencychecker.dependencychecker import main
import os
import pkg_resources
import shutil
import sys
import tempfile
import pytest


class change_dir(object):
    """Step into a directory temporarily

    Copied from https://pythonadventures.wordpress.com/2013/12/15/chdir-a-context-manager-for-switching-working-directories/  # noqa: F501
    """

    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path

    def __enter__(self):
        os.chdir(self.new_dir)

    def __exit__(self, *args):
        os.chdir(self.old_dir)


class fake_sys_argv(object):

    def __init__(self):
        self.old_sys_argv = sys.argv[:]

    def __enter__(self):
        sys.argv[1:] = []

    def __exit__(self, *args):
        sys.argv[:] = self.old_sys_argv


@pytest.fixture(scope='module')
def fake_project():
    temp_folder = tempfile.mkdtemp(prefix='depcheck')
    fake_package_files = pkg_resources.resource_filename(
        'z3c.dependencychecker.tests',
        'sample1',
    )
    package_folder = os.path.join(temp_folder, 'sample1')
    shutil.copytree(fake_package_files, package_folder)
    # To prevent the sample .py files to be picked up by ourselves or other
    # tools, I'm postfixing them with ``_in``, now we get to rename them.
    # Same for zcml files.
    for (dirpath, dirnames, filenames) in os.walk(package_folder):
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

    yield package_folder
    shutil.rmtree(temp_folder)


MAIN_OUTPUT = """Unused imports
==============
src/sample1/unusedimports.py:7:  tempfile
src/sample1/unusedimports.py:4:  zest.releaser
src/sample1/unusedimports.py:6:  os

Missing requirements
====================
     Products.GenericSetup.interfaces.EXTENSION
     missing.req
     other.generic.setup.dependency
     plone.app.content.interfaces.INameFromTitle
     plone.app.dexterity.behaviors.metadata.IBasic
     plone.random1.interfaces.IMySchema
     plone.random2.content.MyType
     some_django_app
     something.origname
     zope.exceptions
     zope.interface
     zope.interface.verify

Missing test requirements
=========================
     plone.dexterity.browser.views.ContentTypeView
     plone.dexterity.interfaces.IContentType
     reinout.hurray
     transaction
     zope.filerepresentation.interfaces.IRawReadFile

Unneeded requirements
=====================
     some.other.extension
     unneeded.req

Requirements that should be test requirements
=============================================
     Needed.By.Test

Unneeded test requirements
==========================
     zope.testing

Note: requirements are taken from the egginfo dir, so you need
to re-run buildout (or setup.py or whatever) for changes in
setup.py to have effect.

"""


def test_main(capsys, fake_project):
    with change_dir(fake_project):
        with fake_sys_argv():
            main()
            out, err = capsys.readouterr()
            assert out == MAIN_OUTPUT

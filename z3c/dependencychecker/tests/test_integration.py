# -*- coding: utf-8 -*-
from z3c.dependencychecker.dependencychecker import main
from z3c.dependencychecker.tests.utils import change_dir
import mock
import sys


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


def test_highlevel_integration(capsys, fake_project):
    with change_dir(fake_project):
        arguments = ['dependencychecker']
        with mock.patch.object(sys, 'argv', arguments):
            main()
            out, err = capsys.readouterr()
            assert MAIN_OUTPUT in out

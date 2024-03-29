from pkg_resources import load_entry_point
from unittest import mock
from z3c.dependencychecker.main import main
from z3c.dependencychecker.utils import change_dir

import sys


MAIN_OUTPUT = """
Missing requirements
====================
     Products.GenericSetup.interfaces.EXTENSION
     missing.req
     other.generic.setup.dependency
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
to re-generate it, via `python -m build`, setuptools, zc.buildout
or any other means.

"""


def test_highlevel_integration(capsys, fake_project):
    with change_dir(fake_project):
        arguments = ["dependencychecker"]
        try:
            with mock.patch.object(sys, "argv", arguments):
                main()
        except SystemExit:
            out, err = capsys.readouterr()
            assert MAIN_OUTPUT in out
        else:
            assert True is False  # pragma: nocover


def test_entry_point_installed():
    """Check that pkg_resources can find the entry point defined in setup.py"""
    entry_point = load_entry_point(
        "z3c.dependencychecker", "console_scripts", "dependencychecker"
    )
    assert entry_point


def test_entry_point_run():
    """Check that calling the entry point calls a z3c.dependencychecker
    function
    """

    def fake_main():
        return "All dependencies are fine"

    import z3c.dependencychecker.main

    with mock.patch.object(z3c.dependencychecker.main, "main", fake_main):
        entry_point = load_entry_point(
            "z3c.dependencychecker", "console_scripts", "dependencychecker"
        )

    assert entry_point() == "All dependencies are fine"

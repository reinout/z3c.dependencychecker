from .utils import dist_info
from importlib.metadata import entry_points
from unittest import mock
from z3c.dependencychecker.main import main
from z3c.dependencychecker.utils import change_dir

import pytest
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
     pytest
     pytest_cov
     reinout.hurray
     transaction
     zope.filerepresentation.interfaces.IRawReadFile

Unneeded requirements
=====================
     setuptools
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


@pytest.fixture()
def mock_find_wheel(mocker):
    """Patch PackageMetadata to ignore that there is no real .whl file"""
    mock_find_wheel = mocker.patch(
        "z3c.dependencychecker.package.PackageMetadata._find_wheel_path"
    )
    return mock_find_wheel


def test_highlevel_integration(
    capsys, fake_project, mock_inspect_wheel, mock_find_wheel
):
    mock_inspect_wheel.return_value = dist_info(
        name="sample1",
        requirements=[
            "|setuptools|",
            "|zest.releaser|",
            "|unneeded.req|",
            "|Needed.By.Test|",
            "|needed.by.zcml|",
            "|also.needed.by.zcml|",
            "|generic.setup.dependency|",
            "test|my.package|",
            "test|needed.by.test.zcml|",
            "test|z3c.testsetup|",
            "test|zope.testbrowser|",
            "test|zope.testing|",
            "someotherextension|some.other.extension|",
        ],
    )

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
    """Check that the entry points defined do exist"""
    entry_point = entry_points(group="console_scripts", name="dependencychecker")
    assert entry_point


def test_entry_point_run():
    """Check that calling the entry point calls a z3c.dependencychecker
    function
    """

    def fake_main():
        return "All dependencies are fine"

    import z3c.dependencychecker.main

    with mock.patch.object(z3c.dependencychecker.main, "main", fake_main):
        (entry_point,) = entry_points(group="console_scripts", name="dependencychecker")
        main_function = entry_point.load()

    assert main_function() == "All dependencies are fine"

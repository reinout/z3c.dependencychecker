# -*- coding: utf-8 -*-
from z3c.dependencychecker.dotted_name import DottedName
import mock


def test_minimal():
    obj = DottedName('dotted.name')
    assert obj.name == 'dotted.name'


def test_no_path():
    obj = DottedName('dotted.name')
    assert obj.file_path is None


def test_file_path_given():
    obj = DottedName('dotted.name', file_path='/one/two')
    assert obj.file_path == '/one/two'


def test_requirement_constructor():
    mock_object = mock.MagicMock()
    mock_property = mock.PropertyMock(return_value='my.dotted.name')
    type(mock_object).project_name = mock_property

    obj = DottedName.from_requirement(mock_object)

    assert obj.file_path is None
    assert obj.name == 'my.dotted.name'


def test_requirement_constructor_with_path():
    mock_object = mock.MagicMock()
    mock_property = mock.PropertyMock(return_value='my.dotted.name')
    type(mock_object).project_name = mock_property

    obj = DottedName.from_requirement(mock_object, file_path='/one/two')

    assert obj.file_path == '/one/two'


def test_is_test_import():
    obj = DottedName('plone.app.dexterity', is_test=True)
    assert obj.is_test


def test_not_a_test_import():
    obj = DottedName('plone.app.dexterity')
    assert not obj.is_test

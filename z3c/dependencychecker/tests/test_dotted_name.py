from unittest import mock

import pytest

from z3c.dependencychecker.dotted_name import DottedName


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


def test_safe_name_no_changes():
    obj = DottedName('hi.there')
    assert obj.name == obj.safe_name


def test_safe_name_lowercase():
    original_name = 'Hi.There'
    obj = DottedName(original_name)
    assert original_name.lower() == obj.safe_name


def test_safe_name_dash_to_underscore():
    original_name = 'hi-there'
    obj = DottedName(original_name)
    assert original_name.replace('-', '_') == obj.safe_name


def test_safe_name_all_at_once():
    original_name = 'Hi-There'
    obj = DottedName(original_name)
    assert obj.safe_name == 'hi_there'


def test_namespaces_none():
    obj = DottedName('plain_package_name')
    assert obj.namespaces == ['plain_package_name']


def test_namespaces_some():
    obj = DottedName('plone.app.dexterity')
    assert len(obj.namespaces) == 3


def test_namespaces_some_details():
    obj = DottedName('plone.app.dexterity')
    assert obj.namespaces == ['plone', 'app', 'dexterity']


def test_namespaces_really_long():
    obj = DottedName('one.two.three.four.five.six')
    assert len(obj.namespaces) == 6
    assert obj.namespaces == ['one', 'two', 'three', 'four', 'five', 'six']


def test_is_namespaced_not():
    obj = DottedName('nope')
    assert obj.is_namespaced is False


def test_is_namespaced():
    obj = DottedName('plone.app.dexterity')
    assert obj.is_namespaced


def test_comparison_fallback():
    obj1 = DottedName('plone.app.dexterity')
    with pytest.raises(TypeError):
        obj1 < 33  # noqa: B015


def test_comparison_bigger_than():
    obj1 = DottedName('plone.app.ldap')
    obj2 = DottedName('plone.app.dexterity')
    assert obj1 > obj2


def test_comparison_bigger_or_equal_than():
    obj1 = DottedName('plone.app.ldap')
    obj2 = DottedName('plone.app.dexterity')
    assert obj1 >= obj2
    assert obj1 >= obj1


def test_comparison_smaller_than():
    obj1 = DottedName('plone.app.dexterity')
    obj2 = DottedName('plone.app.ldap')
    assert obj1 < obj2


def test_comparison_smaller_or_equal_than():
    obj1 = DottedName('plone.app.dexterity')
    obj2 = DottedName('plone.app.ldap')
    assert obj1 <= obj2
    assert obj1 <= obj1


def test_comparison_equality():
    obj1 = DottedName('plone.app.dexterity')
    assert obj1 == obj1


def test_comparison_equality_fallback():
    obj1 = DottedName('plone.app.dexterity')
    result = obj1 == object()
    assert not result


def test_repr():
    obj = DottedName('z3c.dependencychecker')
    assert repr(obj) == '<DottedName z3c.dependencychecker>'


def test_hash():
    obj1 = DottedName('bla')
    assert isinstance(hash(obj1), int)


def test_hash_in_use():
    obj1 = DottedName('one')
    obj2 = DottedName('two')
    obj3 = DottedName('three')
    obj4 = DottedName('one')
    uniques = {obj1, obj2, obj3, obj4}
    assert len(uniques) == 3

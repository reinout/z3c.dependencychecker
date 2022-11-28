from z3c.dependencychecker.dotted_name import DottedName


def test_fallback():
    test_import = object()
    requirement = DottedName('plone.app.dexterity')
    result = test_import in requirement
    assert not result


def test_same_name_no_namespaces():
    test_import = DottedName('Plone')
    requirement = DottedName('Plone')
    result = test_import in requirement
    assert result


def test_different_name_no_namespaces():
    test_import = DottedName('Plone')
    requirement = DottedName('Zope')
    result = test_import in requirement
    assert not result


def test_no_substring_match_beginning():
    test_import = DottedName('plo')
    requirement = DottedName('plone.app.imaging')
    result = test_import in requirement
    assert not result


def test_no_substring_match_beginning_reverse_check():
    test_import = DottedName('reinout.happy')
    requirement = DottedName('re')
    result = test_import in requirement
    assert not result


def test_no_substring_match_middle():
    test_import = DottedName('ima')
    requirement = DottedName('plone.app.imaging')
    result = test_import in requirement
    assert not result


def test_no_substring_match_end():
    test_import = DottedName('imaging')
    requirement = DottedName('plone.app.imaging')
    result = test_import in requirement
    assert not result


def test_subpackage():
    test_import = DottedName('plone.app.imaging.interfaces.IImage')
    requirement = DottedName('plone.app.imaging')
    result = test_import in requirement
    assert result


def test_same_number_of_namespaces_but_different():
    test_import = DottedName('plone.app.dexterity')
    requirement = DottedName('plone.app.imaging')
    result = test_import in requirement
    assert not result


def test_share_only_part_of_namespace():
    test_import = DottedName('plone.app.dexterity.interfaces')
    requirement = DottedName('plone.app.imaging')
    result = test_import in requirement
    assert not result


def test_both_sides_are_tested():
    test_import = DottedName('plone.app.dexterity')
    requirement = DottedName('plone.app.imaging.interfaces')
    result = test_import in requirement
    assert not result

import pytest

from z3c.dependencychecker.dotted_name import DottedName


def test_fallback():
    test_import = object()
    requirement = DottedName("plone.app.dexterity")
    assert test_import not in requirement


@pytest.mark.parametrize(
    "test_import,requirement,is_contained",
    (
        ("Plone", "Plone", True),
        ("Plone", "Zope", False),
        ("plo", "plone.app.imaging", False),
        ("reinout.happy", "re", False),
        ("ima", "plone.app.imaging", False),
        ("imaging", "plone.app.imaging", False),
        ("plone.app.imaging.interfaces.IImage", "plone.app.imaging", True),
        ("plone.app.dexterity", "plone.app.imaging", False),
        ("plone.app.dexterity.interfaces", "plone.app.imaging", False),
        ("plone.app.dexterity", "plone.app.imaging.interfaces", False),
    ),
)
def test_containment(test_import, requirement, is_contained):
    """Check DottedName.__contains__ dunder logic"""
    test_dotted_name = DottedName(test_import)
    requirement_dotted_name = DottedName(requirement)
    if is_contained:
        assert test_dotted_name in requirement_dotted_name
    else:
        assert test_dotted_name not in requirement_dotted_name

# -*- coding: utf-8 -*-
from z3c.dependencychecker.dotted_name import DottedName
from z3c.dependencychecker.db import ImportsDatabase
from z3c.dependencychecker.tests.utils import get_requirements_names


def test_no_dependencies():
    database = ImportsDatabase()
    assert isinstance(database._requirements, set)
    assert len(database._requirements) == 0


def test_add_dependencies():
    database = ImportsDatabase()
    database.add_requirements([
        DottedName('one'),
        DottedName('two'),
    ])

    names = get_requirements_names(database)
    assert len(names) == 2
    assert 'one' in names
    assert 'two' in names


def test_declared_dependencies_no_duplicates():
    """Check that if there are duplicated requirements,
    they are correctly filtered and only one remains
    """
    database = ImportsDatabase()
    database.add_requirements([
        DottedName('one'),
        DottedName('two'),
        DottedName('three'),
        DottedName('one'),
    ])

    requirements = get_requirements_names(database)
    assert len(requirements) == 3

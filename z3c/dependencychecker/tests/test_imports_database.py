# -*- coding: utf-8 -*-
from z3c.dependencychecker.dotted_name import DottedName
from z3c.dependencychecker.db import ImportsDatabase
from z3c.dependencychecker.tests.utils import get_extras_requirements_names
from z3c.dependencychecker.tests.utils import get_requirements_names
from z3c.dependencychecker.tests.utils import get_requirements_names_for_extra


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


def test_no_extras():
    database = ImportsDatabase()
    assert len(get_extras_requirements_names(database)) == 0


def test_extras_requirements_key_names():
    database = ImportsDatabase()
    database.add_extra_requirements('test', [DottedName('one'), ])
    database.add_extra_requirements('plone', [DottedName('two'), ])

    extras = get_extras_requirements_names(database)
    assert len(extras) == 2
    assert 'test' in extras
    assert 'plone' in extras


def test_add_extra_dependencies():
    database = ImportsDatabase()
    imports = [
        DottedName('one'),
        DottedName('two'),
    ]
    database.add_extra_requirements('test', imports)

    test_extras = get_requirements_names_for_extra(database, extra='test')
    assert len(test_extras) == 2
    assert 'one' in test_extras
    assert 'two' in test_extras


def test_warning_extra_declared_twice(caplog):
    """Show a warning if an extra is declared twice on setup.py"""
    database = ImportsDatabase()
    database.add_extra_requirements('test', [DottedName('one', )])
    database.add_extra_requirements('test', [DottedName('two', )])

    last_log = caplog.records[-1]
    message = 'extra requirement "test" is declared twice on setup.py'
    assert message == last_log.message


def test_direct_requirements_filtered_on_extras():
    """Check that direct requirements are filtered when added to an extra"""
    database = ImportsDatabase()
    database.add_requirements([DottedName('one'), DottedName('two', )])
    database.add_extra_requirements(
        'test',
        [DottedName('one', ), DottedName('three', ), ],
    )

    test_extras = get_requirements_names_for_extra(database, extra='test')
    assert len(test_extras) == 1
    assert 'three' in test_extras
    assert 'one' not in test_extras


def test_filter_duplicate_extra_requirements():
    """If an extra is declared twice, duplicate requirements are filtered"""
    database = ImportsDatabase()
    database.add_extra_requirements(
        'test',
        [DottedName('one', ), DottedName('three', ), ],
    )
    database.add_extra_requirements(
        'test',
        [DottedName('two', ), DottedName('three', ), ],
    )

    test_extras = get_requirements_names_for_extra(database, extra='test')
    assert len(test_extras) == 3
    assert 'one' in test_extras
    assert 'two' in test_extras
    assert 'three' in test_extras


def test_no_used_imports():
    database = ImportsDatabase()
    assert len(database.imports_used) == 0


def test_add_used_imports():
    database = ImportsDatabase()
    database.add_imports([
        DottedName('one'),
        DottedName('two'),
    ])
    assert len(database.imports_used) == 2

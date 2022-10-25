from z3c.dependencychecker.db import ImportsDatabase
from z3c.dependencychecker.dotted_name import DottedName
from z3c.dependencychecker.tests.utils import (
    get_extras_requirements_names,
    get_requirements_names,
    get_requirements_names_for_extra,
)


def test_no_dependencies():
    database = ImportsDatabase()
    assert isinstance(database._requirements, set)
    assert len(database._requirements) == 0


def test_add_dependencies():
    database = ImportsDatabase()
    database.add_requirements([DottedName('one'), DottedName('two')])

    names = get_requirements_names(database)
    assert len(names) == 2
    assert 'one' in names
    assert 'two' in names


def test_declared_dependencies_no_duplicates():
    """Check that if there are duplicated requirements,
    they are correctly filtered and only one remains
    """
    database = ImportsDatabase()
    database.add_requirements(
        [DottedName('one'), DottedName('two'), DottedName('three'), DottedName('one')]
    )

    requirements = get_requirements_names(database)
    assert len(requirements) == 3


def test_no_extras():
    database = ImportsDatabase()
    assert len(get_extras_requirements_names(database)) == 0


def test_extras_requirements_key_names():
    database = ImportsDatabase()
    database.add_extra_requirements('test', [DottedName('one')])
    database.add_extra_requirements('plone', [DottedName('two')])

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
    database.add_extra_requirements('test', [DottedName('one')])
    database.add_extra_requirements('test', [DottedName('two')])

    last_log = caplog.records[-1]
    message = 'extra requirement "test" is declared twice in setup.py'
    assert message == last_log.message


def test_direct_requirements_filtered_on_extras():
    """Check that direct requirements are filtered when added to an extra"""
    database = ImportsDatabase()
    database.add_requirements([DottedName('one'), DottedName('two')])
    database.add_extra_requirements('test', [DottedName('one'), DottedName('three')])

    test_extras = get_requirements_names_for_extra(database, extra='test')
    assert len(test_extras) == 1
    assert 'three' in test_extras
    assert 'one' not in test_extras


def test_filter_duplicate_extra_requirements():
    """If an extra is declared twice, duplicate requirements are filtered"""
    database = ImportsDatabase()
    database.add_extra_requirements('test', [DottedName('one'), DottedName('three')])
    database.add_extra_requirements('test', [DottedName('two'), DottedName('three')])

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
    database.own_dotted_name = DottedName('something-else')
    database.add_imports([DottedName('one'), DottedName('two')])
    assert len(database.imports_used) == 2


def test_unique_imports(minimal_database):
    minimal_database.add_imports(
        [
            DottedName('zope.component.ISite'),
            DottedName('zope.component'),
            DottedName('zope.component'),
        ]
    )

    dotted_names = minimal_database._get_unique_imports()
    names = [x.name for x in dotted_names]

    assert len(dotted_names) == 2
    assert 'zope.component' in names
    assert 'zope.component.ISite' in names


def test_unique_and_sorted_imports(minimal_database):
    minimal_database.add_imports(
        [DottedName('zope.c'), DottedName('zope.a'), DottedName('zope.b')]
    )

    dotted_names = minimal_database._get_unique_imports()

    assert len(dotted_names) == 3
    assert dotted_names[0].name == 'zope.a'
    assert dotted_names[1].name == 'zope.b'
    assert dotted_names[2].name == 'zope.c'


def test_filter_out_known_packages(minimal_database):
    dotted_name = DottedName('bla')
    result = minimal_database._filter_out_known_packages(dotted_name)
    assert result is True


def test_filter_out_known_packages_filtered(minimal_database):
    dotted_name = DottedName('setuptools')
    result = minimal_database._filter_out_known_packages(dotted_name)
    assert result is False


def test_filter_out_known_packages_filtered_nested(minimal_database):
    dotted_name = DottedName('setuptools.my.package')
    result = minimal_database._filter_out_known_packages(dotted_name)
    assert result is False


def test_filter_out_known_packages_filtered_nested_other(minimal_database):
    dotted_name = DottedName('pkg_resources.my.package')
    result = minimal_database._filter_out_known_packages(dotted_name)
    assert result is False


def test_filter_out_testing_imports(minimal_database):
    dotted_name = DottedName('bla', is_test=True)
    result = minimal_database._filter_out_testing_imports(dotted_name)
    assert result is False


def test_filter_out_testing_imports_no_testing_import(minimal_database):
    dotted_name = DottedName('bla', is_test=False)
    result = minimal_database._filter_out_testing_imports(dotted_name)
    assert result is True


def test_filter_out_own_package(minimal_database):
    minimal_database.own_dotted_name = DottedName('zope.component')
    result = minimal_database._filter_out_own_package(DottedName('bla'))
    assert result is True


def test_filter_out_own_package_filtered(minimal_database):
    minimal_database.own_dotted_name = DottedName('zope.component')
    result = minimal_database._filter_out_own_package(
        DottedName('zope.component'),
    )
    assert result is False


def test_filter_out_own_package_if_subpackage(minimal_database):
    minimal_database.own_dotted_name = DottedName('zope.component')
    subpackage = DottedName('zope.component.adapter')
    result = minimal_database._filter_out_own_package(subpackage)
    assert result is False


def test_filter_out_requirements(minimal_database):
    pkg = DottedName('zope.component')
    minimal_database.add_requirements([pkg])
    result = minimal_database._filter_out_requirements(pkg)
    assert result is False


def test_filter_out_std_library(minimal_database):
    pkg = DottedName('os.path.join')
    result = minimal_database._filter_out_python_standard_library(pkg)
    assert result is False


def test_filter_out_requirements_keep_other(minimal_database):
    pkg1 = DottedName('zope.component')
    pkg2 = DottedName('zope.interface')

    minimal_database.add_imports([pkg1, pkg2])
    minimal_database.add_requirements([pkg1])
    dotted_names = minimal_database.get_missing_imports()

    assert len(dotted_names) == 1
    assert pkg2 is dotted_names[0]


def test_filter_out_test_requirements_in_extra(minimal_database):
    dotted_name = DottedName('bli.blu.bla')
    minimal_database.add_extra_requirements(
        'test',
        (DottedName('bla'), DottedName('bli')),
    )
    result = minimal_database._filter_out_test_requirements(dotted_name)
    assert result is False


def test_filter_out_test_requirements_in_extra_variant(minimal_database):
    dotted_name = DottedName('bli.blu.bla')
    minimal_database.add_extra_requirements(
        'tests',
        (DottedName('bla'), DottedName('bli')),
    )
    result = minimal_database._filter_out_test_requirements(dotted_name)
    assert result is False


def test_get_imports_used_filter_subpackage(minimal_database):
    subpkg1 = DottedName('zope.component.adapter')
    subpkg2 = DottedName('zope.component.another.one')

    minimal_database.add_imports([subpkg1, subpkg2])
    minimal_database.add_requirements([DottedName('zope.component')])
    dotted_names = minimal_database.get_missing_imports()

    assert len(dotted_names) == 0


def test_get_imports_used_filter_std_library(minimal_database):
    minimal_database.add_imports(
        [
            DottedName('zope.component'),
            DottedName('os.path.join'),
            DottedName('sys.version_info'),
        ]
    )

    dotted_names = minimal_database.get_missing_imports()

    assert len(dotted_names) == 1
    assert dotted_names[0].name == 'zope.component'


def test_get_missing_testing_imports(minimal_database):
    test_import = DottedName('zope.component', is_test=True)
    regular_import = DottedName('zope.interface', is_test=False)
    minimal_database.add_imports([test_import, regular_import])

    dotted_names = minimal_database.get_missing_test_imports()

    assert len(dotted_names) == 1
    assert dotted_names[0] is test_import


def test_get_missing_testing_imports_filter_test_extras(minimal_database):
    test_import1 = DottedName('zope.component', is_test=True)
    test_import2 = DottedName('zope.interface', is_test=True)
    minimal_database.add_imports([test_import1, test_import2])
    minimal_database.add_extra_requirements('test', (test_import1,))

    dotted_names = minimal_database.get_missing_test_imports()

    assert len(dotted_names) == 1
    assert dotted_names[0] is test_import2


def test_get_test_extra(minimal_database):
    dotted_name = DottedName('bla')
    minimal_database.add_extra_requirements('test', (dotted_name,))
    result = minimal_database._get_test_extra()
    assert len(result) == 1
    assert dotted_name in result


def test_get_test_extra_plural(minimal_database):
    dotted_name = DottedName('bla')
    minimal_database.add_extra_requirements('tests', (dotted_name,))
    result = minimal_database._get_test_extra()
    assert len(result) == 1
    assert dotted_name in result


def test_get_test_extra_no_extra(minimal_database):
    dotted_name = DottedName('bla')
    minimal_database.add_extra_requirements('other', (dotted_name,))
    result = minimal_database._get_test_extra()
    assert result == []

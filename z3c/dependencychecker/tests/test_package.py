# -*- coding: utf-8 -*-
from z3c.dependencychecker.package import Package
from z3c.dependencychecker.package import PackageMetadata
from z3c.dependencychecker.tests.utils import get_extras_requirements_names
from z3c.dependencychecker.tests.utils import get_requirements_names
from z3c.dependencychecker.tests.utils import get_requirements_names_for_extra
import os


def test_package_has_metadata(minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)

    assert bool(getattr(package, 'metadata', False))
    assert isinstance(package.metadata, PackageMetadata)


def test_declared_dependencies(minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)
    package.set_declared_dependencies()

    requirements = get_requirements_names(package.imports)
    assert len(requirements) == 2
    assert 'one' in requirements
    assert 'two' in requirements


def test_declared_dependencies_empty(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = os.path.join(
        path,
        '{0}.egg-info'.format(package_name),
        'requires.txt',
    )
    with open(requires_file_path, 'w') as requires:
        requires.write('')

    package = Package(path)
    package.set_declared_dependencies()

    assert len(get_requirements_names(package.imports)) == 0


def test_declared_extras_dependencies_one_extra(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = os.path.join(
        path,
        '{0}.egg-info'.format(package_name),
        'requires.txt',
    )
    with open(requires_file_path, 'w') as requires:
        requires.write('\n'.join([
            '[extra]',
            'my.package',
            'another.package',
        ]))

    package = Package(path)
    package.set_declared_dependencies()
    package.set_declared_extras_dependencies()

    assert get_extras_requirements_names(package.imports) == ['extra', ]
    names = get_requirements_names_for_extra(package.imports, extra='extra')
    assert 'another.package' in names
    assert 'my.package' in names


def test_declared_extras_dependencies_only_on_extras(minimal_structure):
    """Check that main dependencies are not bundled on the extras"""
    path, package_name = minimal_structure
    requires_file_path = os.path.join(
        path,
        '{0}.egg-info'.format(package_name),
        'requires.txt',
    )
    with open(requires_file_path, 'w') as requires:
        requires.write('\n'.join([
            'setuptools',
            '',
            '[extra]',
            'my_package',
            'my_other_package',
        ]))

    package = Package(path)
    package.set_declared_dependencies()
    package.set_declared_extras_dependencies()

    names = get_requirements_names_for_extra(package.imports, extra='extra')
    assert 'setuptools' not in names


def test_multiple_extras(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = os.path.join(
        path,
        '{0}.egg-info'.format(package_name),
        'requires.txt',
    )
    with open(requires_file_path, 'w') as requires:
        requires.write('\n'.join([
            'setuptools',
            '',
            '[extra]',
            'my_package',
            'my_other_package',
            ''
            '[second]',
            'just',
            'laughs'
        ]))

    package = Package(path)
    package.set_declared_extras_dependencies()

    extras_names = get_extras_requirements_names(package.imports)
    assert len(extras_names) == 2
    assert 'second' in extras_names
    assert 'extra' in extras_names

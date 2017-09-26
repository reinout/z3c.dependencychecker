# -*- coding: utf-8 -*-
from z3c.dependencychecker.package import Package
from z3c.dependencychecker.package import PackageMetadata
from z3c.dependencychecker.tests.utils import get_requirements_names
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

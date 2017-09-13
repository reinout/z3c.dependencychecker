# -*- coding: utf-8 -*-
from z3c.dependencychecker.package import Package
from z3c.dependencychecker.package import PackageMetadata


def test_package_has_metadata(minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)

    assert bool(getattr(package, 'metadata', False))
    assert isinstance(package.metadata, PackageMetadata)

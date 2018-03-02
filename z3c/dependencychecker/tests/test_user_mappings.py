# -*- coding: utf-8 -*-
from z3c.dependencychecker.package import Package
from z3c.dependencychecker.dotted_name import DottedName
import os


EMPTY_FILE = ''
IGNORE_OTHER_KEYS = """[servers]
one = "1.2.3.4"
"""
ONLY_TOOL_TABLE = """[tool]
two = "5.6.7.8"
"""
EMPTY_DEPENDENCY_TABLE_NESTED = """[tool]
    [dependencycheker]
"""
EMPTY_DEPENDENCY_TABLE_MERGED = """[tool.dependencychecker]"""
ONE_MAPPING = """[tool.dependencychecker]
Zope2 = ["Products.Five", ]
"""
MORE_MAPPINGS = """[tool.dependencychecker]
Zope2 = ["Products.Five", ]
Zope4 = ["Products.Counter", "Products.Max" ]
"""
SUBTABLES = """[tool.dependencychecker]
Zope2 = ["Products.Five", ]
[tool.dependencychecker.options]
"""


def _write_user_config(path, content):
    file_path = os.sep.join([path, 'pyproject.toml', ])
    with open(file_path, 'w') as config_file:
        config_file.write(content)


def _update_requires_txt(path, package_name, packages):
    file_path = os.sep.join([
        path,
        '{0}.egg-info'.format(package_name),
        'requires.txt'
    ])
    with open(file_path, 'w') as config_file:
        for package in packages:
            config_file.write('{0}\n'.format(package))


def test_no_file(minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)
    package.set_user_mappings()
    assert package.imports.user_mappings == {}


def test_empty_file(minimal_structure):
    path, package_name = minimal_structure
    _write_user_config(path, EMPTY_FILE)
    package = Package(path)
    package.set_user_mappings()
    assert package.imports.user_mappings == {}


def test_ignore_other_keys(minimal_structure):
    path, package_name = minimal_structure
    _write_user_config(path, IGNORE_OTHER_KEYS)
    package = Package(path)
    package.set_user_mappings()
    assert package.imports.user_mappings == {}


def test_only_tool_table(minimal_structure):
    path, package_name = minimal_structure
    _write_user_config(path, ONLY_TOOL_TABLE)
    package = Package(path)
    package.set_user_mappings()
    assert package.imports.user_mappings == {}


def test_empty_dependency_table_nested(minimal_structure):
    path, package_name = minimal_structure
    _write_user_config(path, EMPTY_DEPENDENCY_TABLE_NESTED)
    package = Package(path)
    package.set_user_mappings()
    assert package.imports.user_mappings == {}


def test_empty_dependency_table_merged(minimal_structure):
    path, package_name = minimal_structure
    _write_user_config(path, EMPTY_DEPENDENCY_TABLE_MERGED)
    package = Package(path)
    package.set_user_mappings()
    assert package.imports.user_mappings == {}


def test_ignore_user_mappings(minimal_structure):
    path, package_name = minimal_structure
    _write_user_config(path, ONE_MAPPING)
    package = Package(path)
    package.inspect()

    assert len(package.imports.user_mappings) == 0


def test_one_user_mapping(minimal_structure):
    path, package_name = minimal_structure
    _write_user_config(path, ONE_MAPPING)
    _update_requires_txt(path, package_name, ['Zope2', ])
    package = Package(path)
    package.inspect()
    five_dotted_name = DottedName('Products.Five')
    zope_dotted_name = DottedName('Zope2')

    assert len(package.imports.user_mappings) == 1
    assert zope_dotted_name in package.imports.user_mappings

    mappings = package.imports.user_mappings[zope_dotted_name]
    assert len(mappings) == 1
    assert {five_dotted_name, } == mappings


def test_more_user_mappings(minimal_structure):
    path, package_name = minimal_structure
    _write_user_config(path, MORE_MAPPINGS)
    _update_requires_txt(path, package_name, ['Zope2', 'Zope4', ])
    package = Package(path)
    package.inspect()
    zope2_dotted_name = DottedName('Zope2')
    zope4_dotted_name = DottedName('Zope4')

    assert len(package.imports.user_mappings) == 2
    assert zope2_dotted_name in package.imports.user_mappings
    assert zope4_dotted_name in package.imports.user_mappings

    assert len(package.imports.user_mappings[zope4_dotted_name]) == 2


def test_subtables(minimal_structure):
    path, package_name = minimal_structure
    _write_user_config(path, SUBTABLES)
    _update_requires_txt(path, package_name, ['Zope2', ])
    package = Package(path)
    package.inspect()
    zope2_dotted_name = DottedName('Zope2')

    assert len(package.imports.user_mappings) == 1
    assert zope2_dotted_name in package.imports.user_mappings

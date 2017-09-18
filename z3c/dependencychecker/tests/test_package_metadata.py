# -*- coding: utf-8 -*-
from z3c.dependencychecker.package import PackageMetadata
import os
import pkg_resources
import shutil
import tempfile


def test_no_setup_py_file_found():
    folder = tempfile.mkdtemp()
    sys_exit = False
    try:
        PackageMetadata(folder)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_distribution_root(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.distribution_root == path


def test_setup_py_path(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.setup_py_path == os.path.join(path, 'setup.py')


def test_package_dir_on_distribution_root(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.package_dir == path


def test_package_dir_on_src_folder(minimal_structure):
    path, package_name = minimal_structure
    egg_info_folder = os.path.join(path, '{0}.egg-info'.format(package_name))
    src_folder = os.path.join(path, 'src')
    shutil.move(egg_info_folder, src_folder)
    metadata = PackageMetadata(path)

    assert metadata.package_dir == src_folder


def test_no_package_dir_found(minimal_structure):
    path, package_name = minimal_structure
    shutil.rmtree(os.path.join(path, '{0}.egg-info'.format(package_name)))

    sys_exit = False
    try:
        PackageMetadata(path)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_no_package_dir_and_no_src_folder(minimal_structure):
    path, package_name = minimal_structure
    shutil.rmtree(os.path.join(path, '{0}.egg-info'.format(package_name)))
    shutil.rmtree(os.path.join(path, 'src'))

    sys_exit = False
    try:
        PackageMetadata(path)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_egg_info_dir_path(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    egg_info_path = os.path.join(
        path,
        '{0}.egg-info'.format(package_name)
    )

    assert metadata.egg_info_dir == egg_info_path


def test_package_name(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.name == package_name


def test_working_set(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert isinstance(metadata._working_set, pkg_resources.WorkingSet)


def test_package_in_working_set(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    ourselves = metadata._get_ourselves_from_working_set()
    assert ourselves.project_name == package_name


def test_package_missing_pkg_info_file(minimal_structure):
    path, package_name = minimal_structure

    pkg_info = os.path.join(
        path,
        '{0}.egg-info'.format(package_name),
        'PKG-INFO',
    )
    os.remove(pkg_info)

    metadata = PackageMetadata(path)

    sys_exit = False
    try:
        metadata._get_ourselves_from_working_set()
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_package_broken_pkg_info_file(minimal_structure):
    path, package_name = minimal_structure

    pkg_info_path = os.path.join(
        path,
        '{0}.egg-info'.format(package_name),
        'PKG-INFO',
    )
    os.remove(pkg_info_path)
    with open(pkg_info_path, 'w') as pkg_info_file:
        pkg_info_file.write('\n'.join([
            'Name: bla',
        ]))

    metadata = PackageMetadata(path)
    sys_exit = False
    try:
        metadata._get_ourselves_from_working_set()
    except SystemExit:
        sys_exit = True

    assert sys_exit

from pathlib import Path
from z3c.dependencychecker.package import METADATA_FILES
from z3c.dependencychecker.package import PackageMetadata

import os
import pkg_resources
import pytest
import shutil
import tempfile


def test_no_setup_py_file_found():
    folder = tempfile.mkdtemp()
    sys_exit = False
    try:
        PackageMetadata(Path(folder))
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_distribution_root(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.distribution_root == path


@pytest.mark.parametrize("filename", METADATA_FILES)
def test_metadata_file_path(minimal_structure, filename):
    path, package_name = minimal_structure
    setup_py_path = path / "setup.py"
    setup_py_path.unlink()

    file_path = path / filename
    file_path.write_text("hi")

    metadata = PackageMetadata(path)
    assert metadata.metadata_file_path == file_path


def test_package_dir_on_distribution_root(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.package_dir == path


def test_package_dir_on_src_folder(minimal_structure):
    def move_top_level_to_src(package_path, egg_folder, src_path):
        top_level_folder = (egg_folder / "top_level.txt").read_text().strip()
        top_level_sources = package_path / top_level_folder

        shutil.move(str(top_level_sources), str(src_path))
        shutil.move(str(egg_folder), str(src_path))

    path, package_name = minimal_structure

    egg_info_folder = path / f"{package_name}.egg-info"
    src_folder = path / "src"

    move_top_level_to_src(path, egg_info_folder, src_folder)

    metadata = PackageMetadata(path)

    assert metadata.package_dir == src_folder


def test_package_dir_on_another_folder(minimal_structure):
    def move_top_level_to_folder(package_path, egg_folder, folder_path):
        top_level_folder = (egg_folder / "top_level.txt").read_text().strip()
        top_level_sources = package_path / top_level_folder

        shutil.move(str(top_level_sources), str(folder_path))
        shutil.move(str(egg_folder), str(folder_path))

    path, package_name = minimal_structure

    egg_info_folder = path / f"{package_name}.egg-info"
    folder_path = path / "somewhere"

    move_top_level_to_folder(path, egg_info_folder, folder_path)

    metadata = PackageMetadata(path)

    assert metadata.package_dir == folder_path


def test_no_package_dir_found(minimal_structure):
    path, package_name = minimal_structure
    shutil.rmtree(path / f"{package_name}.egg-info")

    sys_exit = False
    try:
        PackageMetadata(path)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_no_package_dir_and_no_src_folder(minimal_structure):
    path, package_name = minimal_structure
    shutil.rmtree(path / f"{package_name}.egg-info")
    shutil.rmtree(path / "src")

    sys_exit = False
    try:
        PackageMetadata(path)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_egg_info_dir_path(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    egg_info_path = path / f"{package_name}.egg-info"

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

    pkg_info = path / f"{package_name}.egg-info" / "PKG-INFO"
    pkg_info.unlink()

    metadata = PackageMetadata(path)

    sys_exit = False
    try:
        metadata._get_ourselves_from_working_set()
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_package_broken_pkg_info_file(minimal_structure):
    path, package_name = minimal_structure

    pkg_info_path = path / f"{package_name}.egg-info" / "PKG-INFO"
    pkg_info_path.unlink()
    pkg_info_path.write_text("\n".join(["Name: bla"]))

    metadata = PackageMetadata(path)
    sys_exit = False
    try:
        metadata._get_ourselves_from_working_set()
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_get_dependencies(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    names = [x.name for x in metadata.get_required_dependencies()]
    assert "one" in names
    assert "two" in names


def test_get_no_dependencies(minimal_structure):
    path, package_name = minimal_structure

    requires_file_path = path / f"{package_name}.egg-info" / "requires.txt"
    requires_file_path.unlink()

    metadata = PackageMetadata(path)

    requirements = list(metadata.get_required_dependencies())
    assert len(requirements) == 0


def test_dependencies_with_extras(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = path / f"{package_name}.egg-info" / "requires.txt"
    requires_file_path.write_text(
        "\n".join(
            [
                "one [with_extra]",
                "another[with_extra]",
                "yet[one,two,three,extras]",
                "something[only, two, with, spaces]",
            ]
        )
    )

    metadata = PackageMetadata(path)
    names = [x.name for x in metadata.get_required_dependencies()]

    assert len(names) == 4
    assert "one" in names
    assert "another" in names
    assert "yet" in names
    assert "something" in names


def test_dependencies_with_version_specifiers(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = path / f"{package_name}.egg-info" / "requires.txt"
    requires_file_path.write_text(
        "\n".join(
            ["one > 8.5", "another<=3.4", "yet==5.2", "something >=2.2.1,<2.3dev"]
        )
    )

    metadata = PackageMetadata(path)
    names = [x.name for x in metadata.get_required_dependencies()]

    assert len(names) == 4
    assert "one" in names
    assert "another" in names
    assert "yet" in names


def test_get_extra_dependencies(minimal_structure):
    path, package_name = minimal_structure

    requires_file_path = path / f"{package_name}.egg-info" / "requires.txt"
    requires_file_path.write_text("\n".join(["one", "", "[test]", "pytest", "mock"]))

    metadata = PackageMetadata(path)
    extras = list(metadata.get_extras_dependencies())
    extra_packages = [x.name for x in extras[0][1]]
    assert len(extras) == 1
    assert "pytest" in extra_packages
    assert "mock" in extra_packages


def test_get_extra_dependencies_ignore_zope(minimal_structure):
    path, package_name = minimal_structure

    requires_file_path = path / f"{package_name}.egg-info" / "requires.txt"
    requires_file_path.write_text("\n".join(["one", "", "[test]", "Zope"]))

    metadata = PackageMetadata(path)
    extras = list(metadata.get_extras_dependencies())
    extra_packages = [x.name for x in extras[0][1]]
    assert len(extras) == 1
    assert "Zope" not in extra_packages


def test_no_extras(minimal_structure):
    path, package_name = minimal_structure

    metadata = PackageMetadata(path)

    extras = list(metadata.get_extras_dependencies())
    assert len(extras) == 0


def test_top_level_txt_file_found(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.top_level == [path / package_name]


def test_no_top_level_txt_file_found(minimal_structure):
    path, package_name = minimal_structure
    (path / f"{package_name}.egg-info" / "top_level.txt").unlink()

    sys_exit = False
    metadata = PackageMetadata(path)
    try:
        metadata.top_level
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_no_sources_top_level_folder_found(minimal_structure):
    path, package_name = minimal_structure
    os.removedirs(path / package_name)

    sys_exit = False
    metadata = PackageMetadata(path)
    try:
        metadata.top_level
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_top_level_is_module(minimal_structure):
    path, package_name = minimal_structure
    top_level_path = path / package_name
    os.removedirs(top_level_path)
    top_level_module_path = Path(f"{top_level_path}.py")
    top_level_module_path.write_text("Does not matter")

    metadata = PackageMetadata(path)

    assert metadata.top_level == [top_level_module_path]


def test_top_level_multiple(minimal_structure):
    path, package_name = minimal_structure
    top_level_file = path / f"{package_name}.egg-info" / "top_level.txt"
    top_level_file.write_text("\n".join(["one", "two", "three"]))

    top_level_folders = [
        path / "one",
        path / "two",
        path / "three",
    ]
    for new_top_level in top_level_folders:
        new_top_level.mkdir()

    metadata = PackageMetadata(path)

    assert metadata.top_level == top_level_folders

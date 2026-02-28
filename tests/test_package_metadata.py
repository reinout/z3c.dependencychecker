from .utils import dist_info
from pathlib import Path
from z3c.dependencychecker.package import METADATA_FILES
from z3c.dependencychecker.package import PackageMetadata

import os
import pytest
import tempfile


def test_no_wheels_found():
    folder = tempfile.mkdtemp()
    sys_exit = False
    try:
        PackageMetadata(Path(folder))
    except SystemExit:
        sys_exit = True

    assert sys_exit


@pytest.mark.parametrize("filename", METADATA_FILES)
def test_metadata_file_path(minimal_structure, filename):
    path, _ = minimal_structure
    setup_py_path = path / "setup.py"
    setup_py_path.unlink()

    file_path = path / filename
    file_path.write_text("hi")

    metadata = PackageMetadata(path)
    assert metadata.metadata_file_path == file_path


def test_package_name(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    mock_inspect_wheel.return_value = dist_info(name=package_name)

    metadata = PackageMetadata(path)
    assert metadata.name == package_name


def test_get_dependencies(minimal_structure, mock_inspect_wheel):
    path, _ = minimal_structure
    mock_inspect_wheel.return_value = dist_info(requirements=["|one|", "|two|"])

    metadata = PackageMetadata(path)
    names = [x.name for x in metadata.get_required_dependencies()]
    assert "one" in names
    assert "two" in names


def test_get_no_dependencies(minimal_structure, mock_inspect_wheel):
    path, _ = minimal_structure
    mock_inspect_wheel.return_value = dist_info()

    metadata = PackageMetadata(path)
    requirements = list(metadata.get_required_dependencies())
    assert len(requirements) == 0


def test_dependencies_with_extras(minimal_structure, mock_inspect_wheel):
    path, _ = minimal_structure
    mock_inspect_wheel.return_value = dist_info(
        requirements=[
            "|one|with_extra",
            "|another|with_extra",
            "|yet|one,two,three,extras",
        ]
    )

    metadata = PackageMetadata(path)
    names = [x.name for x in metadata.get_required_dependencies()]

    assert len(names) == 3
    assert "one" in names
    assert "another" in names
    assert "yet" in names


def test_get_extra_dependencies(minimal_structure, mock_inspect_wheel):
    path, _ = minimal_structure

    mock_inspect_wheel.return_value = dist_info(
        requirements=["|one|", "test|pytest|", "test|mock|"]
    )

    metadata = PackageMetadata(path)
    extras = list(metadata.get_extras_dependencies())
    extra_packages = [x.name for x in extras[0][1]]
    assert len(extras) == 1
    assert "pytest" in extra_packages
    assert "mock" in extra_packages


def test_get_extra_dependencies_ignore_zope(minimal_structure, mock_inspect_wheel):
    path, _ = minimal_structure

    mock_inspect_wheel.return_value = dist_info(
        requirements=["|one|", "test|Zope|", "test|zope.interface|"]
    )

    metadata = PackageMetadata(path)
    extras = list(metadata.get_extras_dependencies())
    extra_packages = [x.name for x in extras[0][1]]
    assert len(extras) == 1
    assert "Zope" not in extra_packages
    assert "zope.interface" in extra_packages


def test_no_extras(minimal_structure):
    path, _ = minimal_structure

    metadata = PackageMetadata(path)

    extras = list(metadata.get_extras_dependencies())
    assert len(extras) == 0


def test_top_level_txt_file_found(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    mock_inspect_wheel.return_value = dist_info(top_levels=[package_name])
    metadata = PackageMetadata(path)

    assert metadata.top_level == [path / package_name]


def test_no_top_level_txt_file_found(minimal_structure):
    path, _ = minimal_structure

    sys_exit = False
    metadata = PackageMetadata(path)
    try:
        metadata.top_level
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_no_sources_top_level_folder_found(minimal_structure, mock_inspect_wheel):
    path, _ = minimal_structure

    mock_inspect_wheel.return_value = dist_info()

    sys_exit = False
    metadata = PackageMetadata(path)
    try:
        metadata.top_level
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_top_level_is_module(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    top_level_path = path / package_name
    os.removedirs(top_level_path)

    mock_inspect_wheel.return_value = dist_info(top_levels=[top_level_path.name])

    top_level_module_path = Path(f"{top_level_path}.py")
    top_level_module_path.write_text("Does not matter")

    metadata = PackageMetadata(path)

    assert metadata.top_level == [top_level_module_path]


def test_top_level_multiple(minimal_structure, mock_inspect_wheel):
    path, _ = minimal_structure
    mock_inspect_wheel.return_value = dist_info(top_levels=["one", "two", "three"])

    top_level_folders = [
        path / "one",
        path / "two",
        path / "three",
    ]
    for new_top_level in top_level_folders:
        new_top_level.mkdir()

    metadata = PackageMetadata(path)

    assert metadata.top_level == top_level_folders


def test_top_level_mismatch(minimal_structure, mock_inspect_wheel):
    path, _ = minimal_structure
    mock_inspect_wheel.return_value = dist_info(top_levels=["one", "two", "three"])

    # note that folder "three" is not created
    top_level_folders = [
        path / "one",
        path / "two",
    ]
    for new_top_level in top_level_folders:
        new_top_level.mkdir()

    metadata = PackageMetadata(path)

    assert metadata.top_level == top_level_folders


def test_top_level_in_src_folder(minimal_structure, mock_inspect_wheel):
    path, _ = minimal_structure
    mock_inspect_wheel.return_value = dist_info(top_levels=["one"])

    one_folder = path / "src" / "one"
    one_folder.mkdir()
    metadata = PackageMetadata(path)

    assert metadata.top_level == [one_folder]

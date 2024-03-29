from pathlib import Path
from z3c.dependencychecker.package import Package
from z3c.dependencychecker.package import PackageMetadata
from z3c.dependencychecker.tests.utils import get_extras_requirements_names
from z3c.dependencychecker.tests.utils import get_requirements_names
from z3c.dependencychecker.tests.utils import get_requirements_names_for_extra
from z3c.dependencychecker.tests.utils import get_sorted_imports_paths
from z3c.dependencychecker.tests.utils import write_source_file_at

import os


def test_package_has_metadata(minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)

    assert bool(getattr(package, "metadata", False))
    assert isinstance(package.metadata, PackageMetadata)


def test_declared_dependencies(minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)
    package.set_declared_dependencies()

    requirements = get_requirements_names(package.imports)
    assert len(requirements) == 2
    assert "one" in requirements
    assert "two" in requirements


def test_declared_dependencies_empty(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = path / f"{package_name}.egg-info" / "requires.txt"
    requires_file_path.write_text("")

    package = Package(path)
    package.set_declared_dependencies()

    assert len(get_requirements_names(package.imports)) == 0


def test_declared_extras_dependencies_one_extra(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = path / f"{package_name}.egg-info" / "requires.txt"
    requires_file_path.write_text(
        "\n".join(["[extra]", "my.package", "another.package"])
    )

    package = Package(path)
    package.set_declared_dependencies()
    package.set_declared_extras_dependencies()

    extras_names = get_extras_requirements_names(package.imports)
    assert len(extras_names) == 1
    assert "extra" in extras_names
    names = get_requirements_names_for_extra(package.imports, extra="extra")
    assert "another.package" in names
    assert "my.package" in names


def test_declared_extras_dependencies_only_on_extras(minimal_structure):
    """Check that main dependencies are not bundled on the extras"""
    path, package_name = minimal_structure
    requires_file_path = path / f"{package_name}.egg-info" / "requires.txt"
    requires_file_path.write_text(
        "\n".join(["setuptools", "", "[extra]", "my_package", "my_other_package"])
    )

    package = Package(path)
    package.set_declared_dependencies()
    package.set_declared_extras_dependencies()

    names = get_requirements_names_for_extra(package.imports, extra="extra")
    assert "setuptools" not in names


def test_multiple_extras(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = path / f"{package_name}.egg-info" / "requires.txt"
    requires_file_path.write_text(
        "\n".join(
            [
                "setuptools",
                "",
                "[extra]",
                "my_package",
                "my_other_package",
                "[second]",
                "just",
                "laughs",
            ]
        )
    )

    package = Package(path)
    package.set_declared_extras_dependencies()

    extras_names = get_extras_requirements_names(package.imports)
    assert len(extras_names) == 2
    assert "second" in extras_names
    assert "extra" in extras_names


def test_no_python_modules_found(minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)
    package.analyze_package()
    assert len(package.imports.imports_used) == 0


def test_python_modules_on_top_level_sources(minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(path / package_name, "__init__.py")
    package = Package(path)
    package.analyze_package()

    assert len(package.imports.imports_used) == 1
    paths = get_sorted_imports_paths(package.imports)
    assert paths[0].endswith("__init__.py")


def test_python_modules_found_inner_folders(minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(path / package_name, "__init__.py")
    write_source_file_at(path / package_name / "test", "__init__.py")
    write_source_file_at(path / package_name / "test", "test.py")

    package = Package(path)
    package.analyze_package()
    paths = get_sorted_imports_paths(package.imports)
    assert len(paths) == 3
    assert paths[0].endswith("__init__.py")
    assert paths[1].endswith("__init__.py")
    assert paths[2].endswith("test.py")


def test_top_level_is_a_file(minimal_structure):
    path, package_name = minimal_structure

    egg_info_folder = path / f"{package_name}.egg-info"
    top_level_file_path = egg_info_folder / "top_level.txt"
    top_level_folder = top_level_file_path.read_text().strip()

    top_level_sources = path / top_level_folder
    os.removedirs(top_level_sources)
    top_level_file = Path(f"{top_level_sources}.py")
    top_level_file.write_text("import one")

    package = Package(path)
    package.analyze_package()
    paths = get_sorted_imports_paths(package.imports)
    assert len(paths) == 1
    assert paths[0].parts[-1] == f"{top_level_folder}.py"

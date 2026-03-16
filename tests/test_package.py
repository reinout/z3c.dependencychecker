from .utils import dist_info
from .utils import get_extras_requirements_names
from .utils import get_requirements_names
from .utils import get_requirements_names_for_extra
from .utils import get_sorted_imports_paths
from .utils import write_source_file_at
from z3c.dependencychecker.package import Package
from z3c.dependencychecker.package import PackageMetadata

import os


def test_package_has_metadata(minimal_structure):
    path, _ = minimal_structure
    package = Package(path)

    assert bool(getattr(package, "metadata", False))
    assert isinstance(package.metadata, PackageMetadata)


def test_declared_dependencies(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    mock_inspect_wheel.return_value = dist_info(
        name=package_name, requirements=["|one|", "|two|"]
    )

    package = Package(path)
    package.set_declared_dependencies()

    requirements = get_requirements_names(package.imports)
    assert len(requirements) == 2
    assert "one" in requirements
    assert "two" in requirements


def test_declared_dependencies_empty(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    mock_inspect_wheel.return_value = dist_info(name=package_name)

    package = Package(path)
    package.set_declared_dependencies()

    assert len(get_requirements_names(package.imports)) == 0


def test_declared_extras_dependencies_one_extra(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    mock_inspect_wheel.return_value = dist_info(
        name=package_name, requirements=["extra|my.package|", "extra|another.package|"]
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


def test_no_python_modules_found(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    mock_inspect_wheel.return_value = dist_info(name=package_name)

    package = Package(path)
    package.analyze_package()
    assert len(package.imports.imports_used) == 0


def test_python_modules_on_top_level_sources(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    mock_inspect_wheel.return_value = dist_info(name=package_name)
    write_source_file_at(path / package_name, "__init__.py")

    package = Package(path)
    package.analyze_package()

    assert len(package.imports.imports_used) == 1
    paths = get_sorted_imports_paths(package.imports)
    assert paths[0].endswith("__init__.py")


def test_python_modules_found_inner_folders(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    mock_inspect_wheel.return_value = dist_info(name=package_name)
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


def test_top_level_is_a_file(minimal_structure, mock_inspect_wheel):
    path, package_name = minimal_structure
    mock_inspect_wheel.return_value = dist_info(name=package_name)

    # remove already existing top level folder...
    os.removedirs(path / package_name)
    # ...and instead create a python module
    (path / f"{package_name}.py").write_text("import one")

    package = Package(path)
    package.analyze_package()
    paths = get_sorted_imports_paths(package.imports)
    assert len(paths) == 1
    assert paths[0].parts[-1] == f"{package_name}.py"

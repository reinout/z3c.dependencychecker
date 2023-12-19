"""Standard tests configuration module automatically scanned by pytest.

This module is used to add generic fixtures and other boilerplate needed by
our test suite.

Keeping it here ensures that pytest finds it without extra setup and eases
reusability.
"""
import os
import random
import shutil
import string
import tempfile
from pathlib import Path

import pkg_resources
import pytest

from z3c.dependencychecker.dotted_name import DottedName
from z3c.dependencychecker.package import ImportsDatabase


@pytest.fixture
def fake_project():
    temp_folder = Path(tempfile.mkdtemp(prefix="depcheck"))
    fake_package_files = pkg_resources.resource_filename(
        "z3c.dependencychecker.tests",
        "sample1",
    )
    package_folder = temp_folder / "sample1"
    shutil.copytree(fake_package_files, package_folder)
    # To prevent the sample .py files to be picked up by ourselves or other
    # tools, I'm postfixing them with ``_in``, now we get to rename them.
    # Same for zcml files.
    for dirpath, dirnames, filenames in os.walk(package_folder):
        for filename in filenames + dirnames:
            if not filename.endswith("_in"):
                continue
            new_filename = filename.replace("_in", "")
            if new_filename == "_it__.py":
                # Oopsie :-) The replace works too well...
                new_filename = "__init__.py"
            source = Path(dirpath) / filename
            target = Path(dirpath) / new_filename
            os.rename(source, target)

    yield package_folder
    shutil.rmtree(temp_folder)


@pytest.fixture
def minimal_structure():
    """Creates a folder structure that contains the minimal files needed
    to make Package class be able to initialize without errors
    """
    folder = Path(tempfile.mkdtemp())
    _add_setup_py(folder)
    package_name = _add_egg_info(folder)

    src_folder = folder / "src"
    src_folder.mkdir(parents=True, exist_ok=True)

    yield folder, package_name

    shutil.rmtree(folder)


def _add_setup_py(folder):
    (folder / "setup.py").write_text("hi")


def _add_egg_info(folder):
    package_name = "".join(random.choice(string.ascii_lowercase) for _ in range(10))

    egg_info_folder_path = folder / f"{package_name}.egg-info"
    egg_info_folder_path.mkdir(parents=True, exist_ok=True)

    _write_pkg_info_file(egg_info_folder_path)
    _write_requires_file(egg_info_folder_path)
    _write_top_level_file(egg_info_folder_path, package_name)

    return package_name


def _write_pkg_info_file(folder):
    lines = "\n".join(
        ["Metadata-Version: 1.0", "Name: testpackage", "Version: 1.0.dev0"]
    )
    (folder / "PKG-INFO").write_text(lines)


def _write_requires_file(folder):
    (folder / "requires.txt").write_text("\n".join(["one", "two"]))


def _write_top_level_file(folder, package_name):
    (folder / "top_level.txt").write_text("\n".join([package_name]))

    sources_top_folder = folder.parent / package_name
    sources_top_folder.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def minimal_database():
    database = ImportsDatabase()
    database.own_dotted_name = DottedName("fake")
    return database

from cached_property import cached_property
from collections import defaultdict
from pathlib import Path
from wheel_inspect import inspect_wheel
from z3c.dependencychecker.db import ImportsDatabase
from z3c.dependencychecker.dotted_name import DottedName
from z3c.dependencychecker.modules import MODULES

import logging
import sys
import toml


METADATA_FILES = (
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
)

logger = logging.getLogger(__name__)


class PackageMetadata:
    """Information related to a python source distribution"""

    def __init__(self, path):
        logger.debug("Reading package metadata for %s...", path)
        self._path = path
        self._wheel_path = self._find_wheel_path()
        self.wheel_info = inspect_wheel(self._wheel_path)

    def _find_wheel_path(self):
        dist_folder = self._path / "dist"
        wheel_files = list(dist_folder.glob("*.whl"))
        if not wheel_files:
            logger.error(
                "No wheel file found in %s.\n"
                "You need to build the package first, e.g. with python -m build",
                dist_folder,
            )
            sys.exit(1)

        wheel_path = wheel_files[0]
        logger.debug(
            "Using the wheel %s",
            wheel_path,
        )
        return wheel_path

    @cached_property
    def metadata_file_path(self):
        for metadata_file in METADATA_FILES:
            file_path = self._path / metadata_file
            if file_path.exists():
                return file_path

    @cached_property
    def name(self):
        return self.wheel_info["dist_info"]["metadata"]["name"]

    def get_required_dependencies(self):
        metadata = self.wheel_info["dist_info"]["metadata"]
        all_dependencies = metadata.get("requires_dist", [])
        for requirement in all_dependencies:
            marker = requirement.get("marker")
            if marker and "extra" in requirement["marker"]:
                continue
            yield DottedName(
                requirement["name"],
                file_path=self.metadata_file_path,
            )

    def get_extras_dependencies(self):
        """Get this packages' extras dependencies defined in its configuration"""
        metadata = self.wheel_info["dist_info"]["metadata"]
        all_dependencies = metadata.get("requires_dist", [])
        file_path = self.metadata_file_path

        extras_mapping = defaultdict(list)
        for requirement in all_dependencies:
            if requirement["name"] == "Zope":
                continue

            if requirement["marker"] and "extra" in requirement["marker"]:
                extra_name = requirement["marker"].split("extra == ")[1].strip('"')
                extras_mapping[extra_name].append(
                    DottedName(requirement["name"], file_path=file_path)
                )

        for extra_name, dotted_names in extras_mapping.items():
            yield extra_name, dotted_names

    @cached_property
    def top_level(self):
        top_level_candidates = self.wheel_info["dist_info"]["top_level"]

        top_levels = []
        for candidate in top_level_candidates:
            possible_top_level = self._path / candidate

            if possible_top_level.exists():
                logger.debug("Found top level %s", possible_top_level)
                top_levels.append(possible_top_level)
                continue

            possible_src_path = self._path / "src" / candidate
            if possible_src_path.exists():
                logger.debug("Found top level %s", possible_src_path)
                top_levels.append(possible_src_path)
                continue

            single_module = Path(f"{possible_top_level}.py")
            if single_module.exists():
                logger.debug("Found top level %s", single_module)
                top_levels.append(single_module)
                continue

            logger.warning(
                "Top level %s\n"
                "not found but referenced by top_level metadata in wheel.",
                possible_top_level,
            )

        if top_levels:
            return top_levels

        logger.error(
            "There are paths found in top_level that do not exist.\n"
            "Maybe you need to put the package in development again?",
        )
        sys.exit(1)


class Package:
    """The python package that is being analyzed

    This class itself does not much per se, but connects the PackageMetadata
    with the ImportsDatabase, where the important bits are.
    """

    def __init__(self, path):
        self.path = path
        self.metadata = PackageMetadata(path)
        self.imports = ImportsDatabase()
        self.imports.own_dotted_name = DottedName(self.metadata.name)

    def inspect(self):
        self.set_declared_dependencies()
        self.set_declared_extras_dependencies()
        self.set_user_mappings()
        self.analyze_package()

    def set_declared_dependencies(self):
        """Add this packages' dependencies defined in its configuration to the database"""
        self.imports.add_requirements(self.metadata.get_required_dependencies())

    def set_declared_extras_dependencies(self):
        """Add this packages' extras dependencies defined in its configuration
        to the database
        """
        for extra, dotted_names in self.metadata.get_extras_dependencies():
            self.imports.add_extra_requirements(extra, dotted_names)

    def set_user_mappings(self):
        """Add any user defined mapping

        They need to be on a pyproject.toml file within the table
        tool.dependencychecker.

        See tests/test_user_mappings.py for examples.
        """
        config = self._load_user_config()
        for package, packages_provided in config.items():
            if package == "ignore-packages":
                if isinstance(packages_provided, list):
                    self.imports.add_ignored_packages(packages_provided)
                else:
                    logger.warning(
                        "ignore-packages key in pyproject.toml needs to "
                        "be a list, even for a single package to be ignored."
                    )
            elif isinstance(packages_provided, list):
                self.imports.add_user_mapping(package, packages_provided)

    def analyze_package(self):
        for top_folder in self.metadata.top_level:
            logger.debug("Analyzing package top_level %s...", top_folder)
            for module_obj in MODULES:
                logger.debug(
                    "Starting analyzing files using %s...",
                    module_obj,
                )
                for source_file in module_obj.create_from_files(top_folder):
                    logger.debug(
                        "Searching dependencies (with %s) in file %s...",
                        module_obj.__name__,
                        source_file.path,
                    )
                    self.imports.add_imports(source_file.scan())

    def _load_user_config(self):
        config_file_path = self.path / "pyproject.toml"
        try:
            config = toml.load(config_file_path)
            return config["tool"]["dependencychecker"]
        except (OSError, KeyError):
            return {}

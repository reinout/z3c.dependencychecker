import glob
import logging
import os
import sys

import pkg_resources
import toml
from cached_property import cached_property

from z3c.dependencychecker.db import ImportsDatabase
from z3c.dependencychecker.dotted_name import DottedName
from z3c.dependencychecker.modules import MODULES
from z3c.dependencychecker.utils import change_dir

logger = logging.getLogger(__name__)


class PackageMetadata:
    """Information related to a python source distribution

    It relies heavily on setuptools and pkg_resources APIs.
    """

    def __init__(self, path):
        logger.debug('Reading package metadata for %s...', path)
        self._path = path
        self._working_set = self._generate_working_set_with_ourselves()

    @cached_property
    def distribution_root(self):
        if 'setup.py' not in os.listdir(self._path):
            logger.error(
                'setup.py was not found in %s. '
                'Without it dependencychecker can not work.',
                self._path,
            )
            sys.exit(1)
        return self._path

    @cached_property
    def setup_py_path(self):
        return os.path.join(
            self.distribution_root,
            'setup.py',
        )

    @cached_property
    def package_dir(self):
        """Check where the .egg-info is located"""
        try_paths = [self.distribution_root]
        top_level_elements = [
            os.path.join(self.distribution_root, folder)
            for folder in os.listdir(self.distribution_root)
        ]
        try_paths += [folder for folder in top_level_elements if os.path.isdir(folder)]
        for path in try_paths:
            folder_found = self._find_egg_info_in_folder(path)
            if folder_found:
                logger.debug(
                    '.egg-info folder found at %s folder',
                    path,
                )
                return path

        logger.error('.egg-info folder could not be found')
        sys.exit(1)

    @staticmethod
    def _find_egg_info_in_folder(path):
        with change_dir(path):
            results = glob.glob('*.egg-info')
        return results

    @cached_property
    def egg_info_dir(self):
        results = self._find_egg_info_in_folder(self.package_dir)
        return os.path.join(
            self.package_dir,
            results[0],
        )

    @cached_property
    def name(self):
        path, filename = os.path.split(self.egg_info_dir)
        name = filename[: -len('.egg-info')]
        logger.debug(
            'Package name is %s',
            name,
        )

        return name

    def _generate_working_set_with_ourselves(self):
        """Use pkg_resources API to enable the package being analyzed

        This, enabling the package in pkg_resources, allows to extract
        information from .egg-info folders, for example, its requirements.
        """
        working_set = pkg_resources.WorkingSet()
        working_set.add_entry(self.package_dir)
        return working_set

    def _get_ourselves_from_working_set(self):
        """Use pkg_resources API to get a Requirement (in pkg_resources
        parlance) of the package being analyzed
        """
        ourselves = pkg_resources.Requirement.parse(self.name)
        try:
            package = self._working_set.find(ourselves)
            return package
        except ValueError:
            logger.error(
                'Package %s could not be found.\n'
                'You might need to put it in development mode,\n'
                'i.e. python setup.py develop',
                self.name,
            )
            sys.exit(1)

    def get_required_dependencies(self):
        this_package = self._get_ourselves_from_working_set()
        requirements = this_package.requires()
        for requirement in requirements:
            yield DottedName.from_requirement(
                requirement,
                file_path=self.setup_py_path,
            )

    def get_extras_dependencies(self):
        """Get this packages' extras dependencies defined in setup.py"""
        this_package = self._get_ourselves_from_working_set()

        for extra_name in this_package.extras:
            extra_requirements = this_package.requires(extras=(extra_name,))
            dotted_names = (
                DottedName.from_requirement(req, file_path=self.setup_py_path)
                for req in extra_requirements
            )
            yield extra_name, dotted_names

    @cached_property
    def top_level(self):
        path = os.path.join(
            self.egg_info_dir,
            'top_level.txt',
        )
        if not os.path.exists(path):
            logger.error(
                'top_level.txt could not be found on %s.\n'
                'It is needed for dependencychecker to work properly.',
                self.egg_info_dir,
            )
            sys.exit(1)

        with open(path) as top_level_file:
            content = top_level_file.read().strip()

        top_levels = []
        for candidate in content.split('\n'):
            possible_top_level = os.path.join(
                self.package_dir,
                candidate,
            )

            if os.path.exists(possible_top_level):
                logger.debug('Found top level %s', possible_top_level)
                top_levels.append(possible_top_level)
                continue

            single_module = f'{possible_top_level}.py'
            if os.path.exists(single_module):
                logger.debug('Found top level %s', single_module)
                top_levels.append(single_module)
                continue

            logger.warning(
                'Top level %s not found but referenced by top_level.txt',
                possible_top_level,
            )

        if top_levels:
            return top_levels

        logger.error(
            'There are paths found in %s%stop_level.txt that do not exist.\n'
            'Maybe you need to put the package in development again?',
            self.egg_info_dir,
            os.sep,
        )
        sys.exit(1)


class Package:
    """The python package that is being analyzed

    This class itself does not much per se, but connects the PackageMetadata
    with the ImportsDatabase, where the important bits are.
    """

    def __init__(self, path):
        self.metadata = PackageMetadata(path)
        self.imports = ImportsDatabase()
        self.imports.own_dotted_name = DottedName(self.metadata.name)

    def inspect(self):
        self.set_declared_dependencies()
        self.set_declared_extras_dependencies()
        self.set_user_mappings()
        self.analyze_package()

    def set_declared_dependencies(self):
        """Add this packages' dependencies defined in setup.py to the database"""
        self.imports.add_requirements(self.metadata.get_required_dependencies())

    def set_declared_extras_dependencies(self):
        """Add this packages' extras dependencies defined in setup.py to the
        database
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
            if package == 'ignore-packages':
                if isinstance(packages_provided, list):
                    self.imports.add_ignored_packages(packages_provided)
                else:
                    logger.warning(
                        'ignore-packages key in pyproject.toml needs to '
                        'be a list, even for a single package to be ignored.'
                    )
            elif isinstance(packages_provided, list):
                self.imports.add_user_mapping(package, packages_provided)

    def analyze_package(self):
        for top_folder in self.metadata.top_level:
            logger.debug('Analyzing package top_level %s...', top_folder)
            for module_obj in MODULES:
                logger.debug(
                    'Starting analyzing files using %s...',
                    module_obj,
                )
                for source_file in module_obj.create_from_files(top_folder):
                    logger.debug(
                        'Searching dependencies (with %s) in file %s...',
                        module_obj.__name__,
                        source_file.path,
                    )
                    self.imports.add_imports(source_file.scan())

    def _load_user_config(self):
        config_file_path = os.sep.join(
            [self.metadata.distribution_root, 'pyproject.toml']
        )
        try:
            config = toml.load(config_file_path)
            return config['tool']['dependencychecker']
        except (OSError, KeyError):
            return {}

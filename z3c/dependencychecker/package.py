# -*- coding: utf-8 -*-
from z3c.dependencychecker.dotted_name import DottedName
from z3c.dependencychecker.utils import change_dir
import glob
import logging
import os
import pkg_resources
import sys


logger = logging.getLogger(__name__)


class PackageMetadata(object):
    """Information related to a python source distribution

    It relies heavily on setuptools and pkg_resources APIs.
    """

    def __init__(self, path):
        self.distribution_root = self._get_distribution_root(path)
        self.setup_py_path = self._get_setup_py_path()
        self.package_dir = self._get_package_dir()
        self.egg_info_dir = self._get_egg_info_dir()
        self.name = self._get_package_name()
        self._working_set = self._generate_working_set_with_ourselves()
        self.top_level = self._get_sources_top_level()

    @staticmethod
    def _get_distribution_root(path):
        if 'setup.py' not in os.listdir(path):
            logger.error(
                'setup.py was not found in %s. '
                'Without it dependencychecker can not work.',
                path,
            )
            sys.exit(1)
        return path

    def _get_setup_py_path(self):
        return os.path.join(
            self.distribution_root,
            'setup.py',
        )

    def _get_package_dir(self):
        """Check where the .egg-info is located"""
        try_paths = (
            self.distribution_root,
            os.path.join(self.distribution_root, 'src', )
        )
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
        if not os.path.exists(path):
            logger.error(
                'Folder %s does not exist',
                path,
            )
            sys.exit(1)

        with change_dir(path):
            results = glob.glob('*.egg-info')

        return results

    def _get_egg_info_dir(self):
        results = self._find_egg_info_in_folder(self.package_dir)
        return os.path.join(
            self.package_dir,
            results[0],
        )

    def _get_package_name(self):
        path, filename = os.path.split(self.egg_info_dir)
        name = filename[:-len('.egg-info')]
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
            extra_requirements = this_package.requires(extras=(extra_name, ))
            dotted_names = (
                DottedName.from_requirement(req, file_path=self.setup_py_path)
                for req in extra_requirements
            )
            yield extra_name, dotted_names

    def _get_sources_top_level(self):
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

        sources_top_level = os.path.join(
            self.package_dir,
            content,
        )

        if os.path.exists(sources_top_level):
            return sources_top_level

        single_module_top_level = '{0}.py'.format(sources_top_level)
        if os.path.exists(single_module_top_level):
            return single_module_top_level

        logger.error(
            '%s does not exist but %s%stop_level.txt points there.\n'
            'Maybe you need to put the package in development again?',
            sources_top_level,
            self.egg_info_dir,
            os.sep,
        )
        sys.exit(1)

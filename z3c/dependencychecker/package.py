# -*- coding: utf-8 -*-
from z3c.dependencychecker.utils import change_dir
import glob
import logging
import os
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

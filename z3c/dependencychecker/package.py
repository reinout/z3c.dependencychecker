# -*- coding: utf-8 -*-
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

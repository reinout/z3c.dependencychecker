# -*- coding: utf-8 -*-
import os
import re


TEST_REGEX = r"""
{0}    # Needs to start with the path separator
\w*    # There could be some characters (or none)
test   # has to contain test on it
s?     # ensure plurals are handled as well
(      # Needs to end with either a path or a file extension:
{0}    # path separator
|      # OR
\w*    # some possible characters
\.     # a dot
\w+    # extension
)
""".format(os.sep)

TEST_IN_PATH_REGEX = re.compile(TEST_REGEX, re.VERBOSE)


class BaseModule(object):

    def __init__(self, package_path, full_path):
        self.path = full_path
        self._relative_path = self._get_relative_path(package_path, full_path)
        self.testing = self._is_test_module()

    @staticmethod
    def _get_relative_path(package_path, full_path):
        return full_path[len(package_path):]

    def _is_test_module(self):
        return bool(re.search(TEST_IN_PATH_REGEX, self._relative_path))

    @classmethod
    def create_from_files(cls, top_dir):
        raise NotImplementedError

    def scan(self):
        raise NotImplementedError

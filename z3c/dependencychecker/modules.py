# -*- coding: utf-8 -*-
from z3c.dependencychecker.dotted_name import DottedName
import ast
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


class PythonModule(BaseModule):

    @classmethod
    def create_from_files(cls, top_dir):
        """Find all python files in the package

        For that it gets the path to where top_level.txt points to,
        which is not always a folder:
        - folder example: z3c.dependencychecker itself
        - file example: flake8-isort or any other single file distribution

        Return this very same class, which would allow to call the scan()
        method to get an iterator over all this file's imports.
        """
        if top_dir.endswith('.py'):
            yield cls(top_dir, top_dir)
            return

        for path, folders, filenames in os.walk(top_dir):
            if '__init__.py' not in filenames:
                # Don't descend further into the tree.
                # Clear folders variable in-place.
                folders[:] = []
                continue

            for filename in filenames:
                if filename.endswith('.py'):
                    yield cls(
                        top_dir,
                        os.path.join(path, filename),
                    )

    def scan(self):
        for node in ast.walk(self._get_tree()):
            for dotted_name in self._process_ast_node(node):
                yield dotted_name

    def _get_tree(self):
        with open(self.path) as module_file:
            source_text = module_file.read()
        tree = ast.parse(source_text)
        return tree

    def _process_ast_node(self, node):
        if isinstance(node, ast.Import):
            for name in node.names:
                dotted_name = name.name
                yield DottedName(
                    dotted_name,
                    file_path=self.path,
                    is_test=self.testing,
                )

        elif isinstance(node, ast.ImportFrom):
            for name in node.names:
                if name.name == '*':
                    dotted_name = node.module
                else:
                    dotted_name = '{0}.{1}'.format(node.module, name.name)
                yield DottedName(
                    dotted_name,
                    file_path=self.path,
                    is_test=self.testing,
                )


MODULES = (
    PythonModule,
)

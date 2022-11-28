import ast
import fnmatch
import logging
import os
import re
from xml.etree import ElementTree

from z3c.dependencychecker.dotted_name import DottedName

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
""".format(
    os.sep
)

TEST_IN_PATH_REGEX = re.compile(TEST_REGEX, re.VERBOSE)

logger = logging.getLogger(__name__)


class BaseModule:
    def __init__(self, package_path, full_path):
        self.path = full_path
        self._relative_path = self._get_relative_path(package_path, full_path)
        self.testing = self._is_test_module()

    @staticmethod
    def _get_relative_path(package_path, full_path):
        return full_path[len(package_path) :]

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
            yield from self._process_ast_node(node)

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
            if self._is_relative_import(node):
                return
            for name in node.names:
                if name.name == '*':
                    dotted_name = node.module
                else:
                    dotted_name = f'{node.module}.{name.name}'
                yield DottedName(
                    dotted_name,
                    file_path=self.path,
                    is_test=self.testing,
                )

    @staticmethod
    def _is_relative_import(import_node):
        return import_node.level > 0


class ZCMLFile(BaseModule):
    """Extract imports from .zcml files

    These files are in common use in Zope/Plone based projects to define its
    components and more.
    """

    ELEMENTS = {
        'include': ('package',),
        'adapter': ('for', 'factory', 'provides'),
        'utility': ('provides', 'component'),
        'browser:page': ('class', 'for', 'layer'),
        'subscriber': ('handler', 'for'),
        'securityPolicy': ('component',),
        'genericsetup:registerProfile': ('provides',),
    }

    @classmethod
    def create_from_files(cls, top_dir):
        """Find all ZCML files in the package

        Return this very same class, which would allow to call the scan()
        method to get an iterator over all this file's imports.
        """
        if top_dir.endswith('.py'):
            return

        for path, _folders, filenames in os.walk(top_dir):
            for filename in filenames:
                if filename.endswith('.zcml'):
                    yield cls(
                        top_dir,
                        os.path.join(path, filename),
                    )

    def scan(self):
        tree = ElementTree.parse(self.path).getroot()

        for element in self.ELEMENTS:
            element_namespaced = self._build_namespaced_element(element)
            for node in tree.iter(element_namespaced):
                for attrib in self.ELEMENTS[element]:
                    yield from self._extract_dotted_name(node, attrib)

    def _extract_dotted_name(self, node, attr):
        if attr in node.keys():
            candidate_text = node.get(attr)
            for dotted_name in candidate_text.split(' '):
                if not dotted_name or dotted_name.startswith('.'):
                    continue

                if dotted_name == '*':
                    continue

                yield DottedName(
                    dotted_name,
                    file_path=self.path,
                    is_test=self.testing,
                )

    @staticmethod
    def _build_namespaced_element(element):
        if ':' in element:
            namespace, name = element.split(':')
            return '{{http://namespaces.zope.org/{0}}}{1}'.format(
                namespace,
                name,
            )

        return f'{{http://namespaces.zope.org/zope}}{element}'


class FTIFile(BaseModule):
    """Extract imports from Factory Type Information files

    These are xml files, usually located inside a types folder and used by
    Zope/Plone based projects to define its content types.
    """

    TYPES_FOLDER = f'{os.sep}types'

    @classmethod
    def create_from_files(cls, top_dir):
        """Find all FTI files, which are xml, in the package

        Return this very same class, which would allow to call the scan()
        method to get an iterator over all this file's imports.
        """
        if top_dir.endswith('.py'):
            return

        for path, _folders, filenames in os.walk(top_dir):
            for filename in filenames:
                if filename.endswith('.xml') and cls.TYPES_FOLDER in path:
                    yield cls(
                        top_dir,
                        os.path.join(path, filename),
                    )

    def scan(self):
        tree = ElementTree.parse(self.path).getroot()

        for node in tree.iter('property'):
            if 'name' in node.keys():
                name = node.get('name')
                if name == 'behaviors':
                    for subnode in node.iter('element'):
                        if 'value' in subnode.keys():
                            yield DottedName(
                                subnode.get('value'),
                                file_path=self.path,
                                is_test=self.testing,
                            )
                elif name in ('klass', 'schema'):
                    if node.text:
                        yield DottedName(
                            node.text.strip(),
                            file_path=self.path,
                            is_test=self.testing,
                        )


class GSMetadata(BaseModule):
    """Extract imports from Generic Setup metadata.xml files

    These files are in common use in Zope/Plone to define Generic Setup
    profile dependencies between projects.
    """

    PROFILE_RE = re.compile(r'profile-(?P<dotted_name>[\w.]+):[\w\W]+')

    @classmethod
    def create_from_files(cls, top_dir):
        """Find all metadata.xml files in the package

        Return this very same class, which would allow to call the scan()
        method to get an iterator over all this file's imports.
        """
        if top_dir.endswith('.py'):
            return

        for path, _folders, filenames in os.walk(top_dir):
            for filename in filenames:
                if filename == 'metadata.xml':
                    yield cls(
                        top_dir,
                        os.path.join(path, filename),
                    )

    def scan(self):
        tree = ElementTree.parse(self.path).getroot()

        for node in tree.iter('dependency'):
            if not node.text:
                continue
            result = self.PROFILE_RE.search(node.text.strip())
            if result:
                yield DottedName(
                    result.group('dotted_name'),
                    file_path=self.path,
                    is_test=self.testing,
                )


class PythonDocstrings(PythonModule):
    """Extract imports from docstrings found inside python modules

    There are some projects that rather than having separate files to keep the
    tests, they add the inline with the code as docstrings,
    either at class or method/function level.
    """

    NODES_WITH_DOCSTRINGS = (
        ast.Module,
        ast.ClassDef,
        ast.FunctionDef,
    )

    def scan(self):
        for node in ast.walk(self._get_tree()):
            if isinstance(node, self.NODES_WITH_DOCSTRINGS):
                docstring = ast.get_docstring(node)
                yield from self._parse_docstring(docstring)

    def _parse_docstring(self, docstring):
        if not docstring:
            return

        for line in docstring.split('\n'):
            code = self._extract_code(line)
            if code:
                try:
                    tree = ast.parse(code)
                except SyntaxError:
                    logger.debug(
                        'Could not parse "%s" in %s',
                        line,
                        self.path,
                    )
                    continue

                for node in ast.walk(tree):
                    for dotted_name in self._process_ast_node(node):
                        dotted_name.is_test = True
                        yield dotted_name

    @staticmethod
    def _extract_code(line):
        if '>>>' in line:
            position = line.find('>>>') + 3
            return line[position:].strip()


class DocFiles(PythonDocstrings):
    """Extract imports from documentation-like documents

    One extended testing pattern (at least in Zope/Plone based projects) is to
    write documentation in txt/rst files that contain tests to assert that
    documentation.
    """

    @classmethod
    def create_from_files(cls, top_dir):
        """Find all documentation files in the package

        For that it gets the path to where top_level.txt points to,
        which is not always a folder:
        - folder example: z3c.dependencychecker itself
        - file example: flake8-isort or any other single file distribution

        Return this very same class, which would allow to call the scan()
        method to get an iterator over all this file's imports.
        """
        if top_dir.endswith('.py'):
            return

        for path, _folders, filenames in os.walk(top_dir):
            for filename in filenames:
                if filename.endswith('.txt') or filename.endswith('.rst'):
                    yield cls(
                        top_dir,
                        os.path.join(path, filename),
                    )

    def scan(self):
        with open(self.path) as doc_file:
            for line in doc_file:
                code = self._extract_code(line)
                if code:
                    try:
                        tree = ast.parse(code)
                    except SyntaxError:
                        logger.debug(
                            'Could not parse "%s" in %s',
                            line,
                            self.path,
                        )
                        continue

                    for node in ast.walk(tree):
                        for dotted_name in self._process_ast_node(node):
                            dotted_name.is_test = True
                            yield dotted_name


class DjangoSettings(PythonModule):
    """Extract imports from Django settings.py

    These files are used to enable Django components.
    """

    @classmethod
    def create_from_files(cls, top_dir):
        """Find all settings.py files in the package

        For that it gets the path to where top_level.txt points to,
        which is not always a folder:
        - folder example: z3c.dependencychecker itself
        - file example: flake8-isort or any other single file distribution

        Return this very same class, which would allow to call the scan()
        method to get an iterator over all this file's imports.
        """
        if top_dir.endswith('.py'):
            return

        for path, _folders, filenames in os.walk(top_dir):
            for filename in filenames:
                if fnmatch.fnmatch(filename, '*settings.py'):
                    yield cls(
                        top_dir,
                        os.path.join(path, filename),
                    )

    def scan(self):
        for node in ast.walk(self._get_tree()):
            if isinstance(node, ast.Assign):
                if self._is_installed_apps_assignment(node):
                    if isinstance(node.value, (ast.Tuple, ast.List)):
                        for element in node.value.elts:
                            if isinstance(element, ast.Str):
                                yield DottedName(
                                    element.s,
                                    file_path=self.path,
                                    is_test=self.testing,
                                )

                if self._is_test_runner_assignment(node):
                    if isinstance(node.value, ast.Str):
                        yield DottedName(
                            node.value.s,
                            file_path=self.path,
                            is_test=True,
                        )

    @staticmethod
    def _is_installed_apps_assignment(node):
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == 'INSTALLED_APPS'
        ):
            return True

        return False

    @staticmethod
    def _is_test_runner_assignment(node):
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == 'TEST_RUNNER'
        ):
            return True

        return False


MODULES = (
    PythonModule,
    ZCMLFile,
    FTIFile,
    GSMetadata,
    PythonDocstrings,
    DocFiles,
    DjangoSettings,
)

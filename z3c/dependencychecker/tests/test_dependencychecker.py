# -*- coding: utf-8 -*-
from z3c.dependencychecker.dependencychecker import filter_missing
from z3c.dependencychecker.dependencychecker import filter_unneeded
from z3c.dependencychecker.dependencychecker import ZCML_PACKAGE_PATTERN
from z3c.dependencychecker.dependencychecker import ZCML_PROVIDES_PATTERN
from z3c.dependencychecker.dependencychecker import ZCML_COMPONENT_PATTERN
from z3c.dependencychecker.dependencychecker import ZCML_CLASS_PATTERN
from z3c.dependencychecker.dependencychecker import ZCML_FOR_PATTERN
from z3c.dependencychecker.dependencychecker import ZCML_HANDLER_PATTERN
from z3c.dependencychecker.dependencychecker import FTI_BEHAVIOR_PATTERN
from z3c.dependencychecker.dependencychecker import FTI_KLASS_PATTERN
from z3c.dependencychecker.dependencychecker import FTI_SCHEMA_PATTERN
from z3c.dependencychecker.dependencychecker import DOCTEST_FROM_IMPORT
from z3c.dependencychecker.dependencychecker import DOCTEST_IMPORT
from z3c.dependencychecker.dependencychecker import METADATA_DEPENDENCY_PATTERN
from z3c.dependencychecker.dependencychecker import PACKAGE_NAME_PATTERN
from z3c.dependencychecker.dependencychecker import SETUP_PY_PACKAGE_NAME_PATTERN  # noqa: E501
from z3c.dependencychecker.dependencychecker import name_from_setup
from z3c.dependencychecker.dependencychecker import existing_requirements
from z3c.dependencychecker.dependencychecker import determine_path
from z3c.dependencychecker.dependencychecker import normalize
from z3c.dependencychecker.tests.test_main import change_dir
import os
import re
import shutil
import tempfile
import unittest


class TestFilterMissing(unittest.TestCase):

    def test_empty_list(self):
        imports_found = []
        required_imports = []
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            [],
        )

    def test_exact_matching(self):
        """Exact matching lists result in an empty list"""
        imports_found = ['a', ]
        required_imports = ['a', ]
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            [],
        )

    def test_report_missing_imports(self):
        imports_found = ['flup', ]
        required_imports = []
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            ['flup', ],
        )

    def test_report_missing_imports_only_once(self):
        imports_found = ['flup', 'flup', ]
        required_imports = []
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            ['flup', ],
        )

    def test_sorted_output(self):
        """Results are returned sorted so it prints a reproducible output"""
        imports_found = ['a', 'c', 'b', ]
        required_imports = []
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            ['a', 'b', 'c', ],
        )

    def test_subpackage_matching(self):
        """A requirement for some.thing is assumed to be enough for
        some.thing.else
        """
        imports_found = ['some.thing.else', ]
        required_imports = ['some.thing', ]
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            [],
        )

    def test_subpackage_matching_ignores_case(self):
        """A requirement for Some.Thing is assumed to be enough for
        some.thing.else
        """
        imports_found = ['some.thing.else', ]
        required_imports = ['Some.Thing', ]
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            [],
        )

    def test_subpackage_matching_no_namespace(self):
        """A requirement for Some is assumed to be enough for
        some.thing.else
        """
        imports_found = ['some.thing.else', ]
        required_imports = ['Some', ]
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            [],
        )

    def test_import_more_specific_than_requirement(self):
        """A requirement for some.thing.else is NOT assumed to be enough for
        some.thing
        """
        imports_found = ['some.thing', ]
        required_imports = ['some.thing.else', ]
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            ['some.thing', ],
        )

    def test_similar_names(self):
        imports_found = ['zope.app.securitypolicy', ]
        required_imports = ['zope.app.security', ]
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            ['zope.app.securitypolicy', ],
        )

    def test_package_from_import(self):
        """An oft-occurring example:

        An import like ``from zope import interface``,
        and a requirement for ``zope.interface``.
        zope is picked up by the importchecker mechanism (not zope.interface!),
        so we get the following problem:
        """
        imports_found = ['zope', ]
        required_imports = ['zope.interface', ]
        result = filter_missing(imports_found, required_imports)
        self.assertEqual(
            result,
            ['zope', ],
        )


class TestFilterUnneeded(unittest.TestCase):

    def test_empty(self):
        imports_found = []
        required_imports = []
        result = filter_unneeded(imports_found, required_imports)
        self.assertEqual(
            result,
            [],
        )

    def test_exact_match(self):
        imports_found = ['zope.interface', ]
        required_imports = ['zope.interface', ]
        result = filter_unneeded(imports_found, required_imports, name='test')
        self.assertEqual(
            result,
            [],
        )

    def test_report_too_specific_requirements(self):
        imports_found = ['zope', ]
        required_imports = ['zope.interface', ]
        result = filter_unneeded(imports_found, required_imports)
        self.assertEqual(
            result,
            ['zope.interface', ],
        )

    def test_no_duplicates(self):
        imports_found = []
        required_imports = ['a', 'a', ]
        result = filter_unneeded(imports_found, required_imports)
        self.assertEqual(
            result,
            ['a', ],
        )

    def test_sorted_output(self):
        imports_found = []
        required_imports = ['a', 'c', 'b', ]
        result = filter_unneeded(imports_found, required_imports)
        self.assertEqual(
            result,
            ['a', 'b', 'c', ],
        )


class TestXMLRegexes(unittest.TestCase):

    @staticmethod
    def check_regex(regex, one_match, two_matches):
        empty = re.findall(regex, '')
        one = re.findall(regex, one_match)
        two = re.findall(regex, two_matches)
        return empty, one, two

    def test_zcml_package(self):
        one = '<bla\npackage="zope.interface"/>'
        two = one + '<bla\npackage="zope.component"/>'
        results = self.check_regex(ZCML_PACKAGE_PATTERN, one, two, )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['zope.interface', ],
        )
        self.assertEqual(
            results[2],
            ['zope.interface', 'zope.component', ]
        )

    def test_zcml_provides(self):
        one = '<bla\nprovides="Products.GenericSetup"/>'
        two = one + '<bla\nprovides="Products.SpecificSetup"/>'
        results = self.check_regex(ZCML_PROVIDES_PATTERN, one, two, )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['Products.GenericSetup', ],
        )
        self.assertEqual(
            results[2],
            ['Products.GenericSetup', 'Products.SpecificSetup', ],
        )

    def test_zcml_component(self):
        one = '<bla\ncomponent="Products.CMFPlone"/>'
        two = one + '<bla\ncomponent="Products.CMFCore"/>'
        results = self.check_regex(ZCML_COMPONENT_PATTERN, one, two, )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['Products.CMFPlone', ],
        )
        self.assertEqual(
            results[2],
            ['Products.CMFPlone', 'Products.CMFCore', ],
        )

    def test_zcml_class(self):
        one = '<bla\nclass="plone.app.upgrade"/>'
        two = one + '<bla\nclass="plone.app.dexterity"/>'
        results = self.check_regex(ZCML_CLASS_PATTERN, one, two, )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['plone.app.upgrade', ],
        )
        self.assertEqual(
            results[2],
            ['plone.app.upgrade', 'plone.app.dexterity', ],
        )

    def test_zcml_for(self):
        one = '<bla\nfor="plone.app.iterate"/>'
        two = one + '<bla\nfor="plone.app.registry"/>'
        results = self.check_regex(ZCML_FOR_PATTERN, one, two, )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['plone.app.iterate', ],
        )
        self.assertEqual(
            results[2],
            ['plone.app.iterate', 'plone.app.registry', ],
        )

    def test_zcml_handler(self):
        one = '<bla\nhandler="plone.app.multilingual"/>'
        two = one + '<bla\nhandler="plone.app.layout"/>'
        results = self.check_regex(ZCML_HANDLER_PATTERN, one, two, )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['plone.app.multilingual', ],
        )
        self.assertEqual(
            results[2],
            ['plone.app.multilingual', 'plone.app.layout', ],
        )

    def test_fti_behavior(self):
        one = ' <element value="plone.app.behavior.Super"/>'
        two = one + ' <element value="plone.app.behavior.EvenBetter"/>'
        results = self.check_regex(FTI_BEHAVIOR_PATTERN, one, two, )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['plone.app.behavior.Super', ],
        )
        self.assertEqual(
            results[2],
            ['plone.app.behavior.Super', 'plone.app.behavior.EvenBetter', ],
        )

    def test_fti_schema(self):
        one = ' name="schema">Products.CMFPlone.interfaces.IFile<'
        results = self.check_regex(FTI_SCHEMA_PATTERN, one, '', )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['Products.CMFPlone.interfaces.IFile', ],
        )

    def test_fti_klass(self):
        one = ' name="klass">Products.CMFPlone.file.MyFile<'
        results = self.check_regex(FTI_KLASS_PATTERN, one, '', )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['Products.CMFPlone.file.MyFile', ],
        )

    def test_generic_setup_metadata_xml(self):
        one = '<dependency>profile-plone.app.theming:default</dependency>'
        two = one + '\n<dependency>profile-plone.app.blob:default</dependency>'
        results = self.check_regex(METADATA_DEPENDENCY_PATTERN, one, two, )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            ['plone.app.theming', ],
        )
        self.assertEqual(
            results[2],
            ['plone.app.theming', 'plone.app.blob', ],
        )


class TestDoctestImportsRegexes(unittest.TestCase):

    @staticmethod
    def check_regex(regex, *examples):
        results = [
            re.findall(regex, ''),
        ]
        for example in examples:
            results.append(
                re.findall(regex, example)
            )
        return results

    def test_imports(self):
        results = self.check_regex(
            DOCTEST_IMPORT,
            '    >>> print 7',
            '    >>> import zope.interface',
            '    >>> #import zope.interface',
        )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            [],
        )
        self.assertEqual(
            results[2],
            ['zope.interface', ],
        )
        self.assertEqual(
            results[3],
            [],
        )

    def test_from_imports(self):
        results = self.check_regex(
            DOCTEST_FROM_IMPORT,
            '    >>> print 7',
            '    >>> from zope import interface',
            '    >>> from zope import interface, component',
            '    >>> #import zope.interface',
        )
        self.assertEqual(results[0], [])
        self.assertEqual(
            results[1],
            [],
        )
        self.assertEqual(
            results[2],
            [('zope', 'interface'), ],
        )
        self.assertEqual(
            results[3],
            [('zope', 'interface, component'), ],
        )
        self.assertEqual(
            results[4],
            [],
        )


class TestPackageNameRegex(unittest.TestCase):
    """Detect proper package names

    To detect whether strings in Django settings can be package names or
    something else
    """

    @staticmethod
    def check_name(input_text):
        return bool(
            re.match(PACKAGE_NAME_PATTERN, input_text)
        )

    def test_proper_package_names(self):
        self.assertFalse(self.check_name(''))
        self.assertTrue(self.check_name('compressor'))
        self.assertTrue(self.check_name('lizard-ui'))
        self.assertTrue(self.check_name('lizard_ui'))
        self.assertTrue(self.check_name('lizard_ui.something.else'))
        self.assertFalse(self.check_name('reinout@lizard_ui'))
        self.assertFalse(self.check_name('reinout with spaces'))


class TestSetupPyPackageName(unittest.TestCase):

    @staticmethod
    def check_name(input_text):
        return re.findall(
            SETUP_PY_PACKAGE_NAME_PATTERN,
            input_text,
        )

    def test_setup_py_package_name(self):
        self.assertEqual(
            self.check_name(''),
            [],
        )
        self.assertEqual(
            self.check_name('my_package'),
            [],
        )
        self.assertEqual(
            self.check_name('name="my_package"'),
            ['my_package', ],
        )
        self.assertEqual(
            self.check_name('setup(name="my_package"'),
            ['my_package', ],
        )
        self.assertEqual(
            self.check_name('    name=\'my_package\','),
            ['my_package', ],
        )


class TestUtilities(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix='depcheck')

    def tearDown(self):
        shutil.rmtree(self.directory)

    def write_setup_py_file(self, file_lines):
        setup_py_file_path = os.path.join(self.directory, 'setup.py')
        with open(setup_py_file_path, 'w') as setup_py:
            setup_py.write('\n'.join(file_lines))

        return setup_py_file_path

    def test_grab_name(self):
        file_lines = [
            'import sys',
            'assert "--name" in sys.argv',
            'print "my_name"',
        ]
        self.write_setup_py_file(file_lines)
        with change_dir(self.directory):
            name = name_from_setup()
        self.assertEqual(
            name,
            'my_name',
        )

    def test_grab_no_name_raises_exception(self):
        file_lines = [
            'raise UserError("aaaa")',
        ]
        self.write_setup_py_file(file_lines)

        # can not use assertRaises as SystemExit does not subclass Exception
        sys_exit = False
        try:
            with change_dir(self.directory):
                name_from_setup()
        except SystemExit:
            sys_exit = True

        self.assertTrue(sys_exit)

    def test_grab_name_file_parsed_fine(self):
        """Although the file content would raise an error,
        name_from_setup is able to handle that and use a regex to find it"""
        file_lines = [
            'raise UserError("raargh")',
            'name="my_package"',
        ]
        self.write_setup_py_file(file_lines)
        with change_dir(self.directory):
            name = name_from_setup()

        self.assertEqual(
            name,
            'my_package',
        )

    def test_existing_requirements(self):
        """The normal ``src/xyz.egg-info`` case is already handled by the
        main example.

        Here we create the egg info dir directly in the directory itself.
        Not the common case, but we support the lack of ``src/`` dir.

        If we grab the requirements now, we hit two corner cases:

        - The egg-info dir is here, not in src.

        - The requires.txt file is missing.

        Grab it and watch the fireworks:
        """
        file_lines = [
            'import sys',
            'assert "--name" in sys.argv',
            'print "my_name"',
        ]
        self.write_setup_py_file(file_lines)
        with change_dir(self.directory):
            os.mkdir('my_name.egg-info')

        # can not use assertRaises as SystemExit does not subclass Exception
        sys_exit = False
        try:
            with change_dir(self.directory):
                existing_requirements(name='test')
        except SystemExit:
            sys_exit = True

        self.assertTrue(sys_exit)

    def test_determine_path_acutal(self):
        with change_dir(self.directory):
            self.assertEqual(
                determine_path([self.directory]),
                self.directory
            )

    def test_determine_path_non_existing(self):
        sys_exit = False
        try:
            determine_path(['/does/not/exist'])
        except SystemExit:
            sys_exit = True

        self.assertTrue(sys_exit)

    def test_determine_path_given_a_file(self):
        file_lines = [
            'import sys',
            'assert "--name" in sys.argv',
            'print "my_name"',
        ]
        file_path = self.write_setup_py_file(file_lines)

        sys_exit = False
        try:
            determine_path([file_path])
        except SystemExit:
            sys_exit = True

        self.assertTrue(sys_exit)

    def test_normalize_lowercase(self):
        self.assertEqual(
            normalize('reinout'),
            'reinout',
        )

    def test_normalize_mixedcase(self):
        self.assertEqual(
            normalize('ReiNout'),
            'reinout',
        )

    def test_normalize_dashes(self):
        self.assertEqual(
            normalize('rein-out'),
            'rein_out',
        )
        self.assertEqual(
            normalize('rein-ou-t'),
            'rein_ou_t',
        )

    def test_normalize_underscores(self):
        self.assertEqual(
            normalize('rein_out'),
            'rein_out',
        )
        self.assertEqual(
            normalize('rein_ou_t'),
            'rein_ou_t',
        )

    def test_normalize_a_bit_of_everything(self):
        self.assertEqual(
            normalize('rEin_Ou-t'),
            'rein_ou_t',
        )

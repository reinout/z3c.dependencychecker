# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import _ast
import ast
import commands
import fnmatch
import logging
import optparse
import os
import re
import sys

import pkg_resources

from z3c.dependencychecker import importchecker


logger = logging.getLogger(__name__)

PACKAGE_NAME_PATTERN = re.compile(r"""
^            # Start of string
[a-zA-Z]     # Some character at the beginning.
[\w\-\.]+    # \w is a-z, A-Z, underscore, numbers.
             # Dash is also ok, as is a dot.
$            # End of string
""", re.VERBOSE)

DOTTED_PATH_PATTERN = re.compile(r"""
^            # Start of string
[a-zA-Z]     # Some character at the beginning.
\w*          # \w is a-z, A-Z, underscore, numbers.
\.           # At least one dot
[\w\.]+      # \w is a-z, A-Z, underscore, numbers.
             # more dots are OK.
$            # End of string
""", re.VERBOSE)

ZCML_PACKAGE_PATTERN = re.compile(r"""
\s           # Whitespace.
package=     #
['\"]        # Single or double quote.
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
['\"]        # Single or double quote.
""", re.VERBOSE)

ZCML_PROVIDES_PATTERN = re.compile(r"""
\s           # Whitespace.
provides=    #
['\"]        # Single or double quote.
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
['\"]        # Single or double quote.
""", re.VERBOSE)

ZCML_COMPONENT_PATTERN = re.compile(r"""
\s           # Whitespace.
component=   #
['\"]        # Single or double quote.
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
['\"]        # Single or double quote.
""", re.VERBOSE)

ZCML_CLASS_PATTERN = re.compile(r"""
\s           # Whitespace.
class=       #
['\"]        # Single or double quote.
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
['\"]        # Single or double quote.
""", re.VERBOSE)

ZCML_FOR_PATTERN = re.compile(r"""
\s           # Whitespace.
for=         #
['\"]        # Single or double quote.
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
['\"]        # Single or double quote.
""", re.VERBOSE)

ZCML_HANDLER_PATTERN = re.compile(r"""
\s           # Whitespace.
handler=     #
['\"]        # Single or double quote.
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
['\"]        # Single or double quote.
""", re.VERBOSE)

FTI_BEHAVIOR_PATTERN = re.compile(r"""
\s           # Whitespace.
<element     #
\s+          #
value=       #
['\"]        # Single or double quote.
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
['\"]        # Single or double quote.
""", re.VERBOSE)

FTI_SCHEMA_PATTERN = re.compile(r"""
\s           # Whitespace.
name=        #
['\"]        # Single or double quote.
schema       #
['\"]        # Single or double quote.
>            # End of opening tag
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
<            # Start of closing tag
""", re.VERBOSE)

FTI_KLASS_PATTERN = re.compile(r"""
\s           # Whitespace.
name=        #
['\"]        # Single or double quote.
klass        #
['\"]        # Single or double quote.
>            # End of opening tag
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
<            # Start of closing tag
""", re.VERBOSE)

DOCTEST_IMPORT = re.compile(r"""
^            # From start of line
\s+          # Whitespace.
>>>          # Doctestmarker.
\s+          # Whitespace.
import       # 'import' keyword
\s+          # Whitespace
(?P<module>  # Start of 'module' variable.
[\w.]+       # Alpha-numeric characters.
)            # End of 'import' variable.
""", re.VERBOSE)

DOCTEST_FROM_IMPORT = re.compile(r"""
^            # From start of line
\s+          # Whitespace.
>>>          # Doctestmarker.
\s+          # Whitespace.
from         # 'from' keyword
\s+          # Whitespace
(?P<module>  # Start of 'module' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
\s+          # Whitespace.
import       # 'import' keyword
\s+          # Whitespace.
(?P<sub>     # Start of 'sub' variable.
[            # Any of:
  a-zA-Z     # a-z
  0-9        # numbers
  ,          # comma
  \s         # whitespace
]+           # more than one.
)            # End of 'import' variable.
""", re.VERBOSE)

METADATA_DEPENDENCY_PATTERN = re.compile(r"""
<dependency> #
profile-     # Profile prefix
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
:.*?         # Profile name postfix
</dependency> #
""", re.VERBOSE)


SETUP_PY_PACKAGE_NAME_PATTERN = re.compile(r"""
name\W*=\W*        # 'name =  ' with possible whitespace
["']([\w.]*)["']   # A string containing the name
""", re.VERBOSE)


def normalize(package_name):
    """Return normalized package name.

    Dashes to underscores (to help Django apps). And all-lowercase.
    """
    package_name = package_name.lower()
    package_name = package_name.replace('-', '_')
    return package_name


def print_unused_imports(unused_imports):
    found = []
    for path in sorted(unused_imports.keys()):
        for (module, line_number) in unused_imports[path]:
            found.append((path, line_number, module))
    if found:
        print "Unused imports"
        print "=============="
        for (path, line_number, module) in found:
            print "%s:%s:  %s" % (path, line_number, module)
        print


def name_from_setup():
    cmd = "%s setup.py --name" % sys.executable
    name = commands.getoutput(cmd).strip()

    if 'traceback' in name.lower():
        # Try to get the package name from setup.py
        setup = open('setup.py').read()
        match = SETUP_PY_PACKAGE_NAME_PATTERN.search(setup)
        if match:
            return match.groups()[0]

        print "You probably don't have setuptools installed globally"
        print "Or there's an error in your setup.py."
        print "Try running this by hand:"
        print cmd
        # Use buildout's setuptools_loc environ hack.
        sys.exit(1)

    if '\n' in name:
        logger.debug(
            "setuptools printed a warning together with the package name: %s",
            name)
        name = name.split('\n')[-1].strip()
        logger.info(
            "Extracted '%s' as package name. Run with '-v' if incorrect.",
            name)
    return name


def existing_requirements(name):
    """Extract install and test requirements"""
    underscored_name = name.replace('-', '_')
    egginfo_dir_name = name + '.egg-info'
    egginfo_underscored_dir_name = underscored_name + '.egg-info'
    # Who on earth made it so earth-shattering impossible to get your hands on
    # the egg info stuff via an api?  We'll do it mostly by hand...
    if egginfo_dir_name in os.listdir(os.getcwd()):
        egginfo_dir = egginfo_dir_name
    elif egginfo_underscored_dir_name in os.listdir(os.getcwd()):
        # Django apps often have a name like 'django-something' and a package
        # like 'django_something' as django doesn't like namespace packages in
        # all places.  So we need to check for dashes that became underscores.
        egginfo_dir = egginfo_underscored_dir_name
        name = underscored_name
    else:
        egginfo_dir = os.path.join(os.getcwd(), 'src', egginfo_dir_name)
    requires_filename = os.path.join(egginfo_dir, 'requires.txt')
    if not os.path.exists(requires_filename):
        print "No %s found, exiting" % requires_filename
        sys.exit(1)
    lines = [line.strip() for line in open(requires_filename).readlines()]
    lines = [line for line in lines if line]
    install_required = []
    test_required = []

    current_section = install_required
    for line in lines:
        if line in ('[test]', '[tests]'):
            current_section = test_required
            continue

        elif line.startswith('['):
            current_section = install_required
            continue

        req = pkg_resources.Requirement.parse(line)
        current_section.append(req.project_name)

    # The project itself is of course both available and needed.
    install_required.append(name)
    logger.debug("Appended ourselves (%s) to the required packages.", name)

    # Distribute says it is setuptools.  Setuptools also includes
    # pkg_resources.
    if 'distribute' in install_required:
        install_required.append('setuptools')
    if 'setuptools' in install_required:
        install_required.append('pkg_resources')

    return (install_required, test_required)


def normalize_all(packages):
    return [normalize(package) for package in packages if package]


def filter_missing(imports, required):
    # For imports we want to keep the exact name, required can be normalized.
    required = normalize_all(required)
    missing = []
    for needed in imports:
        found = False
        normalized_needed = normalize(needed)
        for req in required:
            if req == normalized_needed:
                found = True
                break
            if normalized_needed.startswith(req + '.'):
                # 're' should not match 'reinout.something', that's why we
                # check with an extra dot.
                found = True
                break
        if not found:
            missing.append(needed)
    missing = sorted(set(missing))
    return missing


def filter_unneeded(imports, required, name=None):
    if name is not None:
        imports.append(name)  # We always use ourselves, obviously.
    # For required we want to keep the exact name, imports can be normalized.
    imports = normalize_all(imports)
    imports = set(imports)
    required = set(required)
    setuptools_and_friends = set(
        ['distribute', 'setuptools', 'pkg_resources'])
    required = required - setuptools_and_friends

    unneeded = []
    for req in required:
        found = False
        normalized_req = normalize(req)
        for module in imports:
            if module.startswith(normalized_req):
                found = True
                break
        if not found:
            unneeded.append(req)
    unneeded = sorted(set(unneeded))
    return unneeded


def _detect_modules(sample_module):
    sample_file = os.path.realpath(sample_module.__file__)
    modules = []
    if '__init__.py' in sample_file:
        # Directory inside python dir, for instance logging/__init__.py
        parent_dir = os.path.join(os.path.dirname(sample_file), '..')
        for filename in os.listdir(parent_dir):
            if '.' in filename:
                continue  # . and .. dirs... :-)
            possible_dir = os.path.abspath(os.path.join(parent_dir, filename))
            if os.path.isdir(possible_dir):
                modules.append(filename)
        return modules

    stdlib_dir = os.path.dirname(sample_file)
    # Linux now can have 'datetime.x86_64-linux-gnu.so', so the regular
    # os.path.splitext won't work.
    parts = os.path.basename(sample_file).split('.')
    stdlib_extension = '.'.join(parts[1:])
    stdlib_files = os.listdir(stdlib_dir)
    modules = []
    for stdlib_file in stdlib_files:
        if '.' not in stdlib_file:
            continue
        parts = stdlib_file.split('.')
        module = parts[0]
        extension = '.'.join(parts[1:])
        if extension == stdlib_extension:
            if module.endswith('module'):
                # See http://stackoverflow.com/q/6319379/27401
                module = module[:-len('module')]
            modules.append(module)
    return modules


def stdlib_modules():
    py_module = os
    import datetime
    dynload_module = datetime
    import urllib
    import logging
    module_with_init_in_subdir = logging
    modules = _detect_modules(py_module) + \
        _detect_modules(dynload_module) + \
        _detect_modules(urllib) + \
        _detect_modules(module_with_init_in_subdir)
    modules.append('sys')
    modules.append('itertools')
    modules.append('time')
    modules.append('math')

    # C level modules extracted from Python's ``config.c``.
    modules.append('thread')
    modules.append('signal')
    modules.append('posix')
    modules.append('errno')
    modules.append('pwd')
    modules.append('zipimport')

    return list(set(modules))


def includes_from_zcml(path):
    modules = []
    test_modules = []
    for path, dirs, files in os.walk(path):
        for zcml in [os.path.abspath(os.path.join(path, filename))
                     for filename in files
                     if fnmatch.fnmatch(filename, '*.zcml')]:
            contents = open(zcml).read()
            found = [module for module in
                     re.findall(ZCML_PACKAGE_PATTERN, contents)
                     if not module.startswith('.')]
            found += [module for module in
                      re.findall(ZCML_COMPONENT_PATTERN, contents)
                      if not module.startswith('.')]
            found += [module for module in
                      re.findall(ZCML_PROVIDES_PATTERN, contents)
                      if not module.startswith('.')]
            found += [module for module in
                      re.findall(ZCML_CLASS_PATTERN, contents)
                      if not module.startswith('.')]
            found += [module for module in
                      re.findall(ZCML_FOR_PATTERN, contents)
                      if not module.startswith('.') and module.find('*') == -1]
            found += [module for module in
                      re.findall(ZCML_HANDLER_PATTERN, contents)
                      if not module.startswith('.')]
            if 'test' in zcml:
                # ftesting.zcml, mostly.
                test_modules += found
            else:
                modules += found
    return modules, test_modules


def includes_from_plone_fti(path):
    modules = []
    test_modules = []
    for path, dirs, files in os.walk(path):
        for fti in [os.path.abspath(os.path.join(path, filename))
                    for filename in files
                    if fnmatch.fnmatch(filename, '*.xml')]:
            contents = open(fti).read()
            # check that we are on a Dexterity FTI and
            # not any other random XML file
            if contents.find('meta_type="Dexterity FTI"') == -1:
                continue

            found = [module for module in
                     re.findall(FTI_BEHAVIOR_PATTERN, contents)
                     if module.find('.') != -1]
            found += [module for module in
                      re.findall(FTI_SCHEMA_PATTERN, contents)]
            found += [module for module in
                      re.findall(FTI_KLASS_PATTERN, contents)]
            if 'tests' in fti:
                test_modules += found
            else:
                modules += found
    return modules, test_modules


def includes_from_generic_setup_metadata(path):
    modules = []
    test_modules = []
    for path, dirs, files in os.walk(path):
        for xmlfile in [os.path.abspath(os.path.join(path, filename))
                        for filename in files
                        if fnmatch.fnmatch(filename, 'metadata.xml')]:
            contents = open(xmlfile).read()
            found = [module for module in
                     re.findall(METADATA_DEPENDENCY_PATTERN, contents)
                     if not module.startswith('.')]
            found += [module for module in
                      re.findall(METADATA_DEPENDENCY_PATTERN, contents)
                      if not module.startswith('.')]
            if 'test' in xmlfile:
                test_modules += found
            else:
                modules += found
    return modules, test_modules


def includes_from_django_settings(path):
    modules = []
    test_modules = []
    for path, dirs, files in os.walk(path):
        for settingsfile in [os.path.abspath(os.path.join(path, filename))
                             for filename in files
                             if fnmatch.fnmatch(filename, '*settings.py')]:
            found = []
            parsed = ast.parse(open(settingsfile).read())
            # We're looking for assignments like ``INSTALLED_APPS = ``.
            assignments = [obj for obj in parsed.body
                           if isinstance(obj, _ast.Assign)]
            # We're looking for assignments with lists/tuples like
            # ``INSTALLED_APPS = [a, b, c]``.
            lists_or_tuples = [assignment.value for assignment in assignments
                               if isinstance(assignment.value, _ast.List)
                               or isinstance(assignment.value, _ast.Tuple)]
            for list_or_tuple in lists_or_tuples:
                strings = [getattr(element, 's', None)
                           for element in list_or_tuple.elts]
                if None in strings:
                    # A tuple of languages or so: that has no 's' attribute.
                    continue
                suspect_strings = [s for s in strings
                                   if not re.match(PACKAGE_NAME_PATTERN, s)]
                if suspect_strings:
                    # Something doesn't look like a package name.
                    continue
                found += strings

            # Next look for items like:
            # "TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'"
            assigned_strings = [assignment.value for assignment in assignments
                                if isinstance(assignment.value, _ast.Str)]
            for assigned_string in assigned_strings:
                if re.match(DOTTED_PATH_PATTERN, assigned_string.s):
                    found.append(assigned_string.s)

            logger.debug(
                "Found possible packages in Django-like settings file %s:",
                settingsfile)
            logger.debug(found)
            if 'test' in settingsfile:
                # testsettings.py, for instance.
                test_modules += found
            else:
                modules += found
    return modules, test_modules


def imports_from_doctests(path):
    test_modules = []
    for path, dirs, files in os.walk(path):
        for filename in [os.path.abspath(os.path.join(path, filename))
                         for filename in files
                         if fnmatch.fnmatch(filename, '*.txt')
                         or fnmatch.fnmatch(filename, '*.rst')
                         or fnmatch.fnmatch(filename, '*.py')]:
            lines = open(filename).readlines()
            for line in lines:
                test_modules += re.findall(DOCTEST_IMPORT, line)
                for (module, sub) in re.findall(DOCTEST_FROM_IMPORT, line):
                    submodules = [item.strip() for item in sub.split(',')]
                    for submodule in submodules:
                        test_modules.append('.'.join([module, submodule]))
    return sorted(set(test_modules))


def print_modules(modules, heading):
    if modules:
        print heading
        print '=' * len(heading)
        for module in modules:
            print "    ", module
        print


def determine_path(args, name=None):
    if len(args) > 0:
        path = args[0]
        if not os.path.isdir(path):
            logger.error("You passed %s as a path, but that is no directory!",
                         path)
            sys.exit(1)
        logger.debug("Looking in directory %s, passed on the commmand line",
                     path)
        return path

    logger.debug("The detected package name (from setup.py) is %s", name)
    path = name
    if '-' in path:
        path = path.replace('-', '_')
        logger.debug("Replaced dashes with underscores: %s", path)

    if '.' in path:
        path = os.path.join(*path.split('.'))
        logger.debug("Treating periods as directories: %s", path)

    if os.path.isdir(path):
        logger.debug("Found base directory at %s", path)
        return path

    logger.debug("Directory %s does not exist, trying with src/ prefix",
                 path)
    path = os.path.join('src', path)
    if os.path.isdir(path):
        logger.debug("Found base directory at %s", path)
        return path

    logger.error(
        "Couldn't find the base directory with your code. Either pass "
        "a path as the first argument or re-run with the '-v' option "
        "to get more debug information")
    sys.exit(1)


def _version():
    ourselves = pkg_resources.require('z3c.dependencychecker')[0]
    return ourselves.version


def main():
    usage = ("Usage: %prog [path]\n" +
             "(path defaults to package name, fallback is 'src/')")
    parser = optparse.OptionParser(usage=usage, version=_version())
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Show debug output")
    (options, args) = parser.parse_args()
    if options.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel,
                        stream=sys.stdout,
                        format="%(levelname)s: %(message)s")

    name = name_from_setup()
    path = determine_path(args, name=name)
    db = importchecker.ImportDatabase(path)
    db.findModules()
    unused_imports = db.getUnusedImports()
    test_imports = db.getImportedPkgNames(tests=True)
    install_imports = db.getImportedPkgNames(tests=False)
    logger.debug("All found regular imported packages: %s",
                 sorted(install_imports))
    logger.debug("All found regular imported test packages: %s",
                 sorted(test_imports))
    (install_required, test_required) = existing_requirements(name=name)
    stdlib = stdlib_modules()

    (zcml_imports, zcml_test_imports) = includes_from_zcml(path)
    zcml_imports = db.resolvePkgNames(zcml_imports)
    zcml_test_imports = db.resolvePkgNames(zcml_test_imports)
    logger.debug("All found zcml-related packages: %s",
                 sorted(zcml_imports))
    logger.debug("All found zcml-related test packages: %s",
                 sorted(zcml_test_imports))

    (fti_imports, fti_test_imports) = includes_from_plone_fti(path)
    fti_imports = db.resolvePkgNames(fti_imports)
    fti_test_imports = db.resolvePkgNames(fti_test_imports)
    logger.debug("All found FTI-related packages: %s",
                 sorted(fti_imports))
    logger.debug("All found FTI-related test packages: %s",
                 sorted(fti_test_imports))

    (django_settings_imports,
     django_settings_test_imports) = includes_from_django_settings(path)
    django_settings_imports = db.resolvePkgNames(django_settings_imports)
    django_settings_test_imports = db.resolvePkgNames(
        django_settings_test_imports)
    logger.debug("All found django_settings-related packages: %s",
                 sorted(django_settings_imports))
    logger.debug("All found django_settings-related test packages: %s",
                 sorted(django_settings_test_imports))

    doctest_imports = imports_from_doctests(path)

    (generic_setup_required,
     generic_setup_test_required) = includes_from_generic_setup_metadata(path)
    generic_setup_required = db.resolvePkgNames(generic_setup_required)
    generic_setup_test_required = db.resolvePkgNames(
        generic_setup_test_required)
    logger.debug("All found generic_setup-related packages: %s",
                 sorted(generic_setup_required))
    logger.debug("All found generic_setup-related test packages: %s",
                 sorted(generic_setup_test_required))

    print_unused_imports(unused_imports)

    all_install_imports = (
        install_imports +
        zcml_imports +
        generic_setup_required +
        django_settings_imports +
        fti_imports)
    install_missing = filter_missing(
        all_install_imports,
        install_required + stdlib)
    print_modules(install_missing, "Missing requirements")

    all_test_imports = (
        test_imports +
        zcml_test_imports +
        doctest_imports +
        generic_setup_test_required +
        django_settings_test_imports +
        fti_test_imports)
    test_missing = filter_missing(
        all_test_imports,
        install_required + test_required + stdlib)
    print_modules(test_missing, "Missing test requirements")

    install_unneeded = filter_unneeded(
        all_install_imports,
        install_required,
        name=name)
    # See if one of ours is needed by the tests
    really_unneeded = filter_unneeded(
        all_test_imports,
        install_unneeded,
        name=name)
    move_to_test = sorted(set(install_unneeded) - set(really_unneeded))

    print_modules(really_unneeded, "Unneeded requirements")
    print_modules(move_to_test,
                  "Requirements that should be test requirements")

    test_unneeded = filter_unneeded(
        all_test_imports,
        test_required,
        name=name)
    print_modules(test_unneeded, "Unneeded test requirements")

    if install_missing or test_missing or install_unneeded or test_unneeded:
        print "Note: requirements are taken from the egginfo dir, so you need"
        print "to re-run buildout (or setup.py or whatever) for changes in"
        print "setup.py to have effect."
        print

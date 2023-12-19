Changelog of z3c.dependencychecker
==================================

2.13 (2023-12-19)
-----------------

- Drop python 3.7 support, as our dependencies require 3.8 at least.
  [gforcada]

- Add python 3.12 support.
  [gforcada]

2.12 (2023-08-02)
-----------------

- Fix, hopefully finally, the Zope user mapping use case.
  [gforcada]

- Add `Plone` as an umbrella distribution, alongside `Zope`.
  [gforcada]

- Scan the `<implements` directive on `ZCML` files.
  [gforcada]

- Handle new distributions that no longer have a `setup.py`.
  Consider `pyproject.toml` and `setup.cfg` alongside `setup.py`.
  [gforcada]

2.11 (2023-03-03)
-----------------

- Ignore `node_modules` and `__pycache__` folders
  when scanning for files with dependencies.
  [gforcada]

- Do not scan Plone FTI files for behaviors with dotted names.
  [gforcada]

2.10 (2023-01-30)
-----------------

- Do not ignore `Zope` user mappings, fixes previous release.
  [gforcada]

2.9 (2023-01-23)
----------------

- Ignore `Zope` package, as otherwise it swallows all `zope.` namespace packages.
  [gforcada]

2.8 (2022-11-30)
----------------

- Drop python 2.7 support.
  [gforcada]

- Replace travis for GitHub actions.
  [gforcada]

- Test against python 3.7-3.11 and pypy3.
  [gforcada]

- Updated developer documentation.
  [reinout]


2.7 (2018-08-08)
----------------

- Fixed the 'requirement should be test requirement' report. There were corner
  cases when using user mappings.
  [gforcada]


2.6 (2018-07-09)
----------------

- Use the user mappings on the remaining reports:

  - unneeded dependencies
  - unneeded test dependencies
  - dependencies that should be test dependencies

  [gforcada]

- Always consider imports in python docstrings to be test dependencies.
  [gforcada]

2.5.1 (2018-07-06)
------------------

- Re-release 2.5 as it was a brown bag release.
  [gforcada]

2.5 (2018-07-06)
----------------

- Check in every top level folder if the .egg-info folder is in them.
  [gforcada]

2.4.4 (2018-07-04)
------------------

Note: this includes the 2.4.1 - 2.4.4 releases, we had to iterate a bit to get
the formatting right :-)

- Fix rendering of long description in pypi.
  [gforcada, reinout]

- Documentation formatting fixes.
  [reinout]


2.4 (2018-06-30)
----------------

- Handle packages that have multiple top levels, i.e. packages like Zope2.
  [gforcada]

2.3 (2018-06-21)
----------------

- Add a new command line option ``--exit-zero``.
  It forces the program to always exit with a zero status code.
  Otherwise it will report ``1`` if the program does find anything to report.
  [gforcada]

- Fix ZCML parser to discard empty strings.
  [gforcada]

2.2 (2018-06-19)
----------------

- Ignore relative imports (i.e. from . import foo).
  [gforcada]

- Added ``ignore-packages`` config option to totally ignore one or more packages in the reports
  (whether unused imports or unneeded dependencies).
  Handy for soft dependencies.
  [gforcada]

2.1.1 (2018-03-10)
------------------

- Note: 2.1 had a technical release problem, hence 2.1.1.
  [reinout]

- We're releasing it as a wheel, too, now.
  [reinout]

- Small improvements to the debug logging (``-v/--verbose`` shows it).
  [reinout]

- Remove unused parameter in DottedName.
  [gforcada]

- All imports found by DocFiles imports extractor are marked as test ones.
  [gforcada]

- Handle multiple dotted names found in a single ZCML parameter.
  [gforcada]

- Use properties to make code more pythonic.
  [gforcada]

- Allow users to define their own mappings on a `pyproject.toml` file.
  See README.rst.

- Filter imports when adding them to the database, rather than on each report.
  [gforcada]


2.0 (2018-01-04)
----------------

- Complete rewrite: code does no longer use deprecated functionality,
  is more modular, more pythonic, easier to extend and hack, and above all,
  has a 100% test coverage to ensure that it works as expected.
  [gforcada]

- Add support for Python 3.
  [gforcada]


1.16 (2017-06-21)
-----------------

- Don't crash anymore on, for instance, django code that needs a django
  settings file to be available or that needs the django app config step to be
  finished.
  [reinout]

- Improved Django settings extraction.
  [reinout]

- Better detection of python built-in modules. ``logging/__init__.py`` style
  modules were previously missed.
  [reinout]


1.15 (2015-09-02)
-----------------

- The name of a wrong package was sometimes found in case of a directory with
  multiple egg-info directories (like
  ``/usr/lib/python2.7/dist-packages/*.egg-info/``...). Now the
  ``top_level.txt`` file in the egg-info directories is checked if the
  top-level directory matches.
  [reinout]


1.14 (2015-09-01)
-----------------

- The debug logging (``-v``) is now printed to stdout instead of stderr. This
  makes it easier to grep or search in the verbose output for debugging
  purposes.
  [reinout]


1.13 (2015-08-29)
-----------------

- Import + semicolon + statement (like ``import
  transaction;transaction.commit()``) is now also detected correctly.
  [gforcada]

- The starting directory for packages with a dotted name (like
  ``zest.releaser``) is now also found automatically.
  [reinout]

- Internal code change: moved the code out of the ``src/``
  directory. Everything moved one level up.
  [reinout]

- Dependencychecker doesn't descend anymore into directories without an
  ``__init__.py``. This helps with website projects that sometimes have python
  files buried deep in directories that aren't actually part of the project's
  python code.
  [reinout]

- Multiple imports from similarly-named libraries on separate lines are now
  handled correctly. An import of ``zope.interface`` on one line could
  sometimes "hide" a ``zope.component`` import one line down.
  [gforcada]


1.12 (2015-08-16)
-----------------

- Improve ZCML imports coverage (look on ``for`` and ``class`` as well).
  [gforcada]

- Internal project updates (buildout version, test adjustments, etc).
  [gforcada]

- Add support for FTI dependencies (behaviors, schema and class).
  [gforcada]


1.11 (2013-04-16)
-----------------

- Support python installations without global setuptools installed
  by searching the name in the setup.py as fallback.


1.10 (2013-02-24)
-----------------

- Treat non-test extras_require like normal install_requires.


1.9 (2013-02-13)
----------------

- Improved detection for "Django-style" package names with a dash in
  them. Django doesn't deal well with namespace packages, so instead of
  ``zc.something``, you'll see packages like ``zc-something``. The import then
  uses an underscore, ``zc_something``.

- Added support for Django settings files. Anything that matches
  ``*settings.py`` is searched for Django settings like ``INSTALLED_APPS =
  [...]`` or ``MIDDLEWARE_CLASSES = (...)``.


1.8 (2013-02-13)
----------------

- Detect ZCML "provides", as used for generic setup profile registration.


1.7.1 (2012-11-26)
------------------

- Added travis.ci configuration. We're tested there, too, now!


1.7 (2012-11-26)
----------------

- Lookup package name for ZCML modules too, as it is done for python modules.

- Detect generic setup dependencies in ``metadata.xml`` files.


1.6 (2012-11-01)
----------------

- Fix AttributeError when "magic modules" like email.Header are imported.


1.5 (2012-07-03)
----------------

- Add support for zipped dists when looking up pkg name.


1.4 (2012-07-03)
----------------

- Lookup pkg name from egg-infos if possible (python >= 2.5). This helps for
  instance with the PIL problem (which can be ``Imaging`` instead when you
  import it).


1.3.2 (2012-06-29)
------------------

- Fixed broken 1.3.0 and 1.3.0 release: the ``MANIFEST.in`` was missing...


1.3.1 (2012-06-29)
------------------

- Documentation updates because we moved to github:
  https://github.com/reinout/z3c.dependencychecker .


1.3 (2012-06-29)
----------------

- Added fix for standard library detection on OSX when using the python
  buildout. (Patch by Jonas Baumann, as is the next item).

- Supporting ``[tests]`` in addition to ``[test]`` for test requirements.


1.2 (2011-09-19)
----------------

- Looking for a package directory named after the package name in preference
  to the src/ directory.

- Compensating for django-style 'django-something' package names with
  'django_something' package directories.  Dash versus underscore.


1.1 (2010-01-06)
----------------

- Zcml files are also searched for 'component=' patterns as that can be used
  by securitypolicy declarations.

- Dependencychecker is now case insensitive as pypi is too.

- Using optparse for parsing commandline now.  Added --help and --version.


1.0 (2009-12-10)
----------------

- Documentation update.

- Improved test coverage. The dependencychecker module self is at 100%, the
  original import checker module is at 91% coverage.


0.5 (2009-12-10)
----------------

- Searching in doctests (.py, .txt, .rst) for imports, too.  Regex-based by
  necessity, but it seems to catch what I can test it with.


0.4 (2009-12-10)
----------------

- Supporting "from zope import interface"-style imports where you really want
  to be told you're missing an "zope.interface" dependency instead of just
  "zope" (which is just a namespace package).


0.3 (2009-12-08)
----------------

- Sorted "unneeded requirements" reports and filtered out duplicates.

- Reporting separately on dependencies that should be moved from the regular
  to the test dependencies.


0.2 (2009-12-08)
----------------

- Added tests.  Initial quick test puts coverage at 86%.

- Fixed bug in test requirement detection.

- Added documentation.

- Moved source code to zope's svn repository.


0.1 (2009-12-02)
----------------

- Also reporting on unneeded imports.

- Added note on re-running buildout after a setup.py change.

- Added zcml lookup to detect even more missing imports.

- Added reporting on missing regular and test imports.

- Grabbing existing requirements from egginfo directory.

- Copied over Martijn Faassen's zope importchecker script.

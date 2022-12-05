z3c.dependencychecker
=====================

Checks which imports are done and compares them to what's in ``setup.py`` and
warn when discovering missing or unneeded dependencies.

.. image:: https://github.com/reinout/z3c.dependencychecker/actions/workflows/testing.yml/badge.svg?branch=master
   :target: https://github.com/reinout/z3c.dependencychecker/actions/workflows/testing.yml

.. image:: https://coveralls.io/repos/github/reinout/z3c.dependencychecker/badge.svg?branch=master
   :target: https://coveralls.io/github/reinout/z3c.dependencychecker?branch=master

.. contents::


What it does
------------

z3c.dependencychecker reports on:

- **Missing (test) requirements**: imports without a corresponding requirement
  in the ``setup.py``.  There might be false alarms, but at least you've got a
  (hopefully short) list of items to check.

  Watch out for packages that have a different name than how they're imported.
  For instance a requirement on ``pydns`` which is used as ``import DNS`` in
  your code: pydns and DNS lead to separate "missing requirements: DNS" and
  "unneeded requirements: pydns" warnings.

- **Unneeded (test) requirements**: requirements in your setup.py that aren't
  imported anywhere in your code.  You *might* need them because not
  everything needs to be imported.  It at least gives you a much smaller list
  to check by hand.

- **Requirements that should be test-only**: if something is only imported in
  a test file, it shouldn't be in the generic defaults.  So you get a separate
  list of requirements that should be moved from the regular to the test
  requirements.

It checks the following locations:

- Python files for regular imports and their docstrings.

- ZCML files, Plone's generic setup files as well as FTI XML files.

- Python files, ``.txt`` and ``.rst`` files for imports in doctests.

- django settings files.

User mappings
-------------

Some packages available on pypi have a different name than the import
statement needed to use them, i.e. `python-dateutil` is imported as `import
dateutil`.  Others provide more than one package, i.e `Zope2` provides several
packages like `Products.Five` or `Products.OFSP`.

For those cases, z3c.dependencychecker has a solution: user mappings.

Add a `pyproject.toml` file on the root of your project with the following
content::

    [tool.dependencychecker]
    python-dateutil = ['dateutil']
    Zope2 = ['Products.Five', 'Products.OFSP' ]

z3c.dependencychecker will read this information and use it on its reports.

Ignore packages
---------------

Sometimes you need to add a package in `setup.py` although you are not
importing it directly, but maybe is an extra dependency of one of your
dependencies, or your package has a soft dependency on a package, and as a
soft dependency it is not mandatory to install it always.

`z3c.dependencychecker` would complain in both cases. It would report that a
dependency is not needed, or that a missing package is not listed on the
package requirements.

Fortunately, `z3c.dependencychecker` also has a solution for it.

Add a `pyproject.toml` file on the root of your project with the following
content::

    [tool.dependencychecker]
    ignore-packages = ['one-package', 'another.package' ]

`z3c.dependencychecker` will totally ignore those packages in its reports,
whether they're requirements that appear to be unused, or requirements that
appear to be missing.

Credits
-------

z3c.dependencychecker is a different application/packaging of zope's
importchecker utility.  It has been used in quite some projects, I grabbed a
copy from `lovely.recipe's checkout
<http://bazaar.launchpad.net/~vcs-imports/lovely.recipe/trunk/annotate/head%3A/src/lovely/recipe/importchecker/importchecker.py>`_.

- Martijn Faassen wrote the original importchecker script.

- `Reinout van Rees <http://reinout.vanrees.org>`_ added the dependency
  checker functionality and packaged it (mostly while working at `The Health
  Agency <http://www.thehealthagency.com>`_).

- Quite some fixes from `Jonas Baumann <https://github.com/jone>`_.

- Many updates (basically: rewriting the entire codebase to work with AST!) to
  work well with modern Plone versions by `Gil Forcada Codinachs
  <http://gil.badall.net/>`.


Source code, forking and reporting bugs
---------------------------------------

The source code can be found on github:
https://github.com/reinout/z3c.dependencychecker

You can fork and fix it from there. And you can add issues and feature
requests in the github issue tracker.

Every time you commit something, ``bin/code-analysis`` is automatically
run. Pay attention to the output and fix the problems that are reported. Or
fix the setup so that inappropriate reports are filtered out.


Local development setup
-----------------------

Create a virtualenv and install the requirements::

  $ python3 -m venv .
  $ bin/pip install -r requirements.txt

If you changed the actual requirements in ``setup.py`` or the development
requirements in ``requirements.in``, re-generate ``requirements.txt``::

  $ bin/pip-compile requirements.in

To run the tests (there's some pytest configuration in ``setup.cfg``)::

  $ bin/pytest

Some checks that are run by github actions::

  $ bin/black
  $ bin/codespell setup.py z3c/
  $ bin/flake8 setup.py z3c/

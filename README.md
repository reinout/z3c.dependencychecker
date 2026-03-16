# z3c.dependencychecker

Checks which imports are used within a python distribution
and compares them to what's declared on the distribution configuration
(either in `setup.py`, `pyproject.toml`, etc.)
and warn when discovering missing or unneeded dependencies.

[![Tests](https://github.com/reinout/z3c.dependencychecker/actions/workflows/testing.yml/badge.svg?branch=master)](https://github.com/reinout/z3c.dependencychecker/actions/workflows/testing.yml)
[![Coverage](https://coveralls.io/repos/github/reinout/z3c.dependencychecker/badge.svg?branch=master)](https://coveralls.io/github/reinout/z3c.dependencychecker?branch=master)

## What it does

`z3c.dependencychecker` reports on:

- **Missing (test) requirements**: imports without a declared requirement.
  If there are false positives, look at [user mappings](#user-mappings).

- **Unneeded (test) requirements**: declared requirements that aren't
  imported anywhere in your code. You *might* need them because not everything
  needs to be imported. If that's the case, look at [ignore packages](#ignore-packages).

- **Requirements that should be test-only**: if something is only imported in a
  test file, it shouldn't be in the generic defaults. So you get a separate
  list of requirements that should be moved from the regular to the test
  requirements.

It checks the following locations:

- Python files for regular imports and their docstrings.
- ZCML files, Plone's generic setup files as well as FTI XML files.
- Python files, `.txt` and `.rst` files for imports in doctests.
- Django settings files.

## User mappings

Some packages available on PyPI have a different name than the import
statement needed to use them, for example `python-dateutil` is imported as
`import dateutil`. Others provide more than one package, for example `Zope`
provides several packages like `Products.Five` or `Products.OFSP`.

For those cases, `z3c.dependencychecker` has a solution: **user mappings**.

Add a `pyproject.toml` file on the root of your project with the following
content:

```toml
[tool.dependencychecker]
python-dateutil = ["dateutil"]
Zope = ["Products.Five", "Products.OFSP"]
```

`z3c.dependencychecker` will read this information and use it on its reports.

## Ignore packages

Sometimes you declare a dependency although you are not
importing it directly, but maybe is an extra dependency of one of your
dependencies, or your package has a soft dependency on a package, and as a
soft dependency it is not mandatory to install it always.

`z3c.dependencychecker` would complain in both cases. It would report that a
dependency is not needed, or that a missing package is not listed on the
package requirements.

Fortunately, `z3c.dependencychecker` also has a solution for it.

Add a `pyproject.toml` file on the root of your project with the following
content:

```toml
[tool.dependencychecker]
ignore-packages = ["one-package", "another.package"]
```

`z3c.dependencychecker` will ignore those packages in its reports,
whether they're requirements that appear to be unused, or requirements that
appear to be missing.

## Credits

`z3c.dependencychecker` is a different application/packaging of zope's
importchecker utility. It has been used in quite some projects, I grabbed a
copy from [lovely.recipe's checkout](http://bazaar.launchpad.net/~vcs-imports/lovely.recipe/trunk/annotate/head%3A/src/lovely/recipe/importchecker/importchecker.py).

- Martijn Faassen wrote the original importchecker script.
- [Reinout van Rees](http://reinout.vanrees.org) added the dependency checker
  functionality and packaged it, mostly while working at
  [The Health Agency](http://www.thehealthagency.com).
- Quite some fixes from [Jonas Baumann](https://github.com/jone).
- Many updates, basically rewriting the entire codebase to work with AST, to
  work well with modern Plone versions by
  [Gil Forcada Codinachs](https://github.com/gforcada).

## Source code, forking and reporting bugs

The source code can be found on GitHub:
<https://github.com/reinout/z3c.dependencychecker>

You can fork and fix it from there. And you can add issues and feature
requests in the GitHub issue tracker.

There are some CI jobs that check for tests and code quality.

## Local development setup

Create a virtualenv and install the requirements:

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

If you changed the actual requirements in `setup.py` or the development
requirements in `requirements.in`, re-generate `requirements.txt`:

```bash
pip-compile requirements.in
```

To run the tests we use the setup of `plone.meta`. So stuff like:

```bash
tox -e test
tox -e format
pre-commit run --all
```

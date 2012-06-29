z3c.dependencychecker
=====================

Checks which imports are done and compares them to what's in ``setup.py`` and
warn when discovering missing or unneeded dependencies.

.. contents::


What it does
------------

z3c.dependencychecker reports on:

- **Unused imports**: pyflakes is another tool that does this (and that also
  reports on missing variables inside the files).

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

- Python files for regular imports.

- Zcml files for ``package="some.thing"`` attributes.

- Python files, ``.txt`` and ``.rst`` files for imports in doctests.


Credits
-------

z3c.dependencychecker is a different application/packaging of zope's
importchecker utility.  It has been used in quite some projects, I grabbed a
copy from `lovely.recipe's checkout
<http://bazaar.launchpad.net/~vcs-imports/lovely.recipe/trunk/annotate/head%3A/src/lovely/recipe/importchecker/importchecker.py>`_.

- Martijn Faassen wrote the original importchecker script.

- `Reinout van Rees <http://reinout.vanrees.org>`_ (`The Health Agency
  <http://www.thehealthagency.com>`_) added the dependency checker
  functionality and packaged it.


Source code
-----------

The source code can be found in zope's svn repository:
http://svn.zope.org/repos/main/z3c.dependencychecker

At the moment, bugs and suggestions can be send to `Reinout
<mailto:reinout@vanrees.org>`_.

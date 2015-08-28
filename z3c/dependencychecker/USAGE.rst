Usage of z3c.dependencychecker
==============================

.. :doctest:


Installation
------------

Either install z3c.dependencychecker globally (``easy_install
z3c.dependencychecker``) or install it in your buildout.


Usage
-----

Run the ``dependencychecker`` or ``bin/dependencychecker`` script from your
project's root folder and it will report on your dependencies.

By default, it looks in the ``src/`` directory for your sources.
Alternatively, you can specify a start directory yourself, for instance
``'.'`` if there's no ``src/`` directory.

We have a sample project in a temp directory:

    >>> sample1_dir
    '/TESTTEMP/sample1'
    >>> ls(sample1_dir)
    setup.py
    src

For our test, we call the main() method, just like the ``dependencychecker``
script would:

    >>> import os
    >>> os.chdir(sample1_dir)
    >>> from z3c.dependencychecker import dependencychecker
    >>> dependencychecker.main()
    Unused imports
    ==============
    src/sample1/unusedimports.py:7:  tempfile
    src/sample1/unusedimports.py:4:  zest.releaser
    src/sample1/unusedimports.py:6:  os
    <BLANKLINE>
    Missing requirements
    ====================
         Products.GenericSetup.interfaces.EXTENSION
         missing.req
         other.generic.setup.dependency
         plone.app.content.interfaces.INameFromTitle
         plone.app.dexterity.behaviors.metadata.IBasic
         plone.random1.interfaces.IMySchema
         plone.random2.content.MyType
         some_django_app
         something.origname
         zope.exceptions
         zope.interface
    <BLANKLINE>
    Missing test requirements
    =========================
         plone.dexterity.browser.views.ContentTypeView
         plone.dexterity.interfaces.IContentType
         reinout.hurray
         transaction
         zope.filerepresentation.interfaces.IRawReadFile"
    <BLANKLINE>
    Unneeded requirements
    =====================
         some.other.extension
         unneeded.req
    <BLANKLINE>
    Requirements that should be test requirements
    =============================================
         Needed.By.Test
    <BLANKLINE>
    Unneeded test requirements
    ==========================
         zope.testing
    <BLANKLINE>
    Note: requirements are taken from the egginfo dir, so you need
    to re-run buildout (or setup.py or whatever) for changes in
    setup.py to have effect.
    <BLANKLINE>

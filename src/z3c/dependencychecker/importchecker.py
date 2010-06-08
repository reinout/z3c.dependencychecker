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
"""Import checker

This utility finds is based on the zope importchecker script, prints
out unused imports, imports that are only for tests packages and
runtime imports.

$Id: importchecker.py 96082 2009-02-04 16:37:38Z adamg $
"""
import compiler
import os
import os.path


def _findDottedNamesHelper(node, result):
    more_node = node
    name = node.__class__.__name__
    if name == 'Getattr':
        dotted = []
        while name == 'Getattr':
            dotted.append(node.attrname)
            node = node.expr
            name = node.__class__.__name__
        if name == 'Name':
            dotted.append(node.name)
            dotted.reverse()
            for i in range(1, len(dotted)):
                result.append('.'.join(dotted[:i]))
            result.append('.'.join(dotted))
            return
    elif name == 'Name':
        result.append(node.name)
        return
    elif name == 'AssAttr':
        return
    for child in more_node.getChildNodes():
        _findDottedNamesHelper(child, result)


def findDottedNames(node):
    """Find dotted names in an AST tree node
    """
    result = []
    _findDottedNamesHelper(node, result)
    return result


class ImportFinder:
    """An instance of this class will be used to walk over a compiler AST
    tree (a module). During that operation, the appropriate methods of
    this visitor will be called
    """

    def __init__(self):
        self._map = {}

    def visitFrom(self, stmt):
        """Will be called for 'from foo import bar' statements
        """
        x = stmt.asList()
        module_name = x[0]
        names = x[1]
        if module_name == '__future__':
            # we don't care what's imported from the future
            return
        names_dict = {}
        for orig_name, as_name in names:
            # we don't care about from import *
            if orig_name == '*':
                continue
            if as_name is None:
                name = orig_name
            else:
                name = as_name
            names_dict[name] = orig_name
        self._map.setdefault(module_name, {'names': names_dict,
                                           'lineno': stmt.lineno,
                                           'fromimport': True})

    def visitImport(self, stmt):
        """Will be called for 'import foo.bar' statements
        """
        for orig_name, as_name in stmt.names:
            if as_name is None:
                name = orig_name
            else:
                name = as_name
            self._map.setdefault(orig_name, {'names': {name: orig_name},
                                             'lineno': stmt.lineno,
                                             'fromimport': False})

    def getMap(self):
        return self._map


def findImports(mod):
    """Find import statements in module and put the result in a mapping.
    """
    visitor = ImportFinder()
    compiler.walk(mod, visitor)
    return visitor.getMap()


class Module:
    """This represents a python module.
    """

    def __init__(self, path):
        mod = compiler.parseFile(path)
        self._path = path
        self._map = findImports(mod)
        self._dottednames = findDottedNames(mod)

    def getPath(self):
        """Return the path to this module's file.
        """
        return self._path

    def getImportedModuleNames(self):
        """Return the names of imported modules.
        """
        result = []
        for modulename in self._map.keys():
            if not self._map[modulename]['fromimport']:
                # Regular import
                result.append(modulename)
            else:
                # from xyz import abc, return xyz.abc to help with detecting
                # "from zope import interface"-style imports where
                # zope.inteface is the real module and zope just a namespace
                # package.  This is for the dependencychecker, btw.
                if len(self._map[modulename]['names'].values()) == 0:
                    # from xyz import *
                    result.append(modulename)
                for submodule in self._map[modulename]['names'].values():
                    result.append('.'.join([modulename, submodule]))
        return result

    def getImportNames(self):
        """Return the names of imports; add dottednames as well.
        """
        result = []
        map = self._map
        for module_name in map.keys():
            for usedname, originalname in map[module_name]['names'].items():
                result.append((originalname, module_name))
                # add any other name that we could be using
                for dottedname in self._dottednames:
                    usednamedot = usedname + '.'
                    if dottedname.startswith(usednamedot):
                        attrname = dottedname[len(usednamedot):].split('.')[0]
                        result.append((attrname, module_name))

        return result

    def getUnusedImports(self):
        """Get unused imports of this module (the whole import info).
        """
        result = []
        for value in self._map.values():
            for usedname, originalname in value['names'].items():
                if usedname not in self._dottednames:
                    result.append((originalname, value['lineno']))
        return result


class ModuleFinder:

    def __init__(self):
        self._files = []

    def visit(self, arg, dirname, names):
        """This method will be called when we walk the filesystem
        tree. It looks for python modules and stored their filenames.
        """
        for name in names:
            # get all .py files that aren't weirdo emacs droppings
            if name.endswith('.py') and not name.startswith('.#'):
                self._files.append(os.path.join(dirname, name))

    def getModuleFilenames(self):
        return self._files


def findModules(path):
    """Find python modules in the given path and return their absolute
    filenames in a sequence.
    """
    finder = ModuleFinder()
    os.path.walk(path, finder.visit, ())
    return finder.getModuleFilenames()


class ImportDatabase:
    """This database keeps tracks of imports.

    It allows to NOT report cases where a module imports something
    just so that another module can import it (import dependencies).
    """

    def __init__(self, root_path):
        self._root_path = root_path
        self._modules = {}
        self._names = {}

    def resolveDottedModuleName(self, dotted_name, module):
        """Return path to file representing module, or None if no such
        thing. Can do this relative from module.
        """
        dotted_path = dotted_name.replace('.', '/')
        # try relative import first
        path = os.path.join(os.path.dirname(module.getPath()), dotted_path)
        path = self._resolveHelper(path)
        if path is not None:
            return path
        # absolute import (assumed to be from this tree)
        if os.path.isfile(os.path.join(self._root_path, '__init__.py')):
            startpath, dummy = os.path.split(self._root_path)
        else:
            startpath = self._root_path
        return self._resolveHelper(os.path.join(startpath, dotted_path))

    def _resolveHelper(self, path):
        if os.path.isfile(path + '.py'):
            return path + '.py'
        if os.path.isdir(path):
            path = os.path.join(path, '__init__.py')
            if os.path.isfile(path):
                return path
        return None

    def findModules(self):
        """Find modules in the given path.
        """
        for modulepath in findModules(self._root_path):
            module = Module(modulepath)
            self.addModule(module)

    def addModule(self, module):
        """Add information about a module to the database. A module in
        this case is not a python module object, but an instance of
        the above defined Module class.w
        """
        self_path = module.getPath()
        # do nothing if we already know about it
        if self_path in self._modules:
            return

        self._modules[self_path] = module

        # add imported names to internal names mapping; this will
        # allow us identify dependent imports later
        names = self._names
        for name, from_module_name in module.getImportNames():
            path = self.resolveDottedModuleName(from_module_name, module)
            t = (path, name)
            modulepaths = names.get(t, {})
            if not self_path in modulepaths:
                modulepaths[self_path] = 1
            names[t] = modulepaths

    def getUnusedImports(self):
        """Get unused imports of all known modules.
        """
        result = {}
        for path, module in self._modules.items():
            result[path] = self.getUnusedImportsInModule(module)
        return result

    def getImportedModuleNames(self, tests=False):
        """returns all  names imported by modules"""
        result = set()
        import os
        for path, module in self._modules.items():
            # remove .py
            parts = path[:-3].split(os.path.sep)
            isTest = 'tests' in parts or 'testing' in parts \
                     or 'ftests' in parts
            if (tests and isTest) or (not tests and not isTest):
                result.update(module.getImportedModuleNames())
        return sorted(result)

    def getUnusedImportsInModule(self, module):
        """Get all unused imports in a module.
        """
        result = []
        for name, lineno in module.getUnusedImports():
            if not self.isNameImportedFrom(name, module):
                result.append((name, lineno))
        return result

    def isNameImportedFrom(self, name, module):
        """Return true if name is imported from module by another module.
        """
        return (module.getPath(), name) in self._names

    def getModulesImportingNameFrom(self, name, module):
        """Return list of known modules that import name from module.
        """
        result = []
        for path in self._names.get((module.getPath(), name), {}).keys():
            result.append(self._modules[path])
        return result

from z3c.dependencychecker.modules import PythonDocstrings
from z3c.dependencychecker.tests.utils import write_source_file_at

NO_DOC = 'class MyClass(object): ...'
INVALID_PYTHON = '''
"""
>>> and some text here that breaks the parser
"""
'''
DOC_IN_MODULE = '''
"""
Random docstring with code to be evaluated.

>>> import zope.component
"""
'''
DOC_IN_FUNCTION = '''
def test():
    """Random docstring with code to be evaluated.

    >>> import zope.component.adapter
    """
'''
DOC_IN_CLASS = '''
class MyClass(object):
    """Random docstring with code to be evaluated.

    >>> from zope.component import utility
    """
'''
DOC_IN_METHOD = '''
class MyClass(object):
    def test(self):
        """Docstring with code to be evaluated.

        >>> import zope.interface
        """
'''
MULTIPLE_IMPORTS_SAME_LINE = '''
class MyClass(object):
    def test(self):
        """Docstring with code to be evaluated.

        >>> from zope.interface import Interface, Attribute
        """
'''
MULTIPLE_IMPORTS_DIFFERENT_LINES = '''
class MyClass(object):
    def test(self):
        """Docstring with code to be evaluated.

        >>> from zope.component import adapter
        >>> from zope.component import utility
        """
'''
MULTIPLE_IMPORTS_DIFFERENT_LINES_WITH_INVALID_CODE_LINES_BETWEEN = '''
class MyClass(object):
    def test(self):
        """Docstring with code to be evaluated.

        >>> from zope.component import adapter
        >>> this should  be skipped and next line processed happily
        >>> from zope.component import utility
        """
'''


def _get_dependencies_on_file(folder, source):
    temporal_file = write_source_file_at(
        (folder.strpath,),
        source_code=source,
    )

    docstring = PythonDocstrings(folder.strpath, temporal_file)
    dotted_names = [x.name for x in docstring.scan()]
    return dotted_names


def test_no_docstring(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, NO_DOC)
    assert len(dotted_names) == 0


def test_invalid_code_ignored(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, INVALID_PYTHON)
    assert len(dotted_names) == 0


def test_docstring_in_module(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, DOC_IN_MODULE)
    assert len(dotted_names) == 1


def test_docstring_in_module_details(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, DOC_IN_MODULE)
    assert dotted_names == ['zope.component']


def test_docstring_in_function(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, DOC_IN_FUNCTION)
    assert len(dotted_names) == 1


def test_docstring_in_function_details(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, DOC_IN_FUNCTION)
    assert dotted_names == ['zope.component.adapter']


def test_docstring_in_class(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, DOC_IN_CLASS)
    assert len(dotted_names) == 1


def test_docstring_in_class_details(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, DOC_IN_CLASS)
    assert dotted_names == ['zope.component.utility']


def test_docstring_in_method(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, DOC_IN_METHOD)
    assert len(dotted_names) == 1


def test_docstring_in_method_details(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, DOC_IN_METHOD)
    assert dotted_names == ['zope.interface']


def test_docstring_multiple_imports_same_line(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_SAME_LINE,
    )
    assert len(dotted_names) == 2


def test_docstring_multiple_imports_same_line_details(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_SAME_LINE,
    )
    assert 'zope.interface.Interface' in dotted_names
    assert 'zope.interface.Attribute' in dotted_names


def test_docstring_multiple_imports_different_line(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_DIFFERENT_LINES,
    )
    assert len(dotted_names) == 2


def test_docstring_multiple_imports_same_different_line_details(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_DIFFERENT_LINES,
    )
    assert 'zope.component.adapter' in dotted_names
    assert 'zope.component.utility' in dotted_names


def test_docstring_multiple_imports_with_invalid_lines(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_DIFFERENT_LINES_WITH_INVALID_CODE_LINES_BETWEEN,
    )
    assert len(dotted_names) == 2


def test_docstring_multiple_imports_with_invalid_lines_details(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MULTIPLE_IMPORTS_DIFFERENT_LINES_WITH_INVALID_CODE_LINES_BETWEEN,
    )
    assert 'zope.component.adapter' in dotted_names
    assert 'zope.component.utility' in dotted_names

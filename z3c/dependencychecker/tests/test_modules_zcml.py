from pathlib import Path

import pytest

from z3c.dependencychecker.modules import ZCMLFile
from z3c.dependencychecker.tests.utils import write_source_file_at

ZCML_TEMPLATE = """
<configure
  xmlns="http://namespaces.zope.org/zope"
  xmlns:browser="http://namespaces.zope.org/browser"
  xmlns:genericsetup="http://namespaces.zope.org/genericsetup">

{0}

</configure>
"""

RELATIVE_IMPORT = ".IRuleAssignable"
ABSOLUTE_IMPORT_1 = "plone.interfaces.IContent"
ABSOLUTE_IMPORT_2 = "zope.interfaces.IFolder"
ASTERISK_IMPORT = "*"

# list all possible combinations of how the imports can look like
# and how many of them are expected to be considered valid imports
# by z3c.dependencychecker
TEST_IMPORTS_MATRIX = (
    (0, f"{RELATIVE_IMPORT}"),
    (0, f"{ASTERISK_IMPORT}"),
    (0, f"{ASTERISK_IMPORT} {RELATIVE_IMPORT}"),
    (1, f"{ABSOLUTE_IMPORT_1}"),
    (1, f"{ABSOLUTE_IMPORT_2} {RELATIVE_IMPORT}"),
    (1, f"{ASTERISK_IMPORT} {ABSOLUTE_IMPORT_1}"),
    (2, f"{ABSOLUTE_IMPORT_1} {ABSOLUTE_IMPORT_2}"),
    (2, f"{ABSOLUTE_IMPORT_1} {ABSOLUTE_IMPORT_2} {ASTERISK_IMPORT}"),
)


def _get_zcml_imports_on_file(folder, source):
    full_content = ZCML_TEMPLATE.format(source)
    folder = Path(folder.strpath)
    temporal_file = write_source_file_at(
        folder,
        source_code=full_content,
        filename="configure.zcml",
    )

    zcml_file = ZCMLFile(folder, temporal_file)
    dotted_names = [x.name for x in zcml_file.scan()]
    return dotted_names


def _verify_dotted_names(dotted_names, imports, found):
    assert len(dotted_names) == found
    for an_import in imports.split(" "):
        if an_import in (RELATIVE_IMPORT, ASTERISK_IMPORT):
            continue
        assert an_import in dotted_names


def test_create_from_files_nothing(minimal_structure):
    path, package_name = minimal_structure
    modules_found = list(ZCMLFile.create_from_files(path))
    assert len(modules_found) == 0


def test_create_from_files_deep_nested(minimal_structure):
    path, package_name = minimal_structure
    src_path = path / "src"
    write_source_file_at(src_path / "a" / "b", filename="configure.zcml")

    modules_found = list(ZCMLFile.create_from_files(src_path))
    assert len(modules_found) == 1


@pytest.mark.parametrize("result,imports", TEST_IMPORTS_MATRIX)
def test_zcml_include(tmpdir, result, imports):
    """Check that the ZCML <include directive is scanned."""
    zcml_stanza = f'<include package="{imports}" />'
    dotted_names = _get_zcml_imports_on_file(tmpdir, zcml_stanza)
    _verify_dotted_names(dotted_names, imports, result)


@pytest.mark.parametrize("attribute", ("for", "factory", "provides"))
@pytest.mark.parametrize("result,imports", TEST_IMPORTS_MATRIX)
def test_zcml_adapter(tmpdir, result, imports, attribute):
    """Check that the ZCML <adapter directive is scanned."""
    zcml_stanza = f'<adapter {attribute}="{imports}" />'
    dotted_names = _get_zcml_imports_on_file(tmpdir, zcml_stanza)
    _verify_dotted_names(dotted_names, imports, result)


@pytest.mark.parametrize("attribute", ("provides", "component"))
@pytest.mark.parametrize("result,imports", TEST_IMPORTS_MATRIX)
def test_zcml_utility(tmpdir, result, imports, attribute):
    """Check that the ZCML <utility directive is scanned."""
    zcml_stanza = f'<utility {attribute}="{imports}" />'
    dotted_names = _get_zcml_imports_on_file(tmpdir, zcml_stanza)
    _verify_dotted_names(dotted_names, imports, result)


@pytest.mark.parametrize("attribute", ("class", "for", "layer"))
@pytest.mark.parametrize("result,imports", TEST_IMPORTS_MATRIX)
def test_zcml_browser_page(tmpdir, result, imports, attribute):
    """Check that the ZCML <browser:page directive is scanned."""
    zcml_stanza = f'<browser:page {attribute}="{imports}" />'
    dotted_names = _get_zcml_imports_on_file(tmpdir, zcml_stanza)
    _verify_dotted_names(dotted_names, imports, result)


@pytest.mark.parametrize("attribute", ("handler", "for"))
@pytest.mark.parametrize("result,imports", TEST_IMPORTS_MATRIX)
def test_zcml_subscriber(tmpdir, result, imports, attribute):
    """Check that the ZCML <subscriber directive is scanned."""
    zcml_stanza = f'<subscriber {attribute}="{imports}" />'
    dotted_names = _get_zcml_imports_on_file(tmpdir, zcml_stanza)
    _verify_dotted_names(dotted_names, imports, result)


@pytest.mark.parametrize("result,imports", TEST_IMPORTS_MATRIX)
def test_zcml_security_policy(tmpdir, result, imports):
    """Check that the ZCML <securityPolicy directive is scanned."""
    zcml_stanza = f'<securityPolicy component="{imports}" />'
    dotted_names = _get_zcml_imports_on_file(tmpdir, zcml_stanza)
    _verify_dotted_names(dotted_names, imports, result)


@pytest.mark.parametrize("result,imports", TEST_IMPORTS_MATRIX)
def test_zcml_genericsetup(tmpdir, result, imports):
    """Check that the ZCML <genericsetup:registerProfile directive is scanned."""
    zcml_stanza = f'<genericsetup:registerProfile provides="{imports}" />'
    dotted_names = _get_zcml_imports_on_file(tmpdir, zcml_stanza)
    _verify_dotted_names(dotted_names, imports, result)


@pytest.mark.parametrize("result,imports", TEST_IMPORTS_MATRIX)
def test_zcml_implements(tmpdir, result, imports):
    """Check that the ZCML <implements directive is scanned."""
    zcml_stanza = f'<implements interface="{imports}" />'
    dotted_names = _get_zcml_imports_on_file(tmpdir, zcml_stanza)
    _verify_dotted_names(dotted_names, imports, result)

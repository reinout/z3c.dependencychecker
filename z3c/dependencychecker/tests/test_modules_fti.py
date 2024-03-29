from pathlib import Path
from z3c.dependencychecker.modules import FTIFile
from z3c.dependencychecker.tests.utils import write_source_file_at


XML_TEMPLATE = """<?xml version="1.0"?>
<object>
{0}
</object>
"""

NO_NAME = """
<property class="something"></property>
"""
NO_BEHAVIORS = """
<property name="behaviors"></property>
"""
BEHAVIORS_WITHOUT_VALUE = """
<property name="behaviors">
  <element class="my.behavior"/>
</property>
"""
KLASS = """
<property name="klass">my.class.package</property>
"""
SCHEMA = """
<property name="schema">my.path.to.schema</property>
"""
SOMETHING_ELSE_IGNORE = """
<property name="random_name">my.path.to.schema</property>
"""

SCHEMA_EMPTY = '<property name="schema"></property>'


def _get_fti_imports_on_file(folder, source):
    full_content = XML_TEMPLATE.format(source)
    folder = Path(folder)
    temporal_file = write_source_file_at(
        folder,
        source_code=full_content,
        filename="configure.zcml",
    )

    fti_file = FTIFile(folder, temporal_file)
    dotted_names = [x.name for x in fti_file.scan()]
    return dotted_names


def test_create_from_files_nothing(minimal_structure):
    path, package_name = minimal_structure
    modules_found = list(FTIFile.create_from_files(path))
    assert len(modules_found) == 0


def test_create_from_files_deep_nested(minimal_structure):
    path, package_name = minimal_structure
    src_path = path / "src"
    write_source_file_at(
        src_path / "a" / "b" / "c" / "types",
        filename="test.xml",
    )

    modules_found = list(FTIFile.create_from_files(src_path))
    assert len(modules_found) == 1


def test_ignore_nodes_without_name(tmpdir):
    dotted_names = _get_fti_imports_on_file(tmpdir, NO_NAME)
    assert len(dotted_names) == 0


def test_no_behavior(tmpdir):
    dotted_names = _get_fti_imports_on_file(tmpdir, NO_BEHAVIORS)
    assert len(dotted_names) == 0


def test_behavior_without_value(tmpdir):
    dotted_names = _get_fti_imports_on_file(tmpdir, BEHAVIORS_WITHOUT_VALUE)
    assert len(dotted_names) == 0


def test_klass(tmpdir):
    dotted_names = _get_fti_imports_on_file(tmpdir, KLASS)
    assert len(dotted_names) == 1


def test_klass_details(tmpdir):
    dotted_names = _get_fti_imports_on_file(tmpdir, KLASS)
    assert "my.class.package" in dotted_names


def test_schema(tmpdir):
    dotted_names = _get_fti_imports_on_file(tmpdir, SCHEMA)
    assert len(dotted_names) == 1


def test_schema_details(tmpdir):
    dotted_names = _get_fti_imports_on_file(tmpdir, SCHEMA)
    assert "my.path.to.schema" in dotted_names


def test_something_to_ignore(tmpdir):
    dotted_names = _get_fti_imports_on_file(tmpdir, SOMETHING_ELSE_IGNORE)
    assert len(dotted_names) == 0


def test_schema_emtpy(tmpdir):
    dotted_names = _get_fti_imports_on_file(tmpdir, SCHEMA_EMPTY)
    assert len(dotted_names) == 0

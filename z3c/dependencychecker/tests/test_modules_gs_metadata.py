import os

from z3c.dependencychecker.modules import GSMetadata
from z3c.dependencychecker.tests.utils import write_source_file_at

XML_TEMPLATE = """<metadata>
<dependencies>
{0}
</dependencies>
</metadata>
"""

SOMETING_ELSE_IGNORED = """<property class="something"></property>"""
EMPTY_DEPENDENCY = """<dependency></dependency>"""
ONLY_SPACES_DEPENDENCY = """<dependency> </dependency>"""
MISSING_PREFIX = """<dependency>plone.app.caching:default</dependency>"""
MISSING_PROFILE_NAME_SUFFIX = """
<dependency>profile-plone.app.caching</dependency>
"""

ONE_DEPENDENCY = """
<dependency>profile-plone.app.caching:default</dependency>
"""
MORE_DEPENDENCIES = """
<dependency>profile-plone.app.caching:default</dependency>
<dependency>profile-plone.app.dexterity:default</dependency>
"""


def _get_dependencies_on_file(folder, source):
    full_content = XML_TEMPLATE.format(source)
    temporal_file = write_source_file_at(
        (folder.strpath,),
        source_code=full_content,
        filename='configure.zcml',
    )

    gs_metadata = GSMetadata(folder.strpath, temporal_file)
    dotted_names = [x.name for x in gs_metadata.scan()]
    return dotted_names


def test_create_from_files_nothing(minimal_structure):
    path, package_name = minimal_structure
    modules_found = list(GSMetadata.create_from_files(path))
    assert len(modules_found) == 0


def test_create_from_files_deep_nested(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at(
        [src_path, 'a', 'b', 'c'],
        filename='metadata.xml',
    )

    modules_found = list(GSMetadata.create_from_files(src_path))
    assert len(modules_found) == 1


def test_ignore_other_nodes(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, SOMETING_ELSE_IGNORED)
    assert len(dotted_names) == 0


def test_empty_dependency(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, EMPTY_DEPENDENCY)
    assert len(dotted_names) == 0


def test_only_spaces_dependency(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, ONLY_SPACES_DEPENDENCY)
    assert len(dotted_names) == 0


def test_malformed_dependency_no_prefix(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, MISSING_PREFIX)
    assert len(dotted_names) == 0


def test_malformed_dependency_no_suffix(tmpdir):
    dotted_names = _get_dependencies_on_file(
        tmpdir,
        MISSING_PROFILE_NAME_SUFFIX,
    )
    assert len(dotted_names) == 0


def test_one_dependency(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, ONE_DEPENDENCY)
    assert len(dotted_names) == 1


def test_one_dependency_details(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, ONE_DEPENDENCY)
    assert dotted_names == ['plone.app.caching']


def test_more_dependencies(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, MORE_DEPENDENCIES)
    assert len(dotted_names) == 2


def test_more_dependencies_details(tmpdir):
    dotted_names = _get_dependencies_on_file(tmpdir, MORE_DEPENDENCIES)
    assert 'plone.app.caching' in dotted_names
    assert 'plone.app.dexterity' in dotted_names

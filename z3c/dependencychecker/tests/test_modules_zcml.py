import os

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

INCLUDE = '<include package="my.package.include" />'
ADAPTER_FACTORY = '<adapter factory="my.package.factory" />'
ADAPTER_FOR = '<adapter for="my.package.for" />'
ADAPTER_FOR_MULTIPLE = (
    '<adapter for="my.package.for another.package.foo yet.another.one" />'  # noqa
)
ADAPTER_PROVIDES = '<adapter provides="my.package.provides" />'
UTILITY_COMPONENT = '<utility component="my.package.component" />'
UTILITY_PROVIDES = '<utility provides="my.package.provides" />'
BROWSER_PAGE_CLASS = '<browser:page class="my.package.class" />'
BROWSER_PAGE_FOR = '<browser:page for="my.package.for" />'
BROWSER_PAGE_LAYER = '<browser:page layer="my.package.layer" />'
SUBSCRIBER_FOR = '<subscriber for="my.package.for" />'
SUBSCRIBER_FOR_MULTIPLE = """<subscriber for="my.package.for
                 another.package" />
"""
SUBSCRIBER_HANDLER = '<subscriber handler="my.package.handler" />'
SECURITYPOLICY_COMPONENT = '<securityPolicy component="my.package.component" />'  # noqa
GS_REGISTERPROFILE_PROVIDES = (
    '<genericsetup:registerProfile provides="my.package.provides" />'  # noqa
)
IGNORE_LOCAL_IMPORT = '<adapter factory=".package.factory" />'
ASTERISK = '<adapter for="*" />'


def _get_zcml_imports_on_file(folder, source):
    full_content = ZCML_TEMPLATE.format(source)
    temporal_file = write_source_file_at(
        (folder.strpath,),
        source_code=full_content,
        filename='configure.zcml',
    )

    zcml_file = ZCMLFile(folder.strpath, temporal_file)
    dotted_names = [x.name for x in zcml_file.scan()]
    return dotted_names


def test_create_from_files_nothing(minimal_structure):
    path, package_name = minimal_structure
    modules_found = list(ZCMLFile.create_from_files(path))
    assert len(modules_found) == 0


def test_create_from_files_deep_nested(minimal_structure):
    path, package_name = minimal_structure
    src_path = os.path.join(path, 'src')
    write_source_file_at([src_path, 'a', 'b'], filename='configure.zcml')

    modules_found = list(ZCMLFile.create_from_files(src_path))
    assert len(modules_found) == 1


def test_include(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, INCLUDE)
    assert len(dotted_names) == 1


def test_include_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, INCLUDE)
    assert dotted_names == ['my.package.include']


def test_adapter_factory(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, ADAPTER_FACTORY)
    assert len(dotted_names) == 1


def test_adapter_factory_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, ADAPTER_FACTORY)
    assert dotted_names == ['my.package.factory']


def test_adapter_for(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, ADAPTER_FOR)
    assert len(dotted_names) == 1


def test_adapter_for_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, ADAPTER_FOR)
    assert dotted_names == ['my.package.for']


def test_adapter_for_multiple(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, ADAPTER_FOR_MULTIPLE)
    assert len(dotted_names) == 3


def test_adapter_for_multiple_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, ADAPTER_FOR_MULTIPLE)
    assert 'my.package.for' in dotted_names
    assert 'another.package.foo' in dotted_names
    assert 'yet.another.one' in dotted_names


def test_adapter_provides(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, ADAPTER_PROVIDES)
    assert len(dotted_names) == 1


def test_adapter_provides_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, ADAPTER_PROVIDES)
    assert dotted_names == ['my.package.provides']


def test_utility_component(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, UTILITY_COMPONENT)
    assert len(dotted_names) == 1


def test_utility_component_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, UTILITY_COMPONENT)
    assert dotted_names == ['my.package.component']


def test_utility_provides(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, UTILITY_PROVIDES)
    assert len(dotted_names) == 1


def test_utility_provides_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, UTILITY_PROVIDES)
    assert dotted_names == ['my.package.provides']


def test_browser_page_class(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, BROWSER_PAGE_CLASS)
    assert len(dotted_names) == 1


def test_browser_page_class_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, BROWSER_PAGE_CLASS)
    assert dotted_names == ['my.package.class']


def test_browser_page_for(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, BROWSER_PAGE_FOR)
    assert len(dotted_names) == 1


def test_browser_page_for_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, BROWSER_PAGE_FOR)
    assert dotted_names == ['my.package.for']


def test_browser_page_layer(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, BROWSER_PAGE_LAYER)
    assert len(dotted_names) == 1


def test_browser_page_layer_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, BROWSER_PAGE_LAYER)
    assert dotted_names == ['my.package.layer']


def test_subscriber_for(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, SUBSCRIBER_FOR)
    assert len(dotted_names) == 1


def test_subscriber_for_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, SUBSCRIBER_FOR)
    assert dotted_names == ['my.package.for']


def test_subscriber_for_multiple(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, SUBSCRIBER_FOR_MULTIPLE)
    assert len(dotted_names) == 2


def test_subscriber_for_multiple_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, SUBSCRIBER_FOR_MULTIPLE)
    assert dotted_names == [
        'my.package.for',
        'another.package',
    ]


def test_subscriber_handler(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, SUBSCRIBER_HANDLER)
    assert len(dotted_names) == 1


def test_subscriber_handler_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, SUBSCRIBER_HANDLER)
    assert dotted_names == ['my.package.handler']


def test_securitypolicy_component(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, SECURITYPOLICY_COMPONENT)
    assert len(dotted_names) == 1


def test_securitypolicy_component_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, SECURITYPOLICY_COMPONENT)
    assert dotted_names == ['my.package.component']


def test_gs_registerprofile_provides(tmpdir):
    dotted_names = _get_zcml_imports_on_file(
        tmpdir,
        GS_REGISTERPROFILE_PROVIDES,
    )
    assert len(dotted_names) == 1


def test_gs_registerprofile_provides_details(tmpdir):
    dotted_names = _get_zcml_imports_on_file(
        tmpdir,
        GS_REGISTERPROFILE_PROVIDES,
    )
    assert dotted_names == ['my.package.provides']


def test_ignore_local_import(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, IGNORE_LOCAL_IMPORT)
    assert len(dotted_names) == 0


def test_ignore_asterisk_import(tmpdir):
    dotted_names = _get_zcml_imports_on_file(tmpdir, ASTERISK)
    assert len(dotted_names) == 0

from unittest import mock

from z3c.dependencychecker.package import Package
from z3c.dependencychecker.report import Report
from z3c.dependencychecker.tests.utils import write_source_file_at


def test_print_header_nothing(capsys):
    fake_package = mock.MagicMock()
    report = Report(fake_package)
    report._print_header(None)
    out, err = capsys.readouterr()
    assert out == ''


def test_print_header_text(capsys):
    fake_project = mock.MagicMock()
    report = Report(fake_project)
    report._print_header('hi')
    out, err = capsys.readouterr()

    assert 'hi' in out
    assert '==' in out
    assert '===' not in out


def test_print_report(capsys, minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)
    report = Report(package)
    report.print_report()
    out, err = capsys.readouterr()
    assert '======' not in out  # there are no errors on the dependencies
    assert '' == err


def test_missing_requirements_nothing(capsys):
    fake_project = mock.MagicMock()
    report = Report(fake_project)
    report.missing_requirements()
    out, err = capsys.readouterr()
    assert out == ''


def test_missing_requirements(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at((path, package_name), '__init__.py', 'import another.package')

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.missing_requirements()
    out, err = capsys.readouterr()

    assert 'Missing requirements\n====================' in out
    assert 'another.package' in out


def test_missing_requirements_with_user_mapping(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'import Products.Five.browser.views.BrowserView',
    )
    write_source_file_at(
        (path, f'{package_name}.egg-info'),
        'requires.txt',
        'Zope2',
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(
            [
                '[tool.dependencychecker]',
                'Zope2 = ["Four", "Products.Five", "Three" ]',
            ]
        ),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.missing_requirements()
    out, err = capsys.readouterr()

    assert 'Missing requirements\n====================' not in out
    assert 'Products.Five' not in out
    assert 'Zope2' not in out


def test_missing_requirements_with_ignored_packages(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'import Products.Five.browser.views.BrowserView',
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(
            [
                '[tool.dependencychecker]',
                'ignore-packages = ["Four", "Products.Five", "Three" ]',
            ]
        ),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.missing_requirements()
    out, err = capsys.readouterr()

    assert 'Missing requirements\n====================' not in out
    assert 'Products.Five' not in out
    assert 'Four' not in out
    assert 'Three' not in out


def test_missing_test_requirements(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        '',
    )
    write_source_file_at(
        (path, package_name, 'tests'),
        '__init__.py',
        'import another.package',
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.missing_test_requirements()
    out, err = capsys.readouterr()

    assert 'Missing test requirements\n=========================' in out
    assert 'another.package' in out


def test_missing_test_requirements_with_user_mapping(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        '',
    )
    write_source_file_at(
        (path, package_name, 'tests'),
        '__init__.py',
        'import Products.Five.browser.views.BrowserView',
    )
    write_source_file_at(
        (path, f'{package_name}.egg-info'),
        'requires.txt',
        'Zope2',
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(['[tool.dependencychecker]', 'Zope2 = ["Products.Five" ]']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.missing_test_requirements()
    out, err = capsys.readouterr()

    assert '' == out
    assert 'Missing requirements\n====================' not in out
    assert 'Products.Five' not in out
    assert 'Zope2' not in out


def test_missing_test_requirements_with_user_mapping_on_test_extra(
    capsys, minimal_structure
):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        '',
    )
    write_source_file_at(
        (path, package_name, 'tests'),
        '__init__.py',
        'import Products.Five.browser.views.BrowserView',
    )
    write_source_file_at(
        (path, f'{package_name}.egg-info'),
        'requires.txt',
        '\n'.join(['[test]', 'Zope2']),
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(['[tool.dependencychecker]', 'Zope2 = ["Products.Five" ]']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.missing_test_requirements()
    out, err = capsys.readouterr()

    assert '' == out
    assert 'Missing requirements\n====================' not in out
    assert 'Products.Five' not in out
    assert 'Zope2' not in out


def test_missing_test_requirements_with_ignored_packages(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        '',
    )
    write_source_file_at(
        (path, package_name, 'tests'),
        '__init__.py',
        'import Products.Five.browser.views.BrowserView',
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(
            [
                '[tool.dependencychecker]',
                'ignore-packages = ["Products.Five" ]',
            ]
        ),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.missing_test_requirements()
    out, err = capsys.readouterr()

    assert '' == out
    assert 'Missing requirements\n====================' not in out
    assert 'Products.Five' not in out


def test_unneeded_requirements(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'import this.package',
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.unneeded_requirements()
    out, err = capsys.readouterr()

    assert 'Unneeded requirements\n=====================' in out
    assert 'one' in out
    assert 'two' in out


def test_unneeded_requirements_with_ignored_packages(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'import this.package',
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(
            [
                '[tool.dependencychecker]',
                'ignore-packages = ["one" ]',
            ]
        ),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.unneeded_requirements()
    out, err = capsys.readouterr()

    assert 'Unneeded requirements\n=====================' in out
    assert 'one' not in out
    assert 'two' in out


def test_unneeded_requirements_with_user_mapping(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'from BTrees import Tree',
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(['[tool.dependencychecker]', '"ZODB3" = ["BTrees" ]']),
    )
    write_source_file_at(
        (path, f'{package_name}.egg-info'),
        'requires.txt',
        '\n'.join(['ZODB3', 'setuptools', 'one']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.unneeded_requirements()
    out, err = capsys.readouterr()

    assert 'Unneeded requirements\n=====================' in out
    assert 'ZODB3' not in out
    assert 'one' in out


def test_unneeded_requirements_with_user_mapping2(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'from Plone import Tree',
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(['[tool.dependencychecker]', '"ZODB3" = ["BTrees" ]']),
    )
    write_source_file_at(
        (path, f'{package_name}.egg-info'),
        'requires.txt',
        '\n'.join(['ZODB3', 'setuptools', 'one']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.unneeded_requirements()
    out, err = capsys.readouterr()

    assert 'Unneeded requirements\n=====================' in out
    assert 'ZODB3' in out
    assert 'one' in out


def test_unneeded_test_requirements(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name + '.egg-info'),
        'requires.txt',
        '\n'.join(['[test]', 'pytest', 'mock']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.unneeded_test_requirements()
    out, err = capsys.readouterr()

    assert 'Unneeded test requirements\n==========================' in out
    assert 'pytest' in out
    assert 'mock' in out


def test_unneeded_test_requirements_with_ignore_packages(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name + '.egg-info'),
        'requires.txt',
        '\n'.join(['[test]', 'pytest', 'mock']),
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(['[tool.dependencychecker]', 'ignore-packages = ["mock" ]']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.unneeded_test_requirements()
    out, err = capsys.readouterr()

    assert 'Unneeded test requirements\n==========================' in out
    assert 'pytest' in out
    assert 'mock' not in out


def test_unneeded_test_requirements_with_user_mappings(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name + '.egg-info'),
        'requires.txt',
        '\n'.join(['[test]', 'pytest', 'ZODB3']),
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(['[tool.dependencychecker]', '"ZODB3" = ["BTrees" ]']),
    )
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        '',
    )
    write_source_file_at(
        (path, package_name, 'tests'),
        '__init__.py',
        'from BTrees import Tree',
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.unneeded_test_requirements()
    out, err = capsys.readouterr()

    assert 'Unneeded test requirements\n==========================' in out
    assert 'pytest' in out
    assert 'ZODB3' not in out
    assert 'BTrees' not in out


def test_unneeded_test_requirements_no_tests_requirements(
    capsys,
    minimal_structure,
):
    path, package_name = minimal_structure

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.unneeded_test_requirements()
    out, err = capsys.readouterr()

    assert '' == out


def test_requirements_that_should_be_test_requirements(
    capsys,
    minimal_structure,
):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'import one',
    )
    write_source_file_at(
        (path, package_name, 'tests'),
        '__init__.py',
        'import two',
    )
    write_source_file_at(
        (path, package_name + '.egg-info'),
        'requires.txt',
        '\n'.join(['one', 'two', '[test]', 'pytest', 'mock']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.requirements_that_should_be_test_requirements()
    out, err = capsys.readouterr()

    assert (
        'Requirements that should be test requirements\n'
        '=============================================' in out
    )
    assert 'two' in out


def test_requirements_that_should_be_test_requirements_with_ignored_packages(
    capsys,
    minimal_structure,
):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'import one',
    )
    write_source_file_at(
        (path, package_name, 'tests'),
        '__init__.py',
        '\n'.join(['import two', 'import three']),
    )
    write_source_file_at(
        (path, package_name + '.egg-info'),
        'requires.txt',
        '\n'.join(['one', 'two', 'three', '[test]', 'pytest', 'mock']),
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(['[tool.dependencychecker]', 'ignore-packages = ["two" ]']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.requirements_that_should_be_test_requirements()
    out, err = capsys.readouterr()

    assert (
        'Requirements that should be test requirements\n'
        '=============================================' in out
    )
    assert 'three' in out
    assert 'two' not in out


def test_requirements_that_should_be_test_requirements_with_user_mappings(
    capsys,
    minimal_structure,
):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'import one',
    )
    write_source_file_at(
        (path, package_name, 'tests'),
        '__init__.py',
        '\n'.join(['import two', 'import BTrees']),
    )
    write_source_file_at(
        (path, package_name + '.egg-info'),
        'requires.txt',
        '\n'.join(['one', 'two', 'ZODB3', '[test]', 'pytest', 'mock']),
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(['[tool.dependencychecker]', '"ZODB3" = ["BTrees" ]']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.requirements_that_should_be_test_requirements()
    out, err = capsys.readouterr()

    assert (
        'Requirements that should be test requirements\n'
        '=============================================' in out
    )
    assert 'ZODB3' in out
    assert 'two' in out
    assert 'one' not in out


def test_requirements_that_should_be_test_requirements_with_user_mapping2(
    capsys,
    minimal_structure,
):
    """Test that user mappings used in both regular and test imports are
    not downgraded to test imports only.
    """
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        '\n'.join(['import one', 'import two', 'import part.of.meta']),
    )
    write_source_file_at(
        (path, package_name, 'tests'),
        '__init__.py',
        '\n'.join(['import three', 'import four', 'import part.of.meta']),
    )
    write_source_file_at(
        (path, package_name + '.egg-info'),
        'requires.txt',
        '\n'.join(['one', 'two', 'three', 'meta-package', '[test]', 'four']),
    )
    write_source_file_at(
        (path,),
        'pyproject.toml',
        '\n'.join(['[tool.dependencychecker]', 'meta-package = ["part.of.meta" ]']),
    )

    package = Package(path)
    package.inspect()
    report = Report(package)
    report.requirements_that_should_be_test_requirements()
    out, err = capsys.readouterr()

    assert (
        'Requirements that should be test requirements\n'
        '=============================================' in out
    )
    assert 'three' in out
    assert 'one' not in out
    assert 'two' not in out
    assert 'part.of.meta' not in out
    assert 'meta-package' not in out


def test_print_notice(capsys, minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)
    report = Report(package)
    report.print_notice()
    out, err = capsys.readouterr()
    assert 'Note: ' in out
    assert '' == err


def test_exit_status_set(minimal_structure):
    path, package_name = minimal_structure
    package = Package(path)
    package.inspect()
    report = Report(package)
    assert report.exit_status == 0
    report.print_report()
    assert report.exit_status == 1

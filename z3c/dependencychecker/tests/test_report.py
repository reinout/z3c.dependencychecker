# -*- coding: utf-8 -*-
from z3c.dependencychecker.package import Package
from z3c.dependencychecker.report import Report
from z3c.dependencychecker.tests.utils import write_source_file_at
import mock


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


def test_missing_requirements_nothing(capsys):
    fake_project = mock.MagicMock()
    report = Report(fake_project)
    report.missing_requirements()
    out, err = capsys.readouterr()
    assert out == ''


def test_missing_requirements(capsys, minimal_structure):
    path, package_name = minimal_structure
    write_source_file_at(
        (path, package_name),
        '__init__.py',
        'import this.package'
    )

    package = Package(path)
    package.analyze_package()
    report = Report(package)
    report.missing_requirements()
    out, err = capsys.readouterr()

    assert 'Missing requirements\n' \
           '====================' in out
    assert 'this.package' in out


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
        'import this.package',
    )

    package = Package(path)
    package.analyze_package()
    report = Report(package)
    report.missing_test_requirements()
    out, err = capsys.readouterr()

    assert 'Missing test requirements\n' \
           '=========================' in out
    assert 'this.package' in out

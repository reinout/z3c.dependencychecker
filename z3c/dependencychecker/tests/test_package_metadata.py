import os
import shutil
import tempfile

import pkg_resources

from z3c.dependencychecker.package import PackageMetadata


def test_no_setup_py_file_found():
    folder = tempfile.mkdtemp()
    sys_exit = False
    try:
        PackageMetadata(folder)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_distribution_root(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.distribution_root == path


def test_setup_py_path(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.setup_py_path == os.path.join(path, 'setup.py')


def test_package_dir_on_distribution_root(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.package_dir == path


def test_package_dir_on_src_folder(minimal_structure):
    def move_top_level_to_src(package_path, egg_folder, src_path):
        top_level_file_path = os.path.join(egg_folder, 'top_level.txt')
        with open(top_level_file_path) as top_level_file:
            top_level_folder = top_level_file.read().strip()

        top_level_sources = os.path.join(package_path, top_level_folder)

        shutil.move(top_level_sources, src_path)
        shutil.move(egg_folder, src_path)

    path, package_name = minimal_structure

    egg_info_folder = os.path.join(path, f'{package_name}.egg-info')
    src_folder = os.path.join(path, 'src')

    move_top_level_to_src(path, egg_info_folder, src_folder)

    metadata = PackageMetadata(path)

    assert metadata.package_dir == src_folder


def test_package_dir_on_another_folder(minimal_structure):
    def move_top_level_to_folder(package_path, egg_folder, folder_path):
        top_level_file_path = os.path.join(egg_folder, 'top_level.txt')
        with open(top_level_file_path) as top_level_file:
            top_level_folder = top_level_file.read().strip()

        top_level_sources = os.path.join(package_path, top_level_folder)

        shutil.move(top_level_sources, folder_path)
        shutil.move(egg_folder, folder_path)

    path, package_name = minimal_structure

    egg_info_folder = os.path.join(path, f'{package_name}.egg-info')
    folder_path = os.path.join(path, 'somewhere')

    move_top_level_to_folder(path, egg_info_folder, folder_path)

    metadata = PackageMetadata(path)

    assert metadata.package_dir == folder_path


def test_no_package_dir_found(minimal_structure):
    path, package_name = minimal_structure
    shutil.rmtree(os.path.join(path, f'{package_name}.egg-info'))

    sys_exit = False
    try:
        PackageMetadata(path)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_no_package_dir_and_no_src_folder(minimal_structure):
    path, package_name = minimal_structure
    shutil.rmtree(os.path.join(path, f'{package_name}.egg-info'))
    shutil.rmtree(os.path.join(path, 'src'))

    sys_exit = False
    try:
        PackageMetadata(path)
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_egg_info_dir_path(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    egg_info_path = os.path.join(path, f'{package_name}.egg-info')

    assert metadata.egg_info_dir == egg_info_path


def test_package_name(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.name == package_name


def test_working_set(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert isinstance(metadata._working_set, pkg_resources.WorkingSet)


def test_package_in_working_set(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    ourselves = metadata._get_ourselves_from_working_set()
    assert ourselves.project_name == package_name


def test_package_missing_pkg_info_file(minimal_structure):
    path, package_name = minimal_structure

    pkg_info = os.path.join(
        path,
        f'{package_name}.egg-info',
        'PKG-INFO',
    )
    os.remove(pkg_info)

    metadata = PackageMetadata(path)

    sys_exit = False
    try:
        metadata._get_ourselves_from_working_set()
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_package_broken_pkg_info_file(minimal_structure):
    path, package_name = minimal_structure

    pkg_info_path = os.path.join(
        path,
        f'{package_name}.egg-info',
        'PKG-INFO',
    )
    os.remove(pkg_info_path)
    with open(pkg_info_path, 'w') as pkg_info_file:
        pkg_info_file.write('\n'.join(['Name: bla']))

    metadata = PackageMetadata(path)
    sys_exit = False
    try:
        metadata._get_ourselves_from_working_set()
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_get_dependencies(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    names = [x.name for x in metadata.get_required_dependencies()]
    assert 'one' in names
    assert 'two' in names


def test_get_no_dependencies(minimal_structure):
    path, package_name = minimal_structure

    requires_file_path = os.path.join(
        path,
        f'{package_name}.egg-info',
        'requires.txt',
    )
    os.remove(requires_file_path)

    metadata = PackageMetadata(path)

    requirements = list(metadata.get_required_dependencies())
    assert len(requirements) == 0


def test_dependencies_with_extras(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = os.path.join(
        path,
        f'{package_name}.egg-info',
        'requires.txt',
    )
    with open(requires_file_path, 'w') as requires:
        requires.write(
            '\n'.join(
                [
                    'one [with_extra]',
                    'another[with_extra]',
                    'yet[one,two,three,extras]',
                    'something[only, two, with, spaces]',
                ]
            )
        )

    metadata = PackageMetadata(path)
    names = [x.name for x in metadata.get_required_dependencies()]

    assert len(names) == 4
    assert 'one' in names
    assert 'another' in names
    assert 'yet' in names
    assert 'something' in names


def test_dependencies_with_version_specifiers(minimal_structure):
    path, package_name = minimal_structure
    requires_file_path = os.path.join(
        path,
        f'{package_name}.egg-info',
        'requires.txt',
    )
    with open(requires_file_path, 'w') as requires:
        requires.write(
            '\n'.join(
                ['one > 8.5', 'another<=3.4', 'yet==5.2', 'something >=2.2.1,<2.3dev']
            )
        )

    metadata = PackageMetadata(path)
    names = [x.name for x in metadata.get_required_dependencies()]

    assert len(names) == 4
    assert 'one' in names
    assert 'another' in names
    assert 'yet' in names


def test_get_extra_dependencies(minimal_structure):
    path, package_name = minimal_structure

    requires_file_path = os.path.join(
        path,
        f'{package_name}.egg-info',
        'requires.txt',
    )
    with open(requires_file_path, 'w') as requires_file:
        requires_file.write('\n'.join(['one', '', '[test]', 'pytest', 'mock']))

    metadata = PackageMetadata(path)
    extras = list(metadata.get_extras_dependencies())
    extra_packages = [x.name for x in extras[0][1]]
    assert len(extras) == 1
    assert 'pytest' in extra_packages
    assert 'mock' in extra_packages


def test_no_extras(minimal_structure):
    path, package_name = minimal_structure

    metadata = PackageMetadata(path)

    extras = list(metadata.get_extras_dependencies())
    assert len(extras) == 0


def test_top_level_txt_file_found(minimal_structure):
    path, package_name = minimal_structure
    metadata = PackageMetadata(path)

    assert metadata.top_level == [os.path.join(path, package_name)]


def test_no_top_level_txt_file_found(minimal_structure):
    path, package_name = minimal_structure
    os.remove(os.path.join(path, f'{package_name}.egg-info', 'top_level.txt'))

    sys_exit = False
    metadata = PackageMetadata(path)
    try:
        metadata.top_level
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_no_sources_top_level_folder_found(minimal_structure):
    path, package_name = minimal_structure
    os.removedirs(os.path.join(path, package_name))

    sys_exit = False
    metadata = PackageMetadata(path)
    try:
        metadata.top_level
    except SystemExit:
        sys_exit = True

    assert sys_exit


def test_top_level_is_module(minimal_structure):
    path, package_name = minimal_structure
    top_level_path = os.path.join(path, package_name)
    os.removedirs(top_level_path)
    top_level_module_path = f'{top_level_path}.py'
    with open(top_level_module_path, 'w') as top_level_file:
        top_level_file.write('Does not matter')

    metadata = PackageMetadata(path)

    assert metadata.top_level == [top_level_module_path]


def test_top_level_multiple(minimal_structure):
    path, package_name = minimal_structure
    top_level_file = os.path.join(
        path,
        f'{package_name}.egg-info',
        'top_level.txt',
    )
    with open(top_level_file, 'w') as top_level:
        top_level.write('one\n')
        top_level.write('two\n')
        top_level.write('three\n')

    top_level_folders = [
        f'{path}/one',
        f'{path}/two',
        f'{path}/three',
    ]
    for new_top_level in top_level_folders:
        os.makedirs(new_top_level)

    metadata = PackageMetadata(path)

    assert metadata.top_level == top_level_folders

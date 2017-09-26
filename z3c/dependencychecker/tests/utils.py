# -*- coding: utf-8 -*-
import os


def write_source_file_at(
    path_parts,
    filename='test.py',
    source_code='import one',
):
    folder_path = os.path.join(*path_parts)

    try:
        os.makedirs(folder_path)
    except OSError:
        pass

    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'w') as new_file:
        new_file.write(source_code)

    return file_path


def get_requirements_names(database):
    return [
        requirement.name
        for requirement in database._requirements
    ]

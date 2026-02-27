def write_source_file_at(
    folder_path,
    filename="test.py",
    source_code="import unknown.dependency",
):
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / filename
    file_path.write_text(source_code)
    return file_path


def get_requirements_names(database):
    return [requirement.name for requirement in database._requirements]


def get_extras_requirements_names(database):
    return database._extras_requirements.keys()


def get_requirements_names_for_extra(database, extra=""):
    return [requirement.name for requirement in database._extras_requirements[extra]]


def get_sorted_imports_paths(database):
    return sorted([x.file_path for x in database.imports_used])

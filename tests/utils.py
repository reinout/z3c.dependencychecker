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


def dist_info(name="test-package", top_levels=None, requirements=None):
    """Generate a `wheel-inspect` JSON structure meant to use in a mock call

    With this JSON we avoid calling `inspect_wheel`,
    which expects to read a properly generated wheel zip file.

    The requirements list expects a list of strings with the following format:

    ```
    EXTRA|PKG-NAME|OPTIONALS
    ```

    Where:
    - `EXTRA` is the extra group (if any) that the package is on (i.e. tests, async, etc.)
    - `PKG-NAME` the package name :-)
    - `OPTIONALS` the package extra groups (if any), i.e. the async on `zope.interface[async]`

    If you want to demonstrate that the package being analyzed (say plone.batching)
    has a testing dependency on `plone.testing` with the `postgres` extra,
    then you need to write it like this: `test|plone.testing|postgres`
    """
    if top_levels is None:
        top_levels = [name]
    if requirements is None:
        requirements = []

    final_requirements = []
    if requirements:
        for requirement in requirements:
            marker, package_name, extras = requirement.split("|")
            extras_list = []
            if extras:
                extras_list = extras.split(",")
            final_marker = ""
            if marker:
                final_marker = f'extra == "{marker}"'
            final_requirements.append(
                {"name": package_name, "extras": extras_list, "marker": final_marker}
            )

    return {
        "dist_info": {
            "top_level": top_levels,
            "metadata": {"name": name, "requires_dist": final_requirements},
        }
    }

import logging
import sys

from z3c.dependencychecker.dotted_name import DottedName

logger = logging.getLogger(__name__)


# starting from python 3.10 the list of builtin methods are available directly
PY_10_OR_HIGHER = sys.version_info[1] >= 10


class ImportsDatabase:
    """Store all imports and requirements of a package

    Use that information to extract useful data out of it,
    like requirements unused, etc.
    """

    def __init__(self):
        self._requirements = set()
        self._extras_requirements = {}
        self.imports_used = []
        self.user_mappings = {}
        self.reverse_user_mappings = {}
        self.ignored_packages = set()
        self.own_dotted_name = None

    def add_requirements(self, requirements):
        self._requirements = set(requirements)

    def add_extra_requirements(self, extra_name, dotted_names):
        # A bit of extra work needs to be done as pkg_resources API returns
        # all common requirements as well as the extras when asking for an
        # extra requirements.
        only_extra_dotted_names = self._filter_duplicates(dotted_names)
        if extra_name in self._extras_requirements.keys():
            self._extras_requirements[extra_name].update(
                only_extra_dotted_names,
            )

            logger.warning(
                'extra requirement "%s" is declared twice in setup.py',
                extra_name,
            )
        else:
            self._extras_requirements[extra_name] = only_extra_dotted_names

    def _filter_duplicates(self, imports):
        """Return all items in imports that are not a requirement already"""
        all_imports = set(imports)
        filtered = all_imports - self._requirements
        return filtered

    def add_imports(self, imports):
        filters = (
            self._filter_out_known_packages,
            self._filter_out_own_package,
            self._filter_out_python_standard_library,
        )
        for single_import in imports:
            logger.debug('    Import found: %s', single_import.name)

            unknown_import = self._apply_filters([single_import], filters)
            if unknown_import:
                self.imports_used.append(single_import)
            else:
                logger.debug('    Import ignored: %s', single_import.name)

    def add_user_mapping(self, package_name, provided_names):
        package = DottedName(package_name)
        packages_provided = [DottedName(name) for name in provided_names]

        if package not in self._all_requirements():
            logger.info(
                'Ignoring package %s as is not a dependency of the '
                'package being analyzed',
                package,
            )
            return

        self.user_mappings[package] = set(packages_provided)

        for single_package in packages_provided:
            self.reverse_user_mappings[single_package] = package

    def add_ignored_packages(self, packages):
        self.ignored_packages = {DottedName(package) for package in packages}

    def _all_requirements(self):
        all_requirements = self._requirements.copy()
        for extra in self._extras_requirements:
            all_requirements.update(self._extras_requirements[extra])

        return all_requirements

    def get_missing_imports(self):
        filters = (
            self._filter_out_testing_imports,
            self._filter_out_requirements,
            self._filter_out_ignored_imports,
        )
        missing = self._apply_filters(self.imports_used, filters)
        unique_imports = self._get_unique_imports(imports_list=missing)
        result = self._filter_user_mappings(unique_imports)
        return result

    def get_missing_test_imports(self):
        filters = (
            self._filter_out_only_testing_imports,
            self._filter_out_requirements,
            self._filter_out_test_requirements,
            self._filter_out_ignored_imports,
        )
        missing = self._apply_filters(self.imports_used, filters)
        unique_imports = self._get_unique_imports(imports_list=missing)
        result = self._filter_user_mappings(unique_imports)
        return result

    def get_unneeded_requirements(self):
        all_but_test_requirements = self._requirements.copy()
        for extra in self._extras_requirements:
            all_but_test_requirements.update(self._extras_requirements[extra])
        test_requirements = self._get_test_extra()
        for dotted_name in test_requirements:
            all_but_test_requirements.remove(dotted_name)
        filters = (
            self._filter_out_known_packages,
            self._filter_out_python_standard_library,
            self._filter_out_used_imports,
            self._filter_out_ignored_imports,
            self._filter_out_mappings,
        )
        unneeded = self._apply_filters(all_but_test_requirements, filters)
        unique_imports = self._get_unique_imports(imports_list=unneeded)
        return unique_imports

    def requirements_that_should_be_test_requirements(self):
        non_testing_filters = (self._filter_out_testing_imports,)
        non_testing_imports = self._apply_filters(
            self.imports_used,
            non_testing_filters,
        )
        complete_non_testing_imports = []
        for non_test_import in non_testing_imports:
            if non_test_import in self.reverse_user_mappings:
                meta_package = self.reverse_user_mappings[non_test_import]
                complete_non_testing_imports.append(meta_package)
                continue
            complete_non_testing_imports.append(non_test_import)

        requirements_not_used = [
            requirement
            for requirement in self._requirements
            if self._discard_if_found_obj_in_list(
                requirement,
                complete_non_testing_imports,
            )
        ]
        testing_filters = (
            self._filter_out_only_testing_imports,
            self._filter_out_own_package,
        )
        testing_imports = self._apply_filters(
            self.imports_used,
            testing_filters,
        )
        complete_test_imports = []
        for test_import in testing_imports:
            if test_import in self.reverse_user_mappings:
                meta_package = self.reverse_user_mappings[test_import]
                complete_test_imports.append(meta_package)
                continue
            complete_test_imports.append(test_import)
        should_be_test_requirements = [
            requirement
            for requirement in requirements_not_used
            if not self._discard_if_found_obj_in_list(
                requirement,
                complete_test_imports,
            )
        ]
        filters = (self._filter_out_ignored_imports,)
        skip_ignored = self._apply_filters(
            should_be_test_requirements,
            filters,
        )
        unique = self._get_unique_imports(imports_list=skip_ignored)
        return unique

    def get_unneeded_test_requirements(self):
        test_requirements = self._get_test_extra()
        if not test_requirements:
            return []

        filters = (
            self._filter_out_known_packages,
            self._filter_out_python_standard_library,
            self._filter_out_used_imports,
            self._filter_out_ignored_imports,
            self._filter_out_mappings_on_test,
        )
        unneeded = self._apply_filters(test_requirements, filters)
        unique_imports = self._get_unique_imports(imports_list=unneeded)
        return unique_imports

    @staticmethod
    def _apply_filters(objects, filters):
        """Filter a list of given objects through a list of given filters

        This helps encapsulating the filtering logic here while keeping the
        methods free from this clutter.

        Callees of this method need to provide a list of objects
        (usually a list of DottedNames) that will be processed by the provided
        list of filters.

        A filter, in this context, is a function that takes a DottedName as a
        single argument and returns a boolean value.

        If a given DottedName returns True in all filters,
        it will make it to the final result an be returned back.
        """
        result = []
        for single_object in objects:
            for filter_func in filters:
                if not filter_func(single_object):
                    break
            else:
                result.append(single_object)

        return result

    def _get_unique_imports(self, imports_list=None):
        if imports_list is None:
            imports_list = self.imports_used
        unique_dotted_names = list(set(imports_list))
        sorted_unique_dotted_names = sorted(unique_dotted_names)
        return sorted_unique_dotted_names

    def _filter_out_used_imports(self, dotted_name):
        return self._discard_if_found_obj_in_list(
            dotted_name,
            self.imports_used,
        )

    def _filter_out_mappings(self, meta_package):
        """Filter meta packages

        If it is not a meta package, let it continue the filtering.

        If it is a meta package, check if any of the packages it provides is
        used. If any of them it is, then filter it.
        """
        if meta_package not in self.user_mappings.keys():
            return True

        for dotted_name in self.user_mappings[meta_package]:
            if not self._discard_if_found_obj_in_list(dotted_name, self.imports_used):
                return False

        return True

    def _filter_out_mappings_on_test(self, meta_package):
        """Filter meta packages

        If it is not a meta package, let it continue the filtering.

        If it is a meta package, check if any of the packages it provides is
        used. If any of them it is, then filter it.
        """
        if meta_package not in self.user_mappings.keys():
            return True

        filters = (self._filter_out_only_testing_imports,)
        test_only_imports = self._apply_filters(self.imports_used, filters)

        for dotted_name in self.user_mappings[meta_package]:
            if not self._discard_if_found_obj_in_list(dotted_name, test_only_imports):
                return False

        return True

    def _filter_out_ignored_imports(self, dotted_name):
        return self._discard_if_found_obj_in_list(
            dotted_name,
            self.ignored_packages,
        )

    def _filter_out_known_packages(self, dotted_name):
        to_ignore = (
            DottedName('setuptools'),
            DottedName('pkg_resources'),
            DottedName('distribute'),
        )
        return self._discard_if_found_obj_in_list(dotted_name, to_ignore)

    @staticmethod
    def _filter_out_testing_imports(dotted_name):
        return not dotted_name.is_test

    @staticmethod
    def _filter_out_only_testing_imports(dotted_name):
        return dotted_name.is_test

    def _filter_out_own_package(self, dotted_name):
        return dotted_name not in self.own_dotted_name

    def _filter_out_requirements(self, dotted_name):
        return self._discard_if_found_obj_in_list(
            dotted_name,
            self._requirements,
        )

    def _filter_out_test_requirements(self, dotted_name):
        test_requirements = self._get_test_extra()
        if not test_requirements:
            return True

        return self._discard_if_found_obj_in_list(
            dotted_name,
            test_requirements,
        )

    def _filter_out_python_standard_library(self, dotted_name):
        std_library = self._build_std_library()
        return self._discard_if_found_obj_in_list(dotted_name, std_library)

    @staticmethod
    def _discard_if_found_obj_in_list(obj, obj_list):
        """Check if obj is on obj_list and return the opposite

        We are interested in filtering out requirements,
        so if a given object is on a given list,
        that object can be discarded as it's already in the list.
        """
        # this is a generator expression, nothing is computed until it is being
        # called some lines below
        iterable = (item for item in obj_list if obj in item)

        # any builtin stops consuming the iterator as soon as an element of the
        # iterable is True
        if any(iterable):
            # if 'obj' is found, the pipeline needs to stop and discard the
            # requirement
            return False

        # 'obj' was not found on the list, means that is fulfilling the
        # pipeline filters so far
        return True

    @staticmethod
    def _build_std_library():
        if PY_10_OR_HIGHER:
            # see https://github.com/jackmaney/python-stdlib-list/issues/55
            libraries = list(
                set(list(sys.stdlib_module_names) + list(sys.builtin_module_names))
            )
        else:
            from stdlib_list import stdlib_list

            python_version = sys.version_info
            libraries = stdlib_list(
                '{}.{}'.format(
                    python_version[0],
                    python_version[1],
                )
            )

        fake_std_libraries = [DottedName(x) for x in libraries]
        return fake_std_libraries

    def _get_test_extra(self):
        candidates = ('test', 'tests')
        for candidate in candidates:
            if candidate in self._extras_requirements:
                return self._extras_requirements[candidate]

        return []

    def _filter_user_mappings(self, dotted_names):
        """Remove dotted names that are in user mappings"""
        result = []
        for single_import in dotted_names:
            for provided_package in self.reverse_user_mappings:
                if single_import in provided_package:
                    logger.debug(
                        'Skip %s as is part of user mapping %s',
                        single_import,
                        self.reverse_user_mappings[provided_package],
                    )
                    break
            else:
                result.append(single_import)

        return result

# -*- coding: utf-8 -*-
from stdlib_list import stdlib_list
from z3c.dependencychecker.dotted_name import DottedName
import logging
import sys


logger = logging.getLogger(__name__)


class ImportsDatabase(object):
    """Store all imports and requirements of a package

    Use that information to extract useful data out of it,
    like requirements unused, etc.
    """

    def __init__(self):
        self._requirements = set()
        self._extras_requirements = {}
        self.imports_used = []
        self.own_dotted_name = None

    def add_requirements(self, requirements):
        self._requirements = set([
            requirement for requirement in requirements
        ])

    def add_extra_requirements(self, extra_name, dotted_names):
        # A bit of extra work needs to be done as pkg_resources API returns
        # all common requirements as well as the extras when asking for an
        # extra requirements.
        only_extra_dotted_names = self._filter_duplicates(dotted_names)
        if extra_name in self._extras_requirements.keys():
            self._extras_requirements[extra_name].update(
                only_extra_dotted_names,
            )

            logger.warn(
                'extra requirement "%s" is declared twice on setup.py',
                extra_name,
            )
        else:
            self._extras_requirements[extra_name] = only_extra_dotted_names

    def _filter_duplicates(self, imports):
        """Return all items in imports that are not a requirement already"""
        all_imports = set([dotted_name for dotted_name in imports])
        filtered = all_imports - self._requirements
        return filtered

    def add_imports(self, imports):
        for single_import in imports:
            self.imports_used.append(single_import)

    def get_missing_imports(self):
        filters = (
            self._filter_out_known_packages,
            self._filter_out_testing_imports,
            self._filter_out_own_package,
            self._filter_out_requirements,
            self._filter_out_python_standard_library,
        )
        missing = self._apply_filters(self.imports_used, filters)
        unique_imports = self._get_unique_imports(imports_list=missing)
        return unique_imports

    def get_missing_test_imports(self):
        filters = (
            self._filter_out_known_packages,
            self._filter_out_only_testing_imports,
            self._filter_out_own_package,
            self._filter_out_requirements,
            self._filter_out_test_requirements,
            self._filter_out_python_standard_library,
        )
        missing = self._apply_filters(self.imports_used, filters)
        unique_imports = self._get_unique_imports(imports_list=missing)
        return unique_imports

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
        )
        unneeded = self._apply_filters(all_but_test_requirements, filters)
        unique_imports = self._get_unique_imports(imports_list=unneeded)
        return unique_imports

    def get_unneeded_test_requirements(self):
        test_requirements = self._get_test_extra()
        if not test_requirements:
            return []

        filters = (
            self._filter_out_known_packages,
            self._filter_out_python_standard_library,
            self._filter_out_used_imports,
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
        iterable = (
            item
            for item in obj_list
            if obj in item
        )

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
        python_version = sys.version_info
        libraries = stdlib_list(
            '{0}.{1}'.format(
                python_version[0],
                python_version[1],
            )
        )

        fake_std_libraries = [DottedName(x) for x in libraries]
        return fake_std_libraries

    def _get_test_extra(self):
        candidates = ('test', 'tests', )
        for candidate in candidates:
            if candidate in self._extras_requirements:
                return self._extras_requirements[candidate]

        return []

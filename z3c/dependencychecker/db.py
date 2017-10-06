# -*- coding: utf-8 -*-
import logging


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

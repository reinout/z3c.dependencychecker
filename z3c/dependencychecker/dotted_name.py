# -*- coding: utf-8 -*-
from functools import total_ordering


@total_ordering
class DottedName(object):

    def __init__(
        self,
        name,
        file_path=None,
        line_number=None,
        is_test=False,
    ):
        self.name = name
        self.safe_name = self._get_safe_name(name)
        self.namespaces = self._get_namespaces(self.safe_name)
        self.is_namespaced = self._is_namespaced(self.namespaces)
        self.file_path = file_path
        self.is_test = is_test

    @classmethod
    def from_requirement(cls, requirement, file_path=None):
        """A requirement in this method's context is a
        pkg_resources.Requirement
        """
        return cls(
            requirement.project_name,
            file_path=file_path,
        )

    @staticmethod
    def _get_safe_name(name):
        safe_name = name.lower().replace('-', '_')
        return safe_name

    @staticmethod
    def _get_namespaces(safe_name):
        parts = safe_name.split('.')
        return parts

    @staticmethod
    def _is_namespaced(namespaces):
        return bool(len(namespaces) - 1)

    def __lt__(self, other):
        if not isinstance(other, DottedName):
            return NotImplemented
        return self.name < other.name

    def __eq__(self, other):
        if not isinstance(other, DottedName):
            return NotImplemented

        return self.safe_name == other.safe_name

    def __repr__(self):
        return '<DottedName {0}>'.format(self.name)

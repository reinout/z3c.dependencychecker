# -*- coding: utf-8 -*-


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

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

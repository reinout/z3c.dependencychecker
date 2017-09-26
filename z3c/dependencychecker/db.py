# -*- coding: utf-8 -*-


class ImportsDatabase(object):
    """Store all imports and requirements of a package

    Use that information to extract useful data out of it,
    like requirements unused, etc.
    """

    def __init__(self):
        self._requirements = set()

    def add_requirements(self, requirements):
        self._requirements = set([
            requirement for requirement in requirements
        ])

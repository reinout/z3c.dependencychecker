# -*- coding: utf-8 -*-


class Report(object):

    def __init__(self, package):
        self._database = package.imports

    def __call__(self):
        self.missing_requirements()
        self.missing_test_requirements()
        self.unneeded_requirements()

    def missing_requirements(self):
        self._print_metric(
            'Missing requirements',
            self._database.get_missing_imports,
        )

    def missing_test_requirements(self):
        self._print_metric(
            'Missing test requirements',
            self._database.get_missing_test_imports,
        )

    def unneeded_requirements(self):
        self._print_metric(
            'Unneeded requirements',
            self._database.get_unneeded_requirements,
        )

    def _print_metric(self, title, method):
        missed = method()
        if len(missed) == 0:
            return

        self._print_header(title)
        for dotted_name in missed:
            print('     {0}'.format(dotted_name.name))

    @staticmethod
    def _print_header(message):
        if message:
            print('')
            print(message)
            print('=' * len(message))

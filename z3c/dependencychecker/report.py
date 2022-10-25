import logging

logger = logging.getLogger(__name__)


class Report:
    def __init__(self, package):
        self._database = package.imports
        self.exit_status = 0

    def print_report(self):
        logger.debug('Package requirements: %s', self._database._requirements)
        logger.debug('Package extras: %s', self._database._extras_requirements)
        logger.debug(
            'User defined mappings: %s',
            self._database.user_mappings,
        )
        self.missing_requirements()
        self.missing_test_requirements()
        self.unneeded_requirements()
        self.requirements_that_should_be_test_requirements()
        self.unneeded_test_requirements()
        self.print_notice()

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

    def requirements_that_should_be_test_requirements(self):
        self._print_metric(
            'Requirements that should be test requirements',
            self._database.requirements_that_should_be_test_requirements,
        )

    def unneeded_test_requirements(self):
        self._print_metric(
            'Unneeded test requirements',
            self._database.get_unneeded_test_requirements,
        )

    @staticmethod
    def print_notice():
        print('')
        print('Note: requirements are taken from the egginfo dir, so you need')
        print('to re-run buildout (or setup.py or whatever) for changes in')
        print('setup.py to have effect.')
        print('')

    def _print_metric(self, title, method):
        missed = method()
        if len(missed) == 0:
            return

        self.exit_status = 1

        self._print_header(title)
        for dotted_name in missed:
            print(f'     {dotted_name.name}')

    @staticmethod
    def _print_header(message):
        if message:
            print('')
            print(message)
            print('=' * len(message))

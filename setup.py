from setuptools import setup, find_packages
import os.path

version = '1.16'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open(os.path.join('z3c', 'dependencychecker', 'USAGE.rst')).read(),
    open('TODO.rst').read(),
    open('CHANGES.rst').read(),
    ])

setup(name='z3c.dependencychecker',
      version=version,
      description="""Checks which imports are done and compares them to what's
      in setup.py and warns when discovering missing or unneeded
      dependencies.""",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='https://github.com/reinout/z3c.dependencychecker',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          ],
      extras_require = {
          'test': [
              'z3c.testsetup>=0.3',
              'zope.testing',
              ],
          },
      entry_points={
          'console_scripts':
          ['dependencychecker = z3c.dependencychecker.dependencychecker:main'
           ]},
      )

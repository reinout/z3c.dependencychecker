from setuptools import setup, find_packages
import os.path

version = '1.2dev'

long_description = '\n\n'.join([
    open('README.txt').read(),
    open(os.path.join('src', 'z3c', 'dependencychecker', 'USAGE.txt')).read(),
    open('TODO.txt').read(),
    open('CHANGES.txt').read(),
    ])

setup(name='z3c.dependencychecker',
      version=version,
      description="",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='The Health Agency',
      author_email='techniek@thehealthagency.com',
      url='http://www.thehealthagency.com',
      license='ZPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
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

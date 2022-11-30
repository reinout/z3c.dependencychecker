import codecs
import os.path

from setuptools import find_packages, setup

version = '2.8'


def read(filename):
    try:
        with codecs.open(filename, encoding='utf-8') as f:
            return unicode(f.read())
    except NameError:
        with open(filename, encoding='utf-8') as f:
            return f.read()


long_description = f"""
{read('README.rst')}

{read(os.path.join('z3c', 'dependencychecker', 'USAGE.rst'))}

{read('CHANGES.rst')}
"""


setup(
    name='z3c.dependencychecker',
    version=version,
    description='Reports on missing or unneeded setup.py dependencies',
    long_description=long_description,
    long_description_content_type='text/x-rst; charset=UTF-8',
    # Get strings from https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Quality Assurance',
    ],
    keywords='dependencies requirements missing imports',
    author='Reinout van Rees',
    author_email='reinout@vanrees.org',
    url='https://github.com/reinout/z3c.dependencychecker',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['z3c'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'stdlib-list; python_version < "3.10"',
        'cached-property',
        'toml',
    ],
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'dependencychecker = z3c.dependencychecker.main:main',
        ]
    },
)

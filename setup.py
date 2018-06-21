from setuptools import setup, find_packages
import os.path

version = '2.3'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open(os.path.join('z3c', 'dependencychecker', 'USAGE.rst')).read(),
    open('CHANGES.rst').read(),
    ])

description = """
Checks which imports are done and compares them to what's
in setup.py and warns when discovering missing or unneeded
dependencies.
"""

setup(
    name='z3c.dependencychecker',
    version=version,
    description=description,
    long_description=long_description,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Quality Assurance',
    ],
    keywords=[
        'dependencies',
        'requirements',
        'missing',
        'imports',
    ],
    author='Reinout van Rees',
    author_email='reinout@vanrees.org',
    url='https://github.com/reinout/z3c.dependencychecker',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', ]),
    namespace_packages=['z3c', ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'stdlib-list',
        'cached-property',
        'toml',
    ],
    extras_require={
        'test': [
            'pytest',
            'mock',
        ],
    },
    entry_points={
        'console_scripts': [
            'dependencychecker = z3c.dependencychecker.main:main',
        ]
    },
)

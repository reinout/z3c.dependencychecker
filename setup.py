from setuptools import find_packages
from setuptools import setup
import codecs
import os.path


version = '2.6'


def read(filename):
    try:
        with codecs.open(filename, encoding='utf-8') as f:
            return unicode(f.read())
    except NameError:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()



long_description = u'\n\n'.join([
    read('README.rst'),
    read(os.path.join('z3c', 'dependencychecker', 'USAGE.rst')),
    read('CHANGES.rst'),
    ])


setup(
    name='z3c.dependencychecker',
    version=version,
    description="Reports on missing or unneeded setup.py dependencies",
    long_description=long_description,
    long_description_content_type='text/x-rst; charset=UTF-8',
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
    keywords='dependencies requirements missing imports',
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

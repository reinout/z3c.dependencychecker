from pathlib import Path
from setuptools import setup


version = "3.1.dev0"


long_description = f"""
{Path('README.md').read_text()}

{Path('CHANGES.md').read_text()}
"""


setup(
    name="z3c.dependencychecker",
    version=version,
    description="Reports on missing or unneeded python dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Get strings from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords="dependencies requirements missing imports",
    author="Reinout van Rees",
    author_email="reinout@vanrees.org",
    url="https://github.com/reinout/z3c.dependencychecker",
    license="BSD",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.11",
    install_requires=[
        "setuptools",
        "cached-property",
        "toml",
        "wheel-inspect",
    ],
    extras_require={
        "test": ["pytest", "pytest-mock"],
    },
    entry_points={
        "console_scripts": [
            "dependencychecker = z3c.dependencychecker.main:main",
        ]
    },
)

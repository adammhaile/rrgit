# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('./requirements.txt') as f:
    INSTALL_REQUIRES = f.read().splitlines()


def _get_version():
    from os.path import abspath, dirname, join
    filename = join(dirname(abspath(__file__)), 'rrgit', 'VERSION')
    return open(filename).read().strip()


setup(
    name="rrgit",
    author="Adam Haile",
    author_email="adammhaile@gmail.com",
    version=_get_version(),
    description="CLI tool for syncing files to and from RepRapFirmware 3 via the web API",
    long_description=open('README.md').read(),
    url="https://github.com/adammhaile/rrgit",
    license="GNU General Public License v3 (GPLv3)",
    packages=find_packages(exclude=[]),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'rrgit = rrgit.cli:main'
        ]
    },
    install_requires=INSTALL_REQUIRES,
    dependency_links=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Environment :: Console",
        "Operating System :: POSIX",
        "License :: OSI Approved :: License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
    ]
)
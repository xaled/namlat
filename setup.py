#!/usr/bin/env python3

from distutils.core import setup

import os

with open("namlat/VERSION") as fin:
    VERSION = fin.read()


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if not path.endswith('__pycache__') and not filename.endswith(".pyc"):
                paths.append(os.path.relpath(os.path.join(path, filename), directory))
    return paths


extra_files = package_files('namlat/')

# print extra_files

setup(
    name='namlat',
    version=VERSION,
    # major.minor.fix: MAJOR incompatible API changes, MINOR add backwards-compatible functionality, FIX bug fixes
    description='Distributed Monitoring and Reporting.',
    long_description='Distributed Monitoring and Reporting.',
    long_description_content_type='text/rst',
    keywords='distributed monitoring reporting',
    author='Khalid Grandi',
    author_email='kh.grandi@gmail.com',
    license='GPL3',
    url='https://github.com/xaled/namlat/',
    install_requires=['requests', 'pycrypto', 'flask', 'jinja2', 'xaled_utils', 'bbcode'],
    python_requires='>=3',
    packages=['namlat'],
    package_data={'': extra_files},
    entry_points={
        'console_scripts': ['namlat = namlat.main:main'],
    }
)

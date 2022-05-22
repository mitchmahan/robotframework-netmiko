#!/usr/bin/env python3

import os
from setuptools import setup

# fill about dict from src/__version__.py
about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'src', '__version__.py')) as f:
    exec(f.read(), about)

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name=about['__title__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    package_dir={'': 'src'},
    package_data={
        'NetmikoLib': ['templates/*.*']
    },
    packages=['NetmikoLib'],
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        'robotframework',
        'netmiko',
        'pyyaml',
        'ttp',
        'jinja2'
    ],
    license=about['__license__'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 0.1 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    keywords='robotframework netmiko'
)

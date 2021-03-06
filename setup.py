#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = open('requirements.txt').readlines()

test_requirements = [
    line for line in open('requirements-dev.txt').readlines()
    if not line.startswith('-')
]

setup(
    name='mockingjay',
    version='0.2.0',
    description="A simple library to build mock http services based on HTTPretty",
    long_description=readme + '\n\n' + history,
    author="Kevin J. Qiu",
    author_email='kevin@idempotent.ca',
    url='https://github.com/kevinjqiu/mockingjay',
    packages=[
        'mockingjay',
    ],
    package_dir={'mockingjay':
                 'mockingjay'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='mockingjay',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)

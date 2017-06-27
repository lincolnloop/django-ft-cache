#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command

version = '1.0.0'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-ft-cache',
    version=version,
    description="""A fault-tolerant pylibmc cache backend for Django""",
    long_description=readme + '\n\n' + history,
    author='Peter Baumgartner',
    author_email='pete@lincolnloop.com',
    url='https://github.com/lincolnloop/django-ft-cache',
    py_modules=['django_ft_cache'],
    cmdclass = {'test': PyTest},
    include_package_data=True,
    extras_require={'test': [
        "Django",
        "pylibmc>=1.3.0"
    ]},
    license="BSD",
    keywords='django-ft-cache',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

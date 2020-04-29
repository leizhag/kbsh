from kubeshell import __version__
from setuptools import setup, find_packages

import sys

version = sys.version_info
error_msg = "kube-shell needs Python>=2.7.10. Found %s" % sys.version

if version.major == 2:
    if version.minor < 7:
        sys.exit(error_msg)
    else:
        if version.micro < 10:
            sys.exit(error_msg)


requires = [
    'prompt-toolkit==2.0.2',
    'Pygments>=2.1.3,<3.0.0',
    'fuzzyfinder>=1.0.0',
    'click>=4.0,<7.0',
    'kubernetes>=0.10.0,<3.0.0',
]

setup(
    name='kbsh',
    version=__version__,
    description='An integrated shell for working effectively with multiple Kubernetes clusters',
    long_description=open('README.rst').read(),
    author='Lei Zhang',
    url='https://github.com/leizhag/kbsh',
    packages=find_packages(),
    package_data={'kubeshell': ['data/cli.json']},
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'kbsh = kubeshell.main:cli',
        ]
    },
    license="Apache License 2.0",
    keywords=('kubernetes', 'autocomplete', 'shell',),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ),
)

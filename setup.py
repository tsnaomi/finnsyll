# coding=utf-8

import os

from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='FinnSyll',
    version='1.0.dev1',
    description='Finnish syllabifier and compound segmenter',
    long_description=read('README.md'),
    url='https://github.com/tsnaomi/finnsyll',
    author='Naomi Tachikawa Shapiro',
    author_email='coder@tsnaomi.net',
    license='BSD',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    keywords='Finnish syllabifier compound segmenter',
    packages=['finnsyll', ],
    install_requires=['morfessor', ],
)

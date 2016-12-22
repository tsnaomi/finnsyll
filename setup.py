# coding=utf-8

from ez_setup import use_setuptools
from os.path import dirname, join
from setuptools import setup

use_setuptools()


def read(filename):
    return open(join(dirname(__file__), filename)).read()

setup(
    name='FinnSyll',
    version='1.0.3',
    description='Finnish syllabifier and compound segmenter',
    long_description=read('README.rst'),
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
    include_package_data=True,
    package_data={'finnsyll': ['data/*'], },
    install_requires=['morfessor', ],
)

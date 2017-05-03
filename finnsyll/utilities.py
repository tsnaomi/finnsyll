# coding=utf-8
from __future__ import unicode_literals

import re
import sys

FLAGS = re.U | re.I

A = r'a-zäö`̈'  # alphabetic characters

# Python 2
if sys.version_info < (3, ):
    A += r'\xc3\xa4\xcc\x88'


def nonalpha_split(string):
    '''Split 'string' along any punctuation or whitespace.'''
    return re.findall(r'[%s]+|[^%s]+' % (A, A), string, flags=FLAGS)


def syllable_split(string):
    '''Split 'string' into syllables and punctuation/whitespace.'''
    return re.findall(r'[%s]+|[^%s\.]+' % (A, A), string, flags=FLAGS)


def extract_words(string):
    '''Extract all alphabetic syllabified forms from 'string'.'''
    return re.findall(r'[%s]+[%s\.]*[%s]+' % (A, A, A), string, flags=FLAGS)

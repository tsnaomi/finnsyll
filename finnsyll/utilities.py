# coding=utf-8
import re

FLAGS = re.I | re.U


def nonalpha_split(string):
    '''Split 'string' along any punctuation or whitespace.'''
    return re.split(
        r'([\s0-9!#$%&*+,.:;<=>?@^_`{}|~\/\\\-\"\'\(\)\[\]]+)',
        string,
        flags=FLAGS,
        )


def extract_words(string):
    '''Extract all alphabetic forms from 'string' and return them as a list.'''
    return re.split(
        r'[\s0-9!#$%&*+,:;<=>?@^_`{}|~\/\\\-\"\'\(\)\[\]]+',
        string,
        flags=FLAGS,
        )

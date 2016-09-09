# coding=utf-8

import re

# Finnish phones --------------------------------------------------------------

# Finnish vowels
VOWELS = ['i', 'e', 'A', 'y', 'O', 'a', 'u', 'o']
# ä is replaced by A
# ö is replaced by O


# Finnish diphthongs
DIPHTHONGS = [
    'ai', 'ei', 'oi', 'Ai', 'Oi', 'au', 'eu', 'ou', 'ey', 'Ay',
    'Oy', 'ui', 'yi', 'iu', 'iy', 'ie', 'uo', 'yO', 'oy']


# Finnish consonants
CONSONANTS = [
    'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p',
    'q', 'r', 's', 't', 'v', 'x', 'z', "'"]


# Finnish consonant clusters (see Karlsson 1985, #4)
CLUSTERS = [
    'bl', 'br', 'dr', 'fl', 'fr', 'gl', 'gr', 'kl', 'kr', 'kv',
    'pl', 'pr', 'cl', 'qv', 'schm']


# Phonotactic functions -------------------------------------------------------

def is_vowel(ch):
    return ch in VOWELS


def is_consonant(ch):
    # return ch in CONSONANTS
    return not is_vowel(ch)  # includes 'w' and other foreign characters


def is_coronal(ch):
    # return ch in [u's', u'z', u'd', u't', u'r', u'n', u'l']
    return ch in ['s', 't', 'r', 'n', 'l']  # Suomi et al. 2008


def is_sonorant(ch):
    return ch in ['m', 'n', 'l', 'r']


def is_cluster(ch):
    return ch in CLUSTERS


def is_diphthong(chars):
    return chars in DIPHTHONGS


def is_long(chars):
    return chars == chars[0] * len(chars)


# Linguistic constraints ------------------------------------------------------

word_final_inventory = [
    'i', 'e', 'A', 'y', 'O', 'a', 'u', 'o',  # vowels
    'l', 'n', 'r', 's', 't']  # coronal consonants

onsets_inventory = [
    'pl', 'pr', 'tr', 'kl', 'kr', 'sp', 'st', 'sk', 'ps', 'ts',
    'sn', 'dr', 'spr', 'str']

codas_inventory = ['ps', 'ts', 'ks']


def min_word(word):
    # check if the segment contains more than one vowel to allow binary footing
    return len(list(filter(is_vowel, word))) > 1


def sonseq(word):
    parts = re.split(r'([ieAyOauo]+)', word)
    onset, coda = parts[0], parts[-1]

    #  simplex onset      Finnish complex onset
    if len(onset) <= 1 or onset in onsets_inventory:
        #      simplex coda    Finnish complex coda
        return len(coda) <= 1  # or coda in codas_inventory

    return False


def word_final(word):
    # check if the word ends in a coronal consonant
    return word[-1] in word_final_inventory


def harmonic(word):
    FRONT_VOWELS = ['A', 'y', 'O']

    BACK_VOWELS = ['a', 'u', 'o']

    NEUTRAL_VOWELS = ['e', 'i']

    DEPTH = {
        'A': 'front',
        'y': 'front',
        'O': 'front',
        'a': 'back',
        'u': 'back',
        'o': 'back',
        }

    def is_front(ch):
        return ch in FRONT_VOWELS

    def is_back(ch):
        return ch in BACK_VOWELS

    def is_neutral(ch):
        return ch in NEUTRAL_VOWELS

    # check if the vowels agree in front/back harmony
    vowels = list(filter(is_vowel, [ch for ch in word]))
    vowels = [x for x in vowels if not is_neutral(x)]
    depths = [DEPTH[x] for x in vowels]

    return len(set(depths)) < 2


class Constraint:

    def __init__(self, name, test, weight=0.0):
        self.name = name
        self.test = test
        self.weight = weight

    def __str__(self):
        if self.weight:
            return '%s=%s' % (self.name, self.weight)

        return self.name

    def __repr__(self):
        return self.__str__()

# unranked constraints
CONSTRAINTS = [
    Constraint('MnWrd', min_word),
    Constraint('SonSeq', sonseq),
    Constraint('Word#', word_final),
    Constraint('Harmonic', harmonic),
    ]


# Normalization functions -----------------------------------------------------

def replace_umlauts(word, put_back=False):  # use translate()
    '''If put_back is True, put in umlauts; else, take them out!'''
    if put_back:
        word = word.replace('A', 'ä').replace('A', '\xc3\xa4')
        word = word.replace('O', 'ö').replace('O', '\xc3\xb6')

    else:
        word = word.replace('ä', 'A').replace('\xc3\xa4', 'A')
        word = word.replace('ö', 'O').replace('\xc3\xb6', 'O')

    return word

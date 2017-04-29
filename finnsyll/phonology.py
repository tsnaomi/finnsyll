# coding=utf-8
from __future__ import unicode_literals
from .utilities import FLAGS

import re


# Finnish phones --------------------------------------------------------------

# Finnish vowels
VOWELS = 'ieaouäöy'

# Finnish phonemic inventory
PHONEMIC_INVENTORY = VOWELS + 'dhjklmnprstv -='

# Finnish diphthongs
DIPHTHONGS = [
    'ai', 'ei', 'oi', 'äi', 'öi', 'ui', 'yi',  # i-final
    'au', 'eu', 'ou', 'iu', 'ey', 'äy', 'öy', 'iy',  # u/y-final
    # 'ie', 'uo', 'yö',  # tail
    'ay', 'oy', 'uy',  # loanword
    ]

# Finnish consonant clusters (see Karlsson 1985, #4)
CLUSTERS = [
    'bl', 'br', 'dr', 'fl', 'fr', 'gl', 'gr', 'kl', 'kr', 'kv',
    'pl', 'pr', 'cl', 'qv', 'schm',
    ]

# Finnish onsets
ONSETS = [
    'pl', 'pr', 'tr', 'kl', 'kr', 'sp', 'st', 'sk', 'ps', 'ts',
    'sn', 'dr', 'spr', 'str',
    ]


# Phonotactic functions -------------------------------------------------------

def is_vowel(ch):
    '''Return True if 'ch' is a Finnish vowel.'''
    return ch.lower() in VOWELS


def is_diphthong(chars):
    '''Return True if 'chars' is a Finnish diphthong.'''
    return chars.lower() in DIPHTHONGS


def is_front(ch):
    '''Return True if 'ch' is a Finnish front vowel.'''
    return ch.lower() in 'äöy'


def is_back(ch):
    '''Return True if 'ch' is a Finnish back vowel.'''
    return ch.lower() in 'aou'


def is_long(chars):
    '''Return True if 'chars' is a long vowel or geminate.'''
    chars = chars.lower()

    return chars == chars[0] * len(chars)


def is_consonant(ch):
    '''Return True if 'ch' is a consonant.'''
    return not is_vowel(ch)  # includes 'w' and other foreign characters


def is_cluster(chars):
    '''Return True if 'chars' is a Finnish consonant cluster.'''
    return chars.lower() in CLUSTERS


def is_coronal(ch):
    '''Return True if 'ch' is a Finnish coronal consonant.'''
    return ch.lower() in 'lnrst'  # Suomi et al. 2008


def is_sonorant(ch):
    '''Return True if 'ch' is a Finnish sonorant consonant.'''
    return ch.lower() in 'lmnr'


# Annotation functions --------------------------------------------------------

def get_vowel(syll):
    '''Return the firstmost vowel in 'syll'.'''
    return re.search(r'([ieaouäöy]{1})', syll, flags=FLAGS).group(1).upper()


def get_weight(syll):
    '''Return the weight of 'syll'.'''
    return 'L' if is_light(syll) else 'H'


def is_light(syll):
    '''Return True if 'syll' is light.'''
    return re.match(r'(^|[^ieaouäöy]+)[ieaouäöy]{1}$', syll, flags=FLAGS)


def is_heavy(syll):
    '''Return True if 'syll' is heavy.'''
    return not is_light(syll)


def stress(syllabified_simplex_word):
    '''Assign primary and secondary stress to 'syllabified_simplex_word'.'''
    syllables = syllabified_simplex_word.split('.')
    stressed = '\'' + syllables[0]  # primary stress

    try:
        n = 0
        medial = syllables[1:-1]

        for i, syll in enumerate(medial):

            if (i + n) % 2 == 0:
                stressed += '.' + syll

            else:
                try:
                    if is_light(syll) and is_heavy(medial[i + 1]):
                        stressed += '.' + syll
                        n += 1
                        continue

                except IndexError:
                    pass

                # secondary stress
                stressed += '.`' + syll

    except IndexError:
        pass

    if len(syllables) > 1:
        stressed += '.' + syllables[-1]

    return stressed


# Linguistic constraints ------------------------------------------------------

def min_word(word):
    '''Return True if 'word' contains two or more vowels.

    A word should minimally contain two vowels to allow binary footing.
    '''
    return len(list(filter(is_vowel, word))) > 1


def sonseq(word):
    '''Return True if 'word' does not violate sonority sequencing.'''
    parts = re.split(r'([ieaouäöy]+)', word, flags=re.I | re.U)
    onset, coda = parts[0], parts[-1]

    #  simplex onset      Finnish complex onset
    if len(onset) <= 1 or onset.lower() in ONSETS:
        #      simplex coda    Finnish complex coda
        return len(coda) <= 1  # or coda in codas_inventory

    return False


def word_final(word):
    '''Return True if 'word' ends in a vowel or coronal consonant.'''
    return is_vowel(word[-1]) or is_coronal(word[-1])


def harmonic(word):
    '''Return True if the word's vowels agree in frontness/backness.'''
    depth = {'ä': 0, 'ö': 0, 'y': 0, 'a': 1, 'o': 1, 'u': 1}
    vowels = filter(lambda ch: is_front(ch) or is_back(ch), word)
    depths = (depth[x.lower()] for x in vowels)

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


# Foreign word detection ------------------------------------------------------

def is_foreign(word):
    '''Return True if 'word' is non-nativized to Finnish.'''
    return _has_foreign_characters(word) or _violates_constraint(word)


def _has_foreign_characters(word):
    # Finnish allows /d/ only word-medially
    phonemic_inventory = VOWELS + 'dhjklmnprstv -='
    word = word.lower()

    if word.startswith(('d')):
        return True

    foreign_chars = set(ch for ch in word if ch not in phonemic_inventory)

    # the letter 'g' indicates a foreign word unless it is preceded by an 'n',
    # in which case, their collective underlying form is /ŋ/, which does appear
    # in the Finnish phonemic inventory
    if set('g') == foreign_chars:
        return word.count('g') != word.count('ng')  # TEST

    return bool(foreign_chars)


def _violates_constraint(word):
    for constituent in re.split(r'-| |=', word):
        for costraint in [min_word, sonseq, word_final, harmonic]:
            if not costraint(constituent):
                return True

    return False


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # from timeit import timeit
    pass

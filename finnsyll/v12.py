# coding=utf-8

# First Python 3-compatible version.

import re

from itertools import product

try:
    from .phonology import (
        is_cluster,
        is_consonant,
        # is_diphthong,
        is_long,
        is_sonorant,
        # is_vowel,
        replace_umlauts,
        )

except (ImportError, ValueError):
    from phonology import (
        is_cluster,
        is_consonant,
        # is_diphthong,
        is_long,
        is_sonorant,
        # is_vowel,
        replace_umlauts,
        )

# This syllabifer departs from the earlier syllabifiers, allowing rules to
# remove previously inserted syllable boundaries (see T8).


# Phonology.py edits ----------------------------------------------------------

# Finnish diphthongs
DIPHTHONGS = [
    'ai', 'ei', 'oi', 'Ai', 'Oi', 'ui', 'yi',  # i-final diphthongs
    'au', 'eu', 'ou', 'iu', 'ey', 'Ay', 'Oy', 'iy',  # u/y-final diphthongs
    # 'ie', 'uo', 'yO',  # TAIL diphthongs
    'ay', 'oy', 'uy',  # loanword diphthongs
    ]


def is_diphthong(chars):
    return chars in DIPHTHONGS


# Syllabifier -----------------------------------------------------------------

def syllabify(word):
    '''Syllabify the given word, whether simplex or complex.'''
    compound = bool(re.search(r'(-| |=)', word))
    syllabify = _syllabify_compound if compound else _syllabify_simplex
    syllabifications = list(syllabify(word))

    for word, rules in rank(syllabifications):
        # post-process
        word = str(replace_umlauts(word, put_back=True))
        rules = rules[1:]

        yield word, rules


def _syllabify_compound(word):
    syllabifications = []

    # split the word along any delimiters (a hyphen, space, or equal sign) and
    # syllabify the individual parts separately
    for w in re.split(r'(-| |=)', word):
        sylls = [(w, ' ='), ] if w in '- =' else list(_syllabify_simplex(w))
        syllabifications.append(sylls)

    WORDS = [w for w in product(*syllabifications)]

    for WORD in WORDS:
        word = ''.join([w for w, r in WORD]).replace('=', '.')
        rules = ''.join([r for w, r in WORD])

        yield word, rules


def _syllabify_simplex(word):
    word, rules = T1(word)
    word, rules = T2(word, rules)
    word, rules = T8(word, rules)

    # T4 produces variation
    syllabifications = list(T4(word, rules))

    for word, rules in syllabifications:
        word, rules = T6(word, rules)
        word, rules = T11(word, rules)

        yield word, rules or ' T0'  # T0 means no rules have applied


# T1 --------------------------------------------------------------------------

def T1(word, T1E=True):  # TODO
    '''Insert a syllable boundary in front of every CV sequence.'''
    # split consonants and vowels: 'balloon' -> ['b', 'a', 'll', 'oo', 'n']
    WORD = [w for w in re.split('([ieAyOauo]+)', word) if w]

    # these are to keep track of which sub-rules are applying
    A, B, C, D, E, F, G = '', '', '', '', '', '', ''

    # a count divisible by 2 indicates an even syllable
    count = 1

    for i, v in enumerate(WORD):

        # T1B
        # If there is a consonant cluster word-initially, the entire cluster
        # forms the onset of the first syllable:
        # CCV > #CCV
        if i == 0 and is_consonant(v[0]):
            B = 'b'

        elif is_consonant(v[0]):
            count += 1

            # True if the current syllable is unstressed, else False
            unstressed = count % 2 == 0

            # T1C
            # If there is a consonant cluster word-finally, the entire cluster
            # forms the coda of the final syllable:
            # VCC# > VCC#
            if i + 1 == len(WORD):
                C = 'c'

            # T1D
            # If there is a bare "Finnish" consonant cluster word-medially and
            # the previous syllable receives stress, the first consonant of the
            # cluster forms the coda of the previous syllable (to create a
            # heavy syllable); otherwise, the whole cluster forms the onset of
            # the current syllable (this is the /kr/ rule):
            # 'VCCV > 'VC.CV,  VCCV > V.CCV
            elif is_cluster(v):
                D = 'd'
                WORD[i] = v[0] + '.' + v[1:] if unstressed else '.' + v

            elif is_cluster(v[1:]):

                # T1E (optional)
                # If there is a word-medial "Finnish" consonant cluster that is
                # preceded by a sonorant consonant, if the previous syllable
                # receives stress, the sonorant consonant and the first
                # consonant of the cluster form the coda of the previous
                # syllable, and the remainder of the cluster forms the onset of
                # the current syllable:
                # 'VlCC > VlC.C
                if T1E and is_sonorant(v[0]) and unstressed:
                    E = 'e'
                    WORD[i] = v[:2] + '.' + v[2:]

                # T1F
                # If there is a word-medial "Finnish" cluster that follows a
                # consonant, that first consonant forms the coda of the
                # previous syllable, and the cluster forms the onset of the
                # current syllable:
                # VCkr > VC.kr
                else:
                    F = 'f'
                    WORD[i] = v[0] + '.' + v[1:]

            # T1A
            # There is a syllable boundary in front of every CV sequence:
            # VCV > V.CV, CCV > C.CV
            else:
                WORD[i] = v[:-1] + '.' + v[-1]
                A = 'a'

    WORD = ''.join(WORD)
    # RULE = ' T1' + A + B + C + D + E + F + G if word != WORD else ''
    rules = ' T1' if word != WORD else ''

    return WORD, rules


# T2 --------------------------------------------------------------------------

def T2(word, rules):
    '''Split any VV sequence that is not a genuine diphthong or long vowel.
    E.g., [ta.e], [ko.et.taa]. This rule can apply within VVV+ sequences.'''
    WORD = word
    offset = 0

    for vv in vv_sequences(WORD):
        seq = vv.group(1)

        if not is_diphthong(seq) and not is_long(seq):
            i = vv.start(1) + 1 + offset
            WORD = WORD[:i] + '.' + WORD[i:]
            offset += 1

    rules += ' T2' if word != WORD else ''

    return WORD, rules

# T3 --------------------------------------------------------------------------

# Diphthongs that arise through Consonant Gradation may contain a syllable
# boundary. E.g. [ha.in] or [hain], [ho.it.te] or [hoit.te], [luim.me] or
# [lu.im.me].


# T4 --------------------------------------------------------------------------

def T4(word, rules):
    '''Optionally split /u,y/-final diphthongs that do not take primary stress.
    E.g., [lau.ka.us], [va.ka.ut.taa].'''
    pattern = r'([aAoOieuy]+[^aAoOieuy]+\.*[aAoOie]{1}(?:u|y)'
    pattern += r'(?:\.*[^aAoOieuy]+|$))'
    WORD = re.split(pattern, word)
    PARTS = [[] for part in range(len(WORD))]

    for i, v in enumerate(WORD):

        if i != 0:
            vv = u_y_final_diphthongs(v)

            if vv:
                I = vv.start(1) + 1
                PARTS[i].append(v[:I] + '.' + v[I:])

        # include original form (non-application of rule)
        PARTS[i].append(v)

    WORDS = [w for w in product(*PARTS)]

    for WORD in WORDS:
        WORD = ''.join(WORD)
        RULES = rules + ' T4' if word != WORD else rules

        yield WORD, RULES


# T6 --------------------------------------------------------------------------

def T6(word, rules):
    '''If a VVV-sequence contains a long vowel, insert a syllable boundary
    between it and the third vowel. E.g. [kor.ke.aa], [yh.ti.öön], [ruu.an],
    [mää.yt.te].'''
    WORD = word
    offset = 0

    for vvv in vvv_sequences(WORD):
        seq = vvv.group(2)
        j = 2 if is_long(seq[:2]) else 1 if is_long(seq[1:]) else 0

        if j:
            i = vvv.start(2) + j + offset
            WORD = WORD[:i] + '.' + WORD[i:]
            offset += 1

    rules += ' T6' if word != WORD else ''

    return WORD, rules


# T8 --------------------------------------------------------------------------

def T8(word, rules):
    '''Join /ie/, /uo/, or /yö/ sequences in syllables that take primary
    stress.'''
    WORD = word

    try:
        vv = tail_diphthongs(WORD)
        i = vv.start(1) + 1
        WORD = WORD[:i] + word[i + 1:]

    except AttributeError:
        pass

    rules += ' T8' if word != WORD else ''

    return WORD, rules


# T11 -------------------------------------------------------------------------

def T11(word, rules):
    '''If a VVV sequence contains a /u,y/-final diphthong, insert a syllable
    boundary between the diphthong and the third vowel.'''
    WORD = word
    offset = 0

    for vvv in g3_precedence_sequences(WORD):
        i = vvv.start(1) + (1 if vvv.group(1)[-1] in 'uy' else 2) + offset
        WORD = WORD[:i] + '.' + WORD[i:]
        offset += 1

    rules += ' T11' if word != WORD else ''

    return WORD, rules


# Sequences -------------------------------------------------------------------


def vv_sequences(word):
    # this pattern searches for (overlapping) VV sequences
    pattern = r'(?=([ieyuaAoO]{2}))'

    return re.finditer(pattern, word)


def vvv_sequences(word):
    # this pattern searches for any VVV sequence that is not directly preceded
    # or followed by a vowel
    pattern = r'(?=(^|\.)[^ieAyOauo]*([ieAyOauo]{3})[^ieAyOauo]*($|\.))'

    return re.finditer(pattern, word)


def tail_diphthongs(word):
    # this pattern searches for any /ie/, /uo/, or /yö/ sequences in the first
    # syllable that are not directly preceded or followed by vowels
    pattern = r'^[^aAoOeuyi]*(i\.e|u\.o|y\.O)(?:\.|[^aAoOeuyi]+|$)'

    return re.match(pattern, word)


def u_y_final_diphthongs(word):
    # this pattern searches for any /u,y/-final diphthong that does not appear
    # under primary stress

    # specifying the relevant diphthongs versus r'([eiaAoO]{1}(u|y)) prevents
    # unnecessary splitting of Vy and Vu loanword sequences that violate vowel
    # harmony (e.g., 'Friday')
    pattern = r'(?:[^aAoOieuy\.]+\.*)(au|eu|ou|iu|iy|ey|Ay|Oy)'
    pattern += r'(?:(\.*[^aAoOieuy\.]+|$))'

    return re.search(pattern, word)


def g3_precedence_sequences(word):
    # this pattern searches for any primary-stressed VVV sequence that contains
    # a /u,y/-final diphthong
    pattern = r'^[^ieAyOauo]*([aAoOie]{1}(au|eu|ou|iu|iy|ey|Ay|Oy)'
    pattern += r'|(au|eu|ou|iu|iy|ey|Ay|Oy)[aAoOie]{1})[^ieAyOauo]'

    return re.finditer(pattern, word)


# Ranking (TODO) --------------------------------------------------------------

def wsp(word):
    '''Return the number of unstressed heavy syllables.'''
    HEAVY = r'[ieaAoO]{1}[\.]*(u|y)[^ieaAoO]+(\.|$)'

    # # if the word is not monosyllabic, lop off the final syllable, which is
    # # extrametrical
    # if '.' in word:
    #     word = word[:word.rindex('.')]

    # gather the indices of syllable boundaries
    delimiters = [i for i, char in enumerate(word) if char == '.']

    if len(delimiters) % 2 != 0:
        delimiters.append(len(word))

    unstressed = []

    # gather the indices of unstressed positions
    for i, d in enumerate(delimiters):
        if i % 2 == 0:
            unstressed.extend(range(d + 1, delimiters[i + 1]))

    # find the number of unstressed heavy syllables
    heavies = re.finditer(HEAVY, word)
    violations = sum(1 for m in heavies if m.start(0) in unstressed)

    return violations


def pk_prom(word):
    '''Return the number of stressed light syllables.'''
    LIGHT = r'[ieaAoO]{1}[\.]*(u|y)(\.|$)'

    # # if the word is not monosyllabic, lop off the final syllable, which is
    # # extrametrical
    # if '.' in word:
    #     word = word[:word.rindex('.')]

    # gather the indices of syllable boundaries
    delimiters = [0, ] + [i for i, char in enumerate(word) if char == '.']

    if len(delimiters) % 2 != 0:
        delimiters.append(len(word))

    stressed = []

    # gather the indices of stressed positions
    for i, d in enumerate(delimiters):
        if i % 2 == 0:
            stressed.extend(range(d + 1, delimiters[i + 1]))

    # find the number of stressed light syllables
    heavies = re.finditer(LIGHT, word)
    violations = sum(1 for m in heavies if m.start(1) in stressed)

    return violations


def rank(syllabifications):
    '''Rank syllabifications.'''
    syllabifications.sort(key=lambda s: wsp(s[0]) + pk_prom(s[0]))

    return syllabifications


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    words = [
        # 'tyOpaikat',
        # 'donaueschingen',
        ]

    for word in words:
        for syll, rules in syllabify(word):
            print syll, rules

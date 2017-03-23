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
        is_vowel,
        replace_umlauts,
        )

except (ImportError, ValueError):
    from phonology import (
        is_cluster,
        is_consonant,
        # is_diphthong,
        is_long,
        is_sonorant,
        is_vowel,
        replace_umlauts,
        )

# This syllabifer departs from the earlier syllabifiers, allowing rules to
# remove previously inserted syllable boundaries (see T8).


# Phonology.py TODO -----------------------------------------------------------

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
    syllabify = _syllabify_complex if compound else _syllabify_simplex
    syllabifications = list(syllabify(word))

    # if variation, order variants from most preferred to least preferred
    if len(syllabifications) > 1:
        syllabifications = rank(syllabifications)

    for word, rules in syllabifications:
        yield _post_process(word, rules)


def _syllabify_complex(word):
    syllabifications = []

    # split the word along any delimiters (a hyphen, space, or equal sign) and
    # syllabify the individual parts separately
    for w in re.split(r'(-| |=)', word):
        sylls = [(w, ' ='), ] if w in '- =' else _syllabify_simplex(w)
        syllabifications.append(sylls)

    for x in (w for w in product(*syllabifications)):
        word, rules = '', ''

        for w, r in x:
            word += w
            rules += r

        yield word, rules


def _syllabify_simplex(word):
    word, rules = T1(word)
    word, rules = T2(word, rules)
    word, rules = T8(word, rules)

    for word, rules in T4(word, rules):  # T4 produces variation
        word, rules = T6(word, rules)
        word, rules = T11(word, rules)

        yield word, rules or ' T0'  # T0 means no rules have applied


def _post_process(word, rules):
    word = str(replace_umlauts(word, put_back=True)).replace('=', '.')
    rules = rules[1:]

    return word, rules


# T1 --------------------------------------------------------------------------

def T1(word, T1E=True):  # TODO
    '''Insert a syllable boundary in front of every CV sequence.'''
    # split consonants and vowels: 'balloon' -> ['b', 'a', 'll', 'oo', 'n']
    WORD = [w for w in re.split('([ieAyOauo]+)', word) if w]

    # keep track of which sub-rules are applying
    sub_rules = set()

    # a count divisible by 2 indicates an even syllable
    count = 1

    for i, v in enumerate(WORD):

        # T1B
        # If there is a consonant cluster word-initially, the entire cluster
        # forms the onset of the first syllable:
        # CCV > #CCV
        if i == 0 and is_consonant(v[0]):
            sub_rules.add('b')

        elif is_consonant(v[0]):
            count += 1

            # True if the current syllable is unstressed, else False
            unstressed = count % 2 == 0

            # T1C
            # If there is a consonant cluster word-finally, the entire cluster
            # forms the coda of the final syllable:
            # VCC# > VCC#
            if i + 1 == len(WORD):
                sub_rules.add('c')

            # T1D
            # If there is a bare "Finnish" consonant cluster word-medially and
            # the previous syllable receives stress, the first consonant of the
            # cluster forms the coda of the previous syllable (to create a
            # heavy syllable); otherwise, the whole cluster forms the onset of
            # the current syllable (this is the /kr/ rule):
            # 'VCCV > 'VC.CV,  VCCV > V.CCV
            elif is_cluster(v):
                sub_rules.add('d')
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
                    sub_rules.add('e')
                    WORD[i] = v[:2] + '.' + v[2:]

                # T1F
                # If there is a word-medial "Finnish" cluster that follows a
                # consonant, that first consonant forms the coda of the
                # previous syllable, and the cluster forms the onset of the
                # current syllable:
                # VCkr > VC.kr
                else:
                    sub_rules.add('f')
                    WORD[i] = v[0] + '.' + v[1:]

            # T1A
            # There is a syllable boundary in front of every CV sequence:
            # VCV > V.CV, CCV > C.CV
            else:
                WORD[i] = v[:-1] + '.' + v[-1]
                sub_rules.add('a')

    WORD = ''.join(WORD)
    rules = '' if word == WORD else ' T1'   # + ''.join(sub_rules)

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


# Ranking ---------------------------------------------------------------------


def wsp(word):
    '''Return the number of unstressed superheavy syllables.'''
    violations = 0
    unstressed = []

    for w in re.split(r'(=| |-)', word):
        unstressed += w.split('.')[1::2]  # even syllables

        # include extrametrical odd syllables as potential WSP violations
        if w.count('.') % 2 == 0:
            unstressed += [w.rsplit('.', 1)[-1], ]

    for syll in unstressed:
        if is_consonant(syll[-1]) and re.search(r'[aAoOieuy]{2}', syll):
            violations += 1

    return violations


def pk_prom(word):
    '''Return the number of stressed light syllables.'''
    violations = 0
    stressed = []

    for w in re.split(r'(=| |-)', word):
        stressed += w.split('.')[2:-1:2]  # odd syllables, excl. word-initial

    for syll in stressed:
        if is_vowel(syll[-1]):
            violations += 1

    return violations


def rank(syllabifications):
    '''Rank syllabifications.'''
    syllabifications.sort(key=lambda s: wsp(s[0]) + pk_prom(s[0]) + len(s[0]))

    return syllabifications


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    words = [
        'rakkauden',        # rak.kau.den, rak.ka.u.den
        'laukausta',        # lau.ka.us.ta, lau.kaus.ta
        'avautuu',          # a.vau.tuu, a.va.u.tuu
        'rakkaus',          # rak.ka.us, rak.kaus
        'valkeus',          # val.ke.us, val.keus
        'kaikeuden',        # kaik.keu.den, kaik.ke.u.den
        'linnoittautua',    # lin.noit.tau.tu.a, lin.noit.ta.u.tu.a
        'maa=oikeuden',     # maa.oi.keu.den, maa.oi.ke.u.den
        'pako=nopeuteni',   # pa.ko.no.peu.te.ni, pa.ko.no.pe.u.te.ni
        'nopeuteni',        # no.peu.te.ni, no.pe.u.te.ni ????
        'turvautumaan',     # tur.vau.tu.maan, tur.va.u.tu.maan
        'korvautumassa',    # kor.vau.tu.mas.sa, kor.va.u.tu.mas.sa

        # # val.mis.tau.tu.mi.ses.taan, val.mis.ta.u.tu.mi.ses.taan
        'valmistautumisestaan',
        'toteutumattomia',  # to.teu.tu.mat.to.mi.a, to.te.u.tu.mat.to.mi.a
        'suhtautumista',    # suh.tau.tu.mis.ta, suh.ta.u.tu.mis.ta
        'ajautumassa',      # a.jau.tu.mas.sa, a.ja.u.tu.mas.sa
        ]

    for word in words:
        print [w for w, _ in syllabify(word)], '\n'

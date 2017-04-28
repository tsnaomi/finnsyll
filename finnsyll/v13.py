# coding=utf-8
from __future__ import unicode_literals

import re

from itertools import product
from . import phonology as phon
from .utilities import FLAGS, extract_words, nonalpha_split


STRESS = False


# Syllabifier -----------------------------------------------------------------

def syllabify(word, stress=False):
    '''Syllabify the given word, whether simplex or complex.'''
    compound = not word.isalpha()
    syllabify = _syllabify_complex if compound else _syllabify_simplex
    syllabifications = list(syllabify(word, stress=stress))

    # if variation, order variants from most preferred to least preferred
    if len(syllabifications) > 1:
        syllabifications = rank(syllabifications)

    for word, rules in syllabifications:
        yield _post_process(word, rules)


def _syllabify_complex(word, stress=False):
    syllabifications = []

    # split the word along any punctuation (e.g., a hyphen, space, or equal
    # sign) and syllabify the individual parts separately
    # for w in re.split(DELIM, word, flags=FLAGS):
    for w in nonalpha_split(word):

        if w.isalpha():
            # append syllabified simplex word
            syllabifications.append(_syllabify_simplex(w, stress=stress))
        else:
            # append delimiter
            syllabifications.append(([(w, ' ' + w), ]))

    for x in (w for w in product(*syllabifications)):
        word, rules = '', ''

        for w, r in x:
            word += w
            rules += r

        yield word, rules


def _syllabify_simplex(word, stress=False):
    word, rules = T1(word)
    word, rules = T2(word, rules)
    word, rules = T8(word, rules)

    for word, rules in T4(word, rules):  # T4 produces variation
        word, rules = T6(word, rules)
        word, rules = T11(word, rules)

        # add stress assignment
        if stress:
            word = phon.stress(word)

        yield word, rules or ' T0'  # T0 means no rules have applied


def _post_process(word, rules):
    word = word.replace('=', '.')
    rules = rules[1:]

    return word, rules


# T1 --------------------------------------------------------------------------

def T1(word):
    '''Insert a syllable boundary in front of every CV sequence.'''
    # split consonants and vowels: 'balloon' -> ['b', 'a', 'll', 'oo', 'n']
    WORD = [i for i in re.split(r'([ieaouäöy]+)', word, flags=FLAGS) if i]

    # keep track of which sub-rules are applying
    sub_rules = set()

    # a count divisible by 2 indicates an even syllable
    count = 1

    for i, v in enumerate(WORD):

        # T1B
        # If there is a consonant cluster word-initially, the entire cluster
        # forms the onset of the first syllable:
        # CCV > #CCV
        if i == 0 and phon.is_consonant(v[0]):
            sub_rules.add('b')

        elif phon.is_consonant(v[0]):
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
            elif phon.is_cluster(v):
                sub_rules.add('d')
                WORD[i] = v[0] + '.' + v[1:] if unstressed else '.' + v

            elif phon.is_cluster(v[1:]):

                # T1E (optional)
                # If there is a word-medial "Finnish" consonant cluster that is
                # preceded by a sonorant consonant, if the previous syllable
                # receives stress, the sonorant consonant and the first
                # consonant of the cluster form the coda of the previous
                # syllable, and the remainder of the cluster forms the onset of
                # the current syllable:
                # 'VlCC > VlC.C
                if phon.is_sonorant(v[0]) and unstressed:
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
    rules = '' if word == WORD else ' T1'  # + ''.join(sub_rules)  # TODO: sort

    return WORD, rules


# T2 --------------------------------------------------------------------------

def T2(word, rules):
    '''Split any VV sequence that is not a genuine diphthong or long vowel.
    E.g., [ta.e], [ko.et.taa]. This rule can apply within VVV+ sequences.'''
    WORD = word
    offset = 0

    for vv in vv_sequences(WORD):
        seq = vv.group(1)

        if not phon.is_diphthong(seq) and not phon.is_long(seq):
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
    WORD = re.split(
        r'([ieaouäöy]+[^ieaouäöy]+\.*[ieaoäö]{1}(?:u|y)(?:\.*[^ieaouäöy]+|$))',  # noqa
        word, flags=re.I | re.U)

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
    offset = 0

    try:
        WORD, rest = tuple(word.split('.', 1))

        for vvv in long_vowel_sequences(rest):
            i = vvv.start(2)
            vvv = vvv.group(2)
            i += (2 if phon.is_long(vvv[:2]) else 1) + offset
            rest = rest[:i] + '.' + rest[i:]
            offset += 1

    except ValueError:
        WORD = word

    for vvv in long_vowel_sequences(WORD):
        i = vvv.start(2) + 2
        WORD = WORD[:i] + '.' + WORD[i:]

    try:
        WORD += '.' + rest

    except UnboundLocalError:
        pass

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

    for vvv in precedence_sequences(WORD):
        i = vvv.start(1) + (1 if vvv.group(1)[-1] in 'uyUY' else 2) + offset
        WORD = WORD[:i] + '.' + WORD[i:]
        offset += 1

    rules += ' T11' if word != WORD else ''

    return WORD, rules

# Sequences / Regex -----------------------------------------------------------


def vv_sequences(word):
    # this pattern searches for (overlapping) VV sequences
    return re.finditer(r'(?=([ieaouäöy]{2}))', word, flags=FLAGS)


def long_vowel_sequences(word):
    # this pattern searches for any VVV sequence that contains a long vowel
    return re.finditer(
        r'(^|[^ieaouäöy]+)([ieaouäöy]{1}(ii|ee|aa|oo|uu|ää|öö|yy)|(ii|ee|aa|oo|uu|ää|öö|yy)[ieaouäöy])([^ieaouäöy]+|$)',  # noqa
        word,
        flags=FLAGS,
        )


def tail_diphthongs(word):
    # this pattern searches for any standalone /ie/, /uo/, or /yö/ sequence in
    # the first syllable
    return re.match(
        r'^[^ieaouäöy]*(i\.e|u\.o|y\.ö)(?:\.|[^ieaouäöy]+|$)',
        word,
        flags=FLAGS,
        )


def u_y_final_diphthongs(word):
    # this pattern searches for any /u,y/-final diphthong that does not appear
    # under primary stress

    # specifying the relevant diphthongs versus r'([eiaAoO]{1}(u|y)) prevents
    # unnecessary splitting of Vy and Vu loanword sequences that violate vowel
    # harmony (e.g., 'Friday')
    return re.search(
        r'(?:[^ieaouäöy\.]+\.*)(au|eu|ou|iu|iy|ey|äy|öy)(?:(\.*[^ieaouäöy\.]+|$))',  # noqa
        word,
        flags=FLAGS,
        )


def precedence_sequences(word):
    # this pattern searches for any primary-stressed VVV sequence that contains
    # a /u,y/-final diphthong
    return re.finditer(
        r'^[^ieaouäöy]*([ieaoäö]{1}(au|eu|ou|iu|iy|ey|äy|öy)|(au|eu|ou|iu|iy|ey|äy|öy)[ieaoäö]{1})[^ieaouäöy]',  # noqa
        word,
        flags=FLAGS,
        )


# Ranking ---------------------------------------------------------------------

def wsp(word):
    '''Return the number of unstressed superheavy syllables.'''
    violations = 0
    unstressed = []

    for w in extract_words(word):
        unstressed += w.split('.')[1::2]  # even syllables

        # include extrametrical odd syllables as potential WSP violations
        if w.count('.') % 2 == 0:
            unstressed += [w.rsplit('.', 1)[-1], ]

    # SHSP (CVVC = superheavy)
    for syll in unstressed:
        if re.search(r'[ieaouäöy]{2}[^$ieaouäöy]+', syll, flags=FLAGS):
            violations += 1

    # # WSP (CVV = heavy)
    # for syll in unstressed:
    #     if re.search(
    #             ur'[ieaouäöy]{2}|[ieaouäöy]+[^ieaouäöy]+',
    #             syll, flags=re.I | re.U):
    #         violations += 1

    return violations


def pk_prom(word):
    '''Return the number of stressed light syllables.'''
    violations = 0
    stressed = []

    for w in extract_words(word):
        stressed += w.split('.')[2:-1:2]  # odd syllables, excl. word-initial

    # (CVV = light)
    for syll in stressed:
        if phon.is_vowel(syll[-1]):
            violations += 1

    # # (CVV = heavy)
    # for syll in stressed:
    #     if re.search(
    #             ur'^[^ieaouäöy]*[ieaouäöy]{1}$',  syll, flags=re.I | re.U):
    #         violations += 1

    return violations


def nuc(word):
    '''Return the number of nuclei.'''
    return word.count('.') + 1


def rank(syllabifications):
    '''Rank syllabifications.'''

    # def key(s):
    #     word = s[0]
    #     w = wsp(word)
    #     p = pk_prom(word)
    #     n = nuc(word)
    #     t = w + p + n
    #     print('%s\twsp: %s\tpk: %s\tnuc: %s\ttotal: %s' % (word, w, p, n, t))

    #     return w + p + n

    # syllabifications.sort(key=key)

    syllabifications.sort(key=lambda s: wsp(s[0]) + pk_prom(s[0]) + nuc(s[0]))

    return syllabifications


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    words = [
        u'rakkauden',           # rak.kau.den, rak.ka.u.den
        u'laukausta',           # lau.ka.us.ta, lau.kaus.ta
        u'avautuu',             # a.vau.tuu, a.va.u.tuu
        u'rakkaus',             # rak.ka.us, rak.kaus
        u'valkeus',             # val.ke.us, val.keus
        u'kaikeuden',           # kaik.keu.den, kaik.ke.u.den
        u'linnoittautua',       # lin.noit.tau.tu.a, lin.noit.ta.u.tu.a
        u'maa=oikeuden',        # maa.oi.keu.den, maa.oi.ke.u.den
        u'pako=nopeuteni',      # pa.ko.no.peu.te.ni, pa.ko.no.pe.u.te.ni
        u'nopeuteni',           # no.peu.te.ni, no.pe.u.te.ni ????
        u'turvautumaan',        # tur.vau.tu.maan, tur.va.u.tu.maan
        u'korvautumassa',       # kor.vau.tu.mas.sa, kor.va.u.tu.mas.sa
        u'toteutumattomia',     # to.teu.tu.mat.to.mi.a, to.te.u.tu.mat.to.mi.a
        u'suhtautumista',       # suh.tau.tu.mis.ta, suh.ta.u.tu.mis.ta
        u'ajautumassa',         # a.jau.tu.mas.sa, a.ja.u.tu.mas.sa

        u'ensimmäisen',         # en.sim.mäi.sen
        u'käytännössä',         # käy.tän.nös.sä
        u'öljyn',               # öl.jyn
        u'kieltäytyi',          # kiel.täy.tyi, kiel.tä.y.tyi

        u'nauumme',             # nau.um.me
        u'leuun',               # leu.un
        u'riuun',               # riu.un
        u'ruoon',               # ruo.on
        u'mosaiikki',           # mo.sa.iik.ki
        u'herooinen',           # he.ro.oi.nen
        ]

    for word in words:
        variants = '\t'.join(w for w, _ in syllabify(word.upper()))
        print(variants.lower().encode('utf-8'))

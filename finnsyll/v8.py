# coding=utf-8

import re

from itertools import product
from phonology import (
    is_cluster,
    is_consonant,
    is_diphthong,
    is_long,
    is_sonorant,
    is_vowel,
    )


# Syllabifier -----------------------------------------------------------------

def syllabify(word):
    '''Syllabify the given word, whether simplex or complex.'''
    compound = bool(re.search(r'(-| |=)', word))
    syllabify = _syllabify_compound if compound else _syllabify
    syllabifications = list(syllabify(word))

    for syll, rules in syllabifications:
        yield syll, rules

    n = 16 - len(syllabifications)

    # yield empty syllabifications and rules
    for i in range(n):
        yield '', ''


def _syllabify_compound(word, **kwargs):
    syllabifications = []

    # split the word along any delimiters (a hyphen, space, or equal sign) and
    # syllabify the individual parts separately
    for w in re.split(r'(-| |=)', word):
        sylls = [(w, ' |'), ] if w in '- =' else list(_syllabify(w, **kwargs))
        syllabifications.append(sylls)

    WORDS = [w for w in product(*syllabifications)]

    for WORD in WORDS:
        word = ''.join([w for w, r in WORD]).replace('=', '.')
        rules = ''.join([r for w, r in WORD])

        yield word, rules


def _syllabify(word, T1E=True):
    '''Syllabify the given word.'''
    word, rules = apply_T1(word, T1E=T1E)

    if re.search(r'[^ieAyOauo]*([ieAyOauo]{2})[^ieAyOauo]*', word):
        word, T2 = apply_T2(word)
        word, T8 = apply_T8(word)
        word, T9 = apply_T9(word)
        rules += T2 + T8 + T9

        # T4 produces variation
        syllabifications = list(apply_T4(word))

    else:
        syllabifications = [(word, ''), ]

    for word, rule in syllabifications:
        RULES = rules + rule

        if re.search(r'[ieAyOauo]{3}', word):
            word, T6 = apply_T6(word)
            word, T5 = apply_T5(word)
            word, T10 = apply_T10(word)
            word, T7 = apply_T7(word)
            word, T2 = apply_T2(word)
            RULES += T5 + T6 + T10 + T7 + T2

        RULES = RULES or ' T0'  # T0 means no rules have applied

        yield word, RULES


# T1 --------------------------------------------------------------------------

def apply_T1(word, T1E=True):
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
            # the current syllable (thisis the /kr/ rule):
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
    RULE = ' T1' + A + B + C + D + E + F + G if word != WORD else ''

    return WORD, RULE


# T2 --------------------------------------------------------------------------

def apply_T2(word):
    '''There is a syllable boundary within a VV sequence of two nonidentical
    vowels that are not a genuine diphthong, e.g., [ta.e], [ko.et.taa].'''
    WORD = word
    offset = 0

    for vv in vv_sequences(WORD):
        seq = vv.group(2)

        if not is_diphthong(seq) and not is_long(seq):
            i = vv.start(2) + 1 + offset
            WORD = WORD[:i] + '.' + WORD[i:]
            offset += 1

    RULE = ' T2' if word != WORD else ''

    return WORD, RULE


# T4 --------------------------------------------------------------------------

def apply_T4(word):
    '''An agglutination diphthong that ends in /u, y/ optionally contains a
    syllable boundary when -C# or -CCV follow, e.g., [lau.ka.us],
    [va.ka.ut.taa].'''
    WORD = word.split('.')
    PARTS = [[] for part in range(len(WORD))]

    for i, v in enumerate(WORD):

        # i % 2 != 0 prevents this rule from applying to first, third, etc.
        # syllables, which receive stress (WSP)
        if is_consonant(v[-1]) and i % 2 != 0:
            if i + 1 == len(WORD) or is_consonant(WORD[i + 1][0]):
                vv = u_y_final_diphthongs(v)

                if vv:
                    I = vv.start(1) + 1
                    PARTS[i].append(v[:I] + '.' + v[I:])

        # include original form (non-application of rule)
        PARTS[i].append(v)

    WORDS = [w for w in product(*PARTS)]

    for WORD in WORDS:
        WORD = '.'.join(WORD)
        RULE = ' T4' if word != WORD else ''

        yield WORD, RULE


# T5 --------------------------------------------------------------------------

def apply_T5(word):
    '''If a (V)VVV sequence contains a VV sequence that could be an /i/-final
    diphthong, there is a syllable boundary between it and the third vowel,
    e.g., [raa.ois.sa], [huo.uim.me], [la.eis.sa], [sel.vi.äi.si], [tai.an],
    [säi.e], [oi.om.me].'''
    WORD = word
    offset = 0

    for vi in i_final_diphthong_vvv_sequences(WORD):
        s = max(vi.start(1), vi.start(2))
        i = 2 if s + 2 < len(word) and is_vowel(word[s + 2]) else 0

        # if '.' not in word[:s]:
        #     continue

        if not (s == i == 0):
            i += s + offset
            WORD = WORD[:i] + '.' + WORD[i:]
            offset += 1

    RULE = ' T5' if word != WORD else ''

    return WORD, RULE


# T6 --------------------------------------------------------------------------

def apply_T6(word):
    '''If a VVV-sequence contains a long vowel, there is a syllable boundary
    between it and the third vowel, e.g. [kor.ke.aa], [yh.ti.öön], [ruu.an],
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

    RULE = ' T6' if word != WORD else ''

    return WORD, RULE


# T7 --------------------------------------------------------------------------

def apply_T7(word):
    '''If a VVV-sequence does not contain a potential /i/-final diphthong,
    there is a syllable boundary between the second and third vowels, e.g.
    [kau.an], [leu.an], [kiu.as].'''
    WORD = word
    offset = 0

    for vvv in vvv_sequences(WORD):
        i = vvv.start(2) + 2 + offset
        WORD = WORD[:i] + '.' + WORD[i:]
        offset += 1

    RULE = ' T7' if word != WORD else ''

    return WORD, RULE


# T8 --------------------------------------------------------------------------

def apply_T8(word):
    '''Split /ie/ sequences in syllables that do not take primary stress.'''
    WORD = word
    offset = 0

    for ie in ie_sequences(WORD):
        i = ie.start(1) + 1 + offset
        WORD = WORD[:i] + '.' + WORD[i:]
        offset += 1

    RULE = ' T8' if word != WORD else ''

    return WORD, RULE


# T9 --------------------------------------------------------------------------

def apply_T9(word):
    '''Split /iu/ sequences that do not appear in the first or second
    syllables. Split /iu/ sequences in the final syllable iff the final
    syllable would receive stress.'''
    WORD = word
    index = 0
    offset = 0

    for iu in iu_sequences(WORD):
        if iu.start(1) != index:
            i = iu.start(1) + 1 + offset
            WORD = WORD[:i] + '.' + WORD[i:]
            index = iu.start(1)
            offset += 1

    # split any /iu/ sequence in the final syllable iff the final syllable
    # would receive stress -- to capture extrametricality
    if WORD.count('.') % 2 == 0:
        iu = iu_sequences(WORD, word_final=True)

        if iu:
            i = iu.start(1) + 1
            WORD = WORD[:i] + '.' + WORD[i:]

    RULE = ' T9' if word != WORD else ''

    return WORD, RULE


# T10 -------------------------------------------------------------------------

def apply_T10(word):
    '''Any /iou/ sequence contains a syllable boundary between the first and
    second vowel.'''
    WORD = word
    offset = 0

    for iou in iou_sequences(WORD):
        i = iou.start(1) + 1 + offset
        WORD = WORD[:i] + '.' + WORD[i:]
        offset += 1

    RULE = ' T10' if word != WORD else ''

    return WORD, RULE


# Sequences -------------------------------------------------------------------

def vv_sequences(word):
    # this pattern searches for any VV sequence that is not directly preceded
    # or followed by a vowel, and will not match any /ay/ sequence
    pattern = r'(?=(^|\.)[^ieAyOauo]*((?!ay)[ieAyOauo]{2})[^ieAyOauo]*($|\.))'
    return re.finditer(pattern, word)


def vvv_sequences(word):
    # this pattern searches for any VVV sequence that is not directly preceded
    # or followed by a vowel
    pattern = r'(?=(^|\.)[^ieAyOauo]*([ieAyOauo]{3})[^ieAyOauo]*($|\.))'
    return re.finditer(pattern, word)


def iou_sequences(word):
    # this patterns searches for any /iou/ sequence that is not directly
    # preceded or followed by a vowel
    pattern = r'[^ieAyOauo]*(iou)[^ieAyOauo]*'
    return re.finditer(pattern, word)


def ie_sequences(word):
    # this pattern searches for any /ie/ sequence that does not occur in the
    # first syllable, and that is not directly preceded or followed by a vowel
    pattern = r'(?=\.[^ieAyOauo]*(ie)[^ieAyOauo]*($|\.))'
    return re.finditer(pattern, word)


def iu_sequences(word, word_final=False):
    # this pattern searches for any /iu/ sequence that does not occur in the
    # first or second syllables and that is not directly preceded or followed
    # by a vowel
    # if word_final is False, this pattern will not match sequences in the
    # finall syllable
    if word_final:
        pattern = r'\.[^ieAyOauo]*(iu)[^ieAyOauo]*$'

        return re.search(pattern, word)

    pattern = r'\..+\.[^ieAyOauo]*(iu)[^ieAyOauo]*\.'

    return re.finditer(pattern, word)


def i_final_diphthong_vvv_sequences(word):
    # this pattern searches for any (V)VVV sequence that contains an i-final
    # diphthong: 'ai', 'ei', 'oi', 'Ai', 'Oi', 'ui', 'yi'
    pattern = r'[ieAyOauo]+([eAyOauo]{1}i)[ieAyOauo]*'
    pattern += r'|[ieAyOauo]*([eAyOauo]{1}i)[ieAyOauo]+'
    return re.finditer(pattern, word)


def u_y_final_diphthongs(word):
    # this pattern searchs for any VV sequence that ends in /u/ or /y/ (incl.
    # long vowels), and that is not directly preceded or followed by a vowel
    return re.search(
        r'^[^ieAyOauo]*(au|eu|ou|iu|iy|ey|Ay|Oy)[^ieAyOauo]*$',
        word,
        )


# -----------------------------------------------------------------------------

if __name__ == '__main__':

    # WRITE TESTS

    words = [
        # u'belgradin',               # belg.ra.din ~ bel.gra.din
        # u'demokratian',             # de.mo.kra.ti.an
        # u'lastenklinikalla',        # las.ten.kli.ni.kal.la
        # u'diabetesklinikan',        # di.a.be.tes.kli.ni.kan
        # u'express',                 # ex.press
        # u'aggressiivisesti',        # agg.res.sii.vi.ses.ti
        # u'esplanadi',               # esp.la.na.di
        # u'eteläesplanadilla',       # e.te.lä.esp.la.na.dil.la
        # u'battaglia',               # bat.tag.li.a (?)
        # u'sibelius',                # si.be.li.us
        # u'helenius',                # he.le.ni.us
        # u'kotitalouksien',      # ko.ti.ta.lo.uk.si.en ~ ko.ti.ta.louk.si.en
        # u'kauimmin',                # kau.im.min
        # u'serious',                 # se.ri.ous
        # u'hioutuneen',              # hi.ou.tu.neen
        # u'york',                    # york
        # u'young',                   # young
        u'lukuun=ottamatta',        # lu.kuun.ot.ta.mat.ta
        ]

    for word in words:
        syllabifications = [(s, r) for s, r in syllabify(word) if s]
        print ' ~ '.join([s for s, r in syllabifications])
        print ' ~ '.join([r for s, r in syllabifications])

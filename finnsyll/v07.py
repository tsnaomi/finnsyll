# coding=utf-8

import re

from phonology import (
    is_cluster,
    is_consonant,
    is_diphthong,
    is_long,
    is_sonorant,
    is_vowel,
    )


# Syllabifier -----------------------------------------------------------------

def syllabify(word, compound=None):
    '''Syllabify the given word, whether simplex or complex.'''
    if compound is None:
        compound = bool(re.search(r'(-| |=)', word))

    syllabify = _syllabify_compound if compound else _syllabify
    syll, rules = syllabify(word)

    yield syll, rules

    n = 7

    if 'T4' in rules:
        yield syllabify(word, T4=False)
        n -= 1

    if 'e' in rules:
        yield syllabify(word, T1E=False)
        n -= 1

    if 'e' in rules and 'T4' in rules:
        yield syllabify(word, T4=False, T1E=False)
        n -= 1

    # yield empty syllabifications and rules
    for i in range(n):
        yield '', ''


def _syllabify_compound(word, **kwargs):
    WORD, RULES = [], []

    # split the word along any delimiters (a hyphen, space, or equal sign) and
    # syllabify the individual parts separately
    for w in re.split(r'(-| |=)', word):
        syll, rules = (w, ' |') if w in '- =' else _syllabify(w, **kwargs)

        WORD.append(syll)
        RULES.append(rules)

    WORD = ''.join(WORD).replace('=', '.')  # remove equal signs
    RULES = ''.join(RULES)

    return WORD, RULES


def _syllabify(word, T4=True, T1E=True):
    '''Syllabify the given word.'''
    word, rules = apply_T1(word, T1E=T1E)

    if re.search(r'[^ieAyOauo]*([ieAyOauo]{2})[^ieAyOauo]*', word):
        word, T2 = apply_T2(word)
        word, T8 = apply_T8(word)
        word, T9 = apply_T9(word)
        word, T4 = apply_T4(word) if T4 else (word, '')
        rules += T2 + T8 + T9 + T4

    if re.search(r'[ieAyOauo]{3}', word):
        word, T6 = apply_T6(word)
        word, T5 = apply_T5(word)
        word, T7 = apply_T7(word)
        word, T2 = apply_T2(word)
        rules += T5 + T6 + T7 + T2

    rules = rules or ' T0'  # T0 means no rules have applied

    return word, rules


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
    '''An agglutination diphthong that ends in /u, y/ contains a syllable
    boundary when the sequence would appear in an unstressed syllable, e.g.,
    [lau.ka.us], [va.ka.ut.taa].'''
    WORD = word.split('.')

    for i, v in enumerate(WORD):

        # i % 2 != 0 prevents this rule from applying to first, third, etc.
        # syllables, which receive stress (WSP)
        if i % 2 != 0:
            vv = u_y_final_diphthongs(v)

            if vv and not is_long(vv.group(1)):
                I = vv.start(1) + 1
                WORD[i] = v[:I] + '.' + v[I:]

    WORD = '.'.join(WORD)
    RULE = ' T4' if word != WORD else ''

    return WORD, RULE


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
    '''Split /iu/ sequences that do not appear in the first, second, or final
    syllables.'''
    WORD = word
    index = 0
    offset = 0

    for iu in iu_sequences(WORD):
        if iu.start(1) != index:
            i = iu.start(1) + 1 + offset
            WORD = WORD[:i] + '.' + WORD[i:]
            index = iu.start(1)
            offset += 1

    RULE = ' T9' if word != WORD else ''

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


def ie_sequences(word):
    # this pattern searches for any /ie/ sequence that does not occur in the
    # first syllable, and that is not directly preceded or followed by a vowel
    pattern = r'(?=\.[^ieAyOauo]*(ie)[^ieAyOauo]*($|\.))'
    return re.finditer(pattern, word)


def iu_sequences(word):
    # this pattern searches for any /iu/ sequence that does do occur in the
    # first, second, or final syllables, and that is not directly preceded or
    # followed by a vowel
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
    return re.search(r'^[^ieAyOauo]*([ieAyOauo]{1}(u|y))[^ieAyOauo]*$', word)


# -----------------------------------------------------------------------------

if __name__ == '__main__':

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
        # u'tshetsheniaan',
        # u'armstrong',
        # u'ekspress',
        u'hääyöaie',
        ]

    for word in words:
        syllabifications = [(s, r) for s, r in syllabify(word) if s]
        print ' ~ '.join([s for s, r in syllabifications])
        print ' ~ '.join([r for s, r in syllabifications])

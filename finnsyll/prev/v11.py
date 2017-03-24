# coding=utf-8

# First Python 3-compatible version.

import re

from itertools import product

try:
    from .phonology import (
        is_cluster,
        is_consonant,
        is_diphthong,
        is_foreign,
        is_long,
        is_sonorant,
        is_vowel,
        replace_umlauts,
        )

except (ImportError, ValueError):
    from phonology import (
        is_cluster,
        is_consonant,
        is_diphthong,
        is_long,
        is_sonorant,
        is_vowel,
        replace_umlauts,
        )


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
    word, rules = apply_T1(word)

    if re.search(r'[^ieAyOauo]*([ieAyOauo]{2})[^ieAyOauo]*', word):
        word, T12 = apply_T12(word)
        word, T8 = apply_T8(word)
        rules += T12 + T8

        # T4 produces variation
        syllabifications = list(apply_T4(word))

    else:
        syllabifications = [(word, ''), ]

    for word, rule in syllabifications:
        RULES = rules + rule

        if re.search(r'[ieAyOauo]{3}', word):
            word, T6 = apply_T6(word)
            word, T11 = apply_T11(word)
            # word, T5 = apply_T5(word)
            # word, T7 = apply_T7(word)
            RULES += T11 + T6 # + T5  # + T7

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
    RULE = ' T1' if word != WORD else ''

    return WORD, RULE


# T2 --------------------------------------------------------------------------

def apply_T2(word, rules):
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

# def apply_T4(word):
#     '''An agglutination diphthong that ends in /u, y/ optionally contains a
#     syllable boundary when -C# or -CCV follow, e.g., [lau.ka.us],
#     [va.ka.ut.taa].'''
#     WORD = word.split('.')
#     PARTS = [[] for part in range(len(WORD))]

#     for i, v in enumerate(WORD):

#         if i != 0:
#             vv = u_y_final_diphthongs(v)

#             if vv:
#                 I = vv.start(1) + 1
#                 PARTS[i].append(v[:I] + '.' + v[I:])

#         # include original form (non-application of rule)
#         PARTS[i].append(v)

#     WORDS = [w for w in product(*PARTS)]

#     for WORD in WORDS:
#         WORD = '.'.join(WORD)
#         RULE = ' T4' if word != WORD else ''

#         yield WORD, RULE


def apply_T4(word):
    '''An agglutination diphthong that ends in /u, y/ optionally contains a
    syllable boundary when -C# or -CCV follow, e.g., [lau.ka.us],
    [va.ka.ut.taa].'''
    # WORD = word.split('.')
    pattern = r'([aAoOieuy]+[^aAoOieuy]+\.*[aAoOie]{1}(?:u|y)(?:\.*[^aAoOieuy]+|$))'
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
    '''Split /ie/, /uo/, or /yö/ sequences in syllables that do not take
    primary stress.'''
    WORD = word
    offset = 0

    for vv in tail_diphthongs(WORD):
        i = vv.start(1) + 1 + offset
        WORD = WORD[:i] + '.' + WORD[i:]
        offset += 1

    RULE = ' T8' if word != WORD else ''

    return WORD, RULE


# T11 -------------------------------------------------------------------------

def apply_T11(word):
    '''If a VVV sequence contains a /u, y/-final diphthong and the third vowel
    is /i/, there is a syllable boundary between the diphthong and /i/.'''
    WORD = word
    offset = 0

    for vvv in t11_vvv_sequences(WORD):
        # i = vvv.start(1) + (1 if vvv.group(1).startswith('i') else 2) + offset
        i = vvv.start(1) + (1 if vvv.group(1)[-1] in 'uy' else 2) + offset
        WORD = WORD[:i] + '.' + WORD[i:]
        offset += 1

    RULE = ' T11' if word != WORD else ''

    return WORD, RULE


# T12 -------------------------------------------------------------------------

def apply_T12(word):
    '''There is a syllable boundary within a VV sequence of two nonidentical
    vowels that are not a genuine diphthong, e.g., [ta.e], [ko.et.taa].'''
    WORD = word
    offset = 0

    for vv in new_vv(WORD):
        # import pdb; pdb.set_trace()
        seq = vv.group(1)

        if not is_diphthong(seq) and not is_long(seq):
            i = vv.start(1) + 1 + offset
            WORD = WORD[:i] + '.' + WORD[i:]
            offset += 1

    RULE = ' T2' if word != WORD else ''

    return WORD, RULE

# Sequences -------------------------------------------------------------------


def new_vv(word):
    pattern = r'(?=([ieyuaAoO]{2}))'
    return re.finditer(pattern, word)


def vv_sequences(word):  # TODO
    # this pattern searches for any VV sequence that is not directly preceded
    # or followed by a vowel, and will not match any /ay/ sequence
    pattern = r'(?=(^|\.)[^ieAyOauo]*((?!ay)[ieAyOauo]{2})[^ieAyOauo]*($|\.))'
    return re.finditer(pattern, word)


def vvv_sequences(word):
    # this pattern searches for any VVV sequence that is not directly preceded
    # or followed by a vowel
    pattern = r'(?=(^|\.)[^ieAyOauo]*([ieAyOauo]{3})[^ieAyOauo]*($|\.))'
    return re.finditer(pattern, word)


def tail_diphthongs(word):
    # this pattern searches for any /ie/, /uo/, or /yö/ sequence that does not
    # occur in the first syllable, and that is not directly preceded or
    # followed by a vowel
    # pattern = r'(?=\.[^ieAyOauo]*(ie|uo|yO)[^ieAyOauo]*($|\.))'
    # pattern = r'^[^ieAyOauo]*[ieAyOauo]+[^ieAyOauo]*(ie|uo|yO)'
    pattern = r'\.+[A-Za-z]*(ie|uo|yO)'
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

    # specifying the relevant diphthongs versus r'([eiaAoO]{1}(u|y)) prevents
    # unnecessary splitting of Vy and Vu loanword sequences that violate vowel
    # harmony (e.g., 'Friday')

    # pattern = r'^[^ieAyOauo]*\.*(au|eu|ou|iu|iy|ey|Ay|Oy)\.*[^ieAyOauo]*$'
    pattern = r'(?:[^aAoOieuy\.]+\.*)(au|eu|ou|iu|iy|ey|Ay|Oy)(?:(\.*[^aAoOieuy\.]+|$))'
    return re.search(pattern, word)


def t11_vvv_sequences(word):
    # this pattern searches for any syllable-initial VVV sequence that contains
    # /i/ and a /u,y/-final diphthong -- word-inital
    # pattern = r'[^ieAyOauo](i(au|eu|ou|iu|iy|ey|Ay|Oy)'
    # pattern += r'|(au|eu|ou|iu|iy|ey|Ay|Oy)i)[^ieAyOauo]'
    pattern = r'^[^ieAyOauo]*([aAoOie]{1}(au|eu|ou|iu|iy|ey|Ay|Oy)|(au|eu|ou|iu|iy|ey|Ay|Oy)[aAoOie]{1})[^ieAyOauo]'
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
    print [i for i in syllabify('purouoma')]
    print [i for i in syllabify('saippuoita')]
    # print [i for i in syllabify('daunauschingen')]
    # print [i for i in syllabify('donaueschingen')]
    # print [i for i in syllabify('donauhingen')]
    # print [i for i in syllabify('hauiksella')]  # T11 hau.ik.sel.la GOOD
    # print [i for i in syllabify('aiemmin')]     # T5  ai.em.min BAD
    # print [i for i in syllabify('lauantaina')]  # T7  lau.an.tai.na GOOD

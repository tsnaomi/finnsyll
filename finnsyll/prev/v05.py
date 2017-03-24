# coding=utf-8

import re

from compound import split
from phonology import (
    is_cluster,
    is_consonant,
    is_diphthong,
    is_long,
    # is_sonorant,
    is_vowel,
    replace_umlauts,
    )

# SYLLABIFIER.V5 introduces variation

# Gold Variation Notes --------------------------------------------------------

# NB: Onset clusters are dispreferred

# 1 Consonant clusters:
#       ju.gos.la.vi.an ~ ju.go.sla.vi.an                                [sl]
#       manc.hes.ter ~ man.ches.ter                                      [ch]
#       tshets.he.ni.as.sa ~ tshet.she.ni.as.sa ~ tshe.tshe.ni.as.sa     [tsch]
#       belg.ra.din ~ bel.gra.din                                        [gr]
#       armst.rong ~ arms.trong ~ arm.strong                             [str]
#       belg.ra.dis.sa ~ bel.gra.dis.sa
#       ka.tast.ro.fi ~ ka.tas.tro.fi ~ ka.ta.stro.fi
#       inf.laaa.ti.o ~ in.flaa.ti.o                                     [fl]
#       fisc.her ~ fis.cher ~ fi.scher                                   [sch]
#       deutsch.he ~ deuts.che ~ deut.sche
#       sha.kes.pe.a.re ~ sha.ke.spe.a.re                                [sp]
#       mit.su.bis.hi ~ mit.su.bi.shi                                    [sh]
#       wimb.le.do.nin ~ wim.ble.do.nin                                  [bl]
#       e.rit.re.an ~ e.ri.tre.an                                        [tr]

# 2 Vowel/glide ambiguity:
#       y.or.kin ~ yor.kin
#       y.or.kis.sa ~ yor.kis.sa
#       and.rew ~ an.drew

# 3 Vowels:

#       pi.an ~ pian
#       pi.a.no ~ pia.no
#       blue.es
#       pi.ak.koin ~ piak.koin
#       luin ~ luin
#       sel.viy.ty.ä ~ sel.vi.t.ty.ä
#       taus.ta ~ ta.us.ta [stopword]

#       lais.sa ~ la.is.sa
#       be.at ~ beat
#       kva.er.ne.rin ~ kvaer.ne.rin
#       haus.sa ~ ha.us.sa
#       maun ~ ma.un
#       yh.ti.ö.ko.ko.us ~ yh.ti.ó.ko.kous
#       te.am ~ team


# Syllabifier -----------------------------------------------------------------

def syllabify(word):
    '''Syllabify the given word, whether simplex or complex.'''
    word = split(word)  # detect any non-delimited compounds
    compound = True if re.search(r'-| |\.', word) else False
    syllabify = _syllabify_compound if compound else _syllabify
    syll, rules = syllabify(word)

    yield syll, rules

    n = 3

    if 'T4' in rules:
        yield syllabify(word, T4=False)
        n -= 1

    # yield empty syllabifications and rules
    for n in range(3):
        yield '', ''


def _syllabify_compound(word, T4=True):
    WORD, RULES = [], []

    # if the word contains a delimiter (a hyphens or space), split the word
    # along the delimiter(s) and syllabify the individual parts separately
    for w in re.split(r'(-| |\.)', word):
        syll, rules = (w, ' |') if w in '- .' else _syllabify(w, T4=T4)
        WORD.append(syll)
        RULES.append(rules)

    return ''.join(WORD), ''.join(RULES)


def _syllabify(word, T4=True):
    '''Syllabify the given word.'''
    word = replace_umlauts(word)
    word, rules = apply_T1(word)

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

    word = replace_umlauts(word, put_back=True)
    rules = rules or ' T0'  # T0 means no rules have applied

    return word, rules


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
    return re.search(r'^[^ieAyOauo]*([ieAyOao]{1}(u|y))[^ieAyOauo]*$', word)


# T1 --------------------------------------------------------------------------

def apply_T1(word):
    '''There is a syllable boundary in front of every CV-sequence.'''
    # split consonants and vowels: 'balloon' -> ['b', 'a', 'll', 'oo', 'n']
    WORD = [w for w in re.split('([ieAyOauo]+)', word) if w]
    count = 0

    for i, v in enumerate(WORD):

        if i == 0 and is_consonant(v[0]):
            continue

        elif is_consonant(v[0]) and i + 1 != len(WORD):
            if is_cluster(v):  # WSP
                if count % 2 == 0:
                    WORD[i] = v[0] + '.' + v[1:]  # CC > C.C, CCC > C.CC

                else:
                    WORD[i] = '.' + v  # CC > .CC, CCC > .CCC

            # elif is_sonorant(v[0]) and is_cluster(v[1:]):  # NEW
            #     if count % 2 == 0:
            #         WORD[i] = v[0:2] + '.' + v[2:]

            #     else:
            #         WORD[i] = v[0] + '.' + v[1:]

            else:
                WORD[i] = v[:-1] + '.' + v[-1]  # CC > C.C, CCC > CC.C

            count += 1

    WORD = ''.join(WORD)
    RULE = ' T1' if word != WORD else ''

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

# VARIATION : It is ambiguous whether these dipthongs split when they appear
# word-finally or precede a coda.

def apply_T4(word):
    '''An agglutination diphthong that ends in /u, y/ usually contains a
    syllable boundary when -C# or -CCV follow, e.g., [lau.ka.us],
    [va.ka.ut.taa].'''
    WORD = word.split('.')

    for i, v in enumerate(WORD):

        # i % 2 != 0 prevents this rule from applying to first, third, etc.
        # syllables, which receive stress (WSP)
        if is_consonant(v[-1]) and i % 2 != 0:
            if i + 1 == len(WORD) or is_consonant(WORD[i + 1][0]):
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


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    pass

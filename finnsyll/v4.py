# coding=utf-8

import re

from phonology import (
    is_cluster,
    is_consonant,
    is_diphthong,
    is_long,
    is_vowel,
    replace_umlauts,
    )


# Syllabifier -----------------------------------------------------------------

def syllabify(word):
    compound = True if re.search(r'-| ', word) else False

    # if the word contains a delimiter (a hyphens or space), split the word
    # along the delimiter(s) and syllabify the individual parts separately
    if compound:
        WORD, RULES = [], []

        for w in re.split(r'(-| |\.)', word):
            syll, rules = (w, ' |') if w in '- .' else _syllabify(w)
            WORD.append(syll)
            RULES.append(rules)

        return ''.join(WORD), ''.join(RULES)

    return _syllabify(word)


def _syllabify(word):
    '''Syllabify the given word.'''
    word = replace_umlauts(word)
    word, applied_rules = apply_T1(word)

    if re.search(r'[^ieAyOauo]*([ieAyOauo]{2})[^ieAyOauo]*', word):
        word, T2 = apply_T2(word)
        word, T8 = apply_T8(word)
        word, T9 = apply_T9(word)
        word, T4 = apply_T4(word)
        applied_rules += T2 + T8 + T9 + T4

    if re.search(r'[ieAyOauo]{3}', word):
        word, T6 = apply_T6(word)
        word, T5 = apply_T5(word)
        word, T7 = apply_T7(word)
        word, T2 = apply_T2(word)  # ordering T2 last
        applied_rules += T5 + T6 + T7 + T2

    word = replace_umlauts(word, put_back=True)
    applied_rules = applied_rules or ' T0'  # T0 means no rules have applied

    return word, applied_rules


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

            else:
                WORD[i] = v[:-1] + '.' + v[-1]  # CC > C.C, CCC > CC.C

            count += 1

    WORD = ''.join(WORD)
    RULE = ' T1' if word != WORD else ''

    return WORD, RULE


# T2 --------------------------------------------------------------------------

def apply_T2(word):
    '''There is a syllable boundary within a sequence VV of two nonidentical
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
    '''If a (V)VVV-sequence contains a VV-sequence that could be an /i/-final
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
    import sys

    args = sys.argv[1:]

    if args:
        for arg in args:
            if isinstance(arg, str):
                print syllabify(arg) + '\n'

    else:
        words = [
            (u'tae', u'ta.e'),
            (u'koettaa', u'ko.et.taa'),
            (u'hain', u'hain'),  # ha.in (alternative)
            (u'laukaus', u'lau.ka.us'),
            (u'vakauttaa', u'va.ka.ut.taa'),
            (u'raaoissa', u'raa.ois.sa'),
            (u'huouimme', u'huo.uim.me'),
            (u'laeissa', u'la.eis.sa'),
            (u'selviäisi', u'sel.vi.äi.si'),
            (u'taian', u'tai.an'),
            (u'säie', u'säi.e'),
            (u'oiomme', u'oi.om.me'),
            (u'korkeaa', u'kor.ke.aa'),
            (u'yhtiöön', u'yh.ti.öön'),
            (u'ruuan', u'ruu.an'),
            (u'määytte', u'mää.yt.te'),
            (u'kauan', u'kau.an'),
            (u'leuan', u'leu.an'),
            (u'kiuas', u'kiu.as'),
            (u'haluaisin', u'ha.lu.ai.sin'),
            (u'hyöyissä', u'hyö.yis.sä'),
            (u'pamaushan', u'pa.ma.us.han'),
            (u'saippuaa', u'saip.pu.aa'),
            (u'joissa', u'jois.sa'),  # jo.is.sa (alternative)
            (u'tae', u'ta.e'),
            (u'kärkkyä', u'kärk.ky.ä'),
            (u'touon', u'tou.on'),
            (u'värväytyä', u'vär.väy.ty.ä'),
            (u'värväyttää', u'vär.vä.yt.tää'),
            (u'daniel', u'da.ni.el'),
            (u'sosiaalinen', u'so.si.aa.li.nen'),
            (u'välierien', u'vä.li.e.ri.en'),
            (u'lounais-suomen puhelin', u'lou.nais-suo.men pu.he.lin'),
            (u'powers', u'po.wers'),
            (u'uusivuosi', u'uu.si.vuo.si'),
            (u'elämäntyömerkki', u'e.lä.män.työ.merk.ki'),
            (u'imperiumiin', u'im.pe.ri.u.miin'),
            (u'demokraattisen', u'de.mo.kraat.ti.sen'),
            (u'mikrojäähdytin', u'mik.ro.jääh.dy.tin'),
            (u'republikaani', u're.pub.li.kaa.ni'),
            (u'Jakobson', u'Ja.kob.son'),
            ]

        for word in words:
            syll = syllabify(word[0])

            if syll[0] != word[1]:
                print u'TRY: %s  %s\nYEA: %s\n' % (syll[0], syll[1], word[1])
                # print u'TEST: %s\nGOLD: %s\n' % (syll[0], word[1])

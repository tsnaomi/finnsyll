# coding=utf-8

from phonology import (
    CONSONANTS,
    is_consonant,
    is_consonantal_onset,
    is_diphthong,
    is_vowel,
    replace_umlauts,
    VOWELS
    )


def same_syllabic_feature(ch1, ch2):
    '''Return True if ch1 and ch2 are both vowels or both consonants.'''
    if ch1 == '.' or ch2 == '.':
        return False

    ch1 = 'V' if ch1 in VOWELS else 'C' if ch1 in CONSONANTS else None
    ch2 = 'V' if ch2 in VOWELS else 'C' if ch2 in CONSONANTS else None

    return ch1 == ch2


def _split_consonants_and_vowels(word):
    # 'balloon' -> {1: 'b', 2: 'a', 3: 'll', 4: 'oo', 5: 'n'}
    # 'bal.loon' -> {1: 'b', 2: 'a', 3: 'l', 4: '.'. 5: 'l', 6: 'oo', 7: 'n'}
    WORD = {}

    prev = [0, 0]

    for i, ch in enumerate(word):

        if same_syllabic_feature(prev[1], ch):
            WORD[prev[0]] += ch

        else:
            prev[0] += 1
            prev[1] = ch
            WORD[prev[0]] = ch

    return WORD


def _compile_dict_into_word(WORD):
    word = ''

    for i in xrange(1, len(WORD) + 1):
        word += WORD[i]

    return word


# Syllabifier -----------------------------------------------------------------

def syllabify(word):
    '''Syllabify the given word.'''

    word = replace_umlauts(word)

    word = apply_T1(word)
    word = apply_T2(word)
    word = apply_T4(word)
    word = apply_T5(word)
    word = apply_T6(word)
    word = apply_T7(word)

    word = replace_umlauts(word, put_back=True)[1:]  # FENCEPOST

    return word


# T1 --------------------------------------------------------------------------

def apply_T1(word):
    '''There is a syllable boundary in front of every CV-sequence.'''
    WORD = _split_consonants_and_vowels(word)

    for k, v in WORD.iteritems():

        if k == 1 and is_consonantal_onset(v):
            WORD[k] = '.' + v

        elif is_consonant(v[0]) and WORD.get(k + 1, 0):
            WORD[k] = v[:-1] + '.' + v[-1]

    word = _compile_dict_into_word(WORD)

    return word


# T2 --------------------------------------------------------------------------

def apply_T2(word):
    '''There is a syllable boundary within a sequence VV of two nonidentical
    that are not a genuine diphthong, e.g., [ta.e], [ko.et.taa].'''
    WORD = _split_consonants_and_vowels(word)

    for k, v in WORD.iteritems():

        if is_diphthong(v):
            continue

        if len(v) == 2 and is_vowel(v[0]):

            if v[0] != v[1]:
                WORD[k] = v[0] + '.' + v[1]

    word = _compile_dict_into_word(WORD)

    return word


# T4 --------------------------------------------------------------------------

def apply_T4(word):  # OPTIMIZE
    '''An agglutination diphthong that ends in /u, y/ usually contains a
    syllable boundary when -C# or -CCV follow, e.g., [lau.ka.us],
    [va.ka.ut.taa].'''
    WORD = _split_consonants_and_vowels(word)

    for k, v in WORD.iteritems():

        if len(v) == 2 and v.endswith(('u', 'y')):

            if WORD.get(k + 2, 0):

                if not WORD.get(k + 3, 0):
                    if len(WORD[k + 2]) == 1 and is_consonant(WORD[k + 2]):
                        WORD[k] = v[0] + '.' + v[1]

                elif len(WORD[k + 1]) == 1 and WORD.get(k + 3, 0):
                    if is_consonant(WORD[k + 3][0]):
                        WORD[k] = v[0] + '.' + v[1]

                elif len(WORD[k + 2]) == 2:
                    WORD[k] = v[0] + '.' + v[1]

    word = _compile_dict_into_word(WORD)

    return word


# T5 --------------------------------------------------------------------------

i_DIPHTHONGS = ['ai', 'ei', 'oi', 'Ai', 'Oi', 'ui', 'yi']


def apply_T5(word):
    '''If a (V)VVV-sequence contains a VV-sequence that could be an /i/-final
    diphthong, there is a syllable boundary between it and the third vowel,
    e.g., [raa.ois.sa], [huo.uim.me], [la.eis.sa], [sel.vi.äi.si], [tai.an],
    [säi.e], [oi.om.me].'''
    WORD = _split_consonants_and_vowels(word)

    for k, v in WORD.iteritems():

        if len(v) >= 3 and is_vowel(v[0]):
            vv = [v.find(i) for i in i_DIPHTHONGS if v.find(i) > 0]

            if any(vv):
                vv = vv[0]

                if vv == v[0]:
                    WORD[k] = v[:2] + '.' + v[2:]

                else:
                    WORD[k] = v[:vv] + '.' + v[vv:]

    word = _compile_dict_into_word(WORD)

    return word


# T6 --------------------------------------------------------------------------

LONG_VOWELS = [i + i for i in VOWELS]


def apply_T6(word):
    '''If a VVV-sequence contains a long vowel, there is a syllable boundary
    between it and the third vowel, e.g. [kor.ke.aa], [yh.ti.öön], [ruu.an],
    [mää.yt.te].'''
    WORD = _split_consonants_and_vowels(word)

    for k, v in WORD.iteritems():

        if len(v) == 3 and is_vowel(v[0]):
            vv = [v.find(i) for i in LONG_VOWELS if v.find(i) > 0]

            if any(vv):
                vv = vv[0]

                if vv == v[0]:
                    WORD[k] = v[:2] + '.' + v[2:]

                else:
                    WORD[k] = v[:vv] + '.' + v[vv:]

    word = _compile_dict_into_word(WORD)

    return word


# T7 --------------------------------------------------------------------------

def apply_T7(word):
    '''If a VVV-sequence does not contain a potential /i/-final diphthong,
    there is a syllable boundary between the second and third vowels, e.g.
    [kau.an], [leu.an], [kiu.as].'''
    WORD = _split_consonants_and_vowels(word)

    for k, v in WORD.iteritems():

        if len(v) == 3 and is_vowel(v[0]):
            WORD[k] = v[:2] + '.' + v[2:]

    word = _compile_dict_into_word(WORD)

    return word


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    args = sys.argv[1:]

    if args:
        for arg in args:
            if isinstance(arg, str):
                print syllabify(arg) + '\n'

    else:
        # test syllabifications -- from Arto's finnish_syllabification.txt
        words = [
            (u'kala', u'ka.la'),  # T-1
            (u'järjestäminenkö', u'jär.jes.tä.mi.nen.kö'),  # T-1, 1, 1, 1, 1
            (u'kärkkyä', u'kärk.ky.ä'),  # T-1, 2
            (u'värväytyä', u'vär.väy.ty.ä'),  # T-1, 1, 2
            (u'pamaushan', u'pa.ma.us.han'),  # T-1, 4, 1
            (u'värväyttää', u'vär.vä.yt.tää'),  # T-1, 4, 1
            (u'haluaisin', u'ha.lu.ai.sin'),  # T-1, 5
            (u'hyöyissä', u'hyö.yis.sä'),  # T-5, 1
            (u'saippuaa', u'saip.pu.aa'),  # T-1, 6
            (u'touon', u'tou.on'),  # T-7
            ]

        for word in words:
            print u'TRY: %s\nYEA: %s\n' % (syllabify(word[0]), word[1])

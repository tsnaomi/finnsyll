# coding=utf-8

# python -m unittest discover

import unittest

import finnsyll.phonology as phon

try:
    import cpickle as pickle

except ImportError:
    import pickle

try:
    # Python 3
    from ..finnsyll import FinnSyll

except (ImportError, ValueError):
    # Python 2
    from finnsyll import FinnSyll


def error_helper(self, func, cases):
    # accrue all of the errors for each test and print them in bulk
    errors = []

    for i, expected in cases.iteritems():
        test = func(i)

        try:
            self.assertEqual(test, expected)

        except AssertionError as e:
            errors.append(e.message)

    if errors:
        raise AssertionError('\n\n' + '\n\n'.join(errors).encode('utf-8'))


class TestSyllabifierKwargs(unittest.TestCase):

    def test_full_functionality(self):
        # ensure that the syllabifier returns all known variants and applied
        # rules as a list of tuples, with compound splitting
        F = FinnSyll(split_compounds=True, variation=True, track_rules=True)

        cases = {
            # simplex, no variation
            'runoja': [
                ('ru.no.ja', 'T1'),
                ],
            # simplex, variation
            'oikeus': [
                ('oi.ke.us', 'T1 T4'),
                ('oi.keus', 'T1'),
                ],
            # complex, no variation
            'kuukautta': [
                ('kuu.kaut.ta', 'T0 = T1'),
                ],
            # complex, variation
            'hovioikeus': [
                ('ho.vi.oi.ke.us', 'T1 = T1 T4'),
                ('ho.vi.oi.keus', 'T1 = T1'),
                ],
            }

        error_helper(self, F.syllabify, cases)

    def test_no_splitting(self):
        # ensure that the syllabifier returns all known variants and applied
        # rules as a list of tuples, minus compound splitting
        F = FinnSyll(split_compounds=False, variation=True, track_rules=True)

        cases = {
            # simplex, no variation
            'runoja': [
                ('ru.no.ja', 'T1'),
                ],
            # simplex, variation
            'oikeus': [
                ('oi.ke.us', 'T1 T4'),
                ('oi.keus', 'T1'),
                ],
            # complex, no variation
            'jukolantupien': [
                ('ju.ko.lan.tu.pi.en', 'T1 T2'),
                ],
            # complex, variation
            'hovioikeus': [
                ('ho.vi.oi.ke.us', 'T1 T2 T4'),
                ('ho.vi.oi.keus', 'T1 T2'),
                ],
            }

        error_helper(self, F.syllabify, cases)

    def test_no_variation(self):
        # ensure that the syllabifier returns the most preferred variant and
        # its applied rules as a tuple, with compound splitting
        F = FinnSyll(split_compounds=True, variation=False, track_rules=True)

        cases = {
            # simplex, no variation
            'runoja': ('ru.no.ja', 'T1'),
            # simplex, variation
            'oikeus': ('oi.ke.us', 'T1 T4'),
            # complex, no variation
            'kuukautta': ('kuu.kaut.ta', 'T0 = T1'),
            # complex, variation
            'hovioikeus': ('ho.vi.oi.ke.us', 'T1 = T1 T4'),
            }

        error_helper(self, F.syllabify, cases)

    def test_no_rules(self):
        # ensure that the syllabifier returns all known variants as a list of
        # strings, with compound splitting
        F = FinnSyll(split_compounds=True, variation=True, track_rules=False)

        cases = {
            # simplex, no variation
            'runoja': [
                'ru.no.ja',
                ],
            # simplex, variation
            'oikeus': [
                'oi.ke.us',
                'oi.keus',
                ],
            # complex, no variation
            'kuukautta': [
                'kuu.kaut.ta',
                ],
            # complex, variation
            'hovioikeus': [
                'ho.vi.oi.ke.us',
                'ho.vi.oi.keus',
                ],
            }

        error_helper(self, F.syllabify, cases)

    def test_no_splitting_or_variation(self):
        # ensure that the syllabifier returns the most preferred variant and
        # its applied rules as a tuple, minus compound splitting
        F = FinnSyll(split_compounds=False, variation=False, track_rules=True)

        cases = {
            # simplex, no variation
            'runoja': ('ru.no.ja', 'T1'),
            # simplex, variation
            'oikeus': ('oi.ke.us', 'T1 T4'),
            # complex, no variation
            'kuukautta': ('kuu.ka.ut.ta', 'T1 T4'),
            # complex, variation
            'hovioikeus': ('ho.vi.oi.ke.us', 'T1 T2 T4'),
            }

        error_helper(self, F.syllabify, cases)

    def test_no_splitting_or_rules(self):
        # ensure that the syllabifier returns all known variants as a list of
        # strings, minus compound splitting
        F = FinnSyll(split_compounds=False, variation=True, track_rules=False)

        cases = {
            # simplex, no variation
            'runoja': [
                'ru.no.ja',
                ],
            # simplex, variation
            'oikeus': [
                'oi.ke.us',
                'oi.keus',
                ],
            # complex, no variation
            'jukolantupien': [
                'ju.ko.lan.tu.pi.en',
                ],
            # complex, variation
            'hovioikeus': [
                'ho.vi.oi.ke.us',
                'ho.vi.oi.keus',
                ],
            }

        error_helper(self, F.syllabify, cases)

    def test_no_variation_or_rules(self):
        # ensure that the syllabifier returns the most preferred variant as a
        # string, with compound splitting
        F = FinnSyll(split_compounds=True, variation=False, track_rules=False)

        cases = {
            # simplex, no variation
            'runoja': 'ru.no.ja',
            # simplex, variation
            'oikeus': 'oi.ke.us',
            # complex, no variation
            'kuukautta': 'kuu.kaut.ta',
            # complex, variation
            'hovioikeus': 'ho.vi.oi.ke.us',
            }

        error_helper(self, F.syllabify, cases)

    def test_no_splitting_or_variation_or_rules(self):
        # ensure that the syllabifier returns the most preferred variant as a
        # string, minus compound splitting
        F = FinnSyll(split_compounds=False, variation=False, track_rules=False)

        cases = {
            # simplex, no variation
            'runoja': 'ru.no.ja',
            # simplex, variation
            'oikeus': 'oi.ke.us',
            # complex, no variation
            'kuukautta': 'kuu.ka.ut.ta',
            # complex, variation
            'hovioikeus': 'ho.vi.oi.ke.us',
            }

        error_helper(self, F.syllabify, cases)


class TestSyllabifierOutput(unittest.TestCase):

    def test_byte_unicode_input(self):
        # ensure that the syllabifier outputs utf-8 decoded unicode while
        # accepting byte or unicode input
        F = FinnSyll(split_compounds=True, variation=False, track_rules=False)
        errors = []

        cases = (
            # byte strings
            'kesäillan',
            unicode('kesäillan', 'latin-1').encode('latin-1'),
            unicode('kesäillan', 'utf-8').encode('utf-8'),
            # unicode strings
            u'kesäillan',
            unicode('kesäillan', 'utf-8'),
            )

        for case in cases:
            try:
                self.assertEqual(F.syllabify(case), u'ke.sä.il.lan')

            except AssertionError as e:
                errors.append(e.message)

        if errors:
            raise AssertionError('\n\n' + '\n\n'.join(errors).encode('utf-8'))

    def test_syllabify_sentence(self):
        # ensure that the syllabififer can syllabify an entire sentence or text
        # with FinnSyll.syllabify_sent()
        F = FinnSyll(split_compounds=True, variation=True, track_rules=True)

        lines = (
            u'Ei olko kaipuumme kuin haave naisentai sairaan näky,\n'
            u'houre humalaisen.\n\n'

            u'Nuo äänet on kuorona rinnassas.\n'
            u'ja villi on leimaus katseessas.--\n'
            u'peru päiviltä muinaisilta se lie\n'
            u'kun käytiin katkera kostontie.'
            )

        expected = (
            u'Ei ol.ko kai.puum.me kuin haa.ve nai.sen.tai sai.raan nä.ky,\n'
            u'hou.re hu.ma.lai.sen.\n\n'

            u'Nuo ää.net on kuo.ro.na rin.nas.sas.\n'
            u'ja vil.li on lei.ma.us kat.sees.sas.--\n'
            u'pe.ru päi.vil.tä mui.nai.sil.ta se lie\n'
            u'kun käy.tiin kat.ke.ra kos.ton.ti.e.'
            )

        self.assertEqual(F.syllabify_sent(lines), expected)

    def test_is_vowel_consonant_capitalization(self):
        # ensure that is_vowel() and is_consonant() work for both upper and
        # lowercase letters
        vowels = phon.VOWELS + phon.VOWELS.upper()
        consonants = u'dhjklmnprstv' + u'dhjklmnprstv'.upper()

        for ch in vowels:
            self.assertEqual(phon.is_vowel(ch), True)
            self.assertEqual(phon.is_consonant(ch), False)

        for ch in consonants:
            self.assertEqual(phon.is_vowel(ch), False)
            self.assertEqual(phon.is_consonant(ch), True)


class TestVariantOrdering(unittest.TestCase):

    def test_variant_ordering(self):
        # ensure that the syllabifier returns variants in order from most
        # preferred to least preferred
        F = FinnSyll(split_compounds=True, variation=True, track_rules=False)

        with open('tests/ranked_sylls.pickle', 'r+') as f:
            pairs = pickle.load(f)

        errors = 0

        for i, expected in pairs.iteritems():
            try:
                test = F.syllabify(unicode(i, 'utf-8').lower())

            except TypeError:
                test = F.syllabify(i.lower())

            try:
                self.assertEqual(test, expected)

            except AssertionError as e:
                errors += 1
                message = ''

                for line in e.message.split('\n'):

                    if line.startswith('-'):
                        message += line + '\n'
                    elif line.startswith('+'):
                        message += line

                print message + '\n'

        if errors:
            raise AssertionError(errors)


class TestSegmenter(unittest.TestCase):

    def test_segmenter(self):
        # ensure that FinnSylll.split() splits words into any constituent words
        F = FinnSyll()

        cases = {
            'runoja': u'runoja',
            'oikeus': u'oikeus',
            'kuukautta': u'kuu=kautta',
            'linja-autoaseman': u'linja-auto=aseman',
            'loppuottelussa': u'loppu=ottelussa',
            'muutostöitä': u'muutos=töitä',
            }

        error_helper(self, F.split, cases)

    def test_is_compound(self):
        # ensure that FinnSylll.is_compound() detects compounds
        F = FinnSyll()

        cases = {
            'runoja': False,
            'oikeus': False,
            'kuukautta': True,
            'linja-autoaseman': True,
            'loppuottelussa': True,
            'muutostöitä': True,
            }

        error_helper(self, F.is_compound, cases)


class TestConstraints(unittest.TestCase):

    def test_min_word(self):
        # ensure that min_word() detects 'minimal word' violations
        cases = {
            # violations
            u'Ä': False,    # V
            u'CE': False,   # CV
            u'ÄC': False,   # VC
            u'CEC': False,  # CVC
            u'C': False,    # C
            u'CC': False,   # CC
            # good
            u'ÄÄ': True,    # VV
            u'CEE': True,   # CVV
            u'ÄÄC': True,   # VVC
            u'ECE': True,   # CVC
            }

        for k, v in cases.items():
            cases[k.lower()] = v

        error_helper(self, phon.min_word, cases)

    def test_word_final(self):
        # ensure that word_final() detects words that do not end in vowels or
        # coronal consonants
        cases = {
            # violations
            u'äk': False,
            u'ep': False,
            u'eng': False,
            u'äd': False,
            u'd': False,
            u'eg': False,
            # good
            u'än': True,
            u'es': True,
            u'et': True,
            u'n': True,
            u'ä': True,
            u'ätt': True,
            }

        for k, v in cases.items():
            cases[k.upper()] = v

        error_helper(self, phon.word_final, cases)

    def test_sonseq(self):
        # ensure that sonseq() detects 'sonority sequencing' violations
        cases = {
            # violations
            u'äpl': False,  # bad sonority slopes
            u'nta': False,
            u'mpa': False,
            u'nne': False,
            u'tshe': False,
            u'tlä': False,
            u'cks': False,  # word-final CC in Finnish interjections
            u'aps': False,
            u'itts': False,
            u'bri': False,  # foreign CC
            u'fri': False,
            u'erg': False,
            # good
            u'psy': True,   # borrowed word-initial CC
            u'tsa': True,
            u'sna': True,
            u'dra': True,
            u'pri': True,   # Finnish word-initial CC
            u'sta': True,
            u'kri': True,
            u'plä': True,
            u'stra': True,  # Finnish word-initial CCC
            u'spra': True,
            u'a': True,     # V
            u'c': True,     # C
            u'cac': True,   # CVC
            }

        for k, v in cases.items():
            cases[k.upper()] = v

        error_helper(self, phon.sonseq, cases)

    def test_harmonic(self):
        # ensure that harmonic() detects 'vowel harmony' violations
        cases = {
            # violations
            u'kesäillan': False,    # closed compounds
            u'taaksepäin': False,
            u'muutostoitä': False,
            u'kallström': False,    # loanwords
            u'donaueschingenissä': False,
            u'finlaysonin': False,
            u'affärer]': False,
            # good
            u'kesä': True,          # Finnish stems
            u'illan': True,
            u'taakse': True,
            u'päin': True,
            u'muutos': True,
            u'töitä': True,
            u'yleensä': True,
            }

        for k, v in cases.items():
            cases[k.upper()] = v

        error_helper(self, phon.harmonic, cases)

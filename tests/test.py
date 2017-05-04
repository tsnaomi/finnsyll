# coding=utf-8
# python -m unittest discover

try:
    import cpickle as pickle

except ImportError:
    import pickle

import unittest
import finnsyll.phonology as phon
import finnsyll.utilities as utilities

from finnsyll import FinnSyll


def error_helper(self, func, cases):
    # accrue all of the errors for each test and print them in bulk
    errors = []

    for i, expected in cases.items():
        test = func(i)

        try:
            # print '\n', (test)
            # print(expected)
            self.assertEqual(test, expected)

        except AssertionError as exception:
            errors.append(str(exception))

    if errors:

        try:
            raise AssertionError('\n\n' + '\n\n'.join(errors).encode('utf-8'))

        except TypeError:
            raise AssertionError('\n\n' + '\n\n'.join(errors))


class TestSyllabifierKwargs(unittest.TestCase):

    def test_full_functionality(self):
        # ensure that the syllabifier returns all known variants and applied
        # rules as a list of tuples, with compound splitting and stress
        # assignment
        F = FinnSyll(split=True, variation=True, rules=True, stress=True)

        cases = {
            # simplex, no variation
            'runoja': [
                ('\'ru.no.ja', 'T1'),
                ],
            # simplex, variation
            'oikeus': [
                ('\'oi.ke.us', 'T1 T4'),
                ('\'oi.keus', 'T1'),
                ],
            # complex, no variation
            'kuukautta': [
                ('\'kuu.\'kaut.ta', 'T0 = T1'),
                ],
            # complex, variation
            'hovioikeus': [
                ('\'ho.vi.\'oi.ke.us', 'T1 = T1 T4'),
                ('\'ho.vi.\'oi.keus', 'T1 = T1'),
                ],
            }

        error_helper(self, F.syllabify, cases)

    def test_no_stress(self):
        # ensure that the syllabifier returns all known variants and applied
        # rules as a list of tuples, with compound splitting or stress
        # assignment
        F = FinnSyll(split=True, variation=True, rules=True, stress=False)

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
        # rules as a list of tuples, minus compound splitting but including
        # stress assignment
        F = FinnSyll(split=False, variation=True, rules=True, stress=True)

        cases = {
            # simplex, no variation
            'runoja': [
                ('\'ru.no.ja', 'T1'),
                ],
            # simplex, variation
            'oikeus': [
                ('\'oi.ke.us', 'T1 T4'),
                ('\'oi.keus', 'T1'),
                ],
            # complex, no variation
            'jukolantupien': [
                ('\'ju.ko.`lan.tu.`pi.en', 'T1 T2'),
                ],
            # complex, variation
            'hovioikeus': [
                ('\'ho.vi.`oi.ke.us', 'T1 T2 T4'),
                ('\'ho.vi.`oi.keus', 'T1 T2'),
                ],
            }

        error_helper(self, F.syllabify, cases)

    def test_no_variation(self):
        # ensure that the syllabifier returns the most preferred variant and
        # its applied rules as a tuple, with compound splitting and stress
        # assignment
        F = FinnSyll(split=True, variation=False, rules=True, stress=True)

        cases = {
            # simplex, no variation
            'runoja': ('\'ru.no.ja', 'T1'),
            # simplex, variation
            'oikeus': ('\'oi.ke.us', 'T1 T4'),
            # complex, no variation
            'kuukautta': ('\'kuu.\'kaut.ta', 'T0 = T1'),
            # complex, variation
            'hovioikeus': ('\'ho.vi.\'oi.ke.us', 'T1 = T1 T4'),
            }

        error_helper(self, F.syllabify, cases)

    def test_no_rules(self):
        # ensure that the syllabifier returns all known variants as a list of
        # strings, with compound splitting and stress assignment
        F = FinnSyll(split=True, variation=True, rules=False, stress=True)

        cases = {
            # simplex, no variation
            'runoja': [
                '\'ru.no.ja',
                ],
            # simplex, variation
            'oikeus': [
                '\'oi.ke.us',
                '\'oi.keus',
                ],
            # complex, no variation
            'kuukautta': [
                '\'kuu.\'kaut.ta',
                ],
            # complex, variation
            'hovioikeus': [
                '\'ho.vi.\'oi.ke.us',
                '\'ho.vi.\'oi.keus',
                ],
            }

        error_helper(self, F.syllabify, cases)

    def test_no_variation_or_stress(self):
        # ensure that the syllabifier returns the most preferred variant and
        # its applied rules as a tuple, with compound splitting but minus
        # stress assignment
        F = FinnSyll(split=True, variation=False, rules=True, stress=False)

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

    def test_no_splitting_or_stress(self):
        # ensure that the syllabifier returns all known variants and applied
        # rules as a list of tuples, minus compound splitting and stress
        # assignment
        F = FinnSyll(split=False, variation=True, rules=True, stress=False)

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

    def test_no_rules_or_stress(self):
        # ensure that the syllabifier returns all known variants as a list of
        # strings, with compound splitting but minus stress assignment
        F = FinnSyll(split=True, variation=True, rules=False, stress=False)

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

    def test_no_splitting_or_rules(self):
        # ensure that the syllabifier returns all known variants as a list of
        # strings, minus compound splitting but including stress assignment
        F = FinnSyll(split=False, variation=True, rules=False, stress=True)

        cases = {
            # simplex, no variation
            'runoja': [
                '\'ru.no.ja',
                ],
            # simplex, variation
            'oikeus': [
                '\'oi.ke.us',
                '\'oi.keus',
                ],
            # complex, no variation
            'jukolantupien': [
                '\'ju.ko.`lan.tu.`pi.en',
                ],
            # complex, variation
            'hovioikeus': [
                '\'ho.vi.`oi.ke.us',
                '\'ho.vi.`oi.keus',
                ],
            }

        error_helper(self, F.syllabify, cases)

    def test_no_splitting_or_variation(self):
        # ensure that the syllabifier returns the most preferred variant and
        # its applied rules as a tuple, minus compound splitting but including
        # stress assignment
        F = FinnSyll(split=False, variation=False, rules=True, stress=True)

        cases = {
            # simplex, no variation
            'runoja': ('\'ru.no.ja', 'T1'),
            # simplex, variation
            'oikeus': ('\'oi.ke.us', 'T1 T4'),
            # complex, no variation
            'kuukautta': ('\'kuu.ka.`ut.ta', 'T1 T4'),
            # complex, variation
            'hovioikeus': ('\'ho.vi.`oi.ke.us', 'T1 T2 T4'),
            }

        error_helper(self, F.syllabify, cases)

    def test_no_variation_or_rules(self):
        # ensure that the syllabifier returns the most preferred variant as a
        # string, with compound splitting and stress assignment
        F = FinnSyll(split=True, variation=False, rules=False, stress=True)

        cases = {
            # simplex, no variation
            'runoja': '\'ru.no.ja',
            # simplex, variation
            'oikeus': '\'oi.ke.us',
            # complex, no variation
            'kuukautta': '\'kuu.\'kaut.ta',
            # complex, variation
            'hovioikeus': '\'ho.vi.\'oi.ke.us',
            }

        error_helper(self, F.syllabify, cases)

    def test_no_splitting_or_variation_or_stress(self):
        # ensure that the syllabifier returns the most preferred variant and
        # its applied rules as a tuple, minus compound splitting and stress
        # assignment
        F = FinnSyll(split=False, variation=False, rules=True, stress=False)

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

    def test_no_splitting_or_rules_or_stress(self):
        # ensure that the syllabifier returns all known variants as a list of
        # strings, minus compound splitting and stress assignment
        F = FinnSyll(split=False, variation=True, rules=False, stress=False)

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

    def test_no_variation_or_rules_or_stress(self):
        # ensure that the syllabifier returns the most preferred variant as a
        # string, with compound splitting but minus stress assignment
        F = FinnSyll(split=True, variation=False, rules=False, stress=False)

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
        # string, minus compound splitting but including stress assignment
        F = FinnSyll(split=False, variation=False, rules=False, stress=True)

        cases = {
            # simplex, no variation
            'runoja': '\'ru.no.ja',
            # simplex, variation
            'oikeus': '\'oi.ke.us',
            # complex, no variation
            'kuukautta': '\'kuu.ka.`ut.ta',
            # complex, variation
            'hovioikeus': '\'ho.vi.`oi.ke.us',
            }

        error_helper(self, F.syllabify, cases)

    def test_no_splitting_or_variation_or_rules_or_stress(self):
        # ensure that the syllabifier returns the most preferred variant as a
        # string, minus compound splitting and stress assignment
        F = FinnSyll(split=False, variation=False, rules=False, stress=False)

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

    def test_str_unicode_input(self):
        # ensure that the syllabifier outputs utf-8 decoded unicode while
        # accepting byte or unicode input
        F = FinnSyll(split=True, variation=False, rules=False, stress=False)
        errors = []

        cases = ('kesäillan', u'kesäillan')

        for case in cases:
            try:
                self.assertEqual(F.syllabify(case), u'ke.sä.il.lan')

            except AssertionError as e:
                errors.append(e.message)

        if errors:
            raise AssertionError('\n\n' + '\n\n'.join(errors).encode('utf-8'))

    def test_non_str_unicode_input(self):
        # ensure that the syllabifier throws up when it receives non-str /
        # non-unicode input
        F = FinnSyll(split=True, variation=False, rules=False, stress=False)

        cases = (31415926, True)

        for case in cases:
            with self.assertRaises(TypeError):
                F.syllabify(case)

    def test_punctuated_input(self):
        # ensure that the syllabififer can syllabify delimited and punctuated
        # input
        F = FinnSyll(split=True, variation=False, rules=False, stress=False)

        lines = (
            u'Ei olko kaipuumme kuin haave naisentai sairaan näky,\n'
            u'houre humalaisen.\n\n'

            u'Nuo äänet on kuorona rinnassas.\n'
            u'ja villi on leimaus katseessas.--\n'
            u'peru päiviltä muinaisilta se lie\n'
            u'kun käytiin katkera kostontie.\n\n'

            u'hypo_lemma'  # hypothetical lemma
            )

        expected = (
            u'Ei ol.ko kai.puum.me kuin haa.ve nai.sen.tai sai.raan nä.ky,\n'
            u'hou.re hu.ma.lai.sen.\n\n'

            u'Nuo ää.net on kuo.ro.na rin.nas.sas.\n'
            u'ja vil.li on lei.ma.us kat.sees.sas.--\n'
            u'pe.ru päi.vil.tä mui.nais.il.ta se lie\n'
            u'kun käy.tiin kat.ke.ra kos.ton.tie.\n\n'

            u'hy.po_lem.ma'
            )

        self.assertEqual(F.syllabify(lines), expected)

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

    def test_edge_cases(self):
        # ensure that the syllabifier can handle edge cases not included in
        # the Aamulehti corpus
        F = FinnSyll(split=True, variation=False, rules=False, stress=False)

        cases = {
            'nauumme': u'nau.um.me',
            'leuun': u'leu.un',
            'riuun': u'riu.un',
            # 'ruoon': u'ruo.on',
        }

        with self.assertRaises(AssertionError):
            assert F.syllabify('ruoon') == u'ruo.on'

        error_helper(self, F.syllabify, cases)


class TestAnotation(unittest.TestCase):

    def test_stress_assignment(self):
        # ensure that the syllabifier can assign stress to syllabifications
        F = FinnSyll(split=True, variation=True, rules=False, stress=True)

        cases = {
            # punctuated input
            'ja villi on leimaus katseessas.--\nperu': [
                '\'ja \'vil.li \'on \'lei.ma.us \'kat.sees.sas.--\n\'pe.ru',
                '\'ja \'vil.li \'on \'lei.maus \'kat.sees.sas.--\n\'pe.ru',
                ],
            # secondary stress
            'voimistelutti': [
                '\'voi.mis.te.`lut.ti',
                ],
            # caveat
            'voimistelut': [
                '\'voi.mis.`te.lut',
                ]
            }

        error_helper(self, F.syllabify, cases)

    def test_annotate(self):
        # ensure that the syllabifier can extract stress, weights, and vowel
        # qualities in syllabifications
        F1 = FinnSyll(split=True)
        F2 = FinnSyll(split=False)

        cases1 = {
            'kellon': [
                ('\'kel.lon', 'PU', 'HH', 'EO'),
                ],
            'ontuvaa': [
                ('\'on.tu.vaa', 'PUU', 'HLH', 'OUA'),
                ],
            'naksutusta': [
                ('\'nak.su.`tus.ta', 'PUSU', 'HLHL', 'AUUA'),
                ],
            'hovioikeus': [
                ('\'ho.vi.\'oi.ke.us', 'PUPUU', 'LLHLH', 'OIOEU'),
                ('\'ho.vi.\'oi.keus', 'PUPU', 'LLHH', 'OIOE'),
                ],
            'hovi oikeus': [
                ('\'ho.vi \'oi.ke.us', 'PU PUU', 'LL HLH', 'OI OEU'),
                ('\'ho.vi \'oi.keus', 'PU PU', 'LL HH', 'OI OE'),
                ],
            'liu\'uttaa': [
                ('\'liu\'\'ut.taa', 'P PU', 'H HH', 'I UA'),
                ],
            }

        cases2 = {
            'hovioikeus': [
                ('\'ho.vi.`oi.ke.us', 'PUSUU', 'LLHLH', 'OIOEU'),
                ('\'ho.vi.`oi.keus', 'PUSU', 'LLHH', 'OIOE'),
                ],
            'hovi oikeus': [
                ('\'ho.vi \'oi.ke.us', 'PU PUU', 'LL HLH', 'OI OEU'),
                ('\'ho.vi \'oi.keus', 'PU PU', 'LL HH', 'OI OE'),
                ],
            }

        error_helper(self, F1.annotate, cases1)
        error_helper(self, F2.annotate, cases2)


class TestVariantOrdering(unittest.TestCase):  # TODO: TEST WITH STRESS

    def test_variant_ordering_no_stress(self):
        # ensure that the syllabifier returns variants in order from most
        # preferred to least preferred
        F = FinnSyll(split=True, variation=True, rules=False, stress=False)

        with open('tests/ranked_sylls.pickle', 'rb') as f:
            pairs = pickle.load(f)

        errors = 0

        for i, expected in pairs.items():

            try:
                test = F.syllabify(unicode(i, 'utf-8').lower())

            except (TypeError, NameError):
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

                print(message + '\n')

        if errors:
            raise AssertionError(errors)


class TestSegmenter(unittest.TestCase):

    def test_segmenter(self):
        # ensure that FinnSylll.split() splits words into any constituent words
        F = FinnSyll(split=True, variation=True, rules=False, stress=False)

        cases = {
            'runoja': u'runoja',
            'oikeus': u'oikeus',
            'kuukautta': u'kuu=kautta',
            'linja-autoaseman': u'linja-auto=aseman',
            'loppuottelussa': u'loppu=ottelussa',
            'muutostöitä': u'muutos=töitä',
            'kesäillan': u'kesä=illan',
            'äidinkielen': u'äidin=kielen',
            'ääntenenemmistöllä': u'äänten=enemmistöllä',
            }

        error_helper(self, F.split, cases)

    def test_punctuated_capitalized_input(self):
        # ensure that FinnSyll.split() can split delimited, punctuated, and
        # capitalized input
        F = FinnSyll(split=True, variation=True, rules=False, stress=False)

        case = (
            'runoja_oikeus8910kuukautta linja-AUTOASEMAN'
            '....Loppuottelussa//muutostöitä1234kesäillan'
            )

        expected = (
            u'runoja_oikeus8910kuu=kautta linja-AUTO=ASEMAN'
            u'....Loppu=ottelussa//muutos=töitä1234kesä=illan'
            )

        self.assertEqual(F.split(case), expected)

    def test_is_complex(self):
        # ensure that FinnSylll.is_complex() detects compounds
        F = FinnSyll(split=True, variation=True, rules=False, stress=False)

        cases = {
            'runoja': False,
            'oikeus': False,
            'kuukautta': True,
            'linja-autoaseman': True,
            'loppuottelussa': True,
            'muutostöitä': True,
            }

        error_helper(self, F.is_complex, cases)


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

        cases = {k.upper(): v for k, v in cases.items()}

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

        cases = {k.upper(): v for k, v in cases.items()}

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

        cases = {k.upper(): v for k, v in cases.items()}

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

        cases = {k.upper(): v for k, v in cases.items()}

        error_helper(self, phon.harmonic, cases)


class TestUtilities(unittest.TestCase):

    def test_nonalpha_split(self):
        # ensure that utitilies.nonalpha_split() splits strings along any
        # punctuation or whitespace
        lines = (
            'Nuo äänet on kuorona~rinnassas.\n'
            'ja villi.on leimaus katseessas.--\n'
            'peru päiviltä/muinaisilta se lie\n'
            'kun käytiin katkera kostontie.\n\n'
            'muutostöitä'
            )

        expected = [
            'Nuo', ' ', 'äänet', ' ', 'on', ' ', 'kuorona', '~', 'rinnassas',
            '.\n', 'ja', ' ', 'villi', '.', 'on', ' ', 'leimaus', ' ',
            'katseessas', '.--\n', 'peru', ' ', 'päiviltä', '/',
            'muinaisilta', ' ', 'se', ' ', 'lie', '\n', 'kun', ' ', 'käytiin',
            ' ', 'katkera', ' ', 'kostontie', '.\n\n', 'muutostöitä',
            ]

        self.assertEqual(utilities.nonalpha_split(lines), expected)

    def test_syllable_split(self):
        # ensure that utitilies.syllable_split() splits strings into (stressed)
        # syllables and punctuation/whitespace
        lines = (
            'Nuo ää.net on kuo.ro.na~rin.näs.säs.\n'
            'ja vil.li on/lei.ma.us kat.sees.sas.--\n'
            'räin \'ju.ko.`lan.tu.`pi.en \'liu\'\'ut.taa'
            )

        expected = [
            'Nuo', ' ', 'ää', 'net', ' ', 'on', ' ', 'kuo', 'ro', 'na', '~',
            'rin', 'näs', 'säs', '\n', 'ja', ' ', 'vil', 'li', ' ', 'on', '/',
            'lei', 'ma', 'us', ' ', 'kat', 'sees', 'sas', '--\n', 'räin', ' ',
            '\'ju', 'ko', '`lan', 'tu', '`pi', 'en', ' ', '\'liu', '\'',
            '\'ut', 'taa'
            ]

        self.assertEqual(utilities.syllable_split(lines), expected)

    def test_extract_words(self):
        # ensure that utitilies.extract_words() extracts any alphabetic
        # syllabified string
        lines = (
            '.Nuo ää.net on kuo.ro.na~rin.näs.säs.\n'
            'ja vil.li on/lei.ma.us kat.sees.sas.--\n'
            )

        expected = [
            'Nuo', 'ää.net', 'on', 'kuo.ro.na', 'rin.näs.säs',
            'ja', 'vil.li', 'on', 'lei.ma.us', 'kat.sees.sas',
            ]

        self.assertEqual(utilities.extract_words(lines), expected)

# coding=utf-8

# python -m unittest discover

import unittest

try:
    # Python 3
    from ..finnsyll.phonology import min_word, word_final, sonseq, harmonic
    from ..finnsyll import FinnSyll

except (ImportError, ValueError):
    # Python 2
    from finnsyll.phonology import min_word, word_final, sonseq, harmonic
    from finnsyll import FinnSyll


# CIN = Correctly incorrect

class TestSyllabifierArguments(unittest.TestCase):

    def test_full_functionality(self):
        F = FinnSyll(split_compounds=True, variation=True, track_rules=True)

        # simplex, no variation
        expected = [('ru.no.ja', 'T1')]
        test = F.syllabify('runoja')
        self.assertEqual(test, expected)

        # simplex, variation
        expected = [('oi.ke.us', 'T1 T4'), ('oi.keus', 'T1')]
        test = F.syllabify('oikeus')
        self.assertEqual(test, expected)

        # complex, no variation
        expected = [('kuu.kaut.ta', 'T0 = T1')]
        test = F.syllabify('kuukautta')  # kuu=kautta
        self.assertEqual(test, expected)

        # complex, no variation
        expected = [('en.si-il.ta', 'T1 = T1')]
        test = F.syllabify('ensi-ilta')
        self.assertEqual(test, expected)

        # complex, variation
        expected = [('ho.vi.oi.ke.us', 'T1 = T1 T4'), ('ho.vi.oi.keus', 'T1 = T1')]  # noqa
        test = F.syllabify('hovioikeus')  # hovi=oikeus
        self.assertEqual(test, expected)

    def test_no_splitting(self):
        F = FinnSyll(split_compounds=False, variation=True, track_rules=True)

        # simplex, no variation
        expected = [('ru.no.ja', 'T1')]
        test = F.syllabify('runoja')
        self.assertEqual(test, expected)

        # simplex, variation
        expected = [('oi.ke.us', 'T1 T4'), ('oi.keus', 'T1')]
        test = F.syllabify('oikeus')
        self.assertEqual(test, expected)

        # complex, no variation
        expected = [('ju.ko.lan.tu.pi.en', 'T1 T2')]
        test = F.syllabify('jukolantupien')  # jukolan=tupien
        self.assertEqual(test, expected)

        # complex, variation
        expected = [('ho.vi.oi.ke.us', 'T1 T2 T4'), ('ho.vi.oi.keus', 'T1 T2')]
        test = F.syllabify('hovioikeus')  # hovi=oikeus
        self.assertEqual(test, expected)

    def test_no_variation(self):
        F = FinnSyll(split_compounds=True, variation=False, track_rules=True)

        # simplex, no variation
        expected = ('ru.no.ja', 'T1')
        test = F.syllabify('runoja')
        self.assertEqual(test, expected)

        # simplex, variation
        expected = ('oi.ke.us', 'T1 T4')  # CIN
        test = F.syllabify('oikeus')
        self.assertEqual(test, expected)

        # complex, no variation
        expected = ('kuu.kaut.ta', 'T0 = T1')
        test = F.syllabify('kuukautta')  # kuu=kautta
        self.assertEqual(test, expected)

        # complex, variation
        expected = ('ho.vi.oi.ke.us', 'T1 = T1 T4')  # CIN
        test = F.syllabify('hovioikeus')  # hovi=oikeus
        self.assertEqual(test, expected)

    def test_no_rules(self):
        F = FinnSyll(split_compounds=True, variation=True, track_rules=False)

        # simplex, no variation
        expected = ['ru.no.ja']
        test = F.syllabify('runoja')
        self.assertEqual(test, expected)

        # simplex, variation
        expected = ['oi.ke.us', 'oi.keus']
        test = F.syllabify('oikeus')
        self.assertEqual(test, expected)

        # complex, no variation
        expected = ['kuu.kaut.ta']
        test = F.syllabify('kuukautta')  # kuu=kautta
        self.assertEqual(test, expected)

        # complex, variation
        expected = ['ho.vi.oi.ke.us', 'ho.vi.oi.keus']
        test = F.syllabify('hovioikeus')  # hovi=oikeus
        self.assertEqual(test, expected)

    def test_no_splitting_or_variation(self):
        F = FinnSyll(split_compounds=False, variation=False, track_rules=True)

        # simplex, no variation
        expected = ('ru.no.ja', 'T1')
        test = F.syllabify('runoja')
        self.assertEqual(test, expected)

        # simplex, variation
        expected = ('oi.ke.us', 'T1 T4')  # CIN
        test = F.syllabify('oikeus')
        self.assertEqual(test, expected)

        # complex, no variation
        expected = ('kuu.ka.ut.ta', 'T1 T4')  # CIN
        test = F.syllabify('kuukautta')  # kuu=kautta
        self.assertEqual(test, expected)

        # complex, variation
        expected = ('ho.vi.oi.ke.us', 'T1 T2 T4')  # CIN
        test = F.syllabify('hovioikeus')  # hovi=oikeus
        self.assertEqual(test, expected)

    def test_no_splitting_or_rules(self):
        F = FinnSyll(split_compounds=False, variation=True, track_rules=False)

        # simplex, no variation
        expected = ['ru.no.ja']
        test = F.syllabify('runoja')
        self.assertEqual(test, expected)

        # simplex, variation
        expected = ['oi.ke.us', 'oi.keus']
        test = F.syllabify('oikeus')
        self.assertEqual(test, expected)

        # complex, no variation
        expected = ['ju.ko.lan.tu.pi.en']
        test = F.syllabify('jukolantupien')  # jukolan=tupien
        self.assertEqual(test, expected)

        # complex, variation
        expected = ['ho.vi.oi.ke.us', 'ho.vi.oi.keus']
        test = F.syllabify('hovioikeus')  # hovi=oikeus
        self.assertEqual(test, expected)

    def test_no_variation_or_rules(self):
        F = FinnSyll(split_compounds=True, variation=False, track_rules=False)

        # simplex, no variation
        expected = 'ru.no.ja'
        test = F.syllabify('runoja')
        self.assertEqual(test, expected)

        # simplex, variation
        expected = 'oi.ke.us'  # CIN
        test = F.syllabify('oikeus')
        self.assertEqual(test, expected)

        # complex, no variation
        expected = 'kuu.kaut.ta'
        test = F.syllabify('kuukautta')  # kuu=kautta
        self.assertEqual(test, expected)

        # complex, variation
        expected = 'ho.vi.oi.ke.us'  # CIN
        test = F.syllabify('hovioikeus')  # hovi=oikeus
        self.assertEqual(test, expected)

    def test_no_splitting_or_variation_or_rules(self):
        F = FinnSyll(split_compounds=False, variation=False, track_rules=False)

        # simplex, no variation
        expected = 'ru.no.ja'
        test = F.syllabify('runoja')
        self.assertEqual(test, expected)

        # simplex, variation
        expected = 'oi.ke.us'  # CIN
        test = F.syllabify('oikeus')
        self.assertEqual(test, expected)

        # complex, no variation
        expected = 'kuu.ka.ut.ta'  # CIN
        test = F.syllabify('kuukautta')  # kuu=kautta
        self.assertEqual(test, expected)

        # complex, variation
        expected = 'ho.vi.oi.ke.us'  # CIN
        test = F.syllabify('hovioikeus')  # hovi=oikeus
        self.assertEqual(test, expected)


class TestSegmenter(unittest.TestCase):

    def test_segmenter(self):
        F = FinnSyll()

        self.assertEqual(F.split('runoja'), 'runoja')
        self.assertEqual(F.split('oikeus'), 'oikeus')
        self.assertEqual(F.split('kuukautta'), 'kuu=kautta')
        self.assertEqual(F.split('linja-autoaseman'), 'linja-auto=aseman')
        self.assertEqual(F.split('loppuottelussa'), 'loppu=ottelussa')
        self.assertEqual(F.split('muutostöitä'), 'muutos=töitä')

    def test_is_compound(self):
        F = FinnSyll()

        self.assertFalse(F.is_compound('runoja'))
        self.assertFalse(F.is_compound('oikeus'))
        self.assertTrue(F.is_compound('kuukautta'))
        self.assertTrue(F.is_compound('linja-autoaseman'))
        self.assertTrue(F.is_compound('loppuottelussa'))
        self.assertTrue(F.is_compound('muutostöitä'))


class TestConstraints(unittest.TestCase):

    def test_min_word(self):
        pairs = [
            # violations
            ('a', False),  # V
            ('n', False),  # C
            ('kA', False),  # CV
            ('en', False),  # VC
            ('jat', False),  # CVC
            ('kk', False),  # CC

            # not violations
            ('AA', True),  # VV
            ('vAi', True),  # CVV
            ('ien', True),  # VVC
            ('ita', True),  # VCV
        ]

        for test, expected in pairs:
            self.assertEqual(min_word(test), expected)

    def test_word_final(self):
        pairs = [
            # violations
            ('sulok', False),  # C[-coronal]#
            ('hyp', False),
            ('pitem', False),
            ('heng', False),
            ('k', False),
            ('hoid', False),  # /d/-final
            ('d', False),
            ('af', False),  # foreign-final
            ('berg', False),

            # not violations
            ('sairaan', True),  # C[+coronal]#
            ('oikeus', True),
            ('jat', True),
            ('n', True),
            ('jAA', True),  # V-final
            ('bott', True),  # CC[+coronal]#
        ]

        for test, expected in pairs:
            self.assertEqual(word_final(test), expected)

    def test_sonseq(self):
        pairs = [
            # violations
            ('dipl', False),  # bad sonority slopes
            ('ntupien', False),
            ('mpaa', False),
            ('nnin', False),
            ('nn', False),
            ('tsheenien', False),
            ('tlAA', False),

            # not violations
            ('psykologi', True),  # borrowed word-initial CC
            ('tsaari', True),
            ('snobi', True),
            ('draken', True),
            ('draama', True),
            ('primakovin', True),  # Finnish word-initial CC
            ('prosentti', True),
            ('stolaisilla', True),
            ('kritiikki', True),
            ('plAA', True),
            ('klAA', True),
            ('trAA', True),
            ('spAA', True),
            ('skAA', True),
            ('stressaavalle', True),  # Finnish word-initial CCC
            ('strategiansa', True),
            ('spriille', True),
            ('a', True),  # V
            ('n', True),  # C
            ('kas', True),  # CVC

            # uncertain
            ('niks', False),  # Finnish word-final CC
            ('naks', False),
            ('kops', False),
            ('raps', False),
            ('ritts', False),
            ('britannin', False),  # foreign CC
            ('friikeille', False),
            ('berg', False),
        ]

        for test, expected in pairs:
            self.assertEqual(sonseq(test), expected)

    def test_harmonic(self):
        pairs = [
            # violations
            ('kesAillan', False),  # closed compounds
            ('taaksepAin', False),
            ('muutostOitA', False),

            # not violations
            ('kesA', True),  # Finnish stems
            ('illan', True),
            ('taakse', True),
            ('pAin', True),
            ('muutos', True),
            ('tOitA', True),

            # uncertain
            ('kallstrOm', False),  # loanwords
            ('donaueschingenissA', False),
            ('finlaysonin', False),
            ('affArer]', False),
            ]

        for test, expected in pairs:
            self.assertEqual(harmonic(test), expected)


class TestVariation(unittest.TestCase):

    def test_ranking(self):
        F = FinnSyll(split_compounds=True, variation=True, track_rules=False)

        pairs = {
            'rakkauden':
                ['rak.kau.den', 'rak.ka.u.den'],
            'laukausta':
                ['lau.ka.us.ta', 'lau.kaus.ta'],
        }

        for test, expected in pairs.iteritems():
            self.assertEqual(F.syllabify(test), expected)


class TestUmlauts(unittest.TestCase):

    def test_umlaut_preservation(self):
        F = FinnSyll(split_compounds=False, variation=False, track_rules=False)

        # simplex, no variation
        expected = 'pi.tää'
        test = F.syllabify('pitää')
        self.assertEqual(test, expected)

        # simplex, variation
        expected = 'yh.te.yt.tä'
        test = F.syllabify('yhteyttä')
        self.assertEqual(test, expected)

        # complex, no variation
        expected = 'ke.säil.lan'
        test = F.syllabify('kesäillan')  # kesa=̈illan
        self.assertEqual(test, expected)

        # complex, variation
        expected = 'oi.ke.u.den.käyn.nis.sä'
        test = F.syllabify('oikeudenkäynnissä')  # oikeuden=käynnissä
        self.assertEqual(test, expected)

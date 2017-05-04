# coding=utf-8
from __future__ import unicode_literals

try:
    import cpickle as pickle

except ImportError:
    import pickle

try:
    from itertools import zip_longest as izip, product

except ImportError:
    from itertools import izip_longest as izip, product

import math
import morfessor
import os

from os.path import dirname, join
from .phonology import CONSTRAINTS, get_weight, get_vowel
from .utilities import nonalpha_split, syllable_split
from .v13 import syllabify


class FinnSyll:

    def __init__(
        self,
        split=True,
        variation=True,
        rules=False,
        stress=False,
            ):
        self.DEV = bool(os.environ.get('FINNSYLL_DEV'))
        self._split = FinnSeg().segment  # instantiate compound segmenter
        self.split_compounds = split
        self.vary = variation
        self.track_rules = rules
        self.assign_stress = stress

        # if "split" is True, normalizing the syllabifier's input will include
        # attempting to split the input into constituent words
        self.normalize = self.split if split else self._normalize  # TODO/CHECK

        # determine whether the syllabifier will produce variation and/or track
        # which rules have applied in a syllabification
        if variation and rules:
            self._syllabify = self._syllabify_vary_track
        elif variation:
            self._syllabify = self._syllabify_vary
        elif rules:
            self._syllabify = self._syllabify_track
        else:
            self._syllabify = self._syllabify_one

    def __repr__(self):
        return '<FinnSyll: split_compounds=%s variation=%s track_rules=%s>' % (
            str(self.split_compounds),
            str(self.variation),
            str(self.track_rules),
            )

    # pre-process -------------------------------------------------------------

    def _normalize(self, word):
        # convert word to unicode
        if isinstance(word, str):

            try:
                return word.decode('utf-8')

            except AttributeError:
                pass

        return word

    # syllabify ---------------------------------------------------------------

    def syllabify(self, word):
        '''Syllabify 'word'.'''
        return self._syllabify(self.normalize(word))

    def _syllabify_vary_track(self, word):
        # return all known variants and applied rules (as a list of tuples)
        return list(syllabify(word, stress=self.assign_stress))

    def _syllabify_vary(self, word):
        # return all known variants (as a list of strings), minus applied rules
        return [s for s, _ in syllabify(word, stress=self.assign_stress)]

    def _syllabify_track(self, word):
        # return the most preferred variant and its applied rules (as a tuple)
        for syll, rules in syllabify(word, stress=self.assign_stress):
            return syll, rules

    def _syllabify_one(self, word):
        # return the most preferred variant (as a string), minus applied rules
        for syll, _ in syllabify(word, stress=self.assign_stress):
            return syll

    # split -------------------------------------------------------------------

    def split(self, word):
        '''Split 'word' into any constituent words.'''
        return self._split(self._normalize(word))

    def is_complex(self, word):
        '''Return True if 'word' is composed of multiple words; else, False.'''
        return not self.split(word).isalpha()

    # annotation --------------------------------------------------------------

    def annotate(self, word):
        '''Annotate 'word' for syllabification, stress, weights, and vowels.'''
        info = []  # e.g., [ ('\'nak.su.`tus.ta', 'PUSU', 'HLHL', 'AUUA'), ]

        for syllabification, _ in syllabify(self.normalize(word), stress=True):
            stresses = ''
            weights = ''
            vowels = ''
            tail = ''

            for syll in syllable_split(syllabification):

                try:
                    vowels += get_vowel(syll)
                    weights += get_weight(syll)
                    stresses += {'\'': 'P', '`': 'S'}.get(syll[0], 'U')

                except AttributeError:

                    # if the syllable is vowel-less...
                    if syll[-1].isalpha():
                        tail = '*'

                    else:
                        stresses += ' '
                        weights += ' '
                        vowels += ' '

            info.append((
                syllabification,
                stresses + tail,
                weights + tail,
                vowels + tail,
                ))

        return info


class FinnSeg(object):

    def __init__(self):
        DIR = dirname(__file__)
        morfessor_file = join(DIR, 'data/finnsyll-morfessor.bin')
        ngram_file = join(DIR, 'data/finnsyll-ngrams.pickle')

        io = morfessor.MorfessorIO()
        self.model = io.read_binary_model_file(morfessor_file)
        self.constraints = CONSTRAINTS
        self.constraint_count = len(CONSTRAINTS)

        with open(ngram_file, 'rb') as f:
            self.ngrams, self.vocab, self.total = pickle.load(f)

    def __repr__(self):
        return '<FinnSeg>'

    def segment(self, word):
        token = []

        # split the word along any overt delimiters and iterate across the
        # components
        for comp in nonalpha_split(word):

            if len(comp) > 1 and comp[0].isalpha():

                # use the language model to obtain the component's morphemes
                # comp = comp.lower()
                morphemes = self.model.viterbi_segment(comp.lower())[0]

                # preserve capitalization of comp, since viterbi_segment() is
                # case-sensitive... WELP
                if comp != comp.lower():
                    indices = [0, ]
                    offset = 0
                    for m in morphemes[:-1]:
                        m = len(m) + offset
                        indices.append(m)
                        offset = m
                    indices = zip(indices, indices[1:] + [None, ])
                    morphemes = [comp[i:j] for i, j in indices]

                candidates = []
                delimiter_sets = product(['#', '&'], repeat=len(morphemes) - 1)

                # produce and score each candidate segmentation
                for d in delimiter_sets:
                    candidate = [x for y in izip(morphemes, d) for x in y]
                    candidate = [c for c in candidate if c]
                    candidates.append(candidate)

                candidates = self._score_candidates(comp, candidates)

                best = max(candidates)[0]
                candidates = [c for c in candidates if c[0] == best]

                # if multiple candidates have the same score, select the
                # least segmented candidate
                if len(candidates) > 1:
                    candidates.sort(key=lambda c: c[1].count('='))
                    comp = candidates[0][1]

                else:
                    comp = max(candidates)[1]

            token.append(comp)

        # return the segmentation in string form
        return ''.join(token)

    def _score_candidates(self, comp, candidates):
        count = len(candidates)

        # (['#', 'm', '&', 'm', '#', 'm', '#'], 'mm=m')
        for i, cand in enumerate(candidates):
            cand = ''.join(cand)
            cand = cand.replace('#', '=').replace('&', '')
            candidates[i] = (['#', ] + candidates[i] + ['#', ], cand)

        if count > 1:
            #         Cand1   Cand2
            # C1      [0,     0]
            # C2      [0,     0]
            # C3      [0,     0]
            tableau = [[0] * count for i in range(self.constraint_count)]

            for i, const in enumerate(self.constraints):
                for j, cand in enumerate(candidates):
                    for seg in cand[1].split('='):
                        tableau[i][j] += 0 if const.test(seg) else 1

                # ignore violations when they are incurred by every candidate
                min_violations = min(tableau[i])
                tableau[i] = [v - min_violations for v in tableau[i]]

            # tally the number of violations for each candidate
            violations = {
                c[1]: sum(
                    tableau[r][i] for r in range(self.constraint_count)
                    ) for i, c in enumerate(candidates)
                }

            # filter out candidates that violate any constraints
            candidates = [c for c in candidates if not violations[c[1]]]

            # if every candidate violates some constraint, back off to the
            # simplex candidate
            if len(candidates) == 0:
                return [(1.0, comp)]

        return [(self._score_candidate(c1), c2) for c1, c2 in candidates]

    def _score_candidate(self, candidate):  # Stupid Backoff smoothing
        score = 0

        for i, morpheme in enumerate(candidate):
            C = morpheme.lower()

            if i > 0:
                B = candidate[i-1].lower()

                if i > 1:
                    A = candidate[i-2].lower()
                    ABC = A + ' ' + B + ' ' + C
                    ABC_count = self.ngrams.get(ABC, 0)

                    if ABC_count:
                        AB = A + ' ' + B
                        AB_count = self.ngrams[AB]
                        score += math.log(ABC_count)
                        score -= math.log(AB_count)
                        continue

                BC = B + ' ' + C
                BC_count = self.ngrams.get(BC, 0)

                if BC_count:
                    B_count = self.ngrams[B]
                    score += math.log(BC_count * 0.4)
                    score -= math.log(B_count)
                    continue

            C_count = self.ngrams.get(C, 1)  # Laplace smoothed unigram
            score += math.log(C_count * 0.4 * 0.4)
            score -= math.log(self.total + len(self.vocab) + 1)

        return round(score, 4)

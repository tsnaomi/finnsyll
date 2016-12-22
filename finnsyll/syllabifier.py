# coding=utf-8

import math
import morfessor
import os
import re

try:
    import cpickle as pickle

except ImportError:
    import pickle

from os.path import dirname, join

try:
    # Python 3
    from itertools import zip_longest as izip, product

    from .phonology import CONSTRAINTS, replace_umlauts
    from .v9 import syllabify

except (ImportError, ValueError):
    # Python 2
    from itertools import izip_longest as izip, product

    from phonology import CONSTRAINTS, replace_umlauts
    from v12 import syllabify


class FinnSyll:

    def __init__(self, split_compounds=True, variation=True, track_rules=False):  # noqa
        self.DEV = bool(os.environ.get('FINNSYLL_DEV'))

        self.split_compounds = split_compounds
        self.variation = variation
        self.track_rules = track_rules

        self._split = FinnSeg().segment

        if split_compounds:
            self.normalize = self._normalize_then_split
        else:
            self.normalize = self._normalize

        if variation and track_rules:
            self._syllabify = self._syllabify_with_rules_and_variation
        elif variation:
            self._syllabify = self._syllabify_with_variation
        elif track_rules:
            self._syllabify = self._syllabify_with_rules
        else:
            self._syllabify = self._syllabify_single

        # SYLLABIFY:
        #   1. normalize
        #       1a. lowercase-ize word
        #       1b. replace_umlauts
        #       1c. split compound
        #   2. syllabify
        #       2a. syllabify
        #       2b. restore umlauts ?

        # SPLIT:
        #   1. normalize
        #       1a. lowercase-ize word
        #       1b. replace_umlauts
        #   2. split compound
        #   3. restore umlauts ?

    def __repr__(self):
        return '<FinnSyll: split_compounds=%s variation=%s track_rules=%s>' % (
            str(self.split_compounds),
            str(self.variation),
            str(self.track_rules),
            )

    def is_compound(self, word):
        return bool(re.search(r'(-| |=)', self.split(word)))

    def _normalize_then_split(self, word):
        return self._split(self._normalize(word))

    def _normalize(self, word):
        return replace_umlauts(word.decode('utf-8').lower().encode('utf-8'))

    # def _restore(self, word):  # necessary?
    #     return replace_umlauts(word, put_back=True)

    def split(self, word):
        # return self._restore(self._normalize_then_split(word))
        return self._normalize_then_split(word)

    def syllabify(self, word):
        return self._syllabify(self.normalize(word))

    def _syllabify_with_rules_and_variation(self, word):
        return list(syllabify(word))

    def _syllabify_with_variation(self, word):
        return [s for s, r in list(syllabify(word))]

    def _syllabify_with_rules(self, word):
        return list(syllabify(word))[0]  # TODO

    def _syllabify_single(self, word):
        return list(syllabify(word))[0][0]  # TODO


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
        for comp in re.split(r'(-| )', word):

            if len(comp) > 1:

                # use the language model to obtain the component's morphemes
                morphemes = self.model.viterbi_segment(comp)[0]

                candidates = []
                delimiter_sets = product(['#', 'X'], repeat=len(morphemes) - 1)

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

        # (['#', 'm', 'X', 'm', '#', 'm', '#'], 'mm=m')
        for i, cand in enumerate(candidates):
            cand = ''.join(cand)
            cand = cand.replace('#', '=').replace('X', '')
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
            C = morpheme

            if i > 0:
                B = candidate[i-1]

                if i > 1:
                    A = candidate[i-2]
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

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

    from .phonology import CONSTRAINTS
    from .v12 import syllabify

except (ImportError, ValueError):
    # Python 2
    from itertools import izip_longest as izip, product

    from phonology import CONSTRAINTS
    from v12 import syllabify


class FinnSyll:

    def __init__(self, split_compounds=True, variation=True, track_rules=False):  # noqa
        self.DEV = bool(os.environ.get('FINNSYLL_DEV'))
        self._split = FinnSeg().segment  # instantiate compound segmenter
        self.split_compounds = split_compounds
        self.variation = variation
        self.track_rules = track_rules

        # if "split" is True, normalizing the syllabifier's input will include
        # attempting to split the input into constituent words
        self.normalize = self.split if split_compounds else self._normalize

        # determine whether the syllabifier will produce variation and/or track
        # which rules have applied in a syllabification
        if variation and track_rules:
            self._syllabify = self._syllabify_vary_track
        elif variation:
            self._syllabify = self._syllabify_vary
        elif track_rules:
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
        try:
            # if bytes...
            return unicode(word, 'utf-8')

        except TypeError:
            # if unicode...
            return unicode(word.encode('utf-8'), 'utf-8')

    # syllabify ---------------------------------------------------------------

    def syllabify(self, word):
        '''Syllabify 'word'.'''
        return self._syllabify(self.normalize(word))

    def syllabify_sent(self, sentence):
        '''Syllabify 'sent', returning it as a single unicode string.

        The syllabified string will include only the most preferred variant for
        each word.
        '''
        tokens = []

        for w in re.split(r'([\W]+)', sentence, flags=re.I | re.U):
            if re.search(r'([\W]+)', w, flags=re.I | re.U):
                tokens.append(w)
            else:
                tokens.append(self._syllabify_one(w))

        return ''.join(tokens)

    def _syllabify_vary_track(self, word):
        # return all known variants and applied rules (as a list of tuples)
        return list(syllabify(word))

    def _syllabify_vary(self, word):
        # return all known variants (as a list of strings), minus applied rules
        return [s for s, _ in syllabify(word)]

    def _syllabify_track(self, word):
        # return the most preferred variant and its applied rules (as a tuple)
        for syll, rules in syllabify(word):
            return syll, rules

    def _syllabify_one(self, word):
        # return the most preferred variant (as a string), minus applied rules
        for syll, _ in syllabify(word):
            return syll

    # split -------------------------------------------------------------------

    def split(self, word):
        '''Split 'word' into any constituent words.'''
        return self._split(self._normalize(word))

    def is_compound(self, word):
        '''Return True if 'word' is a compound; else, False.'''
        return bool(re.search(r'(-| |=)', self.split(word)))


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
                comp = comp.lower().replace(u'ä', u'A').replace(u'ö', u'O')  # TODO
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

        # return the segmentation in string form  # TODO
        # return ''.join(token)

        segmentation = ''.join(token)  # TODO
        indices = [i for i, ch in enumerate(segmentation) if ch == '=']
        for i in indices:
            word = word[:i] + '=' + word[i:]
        return word

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
                        tableau[i][j] += 0 if const.test(seg.replace( u'A', u'ä').replace(u'O', u'ö')) else 1  # TODO

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

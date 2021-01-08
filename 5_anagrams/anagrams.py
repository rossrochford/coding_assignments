# Given a words.txt file containing a newline-delimited list of dictionary
# words, please implement the Anagrams class so that the get_anagrams() method
# returns all anagrams from words.txt for a given word.
#
# Bonus requirements:
#   - Optimise the code for fast retrieval
#   - Write more tests
#   - Thread safe implementation

import unittest

from collections import defaultdict

WORDS_FILEPATH = 'words.txt'


class Anagrams(object):

    def __init__(self):
        self.words = open(WORDS_FILEPATH).readlines()
        self.words = [w.strip().lower() for w in self.words]

        self.anagrams = defaultdict(list)
        for word in self.words:
            # key dictionary by string of character counts
            key = self._get_key(word)
            self.anagrams[key].append(word)

    @staticmethod
    def _get_key(word):
        word = word.lower()

        char_counts = defaultdict(int)
        for char in word:
            char_counts[char] += 1

        char_counts = [tup for tup in char_counts.items()]
        char_counts.sort(key=lambda tup: tup[0])
        char_counts = ['%s:%s' % tup for tup in char_counts]

        return '-'.join(char_counts)

    def get_anagrams(self, word):
        key = self._get_key(word)
        return self.anagrams[key]


class TestAnagrams(unittest.TestCase):

    def test_anagrams(self):
        anagrams = Anagrams()
        self.assertEquals(
            anagrams.get_anagrams('plates'),
            ['palest', 'pastel', 'petals', 'plates', 'staple']
        )
        self.assertEquals(anagrams.get_anagrams('eat'), ['ate', 'eat', 'tea'])


if __name__ == '__main__':
    unittest.main()

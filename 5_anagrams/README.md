# Anagrams

### Assignment Description:

Given a words.txt file containing a newline-delimited list of dictionary
words, please implement the Anagrams class so that the get_anagrams() method
returns all anagrams from words.txt for a given word.

##### Bonus requirements:
* Optimise the code for fast retrieval
* Write more tests
* Thread safe implementation


Here is the skeleton code to complete:

```
import unittest

class Anagrams(object):

    def __init__(self):
        self.words = open('words.txt').readlines()

    def get_anagrams(self, word):
        pass  # implement this


class TestAnagrams(unittest.TestCase):

    def test_anagrams(self):
        anagrams = Anagrams()
        self.assertEquals(
            anagrams.get_anagrams('plates'), 
            ['palest', 'pastel', 'petals', 'plates', 'staple']
        )
        self.assertEquals(anagrams.get_anagrams('eat'), ['ate', 'eat', 'tea'])
```


if __name__ == '__main__':
    unittest.main()
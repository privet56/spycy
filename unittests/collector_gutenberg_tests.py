import sys, os
import unittest

sys.path.append(os.getcwd()+'/../lib')

from collector_gutenberg import CollectorGutenberg

class KnownValues(unittest.TestCase):

    def test_log(self):
        '''
        test if CollectorGutenberg ansifies correctly
        '''

        g = CollectorGutenberg('source','datadir')

        s = "An ansi sentence with äüöß and an€ and an\u20b0."
        s_should = "An ansi sentence with auoss and anEUR and anPf."
        s_is = g.ansify(s)

        assert s_is == s_should

if __name__ == '__main__':
    unittest.main()

import sys, os
import unittest

sys.path.append(os.getcwd()+'/../lib')

from collector_partitur import Collector_partitur
from logger import Logger

class KnownValues(unittest.TestCase):

    def test_truncateSentence(self):


        logger = Logger(Logger.PREFIX4ONLY_STDOUT, Logger.PREFIX4ONLY_STDOUT)
        g = Collector_partitur('source','datadir', logger=logger)

        s_long = "also den anfang von dieser woche habe ich zur verfügung ich treffe vorbereitungen für die messe gegen ende der woche also den anfang von dieser woche habe ich zur verfügung ich treffe vorbereitungen für die messe gegen ende der woche"
        s_should_long = "also den anfang von dieser woche habe ich zur verfügung ich treffe vorbereitungen für die messe gegen ende der woche also den"
        s_is_long = g.truncateSentence(s_long)
        assert s_is_long == s_should_long

        s_short = "also den an"
        s_should_short = s_short
        s_is_short = g.truncateSentence(s_short)
        assert s_is_short == s_should_short


if __name__ == '__main__':
    unittest.main()

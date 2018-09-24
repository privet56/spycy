import sys, os
import unittest
import xml.etree.ElementTree as ET

sys.path.append(os.getcwd()+'/../lib')

from collector_partitur import Collector_partitur
from logger import Logger

class KnownValues(unittest.TestCase):

    def test_truncateSentenceLong(self):

        logger = Logger(Logger.PREFIX4ONLY_STDOUT, Logger.PREFIX4ONLY_STDOUT)
        g = Collector_partitur('source','datadir', logger=logger)

        s_long = "also den anfang von dieser woche habe ich zur verfügung ich treffe vorbereitungen für die messe gegen ende der woche also den anfang von dieser woche habe ich zur verfügung ich treffe vorbereitungen für die messe gegen ende der woche"
        s_should_long = "also den anfang von dieser woche habe ich zur verfügung ich treffe vorbereitungen für die messe gegen ende der woche also den"
        s_is_long = g.truncateSentence(s_long)
        assert s_is_long == s_should_long

    def test_truncateSentenceShort(self):

        logger = Logger(Logger.PREFIX4ONLY_STDOUT, Logger.PREFIX4ONLY_STDOUT)
        g = Collector_partitur('source','datadir', logger=logger)

        s_short = "also den an"
        s_should_short = s_short
        s_is_short = g.truncateSentence(s_short)
        assert s_is_short == s_should_short

    def test_clarifySentence(self):

        logger = Logger(Logger.PREFIX4ONLY_STDOUT, Logger.PREFIX4ONLY_STDOUT)
        g = Collector_partitur('source','datadir', logger=logger)
        ns = {'ag': 'http://www.ldc.upenn.edu/atlas/ag/'}

        sentence_should = "okay wahrscheinlich irgendwann früh nachmittags oder wir könnten den frühesten flug zurück nehmen könnten möglicherweise geschäftsschluß tschüß ungefähr"

        doc = ET.parse('collector_partitur_tests.ags')
        root = doc.getroot()
        for e in root.findall('./ag:AG[last()]/ag:Annotation[last()]/ag:Feature', ns):
            sentence = e.text.strip()
            if(sentence.startswith("EN>DE")):
                sentence = g.clarifySentence(" ".join(sentence[6:].lower().splitlines()))
                print(">>>"+sentence+"<<<")
                assert sentence == sentence_should



if __name__ == '__main__':
    unittest.main()

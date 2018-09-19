import sys, os
import unittest

sys.path.append(os.getcwd()+'/../lib')

from logger import Logger

class KnownValues(unittest.TestCase):

    def test_log(self):
        '''
        test if logger works correctly
        '''

        logger = Logger(Logger.PREFIX4ONLY_STDOUT,Logger.PREFIX4ONLY_STDOUT)

        msg = "a warning"
        s_should = "WRN " + msg
        s_is = logger.wrn(msg)

        assert s_is == s_should

if __name__ == '__main__':
    unittest.main()

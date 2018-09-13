import os, sys
import re
import pickle
class Collector:

    PICKLE_FILENAME_POSTFIX = ".collector.pickle"

    '''
    base class collector with basic functions
    to be extended
    '''

    # like constructor
    def __init__(self, source, datadir):
        self.source = source
        self.datadir = datadir
        self.aSRCs = None
        self.sCode = None
        self.lChars = None
        self.dChars2idx = None

    ''' helper functions '''
    @staticmethod
    def replacer(value):
        if ' ' in value and sum(1 for ch in value if ch.isalpha()) > 6:
            return ' '
        return value

    def collect(self, source):
        pass

    def writeCollectedData(self, prefix):

        assert self.sCode != None
        assert self.lChars != None
        assert self.dChars2idx != None

        # save as text

        with open(os.path.join(self.datadir, prefix+".code.txt"), 'w', ) as codefile:       # 'w' overwrites
            codefile.write(self.sCode)
        with open(os.path.join(self.datadir, prefix+".chars.txt"), 'w', ) as charsfile:
            charsfile.write('\n'.join(self.lChars))                                     # alt: .write('\n'.join(str(line) for line in self.lChars))
        with open(os.path.join(self.datadir, prefix+".chars2idx.txt"), 'w', ) as chars2idxfile:
            for k, v in self.dChars2idx.items():
                chars2idxfile.write(str(k) + ' = '+ str(v) + '\n')

        # save self as binary, pickle:
        with open(os.path.join(self.datadir, prefix + Collector.PICKLE_FILENAME_POSTFIX), 'wb', ) as p:
            pickle.dump(self.__dict__, p, protocol=pickle.HIGHEST_PROTOCOL)
    
    def loadCollectedData(self, prefix):

        self.sCode = None
        self.lChars = None
        self.dChars2idx = None

        with open(os.path.join(self.datadir, prefix + Collector.PICKLE_FILENAME_POSTFIX), 'rb', ) as p:
            dict = pickle.load(p)
        self.__dict__.update(dict)

        assert self.sCode != None
        assert self.lChars != None
        assert self.dChars2idx != None

        assert len(self.sCode) > 1
        assert len(self.lChars) > 1
        assert len(self.dChars2idx) > 1

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

    @staticmethod
    # replace possible several lines long comments with style a la ''' ... '''
    def replace_literals(st):
        res = []
        start_text = start_quote = i = 0
        quote = ''
        while i < len(st):
            if quote:
                if st[i: i + len(quote)] == quote:
                    quote = ''
                    start_text = i
                    res.append(Collector.replacer(st[start_quote: i]))
            elif st[i] in '"\'':
                quote = st[i]
                if i < len(st) - 2 and st[i + 1] == st[i + 2] == quote:
                    quote = 3 * quote
                start_quote = i + len(quote)
                res.append(st[start_text: start_quote])
            if st[i] == '\n' and len(quote) == 1:
                start_text = i
                res.append(quote)
                quote = ''
            if st[i] == '\\':
                i += 1
            i += 1
        return ''.join(res) + st[start_text:]

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
            dict = pickle.load(self, p, protocol=pickle.HIGHEST_PROTOCOL)
        self.__dict__.update(dict)

        assert self.sCode != None
        assert self.lChars != None
        assert self.dChars2idx != None

        assert len(self.sCode) > 1
        assert len(self.lChars) > 1
        assert len(self.dChars2idx) > 1

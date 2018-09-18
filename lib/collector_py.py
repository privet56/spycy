import os, sys
import re

from collector import Collector

class Collector_py(Collector):

    MAX_FILES_DEFAULT=9999999
    COMMENT_RE = re.compile('#.*')

    def __init__(self, source, datadir):
        Collector.__init__(self, source, datadir)

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

    def collect(self, source, max_files=MAX_FILES_DEFAULT):
        self.read(self.find(source, max_files))

    def find(self, source, max_files=Collector.MAX_FILES_DEFAULT):
        self.aSRCs = Collector.find(self, source, '.py', max_files=max_files)
        return self.aSRCs
    
    def read(self, srcs):
        acode = []
        for fn in srcs:
            try:
                with open(fn, 'r') as fin:
                    src = fin.read()
            except UnicodeDecodeError:
                print('Could not read %s' % fn)
            src = Collector_py.replace_literals(src)
            src = Collector_py.COMMENT_RE.sub('', src)
            acode.append(src)

        self.sCode = '{0}{0}'.format(Collector.SRC_SEPARATOR).join(acode).strip()
        self.lChars = list(sorted(set(self.sCode)))
        self.dChars2idx = {ch: idx for idx, ch in enumerate(self.lChars)}

    def writeCollectedData(self):
        return Collector.writeCollectedData(self, "py")
    def loadCollectedData(self):
        return Collector.loadCollectedData(self, "py")

    def startWith(self):
        return '\ndef '

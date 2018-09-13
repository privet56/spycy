import os, sys
import re

from collector import Collector

class Collector_py(Collector):

    MAX_FILES_DEFAULT=9999999
    COMMENT_RE = re.compile('#.*')

    def __init__(self, source, datadir):
        Collector.__init__(self, source, datadir)

    def collect(self, source, max_files=MAX_FILES_DEFAULT):
        self.read(self.find(source, max_files))

    def find(self, source, max_files=MAX_FILES_DEFAULT):
        self.aSRCs = []
        for root, _, filenames in os.walk(source):
            for fn in filenames:
                if fn.endswith('.py'):
                    self.aSRCs.append(os.path.join(root, fn))
                    if(len(self.aSRCs) > max_files):
                        print("max srcs ({0}) reached -> abort traversing dirs...", max_files)
                        break
        return self.aSRCs
    
    def read(self, srcs):
        acode = []
        for fn in srcs:
            try:
                with open(fn, 'r') as fin:
                    src = fin.read()
            except UnicodeDecodeError:
                print('Could not read %s' % fn)
            src = Collector.replace_literals(src)
            src = Collector_py.COMMENT_RE.sub('', src)
            acode.append(src)

        self.sCode = '\n'.join(acode).strip()
        self.lChars = list(sorted(set(self.sCode)))
        self.dChars2idx = {ch: idx for idx, ch in enumerate(self.lChars)}

    def writeCollectedData(self):
        return Collector.writeCollectedData(self, "py")
    def loadCollectedData(self):
        return Collector.loadCollectedData(self, "py")

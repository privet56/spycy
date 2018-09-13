import os, sys
import re

from collector import Collector

class Collector_java(Collector):

    MAX_FILES_DEFAULT=9999999
    COMMENT_RE = re.compile('//.*')
    MULTILINE_COMMENT_RE = re.compile("/\*.*?\*/",re.DOTALL)

    def __init__(self, source, datadir):
        Collector.__init__(self, source, datadir)

    def collect(self, source, max_files=MAX_FILES_DEFAULT):
        self.read(self.find(source, max_files))

    def find(self, source, max_files=MAX_FILES_DEFAULT):
        self.aSRCs = []
        for root, _, filenames in os.walk(source):
            for fn in filenames:
                if fn.endswith('.java'):
                    self.aSRCs.append(os.path.join(root, fn))
                    if(len(self.aSRCs) > max_files):
                        print("max srcs(.java) ({0}) reached -> abort traversing dirs...", max_files)
                        return self.aSRCs
        return self.aSRCs

    @staticmethod
    # replace mulitline comments
    def replace_literals(src):
        return Collector_java.MULTILINE_COMMENT_RE.sub('', src)
    
    def read(self, srcs):
        acode = []
        for fn in srcs:
            try:
                with open(fn, 'r') as fin:
                    src = fin.read()
            except UnicodeDecodeError:
                print('Could not read %s' % fn)
            src = Collector_java.replace_literals(src)
            src = Collector_java.COMMENT_RE.sub('', src)
            acode.append(src)

        self.sCode = '\n'.join(acode).strip()
        self.lChars = list(sorted(set(self.sCode)))
        self.dChars2idx = {ch: idx for idx, ch in enumerate(self.lChars)}

    def writeCollectedData(self):
        return Collector.writeCollectedData(self, "java")
    def loadCollectedData(self):
        return Collector.loadCollectedData(self, "java")

import os, sys
import re

from collector import Collector

class Collector_java(Collector):

    CHAR_RE = re.compile(r'\'.\'')                                  #eg 'ß'
    STRING_RE = re.compile(r'".*?"')                                #eg "ß"
    COMMENT_RE = re.compile('//.*')                                 #eg //comment
    MULTILINE_COMMENT_RE = re.compile("/\*.*?\*/",re.DOTALL)        #eg /*comment*/

    def __init__(self, source, datadir):
        Collector.__init__(self, source, datadir)

    def collect(self, source, max_files=Collector.MAX_FILES_DEFAULT):
        self.read(self.find(source, max_files))

    def find(self, source, max_files=Collector.MAX_FILES_DEFAULT):
        self.aSRCs = Collector.find(self, source, '.java', max_files=max_files)
        return self.aSRCs

    @staticmethod
    # replace all comments and literals
    def replace_all_comments_and_literals(src):
        src = Collector_java.MULTILINE_COMMENT_RE.sub('', src)
        src = Collector_java.COMMENT_RE.sub('', src)
        src = Collector_java.STRING_RE.sub('"  "', src)
        src = Collector_java.CHAR_RE.sub('\' \'', src)
        return src
    
    def read(self, srcs):
        acode = []
        for fn in srcs:
            try:
                with open(fn, 'r') as fin:
                    src = fin.read()
            except UnicodeDecodeError:
                print('Could not read %s' % fn)
            src = Collector_java.replace_all_comments_and_literals(src)
            acode.append(src)

        self.sCode = '\n\n\n'.join(acode).strip()
        self.lChars = list(sorted(set(self.sCode)))
        self.dChars2idx = {ch: idx for idx, ch in enumerate(self.lChars)}

    def writeCollectedData(self):
        return Collector.writeCollectedData(self, "java")
    def loadCollectedData(self):
        return Collector.loadCollectedData(self, "java")

    def startWith(self):
        return '\npublic class '

import os, sys
import re

from collector import Collector

class Collector_py(Collector):

    COMMENT_RE = re.compile('#.*')

    def __init__(self, source):
        Collector.__init__(self, source)
        self.matches = None
        self.python_code = None
        self.py_chars = None
        self.py_char_to_idx = None

    def collect(self, source):
        self.read(self.find(source))

    def find(self, source):
        self.matches = []
        for root, dirnames, filenames in os.walk(source):
            for fn in filenames:
                if fn.endswith('.py'):
                    self.matches.append(os.path.join(root, fn))
        return self.matches
    
    def read(self, srcs):
        self.python_code = []
        for fn in srcs:
            try:
                with open(fn, 'r') as fin:
                    src = fin.read()
            except UnicodeDecodeError:
                print('Could not read %s' % fn)
            src = Collector.replace_literals(src)
            src = Collector_py.COMMENT_RE.sub('', src)
            self.python_code.append(src)

        self.python_code = '\n\n\n'.join(self.python_code)
        self.py_chars = list(sorted(set(self.python_code)))
        self.py_char_to_idx = {ch: idx for idx, ch in enumerate(self.py_chars)}

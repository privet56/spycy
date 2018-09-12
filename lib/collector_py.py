import os, sys
import re

from collector import Collector

class Collector_py(Collector):

    def __init__(self, source):
        Collector.__init__(self, source)
        self.matches = None

    def find(self, rootdir):
        self.matches = []
        for root, dirnames, filenames in os.walk(rootdir):
            for fn in filenames:
                if fn.endswith('.py'):
                    self.matches.append(os.path.join(root, fn))
        return self.matches

import json
import os, sys
import re
import random

import numpy as np
from pydoc import locate

sys.path.append(os.getcwd()+'/../lib')
from collector import Collector
from logger import Logger

class ShoppingQueenModeler:

    logger = None

    def __init__(self, source, datadir, logger=None):
        self.source = source
        self.datadir = datadir
        self.logger = logger if logger else Logger(source, datadir)

    def fit(self, collector):
        self.logger.err(""+self.__class__.__name__+":collect: yet NOTIMPL")

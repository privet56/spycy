import os, sys, time
import re
import glob
import unidecode
import nltk
import random
from collections import Counter, defaultdict
import pandas as pd

#xml libs:
from xml.dom import minidom
import xml.etree.ElementTree as ET
from xml.parsers import expat
#from xml import xpath
#import xpath
#import libxml2
#from xml.dom.ext.reader import Sax2
#from xml import xpath

from collector import Collector
from logger import Logger

class Collector_Excel(Collector):

    logger = None
    df = None

    def __init__(self, source, datadir, logger=None):
        Collector.__init__(self, source, datadir)
        self.logger = logger if logger else Logger(source, datadir)
        self.df = None

    def collect(self, source, cols2extract, colsDestination, costs='costs', cumsum='cumsum'):
        #self.logger.err("Collector_Excel:collect: yet NOTIMPL")
        df = pd.read_excel(source)
        df = df[cols2extract]
        df[cumsum] = df[costs].cumsum()
        df.columns = colsDestination      #renames the 3 cols
        self.df = df
        print(df.tail())
        return df

if __name__ == '__main__':

    source  = 'amazon_order_history.xlsx'
    datadir = '../shoppingQueen/data/'
    logger = Logger(source, datadir)

    startTime = time.time()
    c = Collector_Excel(source, datadir, logger)
    df = c.collect(os.path.join(datadir, source), cols2extract=['date','costs'], colsDestination=['ds','y','cumsum'], costs='costs', cumsum='cumsum')

    elapsed_time = time.time() - startTime
    sElapsedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    logger.log("FINISH. duration:"+sElapsedTime+" secs")

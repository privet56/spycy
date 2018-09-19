import os, sys
import re
import glob
import unidecode

#xml libs:
from xml.dom import minidom
import xml.etree.ElementTree as ET
#from xml import xpath
#import xpath
#import libxml2
#from xml.dom.ext.reader import Sax2
#from xml import xpath

from collector import Collector

# german conversations from ftp://ftp.bas.uni-muenchen.de/pub/BAS/VM/

class Collector_partitur(Collector):

    def __init__(self, source, datadir):
        Collector.__init__(self, source, datadir)

    def collect(self, source, max_files=Collector.MAX_FILES_DEFAULT):

        subdirs = 0
        agsfiles = 0

        ns = {'ag': 'http://www.ldc.upenn.edu/atlas/ag/'}

        for subdir in os.listdir(source):
            subdirs = subdirs + 1
            absSubDir = os.path.join(source, subdir)        #optional: check with if os.path.isdir(...)
            conversation = []
            for agsfn in [f for f in os.listdir(absSubDir) if f.endswith('.ags')]:
                agsfiles = agsfiles + 1
                if((agsfiles % 500) == 0):
                    print("START-AGSFN("+str(agsfiles)+"):"+agsfn)
                doc = ET.parse(os.path.join(absSubDir, agsfn))
                root = doc.getroot() #root.tag = {http://www.ldc.upenn.edu/atlas/ag/}AGSet
                
                idx=0
                for e in root.findall('./ag:AG[last()]/ag:Annotation[last()]/ag:Feature', ns):
                    if(idx > 0):
                        print("ERR: unexpected more <Features>!")
                    idx = idx+1
                    sentence = e.text.strip()
                    if(sentence.startswith("EN>DE")):
                        sentence = unidecode.unidecode(" ".join(sentence[6:].lower().splitlines())).replace(',', ' ').replace('!', ' ').replace('?', ' ').replace('.', ' ').replace('\t', ' ').replace('"u', 'ü').replace('"o', 'ö').replace('~', ' ').replace('"a', 'ä').replace('"s', 'ß').replace('  ', ' ').replace('  ', ' ').strip()

                        print("INF:fn("+agsfn+"): A german sentence(idx:"+str(len(conversation))+"):'"+sentence+"'")
                        conversation.append(sentence)

                    #print("fn("+agsfn+"):FOUNDFEATURE("+str(idx)+"):"+e.text.strip())


if __name__ == '__main__':
    source  = '../talkFellow/data_ger/VM2_total_par'
    datadir = '../talkFellow/data_ger_partitur'

    c = Collector_partitur(source, datadir)
    c.collect(source)
import os, sys, time
import re
import glob
import unidecode
import nltk
import random
from collections import Counter, defaultdict

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


# german conversations from ftp://ftp.bas.uni-muenchen.de/pub/BAS/VM/

class Collector_partitur(Collector):

    FILE_PREFIX = "partiturconversations"
    RE_TOKEN = re.compile(r'(\w+|\?)', re.UNICODE)
    logger = None

    def __init__(self, source, datadir, logger=None):
        Collector.__init__(self, source, datadir)
        self.logger = logger if logger else Logger(source, datadir)

    def tokenize(self, st):
        st = st.lower().replace('_', ' ')
        return ' '.join(self.RE_TOKEN.findall(st))
    
    max_len_found = -1
    max_len_allowed = 128

    def truncateSentence(self, sentence):
        l = len(sentence)
        if((l > self.max_len_found) and (l > 19)):
            self.max_len_found = l
            self.logger.log("longest sentence had "+str(self.max_len_found)+" chars")

        if(l <= self.max_len_allowed):
            return sentence

        sentence = sentence[0:self.max_len_allowed]

        lastspace = sentence.rfind(' ')         #remove last incomplete word
        sentence = sentence[0:lastspace]
        return sentence

    def collect(self, source, max_files=Collector.MAX_FILES_DEFAULT):

        subdirs = 0
        agsfiles = 0
        conversations = []
        ns = {'ag': 'http://www.ldc.upenn.edu/atlas/ag/'}
        errorsCount = 0

        #//TODO: more warnings if no subdirs or no .ags files found!

        for subdir in os.listdir(source):
            subdirs = subdirs + 1
            absSubDir = os.path.join(source, subdir)        #optional: check with if os.path.isdir(...)
            conversation = []
            
            for agsfn in [f for f in os.listdir(absSubDir) if f.endswith('.ags')]:
                agsfiles = agsfiles + 1
                try:
                    doc = ET.parse(os.path.join(absSubDir, agsfn))
                except ET.ParseError as e:
                    #occurs...: handle ´ = \xB4 = &#xb4; = &acute; = u"\u00B4" = ACUTE ACCENT = &#xb4; = &#180;      # not so urgent, as occuring in english texts
                    #see https://docs.python.org/3/library/pyexpat.html#module-xml.parsers.expat

                    #TODO: try:
                    #parser = ET.XMLParser(encoding="utf-8") #or: ET.XMLParser(encoding='iso-8859-5') # or  parser=expat.ParserCreate('UTF-8') # or parser=expat.ParserCreate('ISO-8859-1')
                    #doc = ET.parse(os.path.join(absSubDir, agsfn), parser=parser)
                    # or:
                    #import codecs
                    #target_file = codecs.open("./my.xml",mode='r',encoding='utf-8')
                    #targetTree = ET.parse( target_file )

                    self.logger.log("ERR: could not parse XML: "+subdir+"/"+agsfn+" excCode:"+str(e.code)+" {}".format(e))
                    errorsCount = errorsCount + 1
                    continue
                root = doc.getroot() #root.tag = {http://www.ldc.upenn.edu/atlas/ag/}AGSet
                
                idx=0
                for e in root.findall('./ag:AG[last()]/ag:Annotation[last()]/ag:Feature', ns):
                    if(idx > 0):
                        #occurs...
                        self.logger.log("WRN: unexpected more <Features> in "+subdir+"/"+agsfn)
                    idx = idx+1
                    sentence = e.text.strip()
                    if(sentence.startswith("EN>DE")):
                        sentence = unidecode.unidecode(" ".join(sentence[6:].lower().splitlines())).replace('#', ' ').replace(',', ' ').replace('!', ' ').replace('?', ' ').replace('.', ' ').replace('\t', ' ').replace('"u', 'ü').replace('"o', 'ö').replace('~', ' ').replace('"a', 'ä').replace('"s', 'ß').replace('  ', ' ').replace('  ', ' ').strip()
                        sentence = self.truncateSentence(sentence)
                        conversation.append(sentence)

            if(len(conversation) > 0):
                conversations.append(conversation)
                self.logger.log("INF:("+subdir+" #("+str(subdirs)+") with a #sentencesInConversation:"+str(len(conversation))+" ... #conversations:"+str(len(conversations)))

        token_counter = Counter()

        with open(os.path.join(self.datadir, self.FILE_PREFIX+'.txt'), 'w', encoding='utf-8') as fout:
            for conversation in conversations:
                fout.write('\n'.join(conversation) + '\n\n')
                for sentence in conversation:
                    line = sentence.lower().replace('_', ' ').strip()
                    if line:
                        token_counter.update(self.RE_TOKEN.findall(line))

        with open(os.path.join(self.datadir, self.FILE_PREFIX+'.tok'), 'w', encoding='utf-8') as fout:
            for token, count in token_counter.items():
                fout.write('%s\t%d\n' % (token, count))

        pairs = []
        prev = None

        with open(os.path.join(self.datadir, self.FILE_PREFIX+'.txt')) as fin:      # ok, this could be done nicer, avoiding to read the just written file...
            for line in fin:
                line = line.strip()
                if line:
                    sentences = nltk.sent_tokenize(line)
                    if prev:
                        pairs.append((prev, self.tokenize(sentences[0])))
                    prev = self.tokenize(sentences[-1])
                else:
                    prev = None

        random.shuffle(pairs)
        ss = len(pairs) // 20
        data = {'dev': pairs[:ss],
                'test': pairs[ss:ss * 2],
                'train': pairs[ss * 2:]}

        for tag, pairs2 in data.items():
            path = self.datadir + '/%s' % tag
            if not os.path.isdir(path):
                os.makedirs(path)
            with open(os.path.join(path,'sources.txt'), 'wt', encoding='utf-8') as sources:
                with open(os.path.join(path,'targets.txt'), 'wt', encoding='utf-8') as targets:
                    for source, target in pairs2:
                        sources.write(source + '\n')
                        targets.write(target + '\n')

        return len(conversations), subdirs, errorsCount

    def loadCollectedData(self):
        pass

if __name__ == '__main__':

    source  = '../talkFellow/data_ger/VM2_total_par'
    datadir = '../talkFellow/data_ger_partitur'
    logger = Logger('partitur', datadir)

    startTime = time.time()
    c = Collector_partitur(source, datadir, logger)
    len_conversations, foundSubDirs, failed = c.collect(source)

    elapsed_time = time.time() - startTime
    sElapsedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    logger.log("FINISH. len_conversations:"+str(len_conversations)+" foundSubDirs:"+str(foundSubDirs)+" failedXmlFiles:"+str(failed)+" duration:"+sElapsedTime+" secs")

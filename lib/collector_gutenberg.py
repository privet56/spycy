# imports
import requests
from bs4 import BeautifulSoup
from collections import Counter, defaultdict
from gutenberg.acquire.text import UnknownDownloadUriException
import re
from gensim.utils import tokenize
import random
import nltk
import os
import glob
import json
import unidecode

# imports gutenberg

try:
    GUTENBERG = True
    from gutenberg.acquire import load_etext
    from gutenberg.query import get_etexts, get_metadata
    from gutenberg.acquire import get_metadata_cache
    from gutenberg.acquire.text import UnknownDownloadUriException
    from gutenberg.cleanup import strip_headers
    from gutenberg._domain_model.exceptions import CacheAlreadyExistsException
except ImportError:
    GUTENBERG = False
    print('Gutenberg is not installed. See instructions at https://pypi.python.org/pypi/Gutenberg')

if GUTENBERG:
    cache = get_metadata_cache()
    try:
        cache.populate()
    except CacheAlreadyExistsException:
        pass

from collector import Collector
from logger import Logger

class CollectorGutenberg(Collector):

    LATIN_1_CHARS = (
        (u'\xe2\x80\x99', "'"),
        (u'\xc3\xa9', 'e'),
        (u'\xe2\x80\x90', '-'),
        (u'\xe2\x80\x91', '-'),
        (u'\xe2\x80\x92', '-'),
        (u'\xe2\x80\x93', '-'),
        (u'\xe2\x80\x94', '-'),
        (u'\xe2\x80\x94', '-'),
        (u'\xe2\x80\x98', "'"),
        (u'\xe2\x80\x9b', "'"),
        (u'\xe2\x80\x9c', '"'),
        (u'\xe2\x80\x9c', '"'),
        (u'\xe2\x80\x9d', '"'),
        (u'\xe2\x80\x9e', '"'),
        (u'\xe2\x80\x9f', '"'),
        (u'\xe2\x80\xa6', '...'),
        (u'\xe2\x80\xb2', "'"),
        (u'\xe2\x80\xb3', "'"),
        (u'\xe2\x80\xb4', "'"),
        (u'\xe2\x80\xb5', "'"),
        (u'\xe2\x80\xb6', "'"),
        (u'\xe2\x80\xb7', "'"),
        (u'\xe2\x81\xba', "+"),
        (u'\xe2\x81\xbb', "-"),
        (u'\xe2\x81\xbc', "="),
        (u'\xe2\x81\xbd', "("),
        (u'\xe2\x81\xbe', ")"),
        (u'\u20b0', " ")                # Unicode Character 'GERMAN PENNY SIGN' (U+20B0)
    )

    PARAGRAPH_SPLIT_RE = re.compile(r'\n *\n+')
    RE_TOKEN = re.compile(r'(\w+|\?)', re.UNICODE)
    FILE_PREFIX = "conversations"

    # like constructor
    def __init__(self, source, datadir):
        Collector.__init__(self, source, datadir)

    def extract_conversations(self, text, quote='"'):
        paragraphs = self.PARAGRAPH_SPLIT_RE.split(text.strip())
        conversations = [['']]
        for paragraph in paragraphs:
            chunks = paragraph.replace('\n', ' ').split(quote)
            for i in range((len(chunks) + 1) // 2):
                if (len(chunks[i * 2]) > 100 or len(chunks) == 1) and conversations[-1] != ['']:
                    if conversations[-1][-1] == '':
                        del conversations[-1][-1]
                    conversations.append([''])
                if i * 2 + 1 < len(chunks):
                    chunk = chunks[i * 2 + 1]
                    if chunk:
                        if conversations[-1][-1]:
                            if chunk[0] >= 'A' and chunk[0] <= 'Z':
                                if conversations[-1][-1].endswith(','):
                                    conversations[-1][-1] = conversations[-1][-1][:-1]
                                conversations[-1][-1] += '.'
                            conversations[-1][-1] += ' '
                        conversations[-1][-1] += chunk
            if conversations[-1][-1]:
                conversations[-1].append('')

        return [x for x in conversations if len(x) > 1]

    def tokenize(self, st):
        st = st.lower().replace('_', ' ')
        return ' '.join(self.RE_TOKEN.findall(st))

    def ansify(self, txt):
        #TODO: leave accents and remove only strange characters, like \u20b0, see Collector:remove_non_ansi(text)
        unaccented_string = unidecode.unidecode(txt)
        txt = unaccented_string

        for ch1, ch2 in self.LATIN_1_CHARS:
            txt = txt.replace(ch1, ch2)
            
        return txt

    def collect(self, source, max_files, gutenbergbookids):

        downloaded_books = 0
        download_book_failed = 0
        conversations = []

        for gutenbergbookid in gutenbergbookids:
            try:
                txt = strip_headers(load_etext(gutenbergbookid)).strip()

                txt = self.ansify(txt)

                conversations += self.extract_conversations(txt)
                downloaded_books = downloaded_books + 1

            except UnknownDownloadUriException:
                download_book_failed = download_book_failed + 1
                continue

        token_counter = Counter()

        with open(os.path.join(self.datadir, self.FILE_PREFIX+'.txt'), 'w') as fout:
            for conv in conversations:
                fout.write('\n'.join(conv) + '\n\n')
                for convlines in conv:
                    line = convlines.lower().replace('_', ' ').strip()
                    if line:
                        token_counter.update(self.RE_TOKEN.findall(line))

        with open(os.path.join(self.datadir, self.FILE_PREFIX+'.tok'), 'w') as fout:
            for token, count in token_counter.items():
                fout.write('%s\t%d\n' % (token, count))

        pairs = []
        prev = None

        with open(os.path.join(self.datadir, self.FILE_PREFIX+'.txt')) as fin:
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
            with open(os.path.join(path,'sources.txt'), 'wt') as sources:
                with open(os.path.join(path,'targets.txt'), 'wt') as targets:
                    for source, target in pairs2:
                        sources.write(source + '\n')
                        targets.write(target + '\n')

        return len(conversations), downloaded_books, download_book_failed

    def loadCollectedData(self):
        pass

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

#TODO: more german books
#TODO: automate getting the gutenberg book numbers.!?
german_bookids_from_gutenberg = [2229, 12108, 23134, 53689, 22517, 52856]

PARAGRAPH_SPLIT_RE = re.compile(r'\n *\n+')

def extract_conversations(text, quote='"'):
    paragraphs = PARAGRAPH_SPLIT_RE.split(text.strip())
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

books = 0

downloaded_books = 0
download_book_failed = 0
conversations = []

for german_bookid_from_gutenberg in german_bookids_from_gutenberg:
    try:
        txt = strip_headers(load_etext(german_bookid_from_gutenberg)).strip()

        #TODO: leave accents and remove only strange characters, like \u20b0
        unaccented_string = unidecode.unidecode(txt)
        txt = unaccented_string

        downloaded_books = downloaded_books + 1
    except UnknownDownloadUriException:
        download_book_failed = download_book_failed + 1
        continue

    for ch1, ch2 in LATIN_1_CHARS:
        txt = txt.replace(ch1, ch2)
    conversations += extract_conversations(txt)
    if((german_bookid_from_gutenberg % 100) == 0):
        print(" ... len(conversations):", len(conversations), "downloaded_books:", downloaded_books, "download_book_failed:", download_book_failed)

print("len(conversations):", len(conversations), "downloaded_books:", downloaded_books, "download_book_failed:", download_book_failed)

with open('data/gutenberg.txt', 'w') as fout:
    for conv in conversations:
        fout.write('\n'.join(conv) + '\n\n')

RE_TOKEN = re.compile(r'(\w+|\?)', re.UNICODE)

token_counter = Counter()
with open('data/gutenberg.txt') as fin:
    for line in fin:
        line = line.lower().replace('_', ' ')
        token_counter.update(RE_TOKEN.findall(line))
with open('data/gutenberg.tok', 'w') as fout:
    for token, count in token_counter.items():
        fout.write('%s\t%d\n' % (token, count))

print("token_counter['?']:", token_counter['?'])

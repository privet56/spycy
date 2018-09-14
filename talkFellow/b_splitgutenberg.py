import nltk
from nltk.corpus import wordnet as wn
import re
import random
import os

RE_TOKEN = re.compile(r'(\w+|\?)', re.UNICODE)
def tokenize(st):
    st = st.lower().replace('_', ' ')
    return ' '.join(RE_TOKEN.findall(st))

pairs = []
prev = None
with open('data/gutenberg.txt') as fin:
    for line in fin:
        line = line.strip()
        if line:
            sentences = nltk.sent_tokenize(line)
            if prev:
                pairs.append((prev, tokenize(sentences[0])))
            prev = tokenize(sentences[-1])
        else:
            prev = None

random.shuffle(pairs)
ss = len(pairs) // 20
data = {'dev': pairs[:ss],
        'test': pairs[ss:ss * 2],
        'train': pairs[ss * 2:]}

for tag, pairs2 in data.items():
    path = 'data/%s' % tag
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + '/sources.txt', 'wt') as sources:
        with open(path + '/targets.txt', 'wt') as targets:
            for source, target in pairs2:
                sources.write(source + '\n')
                targets.write(target + '\n')

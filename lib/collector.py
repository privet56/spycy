import os, sys
import re

class Collector:

    '''
    base class collector with basic functions
    to be extended
    '''

    # like constructor
    def __init__(self, source):
        self.source = source

    ''' helper functions '''
    @staticmethod
    def replacer(value):
        if ' ' in value and sum(1 for ch in value if ch.isalpha()) > 6:
            return 'lit'
        return value

    @staticmethod
    def replace_literals(st):
        res = []
        start_text = start_quote = i = 0
        quote = ''
        while i < len(st):
            if quote:
                if st[i: i + len(quote)] == quote:
                    quote = ''
                    start_text = i
                    res.append(Collector.replacer(st[start_quote: i]))
            elif st[i] in '"\'':
                quote = st[i]
                if i < len(st) - 2 and st[i + 1] == st[i + 2] == quote:
                    quote = 3 * quote
                start_quote = i + len(quote)
                res.append(st[start_text: start_quote])
            if st[i] == '\n' and len(quote) == 1:
                start_text = i
                res.append(quote)
                quote = ''
            if st[i] == '\\':
                i += 1
            i += 1
        return ''.join(res) + st[start_text:]

    def collect(self, source):
        pass

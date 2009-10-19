#!/usr/bin/python
# -*- encoding: utf-8 -*-

#
# a script to preprocess chinese HTML pages to be used as raw corpus
#
# this script will
# 1. remove all HTML tags in the input file
# 2. remove all JS and CSS
# 3. replace all spaces with newline
# 4. replace a line full of alphanumber with a newline
# 5. replace successive punctuations (including full-width puncts) with the leading one
# 6. put a newline after each punctuation of it
# 7. replace successive newlines with one newline

from __future__ import with_statement
import sys
import codecs
from curses import ascii

def is_zh(ch):
    """return True if ch is Chinese character.
    full-width puncts/latins are not counted in.
    """
    x = ord(ch)
    # CJK Radicals Supplement and Kangxi radicals
    if 0x2e80 <= x <= 0x2fef:
        return True
    # CJK Unified Ideographs Extension A
    elif 0x3400 <= x <= 0x4dbf:
        return True
    # CJK Unified Ideographs
    elif 0x4e00 <= x <= 0x9fbb:
        return True
    # CJK Compatibility Ideographs
    elif 0xf900 <= x <= 0xfad9:
        return True
    # CJK Unified Ideographs Extension B
    elif 0x20000 <= x <= 0x2a6df:
        return True
    else:
        return False

def is_punct(ch):
    x = ord(ch)
    # in no-formal literals, space is used as punctuation sometimes.
    if x < 127 and (ascii.ispunct(x) or ascii.isblank(x)):
        return True
    # CJK Symbols and Punctuation
    elif 0x3000 <= x <= 0x303f:
        return True
    # Halfwidth and Fullwidth Forms
    elif 0xff00 <= x <= 0xffef:
        return True
    # CJK Compatibility Forms
    elif 0xfe30 <= x <= 0xfe4f:
        return True
    else:
        return False

def is_terminator(ch):
    return ch in (u'!', u'?', u',', u';', u'.', u'！', u'？', u'，', u'。', u'…')

def split_into_sentences(line):
    tokens = []
    zh_token = []
    en_token = []

    def close_token(token):
        if token:
            tokens.append(''.join(token))
            del(token[:])

    def get_current_token():
        if zh_token:
            return zh_token
        elif en_token:
            return en_token
        else:
            return None
        
    for c in line:
        if is_terminator(c):
            # close current token
            cur_token = get_current_token()
            if cur_token is None:
                continue
            cur_token.append(c)
            close_token(cur_token)
            yield tokens
            tokens = []
        elif is_punct(c):
            cur_token = get_current_token()
            if cur_token is None:
                continue
            close_token(cur_token)
            tokens.append(c)
        elif is_zh(c):
            if en_token:
                close_token(en_token)
            zh_token.append(c)
        else:
            if zh_token:
                close_token(zh_token)
            en_token.append(c)
    if tokens:
        yield tokens

def is_ascii_line(line):
    try:
        line.decode('ascii')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False
    else:
        return True

def process(f):
    for line in f:
        if is_ascii_line(line):
            continue
        for sentence in split_into_sentences(line.strip()):
            s = u' '.join(sentence)
            print s.encode('utf-8')
    
if __name__ == "__main__":
    for fn in sys.argv[1:]:
        with codecs.open(fn, 'r', 'utf-8') as f:
            process(f)
                
                    
        

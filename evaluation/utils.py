import mmap
from ast import literal_eval
try:
    from tqdm import tqdm
except:
    tqdm = lambda x: x
from collections import defaultdict
import re
from os.path import splitext
import subprocess
import logging

class Word:
    def __init__(self, lemma, UDPOS=''):
        self.is_root = lemma == 'ROOT'
        self.lemma = lemma.lower()
        self.UDPOS = UDPOS.lower()

    def __repr__(self):
        if self.is_root:
            return 'ROOT'
        else:
            return (self.lemma +
                ('_' + self.UDPOS if self.UDPOS else ''))

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __hash__(self):
        return hash(self.__repr__())


def read_probs_old(path, progress_bar=True):
    """Reads a probability file and returns tuples"""
    if progress_bar:
        nlines = get_num_lines(path)
    with open(path) as f:
        if progress_bar:
            f = tqdm(f, total=nlines)
        rexp = re.compile("'([^']*)'")
        for line in f:
            x, p = line.strip().split('\t')
            yield (tuple(rexp.findall(x)), float(p))


class StupidDict(dict):
    def __missing__(self, element):
        if element is tuple and len(element)>1:
            return self[element[:-1]]*self.discount
        #elif element is tuple:
        #    return self[element[0]]
        else:
            return 0 #  raise KeyError('no element or backoffs available for this ngram: {}'.format(element))


def read_probs(filepath, progress_bar=False, discount=0.4):
    ext = splitext(filepath)[1]
    if ext == '.cnt':
        awk = subprocess.run(['awk', '{a=a+$1}END{print a}', filepath],
            stdout=subprocess.PIPE)
        total_count = float(awk.stdout.decode().strip())
        logging.info('total prob count: {}'.format(total_count))
    else:
        total_count = 1

    if progress_bar:
        nlines = get_num_lines(filepath)
    with open(filepath, 'r') as f:
        if progress_bar:
            f = tqdm(f, total=nlines)
        lines = (l.strip().split('\t') for l in f)
        d = StupidDict((tuple(l[1:]), float(l[0])/total_count) for l in lines)
        d.discount=discount
    return d


def read_poss_dict(path):
    with open(path, encoding='utf-8') as f:
        # format: 
        #    columnist \t NOUN \t columnistFem_N \t columnistMasc_N
        lines = (l.strip().split('\t') for l in f)
        return defaultdict(lambda: [], {Word(l[0], l[1]): l[2:] for l in lines})

def reverse_poss_dict(poss_dict_path):
    out = dict()
    with open(poss_dict_path, encoding='utf-8') as f:
        lines = (l.strip().split('\t') for l in f)
        for c in lines:
            for fun in c[2:]:
                if fun in out:
                    out[fun].append(Word(c[0], c[1]))
                else:
                    out[fun] = [Word(c[0], c[1])]
    return out
                

def get_num_lines(file_path):
    """Return the number of lines in a file"""
    with open(file_path, "r") as f:
        buf = mmap.mmap(f.fileno(), 0)
        lines = 0
        while buf.readline():
            lines += 1
    return lines


class Memoize:
    """Saves a the output of a function for the next time it is called."""
    def __init__(self, f):
        self.f = f
        self.memo = {}
    def __call__(self, *args):
        if not args in self.memo:
            self.memo[args] = self.f(*args)
        return self.memo[args]

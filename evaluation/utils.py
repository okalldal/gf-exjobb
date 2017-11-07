import mmap
from ast import literal_eval
from tqdm import tqdm
from collections import defaultdict
import re

class Word:
    def __init__(self, lemma, UDPOS=''):
        self.is_root = lemma == 'ROOT'
        self.lemma = lemma
        self.UDPOS = UDPOS

    def __repr__(self):
        return self.lemma + '_' + self.UDPOS

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


def read_probs(filepath, dim=2, progress_bar=True):
    if progress_bar:
        nlines = get_num_lines(filepath)
    with open(filepath) as f:
        if progress_bar:
            f = tqdm(f, total=nlines)
        lines = (l.strip().split('\t') for l in f)
        d = defaultdict(lambda: 0, {tuple(l[1:1+dim]): float(l[0]) for l in lines})
    return d


def read_poss_dict(path):
    with open(path, encoding='utf-8') as f:
        # format: 
        #    columnist \t NOUN \t columnistFem_N \t columnistMasc_N
        lines = [l.strip().split('\t') for l in f]
    return defaultdict(lambda: [], {Word(l[0], l[1]): l[2:] for l in lines})


def get_num_lines(file_path):
    """Return the number of lines in a file"""
    with open(file_path, "r+") as f:
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
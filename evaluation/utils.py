import mmap
from ast import literal_eval
from tqdm import tqdm
import re

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


def read_probs(filepath, progress_bar=True):
    with open(filepath) as f:
        if progress_bar:
            f = tqdm(f, total=nlines)
        lines = (l.strip().split('\t') for l in f)
        d = {tuple(l[1:3]): float(l[0]) for l in lines}
    return d

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
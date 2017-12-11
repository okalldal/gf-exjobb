from database import ProbDatabase, ProbTable
import sqlite3
from math import log


class Unigram():
    def __init__(self, dbfile, basename):
        self.db = ProbDatabase(dbfile)
        self.basename = basename
        self.table = ProbTable(self.db.cursor, self.basename)

    def log(self, key):
        return -log(self.get(key))

    def get(self, key, pos=None):
        """ key: single value tuple"""
        if isinstance(key, str):
            key = (key,)
        val = self.table.get(key)
        return val if val else 0


class Bigram():
    def __init__(self, dbfile, basename, backoff=0.4):
        self.db = ProbDatabase(dbfile)
        self.basename = basename
        self.backoff = backoff
        self.bigram_table = ProbTable(self.db.cursor, self.basename)
        self.unigram_table = ProbTable(self.db.cursor, self.basename + '_uni')

        # marginal distributions
        self.marg_table = ProbTable(self.db.cursor, self.basename + '_headuni')

    def check(self):
        assert(len(self.bigram_table.cols) == 3)
        assert(len(self.unigram_table.cols) == 2)
        assert(len(self.marg_table.cols) == 2)

    def log(self, key):
        return -log(self.get(key))

    def get(self, key, pos=None):
        if len(key) == 2:
            # bigram
            val = self.bigram_table.get(key)
            marg = self.marg_table.get(key[1:])
            if not val or marg == 0:
                return self.backoff*self.unigram(key[0:1])
            else:
                return val/marg
    
    def unigram(self, key):
        val = self.unigram_table.get(key)
        if not val:
            raise ValueError('No estimated prob for %s' % str(key))
        return val

class BigramDeprel(Bigram):

    def get(self, key, pos=None):
        # bigram
        val = self.bigram_table.get(key)
        marg = self.marg_table.get(key[1:])
        if not val or marg == 0:
            return self.backoff*Bigram.unigram(self, key[0:1]+key[2:])
        else:
            return val/marg

class Interpolation():
    def __init__(self, dbfile, basename):
        self.db = ProbDatabase(dbfile)
        self.basename = basename

        self.bigram      = ProbTable(self.db.cursor, self.basename)
        self.unigram     = ProbTable(self.db.cursor, self.basename + '_uni')
        self.marg_head   = ProbTable(self.db.cursor, self.basename + '_headuni')
        self.marg_deprel = ProbTable(self.db.cursor, 'onlydep_zero')
        self.bigramcat   = ProbTable(self.db.cursor, 'nodep_zero')
        self.unigramcat  = ProbTable(self.db.cursor, 'nodep_zero_uni')

        self.delta = [0.4, 0.2, 0.3, 0.1]

    def check(self):
        assert(len(self.bigram.cols) == 3)
        assert(len(self.unigram.cols) == 2)
        assert(len(self.marg_head.cols) == 2)
        assert(len(self.marg_deprel.cols) == 2)
        assert(len(self.bigramcat.cols) == 3)
        assert(len(self.unigramcat.cols) == 2)

    def log(self, bigram_key, pos_key):
        return self.get(bigram_key, pos_key)
    
    def get(self, bigram_key, pos_key):
        total = 0
        
        # bigram
        val = self.bigram.get(bigram_key)
        marg = self.marg_head.get(bigram_key[-1:])
        total = total + self.delta[0] * val/marg if val else total

        # unigram
        val = self.unigram.get(bigram_key[0:1])
        total = total + self.delta[1] * val if val else total

        # bigram categories
        val = self.bigramcat.get(pos_key)
        marg = self.unigramcat.get(pos_key[-1:])
        total = total + self.delta[2] * val/marg if val else total

        # unigram categories
        val = self.unigramcat.get(pos_key[0:1])
        total = total + self.delta[3] * val if val else total
            
        return total
    
class InterpolationDeprel(Interpolation):

    def get(self, bigram_key, pos_key):
        total = 0
        
        # bigram
        val = self.bigram.get(bigram_key)
        marg = self.marg_head.get(bigram_key[1:])
        total = total + self.delta[0] * val/marg if val else total

        # unigram
        val = self.unigram.get(bigram_key[0:1]+bigram_key[2:])
        total = total + self.delta[1] * val if val else total

        # bigram categories
        val = self.bigramcat.get(pos_key[0:2])
        marg = self.unigramcat.get(pos_key[1:2])
        total = total + self.delta[2] * val/marg if val else total

        # unigram categories
        val = self.unigramcat.get(pos_key[0:1])
        total = total + self.delta[3] * val if val else total
            
        return total

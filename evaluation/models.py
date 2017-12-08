from database import ProbDatabase, ProbTable
import sqlite3


class Unigram():
    def __init__(self, dbfile, basename):
        self.db = ProbDatabase(dbfile)
        self.basename = basename
        self.table = ProbTable(self.db.cursor, self.basename)

    def get(self, key):
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
        # marginal distribution
        self.head_table = ProbTable(self.db.cursor, self.basename + '_headuni')
        self.check()

    def check(self):
        assert(len(self.bigram_table.cols) == 3)
        assert(len(self.head_table.cols) == 2)
        assert(len(self.unigram_table.cols) == 2)

    def get(self, key):
        if len(key) == 2:
            # bigram
            val = self.bigram_table.get(key)
            head = self.head_table.get(key[-1:])
            if not val or head == 0:
                return self.backoff*self.get(key[0:1])
            else:
                return val/head
        elif len(key) == 1:
            # unigram
            val = self.unigram_table.get(key)
            return val if val else 0

class BigramDeprel():
    def __init__(self, dbfile, basename, backoff=0.4):
        self.db = ProbDatabase(dbfile)
        self.basename = basename
        self.backoff = backoff
        self.bigram_table = ProbTable(self.db.cursor, self.basename)
        self.unigram_table = ProbTable(self.db.cursor, self.basename + '_uni')

        # marginal distributions
        self.head_table = ProbTable(self.db.cursor, self.basename + '_headuni')
        self.deprel_table = ProbTable(self.db.cursor, 'onlydep_zero')

    def check(self):
        assert(len(self.bigram_table.cols) == 3)
        assert(len(self.unigram_table.cols) == 2)
        assert(len(self.head_table.cols) == 2)
        assert(len(self.deprel_table.cols) == 2)

    def get(self, key):
        if len(key) == 2:
            # bigram
            val = self.bigram_table.get(key)
            head = self.head_table.get(key[1:2])
            dep = self.deprel_table.get(key[2:])
            if not val or head == 0 or dep == 0:
                return self.backoff*self.get(key[0:1])
            else:
                return val/head/dep
        elif len(key) == 1:
            # unigram
            val = self.unigram_table.get(key)
            return val if val else 0

class Interpolation():
    def __init__(self, dbfile, basename):
        self.db = ProbDatabase(dbfile)
        self.basename = basename

        self.bigram = ProbTable(self.db.cursor, self.basename)
        self.unigram = ProbTable(self.db.cursor, self.basename + '_uni')
        self.marg_head = ProbTable(self.db.cursor, self.basename + '_headuni')
        self.marg_deprel = ProbTable(self.db.cursor, 'onlydep_zero')
        self.bigramcat = ProbTable(self.db.cursor, 'nodep_zero')
        self.unigramcat = ProbTable(self.db.cursor, 'nodep_zero_uni')


    def get(self, key):
        pass



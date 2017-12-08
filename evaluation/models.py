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
        tot = self.table.total
        return val/tot if val else 0


class Bigram():
    def __init__(self, dbfile, basename, backoff=0.4):
        self.db = ProbDatabase(dbfile)
        self.basename = basename
        self.backoff = backoff
        self.bigram_table = ProbTable(self.db.cursor, self.basename)
        self.unigram_table = ProbTable(self.db.cursor, self.basename + '_uni')

    def get(self, key):
        if len(key) == 2:
            # bigram
            val = self.bigram_table.get(key)
            tot = self.bigram_table.total
            head = self.get(key[-1:])
            if not val or head == 0:
                return self.backoff*self.get(key[0:1])
            else:
                return val/tot/head
        elif len(key) == 1:
            # unigram
            val = self.unigram_table.get(key)
            tot = self.unigram_table.total
            return val/tot if val else 0

class Interpolation():
    def __init__(self, dbfile, basename):
        self.db = ProbDatabase(dbfile)
        self.basename = basename

        self.bigram = ProbTable(self.db.cursor, self.basename)
        self.unigram = ProbTable(self.db.cursor, self.basename + '_uni')
        self.marg_head = ProbTable(self.db.cursor, self.basename + '_headuni')
        self.marg_deprel = ProbTable(self.db.cursor, 'deprel')
        self.bigramcat = ProbTable(self.db.cursor, self.basename + '_cat')
        self.unigramcat = ProbTable(self.db.cursor, self.basename + '_unicat')


    def get(self, key):
        pass



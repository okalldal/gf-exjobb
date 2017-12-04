import sqlite3
import logging

class Table():
    def __init__(self, conn, tablename):
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.name = tablename

        self.cursor.execute('pragma table_info(%s)' % self.name)
        self.cols = [c[1] for c in self.cursor.fetchall()]
        self.total = self.fetch_total()
        self.sql = 'SELECT prob FROM ' + self.name + ' WHERE ' +
                   ' AND '.join(c + '=?' for c in self.cols[1:])
    
    def get(self, params):
        assert(len(params) == len(self.cols) - 1)
        self.cursor.execute(self.sql, params)
        res = self.cursor.fetchone()
        return res[0] if res else None
    
    def fetch_total(self):
        self.cursor.execute("SELECT total FROM total_probs WHERE name=?",
                (self.name,))
        return self.cursor.fetchone()[0]


class ProbDatabase():
    def __init__(self, filename, table):
        self.tablename = table
        self.open(filename)

    def open(self, filename):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.check()
        self.total = self.fetch_total()

    def check(self):
        # check that table exists
        self.cursor.execute(("SELECT name FROM sqlite_master WHERE "
        "type='table' AND name=?"), (self.tablename,))
        if not self.cursor.fetchone():
            raise Exception('Table {} does not exist in database'
                    .format(self.tablename))

        # save information about table
        self.cursor.execute('pragma table_info(%s)' % self.tablename)
        cols = [c[1] for c in self.cursor.fetchall()]
        self._ncols = len(cols)
        self._deprel = 'deprel' in cols
        self._bigram = 'head' in cols 

    def fetch_total(self):
        self.cursor.execute("SELECT total FROM total_probs WHERE name=?",
                (self.tablename,))
        return self.cursor.fetchone()[0]
    
    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def get(self, key):
        assert(self._ncols-1 == len(key))
        query = 'SELECT prob FROM %s' % self.tablename
        query += ' WHERE child=?'
        if self._bigram:
            query += ' AND head=?'
        if self._deprel:
            query += ' AND deprel=?'
        self.cursor.execute(query, key)
        res = self.cursor.fetchone()
        if not res:
            return 0
        elif res[0] == 'nan':
            logging.warn('Found NaN prob')
            return 0
        else:
            return res[0]/self.total

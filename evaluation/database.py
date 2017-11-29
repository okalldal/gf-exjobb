import sqlite3

class ProbDatabase():
    def __init__(self, filename, table):
        self.tablename = table
        self.open(filename)

    def open(self, filename):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.total = self.fetch_total()
        self.check()

    def check(self):
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
        if res:
            return res[0]/self.total
        else:
            return 0

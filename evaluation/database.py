import sqlite3
import logging

class ProbTable():
    """Class representing one table in the prob-db"""
    def __init__(self, cursor, tablename):
        self.cursor = cursor
        self.name = tablename

        self.cursor.execute('pragma table_info(%s)' % self.name)
        self.cols = [c[1] for c in self.cursor.fetchall()]
        if len(self.cols) < 1:
            raise Exception('Database with name %s doesn\'t exist' % self.name)
        self.total = self.fetch_total()
        self.sql = 'SELECT prob FROM ' + self.name + ' WHERE ' + \
                   ' AND '.join(c + '=?' for c in self.cols[1:])
    
    def get(self, params):
        """returns the count for the given params"""
        assert(len(params) == len(self.cols) - 1)
        self.cursor.execute(self.sql, params)
        res = self.cursor.fetchone()
        tot = self.total
        return res[0]/tot if res else None
    
    def fetch_total(self):
        """returns the total count for the table"""
        self.cursor.execute("SELECT total FROM total_probs WHERE name=?",
                (self.name,))
        return self.cursor.fetchone()[0]

class ProbDatabase():
    """Convinience class for opening and closing a database"""
    def __init__(self, filename):
        self.open(filename)

    def open(self, filename):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

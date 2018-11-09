import sqlite3

class DB:
    conn = None
    source = None

    def __init__(self):
        self.conn = sqlite3.connect('diana.db')

    def __del__(self):
        self.conn.close()

    #取特定類別中的所有問題
    def get_category(self,cat):
        c = self.conn.cursor()
        cursor = c.execute("SELECT * FROM question WHERE category='{}';".format(cat))
        source = cursor.fetchall()
        return source

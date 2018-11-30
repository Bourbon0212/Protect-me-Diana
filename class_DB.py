import sqlite3

class DB:
    conn = None
    source = None

    def __init__(self):
        self.conn = sqlite3.connect('diana.db')

    def __del__(self):
        self.conn.close()

    #取特定類別中的所有問題
    def get_category(self, cat):
        c = self.conn.cursor()
        cursor = c.execute("SELECT * FROM question WHERE category='{}';".format(cat))
        source = cursor.fetchall()
        return source

    # 功能：輸入類別後，傳出所有該類別的問題
    # 輸入：str (類別)
    # 輸出：list (所有該類別的問題)

    def get_all(self):
        c = self.conn.cursor()
        cursor = c.execute("SELECT * FROM question;")
        source = cursor.fetchall()
        return source

    # 功能：傳出所有不分類別的問題
    # 輸入： -
    # 輸出：list (所有問題)

import sqlite3

class DB:
    db = None
    source = None

    def __init__(self):
        self.db = sqlite3.connect('diana.db')

    def __del__(self):
        self.db.conn.close()

    #取特定類別中的所有問題
    def get_category(self, cat):
        c = self.db.conn.cursor()
        cursor = c.execute("SELECT * FROM question WHERE category=%s;", (cat, ))
        source = cursor.fetchall()
        return source

    # 功能：輸入類別後，傳出所有該類別的問題
    # 輸入：str (類別)
    # 輸出：list (所有該類別的問題)

    def get_all(self):
        c = self.db.conn.cursor()
        cursor = c.execute("SELECT * FROM question;")
        source = cursor.fetchall()
        return source

    # 功能：傳出所有不分類別的問題
    # 輸入： -
    # 輸出：list (所有問題)

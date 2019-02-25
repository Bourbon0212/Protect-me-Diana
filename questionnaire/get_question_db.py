#取特定類別中的所有問題
def get_category(cat, db):
    cur = db.conn.cursor()
    cur.execute("SELECT * FROM question WHERE category=%s;", (cat, ))
    ret = cur.fetchall()
    cur.close()
    return ret

# 功能：輸入類別後，傳出所有該類別的問題
# 輸入：str (類別)
# 輸出：list (所有該類別的問題)

def get_all(db):
    cur = db.conn.cursor()
    cur.execute("SELECT * FROM question;")
    ret = cur.fetchall()
    cur.close()
    return ret

# 功能：傳出所有不分類別的問題
# 輸入： -
# 輸出：list (所有問題)

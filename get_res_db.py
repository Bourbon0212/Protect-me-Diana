
import sqlite3

def get_feedback(feedback, userid, quick):

    #DB開關
    conn = sqlite3.connect('response.db')
    c = conn.cursor()

    #建response表格
    c.execute("""CREATE TABLE IF NOT EXISTS responses (
            YN integer,
            description text,
            userid text,
            time datetime default current_timestamp,
            question_id integer,
            assessment_id integer default 0,
            building_id integer default 0);""")



    a = {i:None for i in range(65, 78)} if quick else {i:None for i in range(1, 65)}

    for i,value in feedback:
        a[i] = value

    for i, value in a.items():
        yn = 1 if value is None else 0
        c.execute('INSERT INTO responses (YN, description, userid, question_id) VALUES (?,?,?,?);', (yn, value, userid, i))

    conn.commit()
    conn.close()

    # 功能：把app中的暫時使用者回覆(feedback)，寫進資料庫
    # 輸入：1. feedback:使用者所回覆的待改進內容
    #      2. userid
    #      3. (Bool) quick：看看他是不是填Quick Check，是則T否則F
    # 輸出：寫進response.db

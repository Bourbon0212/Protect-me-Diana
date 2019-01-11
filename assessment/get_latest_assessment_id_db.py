import sqlite3

# 抓最新的assessment id

def get_latest_assessment_id_db():

    conn = sqlite3.connect('diana.db')
    c = conn.cursor()

    cursor = c.execute('SELECT * FROM assessment')

    result = cursor.fetchall()
    ret = result[len(result) - 1]

    conn.commit()
    conn.close()

    return ret

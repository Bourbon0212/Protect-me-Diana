# 抓最新的assessment id

def get_latest_assessment_id_db(db):

    cur = db.conn.cursor()

    cur.execute('SELECT * FROM assessment')
    result = cur.fetchall()
    
    ret = result[len(result) - 1]

    db.conn.commit()
    cur.close()
    
    return ret

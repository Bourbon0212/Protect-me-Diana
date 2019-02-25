
def get_yitianda_db(ass_id, db):

    cur = db.conn.cursor()

    cur.execute('SELECT * FROM responses WHERE assessment_id=%s ', (ass_id,))
    response = cur.fetchall()

    # 整理出以填答過的人，放進一個list

    yitianda = []

    for i in range(len(response)):
        userid = response[i][2]
        if userid not in yitianda:
            yitianda.append(userid)

    db.conn.commit()
    cur.close()

    return yitianda

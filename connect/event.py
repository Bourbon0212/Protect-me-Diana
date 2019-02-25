def event(db):

    # 開 DB

    cur = db.conn.cursor()

    # 從diana.db撈各個學校(schools)

    cur.execute('SELECT * FROM assessment')

    result = cur.fetchall()
    ass_id = []
    event = []

    data = {}

    for i in range(len(result)):
        ass_id.append(result[i][0])
        event.append(result[i][1])

        data[ass_id[i]] = {"ass_id": ass_id[i], "event": event[i]}

    db.conn.commit()
    cur.close()

    return data

import ast


def detail(payload, db):
    payload = ast.literal_eval(payload)

    UID = payload["userid"]
    ass_id = payload["assessment_id"]

    detail = {}

    #找他有沒有填答過
    cur = db.conn.cursor()

    #先抓出待改進的內容跟相對題號

    abs_q = []
    rel_q = []
    description = []
    content = []

    cur.execute(
        """SELECT * FROM responses WHERE (userid=%s AND assessment_id=%s AND yn=%s)""",
        (UID, ass_id, 0),
    )
    #yn 是 responses 裡面的待改進
    ret = cur.fetchall()

    for i in range(len(ret)):
        abs_q.append(ret[i][4])
        description.append(ret[i][1])

    db.conn.commit()

    #用絕對題號回去抓題目跟類別及相對題號

    for i in range(len(abs_q)):
        cur.execute("SELECT * FROM question WHERE no=%s", (abs_q[i],))
        res = cur.fetchall()
        rel_q.append(res[0][2] + " Q" + str(res[0][3]))
        content.append(res[0][1])

        detail[abs_q[i]] = {
            "question":rel_q[i],
            "content":content[i],
            "description":description[i],
        }

    db.conn.commit()

    cur.close()
    return detail

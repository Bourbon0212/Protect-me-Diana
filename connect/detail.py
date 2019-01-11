import ast
import sqlite3

def detail(json):
    json = ast.literal_eval(json)

    UID = json["userid"]
    ass_id = json["assessment_id"]

    detail = {}

    #找他有沒有填答過
    conn = sqlite3.connect('response.db')
    c = conn.cursor()

    #先抓出待改進的內容跟相對題號

    abs_q = []
    rel_q = []
    description = []
    content = []

    cursor = c.execute('SELECT * FROM responses WHERE (userid="{}" AND assessment_id="{}" AND "YN"={}) '.format(UID, ass_id, 0))
    ret = cursor.fetchall()

    for i in range(len(ret)):
        abs_q.append(ret[i][4])
        description.append(ret[i][1])

    conn.commit()
    conn.close()

    #用絕對題號回去抓題目跟類別及相對題號

    conn = sqlite3.connect('diana.db')
    c = conn.cursor()

    for i in range(len(abs_q)):
        cursor = c.execute('SELECT * FROM question WHERE no={} '.format(abs_q[i]))
        res = cursor.fetchall()
        rel_q.append(res[0][2] + " Q" + str(res[0][3]))
        content.append(res[0][1])

        detail[abs_q[i]] = {"question":rel_q[i], "content":content[i], "description":description[i]}

    conn.commit()
    conn.close()

    return detail

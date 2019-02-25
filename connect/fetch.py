import ast


def fetch(payload, db):
    payload = ast.literal_eval(payload)
    county = payload["county"]
    ass_id = payload["assessment_id"]

    # 開 DB

    cur = db.conn.cursor()

    # 從diana.db撈各個學校(schools)

    cur.execute('SELECT * FROM schools WHERE county=%s ', (county,))
    schools = cur.fetchall()

    data = {}

    for i in range(len(schools)):
        data[schools[i][1]] = {
            "county": schools[i][2],
            "address": schools[i][3],
            "latitude": schools[i][4],
            "longitude": schools[i][5],
            "name": "",
            "phone": "",
            "userid": "",
            "YN": 0,
            "severity": 0
        }

    # 從diana.db撈聯絡人資料(contacts)
    school_name = list(data.keys())

    for i in range(len(school_name)):

        cur.execute(
            'SELECT * FROM contacts WHERE (county=%s AND school=%s) ',
            (county, school_name[i]),
        )

        contacts = cur.fetchall()


        if len(contacts) > 0:
            data[school_name[i]]["name"] = contacts[0][1]  # 塞聯絡人名字進去
            data[school_name[i]]["phone"] = contacts[0][4]  # 塞手機進去
            data[school_name[i]]["userid"] = contacts[0][0]  # 塞userid進去
        else:
            data[school_name[i]]["name"] = '無負責人'  # 塞聯絡人名字進去
            data[school_name[i]]["phone"] = '無負責人'  # 塞手機進去
            data[school_name[i]]["userid"] = '無負責人'  # 塞userid進去

    db.conn.commit()

    # 從response.db看看他有沒有填過
    # 從response.db撈特定事件答題過的人，填過就把YN改成1

    cur.execute('SELECT * FROM responses WHERE assessment_id=%s ', (ass_id,))
    response = cur.fetchall()

    # 整理出以填答過的人，放進一個list

    yitianda = []

    for i in range(len(response)):
        userid = response[i][2]
        if userid not in yitianda:
            yitianda.append(userid)
    for i in range(len(data)):
        if data[school_name[i]]["userid"] in yitianda:
            data[school_name[i]]["YN"] = 1
    db.conn.commit()

    score = {}
    for i in range(len(yitianda)):
        cur.execute('SELECT * FROM responses WHERE assessment_id=%s AND userid=%s ', (ass_id, yitianda[i]))
        sheet = cur.fetchall()
        fenshu = 0
        y_n = []

        for j in range(len(sheet)):
            y_n.append(sheet[j][0])

        if 0 not in y_n:
           fenshu = 100
        elif 0 in y_n[0:64]:
            for k in range(64):
                if y_n[k] == 1:
                    fenshu += 100/64
        elif 0 in y_n[64:77]:
            for k in range(64,77):
                if y_n[k] == 1:
                    fenshu += 100/13

        fenshu = round(fenshu)
        score[yitianda[i]] = fenshu
        db.conn.commit()

    for i in range(len(data)):
        if data[school_name[i]]["userid"] in yitianda:
            a = data[school_name[i]]["userid"]
            data[school_name[i]]["severity"] = score[a]

    cur.close()

    return data

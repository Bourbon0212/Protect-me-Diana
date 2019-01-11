import ast
import sqlite3
import json

def fetch(json):
    json = ast.literal_eval(json)
    county = json["county"]
    ass_id = json["assessment_id"]

    #開 DB

    conn = sqlite3.connect("diana.db")
    c = conn.cursor()

    #從diana.db撈各個學校(schools)

    cursor = c.execute('SELECT * FROM schools WHERE county="{}" '.format(county))
    schools = cursor.fetchall()

    data = {}

    for i in range(len(schools)):
        data[schools[i][1]] = {"county":schools[i][2], "address":schools[i][3], "latitude":schools[i][4], "longitude":schools[i][5], "name":"", "phone":"", "userid":"", "YN":0}

    #從diana.db撈聯絡人資料(contacts)
    school_name = list(data.keys())

    for i in range(len(school_name)):

        cursor = c.execute('SELECT * FROM contacts WHERE (county="{}" AND school="{}") '.format(county, school_name[i]))

        contacts = cursor.fetchall()

        if len(contacts) > 0:
            data[school_name[i]]["name"] = contacts[0][1] #塞聯絡人名字進去
            data[school_name[i]]["phone"] = contacts[0][4] #塞手機進去
            data[school_name[i]]["userid"] = contacts[0][0] #塞userid進去
        else:
            data[school_name[i]]["name"] = '無負責人' #塞聯絡人名字進去
            data[school_name[i]]["phone"] = '無負責人' #塞手機進去
            data[school_name[i]]["userid"] = '無負責人' #塞userid進去

    conn.commit()
    conn.close()
    #diana.db結束


    #從response.db看看他有沒有填過
    conn = sqlite3.connect("response.db")
    c = conn.cursor()

    #從response.db撈特定事件答題過的人，填過就把YN改成1

    cursor = c.execute('SELECT * FROM responses WHERE assessment_id="{}" '.format(ass_id))
    response = cursor.fetchall()

    #整理出以填答過的人，放進一個list

    yitianda = []

    for i in range(len(response)):
        userid = response[i][2]
        if userid not in yitianda:
            yitianda.append(userid)

    for i in range(len(data)):
        if data[school_name[i]]["userid"] in yitianda:
            data[school_name[i]]["YN"] = 1

    conn.commit()
    conn.close()


    return data

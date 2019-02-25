def get_account_db(account, db):

    cur = db.conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS contacts (line_userid text, name text, county text, school text, phone text);')

    line_userid = account["userid"]
    name = account["name"]
    county = account["county"]
    school = account["school"]
    phone = account["phone"]
    #寫入資料庫
    cur.execute(
        """INSERT INTO contacts VALUES (%s,%s,%s,%s,%s);""",
        (line_userid, name, county, school, phone),
    )
    db.conn.commit()

    cur.close()

    # 功能： 新增用戶資訊到contacts裡面
    # 輸入：1. account： app 裡面的 account[userid] --> dict{'userid':userid, 'name':0, 'county':0, 'school':0, 'phone':0}
    #      2. db：db
    # 輸出： NA(寫入資料庫)

def get_userid_db(db):

    cur = db.conn.cursor()

    cur.execute('SELECT * FROM contacts')

    result = cur.fetchall()
    userid = []

    for i in range(len(result)):
        uid = result[i][0]
        userid.append(uid)

    return userid

    # 功能：把所有人的userid撈出來
    # 輸入：1. db： db
    # 輸出：一大堆userid(type:list)

def delete_userid_db(userid, db):

    cur = db.conn.cursor()
    cur.execute("DELETE FROM contacts WHERE line_userid=%s", (userid,))

    db.conn.commit()
    cur.close()


    # 功能： 帳號重設刪掉UID
    # 輸入：1. userid：UID
    #      2. db：db
    # 輸出：NA

def get_school_db(county, db):
    #開 DB
    cur = db.conn.cursor()
    #從diana.db撈各個學校(schools)
    cur.execute("SELECT * FROM schools WHERE county=%s", (county,))
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
        }

    #從diana.db撈聯絡人資料(contacts)
    school_name = list(data.keys())

    cur.close()
    return school_name

    # 功能：從現有的schools撈出所有合作學校資料
    # 輸入：1. county：app中account[userid][county]
    #      2. db：db
    # 輸出：一大串該縣市的學校名字(type:list)

def no_repeat_school_db(county, db):
    cur = db.conn.cursor()
    #從diana.db撈各個學校(schools)
    cur.execute('SELECT * FROM contacts WHERE county=%s', (county,))
    schools = cur.fetchall()

    data = {}

    for i in range(len(schools)):
        data[schools[i][3]] = {"county": schools[i][2]}

    #從diana.db撈聯絡人資料(contacts)
    school_name = list(data.keys())

    cur.close()
    return school_name

    # 功能：從現有的contacts中，撈出各縣市的學校名字，避免一校責任不明
    # 輸入：1. county：app中account[userid][county]
    #      2. db：db
    # 輸出：一大串學校名字(type:list)


def get_county_db(db):

    cur = db.conn.cursor()
    cur.execute('SELECT * FROM counties')
    counties = cur.fetchall()

    data = []

    for i in range(len(counties)):
        data.append(counties[i][1])

    cur.close()
    return data

    # 功能：撈出中華民國所有的縣市
    # 輸入：1. db：db
    # 輸出：一串縣市名字(type:list)

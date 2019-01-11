import sqlite3

def get_account_db(account):

    conn = sqlite3.connect('diana.db')
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS contacts (line_userid text, name text, county text, school text, phone text);")

    line_userid = account["userid"]
    name = account["name"]
    county = account["county"]
    school = account["school"]
    phone = account["phone"]

    #寫入資料庫
    c.execute('INSERT INTO contacts VALUES ("{}","{}","{}","{}","{}");'.format(line_userid, name, county, school, phone))
    conn.commit()
    conn.close()

    ##################################
    ##########找所有人的userid#########
    ##################################

def get_userid_db():

    conn = sqlite3.connect('diana.db')
    c = conn.cursor()

    cursor = c.execute('SELECT * FROM contacts')

    result = cursor.fetchall()
    userid = []

    for i in range(len(result)):
        uid = result[i][0]
        userid.append(uid)

    conn.commit()
    conn.close()

    return userid

    ##################################
    ##########刪掉重複的userid#########
    ##################################

def delete_userid_db(userid):

    conn = sqlite3.connect('diana.db')
    c = conn.cursor()

    c.execute("DELETE from contacts WHERE line_userid='{}'".format(userid))

    conn.commit()
    conn.close()



def get_school_db(county):

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

    return school_name

def no_repeat_school_db(county):

    conn = sqlite3.connect("diana.db")
    c = conn.cursor()

    #從diana.db撈各個學校(schools)
    cursor = c.execute('SELECT * FROM contacts WHERE county="{}" '.format(county))
    schools = cursor.fetchall()

    data = {}

    for i in range(len(schools)):
        data[schools[i][3]] = {"county":schools[i][2]}

    #從diana.db撈聯絡人資料(contacts)
    school_name = list(data.keys())

    return school_name


def get_county_db():

    conn = sqlite3.connect("diana.db")
    c = conn.cursor()

    #從diana.db撈各個學校(schools)
    cursor = c.execute('SELECT * FROM counties')
    counties = cursor.fetchall()

    data = []

    for i in range(len(counties)):
        data.append(counties[i][1])

    return data

import sqlite3

def event():

    #開 DB

    conn = sqlite3.connect('diana.db')
    c = conn.cursor()

    #從diana.db撈各個學校(schools)

    cursor = c.execute('SELECT * FROM assessment')

    result = cursor.fetchall()
    ass_id = []
    event = []


    data = {}

    for i in range(len(result)):
        ass_id.append(result[i][0])
        event.append(result[i][1])

        data[ass_id[i]] = {"ass_id":ass_id[i], "event":event[i]}


    conn.commit()
    conn.close()

    return data

from carousel import *               #CT抓欄位

def ct_push(data, userid):
    ct_container = []

    if data[userid]['Normal'] == 12:#該類題數
        ct_container.insert(0, Normal1)
    else:
        ct_container.insert(0, Normal0)

    if data[userid]['Indoors'] == 20:#該類題數
        ct_container.insert(1, Indoors1)
    else:
        ct_container.insert(1, Indoors0)

    if data[userid]['Corridor'] == 13:#該類題數
        ct_container.insert(2, Corridor1)
    else:
        ct_container.insert(2, Corridor0)

    if data[userid]['Outdoors'] == 19:#該類題數
        ct_container.insert(3, Outdoors1)
    else:
        ct_container.insert(3, Outdoors0)

    return ct_container

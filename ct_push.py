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

    if len(data[userid]['Answered']) == 0:
        ct_container.insert(0, Quick)
    else:
        pass

    return ct_container

    # 功能： 判斷每一個類別是否已經填答過，決定要推甚麼carousel columns給他
    #       如果沒有填寫過，就把Quick Check加進要推的carousel template
    # 輸入：data, userid
    # 輸出：CarouselTemplate

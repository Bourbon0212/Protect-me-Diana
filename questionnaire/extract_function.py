import re

def extract(x):
    y = re.findall("no=([^&]+)", x)
    a = re.findall("wer=([^&]+)", x)
    b = a[0]
    z = y[0]
    z = int(z)
    e = [z, b]

    return e

    # 功能：把confirm template的event.postback.data擷取出絕對題號、回應
    # 輸入：event.postback.data (即Line吃到的PostbackEvent)
    #                          EX:'no=' + str(questions[i][0]) + '&answer=OK'
    #                          EX:'no=' + str(questions[i][0]) + '&answer=NO'
    # 輸出：list(['絕對題號', 'OK/NO(沒問題或待改進)'])

def revise_extract(x):
    y = re.findall("([^ ]+)", x)[0]
    z = re.findall("([^ ]+)", x)[1]

    if z[0] == 'Q':
        z = re.findall("Q([^ ]+)", z)
    else:
        z = re.findall("q([^ ]+)", z)

    y = 'Quick' if y == 'quick' else y
    y = 'Normal' if y == 'normal' else y
    y = 'Indoors' if y == 'indoors' else y
    y = 'Corridor' if y == 'corridor' else y
    y = 'Outdoors' if y == 'outdoors' else y

    lst = [y,int(z[0])]
    return lst

    # 功能：把使用者在回答要修改表單答覆之後，我們要把他輸入的文字訊息，抓出類別、題號
    # 輸入：str (即Line吃到的text)
    #          EX:'Normal Q17'
    # 輸出：list(['類別', '相對題號'])

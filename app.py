##################################
#########   Just Import  #########
##################################

from __future__ import unicode_literals
import errno
import os
import sys
import tempfile
from argparse import ArgumentParser
from flask import Flask, request, abort, jsonify, send_from_directory
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, CarouselTemplate, PostbackEvent,
    StickerMessage, StickerSendMessage,
)

from questionnaire.extract_function import extract, revise_extract       #RE抓數字
from questionnaire.ct_push import ct_push               #抓推播新的carousel template
from questionnaire.confirm import confirm          #抓confirm template 進來
from questionnaire.carousel import *               #抓caousel columns
from questionnaire.confirm_push import confirm_push
from questionnaire.next import next
from questionnaire.get_res_db import get_feedback
from account.get_account_db import (
    get_account_db, get_userid_db, delete_userid_db,
    get_school_db, no_repeat_school_db, get_county_db
)
from account.account_confirm import account_confirm
from questionnaire.tempview import takeFirst, tempview, tempview_confirm
from questionnaire.converter import converter
from questionnaire.revise import revise_idiot, revise_confirm, revise_able
from questionnaire.get_yitianda_db import get_yitianda_db
from connect.fetch import fetch
from connect.detail import detail
from connect.event import event
from assessment.get_latest_assessment_id_db import get_latest_assessment_id_db

from db.database import Database

from werkzeug.contrib.cache import SimpleCache, MemcachedCache


db = Database(os.environ.get('DATABASE_URL'), db_type='postgres')
# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

app.config['JSON_AS_ASCII'] = False

    ##################################
    #########儲存使用者填答紀錄#########
    ##################################

data = {}
result = True #True是預設為沒問題；False就改成待改進；詳情請看後續發展
revise_result = True #不要懷疑就是有
feedback = {} #使用者回饋
EPD = 0 #填問卷的時候的絕對題號
revise_EPD = 0
parse_no = 0 #從填寫confirm template的時候，抓出相對題號
account = {} #帳號設定問問題用的
account_q = 0 #記住帳號設定的題數

    ##################################
    ##########  Good Simu   ##########
    ##################################

cache = None
line_bot_api = None

if os.environ.get("FLASK_ENV") == "development":
    line_bot_api = LineBotApi(os.environ.get("TOKEN"), "http://localhost:8080")
    # cache = SimpleCache()

#區分成本機用的跟遠端server用的資料庫
#EX:本機是MYSQL 雲端是POSTGRE
else:
    line_bot_api = LineBotApi(os.environ.get("TOKEN"))
    # cache = MemcachedCache([os.environ.get("CACHE_URL")])

handler = WebhookHandler(os.environ.get("SECRET"))

#
# @app.route('/js/<path:path>')
# def send_js(path):
#     return send_from_directory('js', path)
#
# if __name__ == "__main__":
#     app.run()

@app.route('/report/<path:name>')
# 檔案在不在,在哪裡/有沒有亂戳,怎麼丟
def reportroute(name):
    name = 'index.html' if name is "" else name
    path = os.path.join("report", name)
    with open(path) as f:
        content = f.read()
    return content

def send_js(name):
    return send_from_directory('js', name)

@app.route('/event')
def eventroute():
    return jsonify(event(db))

@app.route('/fetch')
def fetchroute():
    county = request.args.get('county')
    ass_id  = request.args.get('assessment_id')
    return jsonify(fetch('{"county":"' + county + '", "assessment_id":' + ass_id + '}', db))

@app.route('/detail')
def detailroute():
    userid = request.args.get('userid')
    ass_id = request.args.get('assessment_id')
    return jsonify(detail('{"userid":"' + userid + '", "assessment_id":' + ass_id + '}', db))

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'



@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    userid = event.source.user_id

    global data
    global feedback
    global revise_result
    global revise_EPD
    global account
    global account_q

    if text == '請給我使用須知':
        ret1 = TextSendMessage(text="歡迎使用本平台😁\n本平台是作為學校校安機關的安全檢核系統\n目前功能僅有表單檢核功能")
        ret2 = TextSendMessage(text="【填寫表單須知】：\n您可以透過點選選單中的問卷按鈕，或是輸入「問卷」來呼叫問卷。\n本問卷提供兩種填答方式：\n\n1.快速檢核：若情況緊急，請使用此捷徑\n2.常規問卷：共分成四類選單，可交叉填答\n【注意】：兩種填寫方式不可交叉填寫")
        ret3 = TextSendMessage(text="本次填寫的事件為："+str(get_latest_assessment_id_db(db)[1]))
        line_bot_api.reply_message(
            event.reply_token, [ret1] + [ret2] + [ret3])


    if text == '我要統計資料':
        ret = TextSendMessage(text="https://pmdiana.hcilab.katrina.tw/report/index.html")
        line_bot_api.reply_message(event.reply_token, ret)

    if text == '請給我表單填寫':

        if userid not in get_yitianda_db(get_latest_assessment_id_db(db)[0], db): #確認他有沒有填過這次問卷
            if userid not in data:#沒有USERID的話，add key(第一次填寫的時候) 然後推處死carousel
                data[userid] = {"Quick":0, "Normal":0, "Indoors":0, "Corridor":0, "Outdoors":0, "Answered":[]}
                feedback[userid] = []
                ct_container = ct_push(data, userid)  #把4類別加進來
                carousel_template = CarouselTemplate(columns=ct_container)
                template_message = TemplateSendMessage(alt_text='災情回覆問卷', template=carousel_template)
                line_bot_api.reply_message(event.reply_token, template_message)

            elif data[userid]['Quick'] != 0:#QC填到一半智障又打一次carousel
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text="您已選擇快速檢核！請填頁面上的最後一題"))

            else:
                ct_container = ct_push(data, userid)
                carousel_template = CarouselTemplate(columns=ct_container)
                template_message = TemplateSendMessage(alt_text='問卷選單', template=carousel_template)
                line_bot_api.reply_message(event.reply_token, template_message)

        else:
            ret1 = TextSendMessage(text="您已為本次事件提供災情回覆咯~")
            ret2 = TextSendMessage(text="本次填寫的事件為："+str(get_latest_assessment_id_db(db)[1]))
            line_bot_api.reply_message(
                event.reply_token, [ret1] + [ret2])


    elif '已回覆待改進' not in text and '已回覆沒問題' not in text and 'Normal' not in text and 'Indoors' not in text and 'Corridor' not in text and 'Outdoors' not in text:
        global result #就是要
        global EPD

        if result is False: #如果confirm templates 填待改進的話，他就會是 False
            cat = ''
            last = 0
            ret = None #下一題的confirm
            result = True #把值改回來

            feedback[userid].append((EPD, text)) #紀錄(題號, 廢話)
            data[userid]["Answered"].append(EPD)

            if EPD in list(range(65,78)):
                last = 77
                cat = 'Quick'

            elif EPD in list(range(1,13)):
                last = 12
                cat = 'Normal'

            elif EPD in list(range(13,33)):
                last = 32
                cat = 'Indoors'

            elif EPD in list(range(33,46)):
                last = 45
                cat = 'Corridor'

            elif EPD in list(range(46,65)):
                last = 64
                cat = 'Outdoors'

            if EPD == last:
                data[userid][cat] += 1 #待改進填到最後一題+1
                ct_container = ct_push(data, userid)

                if EPD == 77 or ct_container == [Normal1, Indoors1, Corridor1, Outdoors1]:
                    output = feedback[userid]
                    ret = tempview_confirm(output, db)

                else:
                    carousel_template = CarouselTemplate(columns=ct_container)
                    ret = [
                    TemplateSendMessage(
                        alt_text='問卷選單',
                        template=carousel_template,
                    )]

            else:
                data[userid][cat] += 1 #待改進沒填到最後一題+1
                ret = [confirm(cat, data[userid][cat], db)]

            line_bot_api.reply_message(
                event.reply_token, [TextSendMessage(text='『' + text + '』已收到回覆')] + ret)

    #要改答案
    try:
        if revise_able(revise_extract(text)[0], revise_extract(text)[1]) is True:
            cat = revise_extract(text)[0]
            i   = revise_extract(text)[1]#相對題號
            no  = converter(cat, i)      #絕對題號
            revise_EPD = no

            data[userid]['Answered'].remove(no) #從已填答拿掉

            newlist = []
            for j in range(len(feedback[userid])):#從feedback拿掉
                if no != feedback[userid][j][0]:
                    newlist.append(feedback[userid][j])
            feedback[userid] = newlist

            #丟confirm
            ret = [revise_confirm(cat, i, db)]
            data[userid]["Answered"].append(no)#加入已填答
            line_bot_api.reply_message(event.reply_token, ret)

        else:
            ret = revise_idiot(text, revise_extract(text)[0], revise_extract(text)[1])
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=ret))
    except:
        pass

    #處理改答案得時候，他要待改進
    if '已回覆待改進' not in text and '已回覆沒問題' not in text and 'Normal' not in text and 'Indoors' not in text and 'Corridor' not in text and 'Outdoors' not in text:

        if revise_result is False:
            revise_result = True

            feedback[userid].append((revise_EPD, text)) #紀錄(題號, 廢話)
            data[userid]["Answered"].append(revise_EPD)

            output = feedback[userid]
            ret = tempview_confirm(output, db)
            line_bot_api.reply_message(
                event.reply_token, [TextSendMessage(text='『' + text + '』已收到回覆')] + ret)


    if text == '我要設定帳號':
        if userid in get_userid_db(db): #已經填過了，問她要不要再改
            line_bot_api.reply_message(
                event.reply_token, account_confirm())
        elif userid not in get_userid_db(db): #第一次設
            account[userid] = {'userid':userid, 'name':0, 'county':0, 'school':0, 'phone':0}
            ret1 = TextSendMessage(text="【注意】：請一次設定完成")
            ret2 = TextSendMessage(text="請問您尊姓大名？")
            line_bot_api.reply_message(event.reply_token, [ret1] + [ret2])
            account_q = 1
    elif account_q == 1:
        account[userid]['name'] = text
        ret = TextSendMessage(text="請問您的所在縣市？")
        line_bot_api.reply_message(event.reply_token, ret)
        account_q += 1
    elif account_q == 2:
        text = '臺北市' if text == '台北市' else text
        account[userid]['county'] = text
        if text not in get_county_db(db):
            ret = TextSendMessage(text="不好意思，您所輸入的縣市不在我國疆域。提醒您中華民國採用繁體中文😁\n【請重新設定帳戶】")
            line_bot_api.reply_message(event.reply_token, ret)
            account.pop(userid)
            account_q = 0
        else:
            ret = TextSendMessage(text="請問您所在學校名稱為何？")
            line_bot_api.reply_message(event.reply_token, ret)
            account_q += 1
    elif account_q == 3:
        account[userid]['school'] = text
        if text not in get_school_db(account[userid]['county'], db):
            ret = TextSendMessage(text="您的學校尚未與本平台合作，請聯絡我們")
            line_bot_api.reply_message(event.reply_token, ret)
            account.pop(userid)
            account_q = 0
        else:
            if text in no_repeat_school_db(account[userid]['county'], db):
                ret = TextSendMessage(text="您的學校已有負責人，請洽詢主管")
                line_bot_api.reply_message(event.reply_token, ret)
                account.pop(userid)
                account_q = 0
            else:
                account_q += 1
                ret = TextSendMessage(text="請問您的連絡電話？")
                line_bot_api.reply_message(event.reply_token, ret)
    elif account_q == 4:
        account_q = 0
        account[userid]['phone'] = text
        ret = TextSendMessage(text="謝謝您的填答，您的身分已確認😁😁")
        line_bot_api.reply_message(event.reply_token, ret)
        get_account_db(account[userid], db)
        print(account[userid])

    ##################################
    ##########Postback Event#########
    ##################################

@handler.add(PostbackEvent)
def handle_postback(event):
    userid = event.source.user_id#取得Userid

    global parse_no
    global result
    global revise_result
    global EPD
    global account
    global account_q

    ##################################
    ########## 填問卷的過程 ##########
    ##################################

    #QC丟問題，相對題號
    if event.postback.data == 'Quick':
        line_bot_api.reply_message(
            event.reply_token, confirm_push(data, userid, event.postback.data, db))

    #四類丟問題，相對題號
    elif event.postback.data in ['Normal', 'Indoors', 'Corridor', 'Outdoors']:
        line_bot_api.reply_message(
            event.reply_token, confirm_push(data, userid, event.postback.data, db))

    #戳題目的confirm template的時候
    try:
        parse = extract(event.postback.data) #[0]是絕對題號；[1]是OK/NO
        ret = None
        cat = ''
        last = 0
        parse_no = parse[0]

        #給定各類別的最後一題
        if parse[0] in list(range(65,78)):
            last = 77
            cat = 'Quick'

        elif parse[0] in list(range(1,13)):
            last = 12
            cat = 'Normal'

        elif parse[0] in list(range(13,33)):
            last = 32
            cat = 'Indoors'

        elif parse[0] in list(range(33,46)):
            last = 45
            cat = 'Corridor'

        elif parse[0] in list(range(46,65)):
            last = 64
            cat = 'Outdoors'

        #處理carousel template
        #填完該類別最後一題且最後一題是沒問題
        if parse[0] == last and parse[1] == 'OK':
            data[userid][cat] += 1
            ct_container = ct_push(data, userid)
            data[userid]["Answered"].append(parse[0])

            #QC填完 or 全部都填過了
            if parse[0] == 77 or ct_container == [Normal1, Indoors1, Corridor1, Outdoors1]:
                output = feedback[userid]
                ret = tempview_confirm(output, db)#把它目前的回答推個confirm templatea給他看看

            #有類別沒填完
            else:
                carousel_template = CarouselTemplate(columns=ct_container)
                ret = TemplateSendMessage(alt_text='問卷選單', template=carousel_template)

        #處理題目的confirm template
        #待改進的話，或是非該類別的最後一題
        else:
            ret, result = next(data, userid, cat, parse, db)
            EPD = parse[0] if result is False else EPD

        line_bot_api.reply_message(event.reply_token, ret)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR:', exc_type, exc_obj, fname, exc_tb.tb_lineno)
        print(event.postback.data)

        if event.postback.data == 'edit=NO':
            print('AARRR')
            output = feedback.pop(userid) #填完了消滅它
            data.pop(userid)
            get_feedback(output, userid, db) #寫進資料庫

            ret = [
                TextSendMessage(text="已收到您的回覆～謝謝您的貢獻！"),
                StickerSendMessage(package_id=11537,sticker_id=52002739),
            ]

            line_bot_api.reply_message(event.reply_token, ret)

        if event.postback.data == 'edit=OK':
            print('AARRR')
            ret = [
                TextSendMessage(text="請問您要修改哪一題呢?"),
                TextSendMessage(text="【注意】：當您填寫快速檢核時，不能修改其他四類問題；反之亦然。\n\n請按照下列格式填寫，例如：\nNormal Q7"),
            ]
            line_bot_api.reply_message(event.reply_token, ret)

    ##################################
    ########## 修改答案的過程 #########
    ##################################

    if 'revise=' in event.postback.data and 'OK' in event.postback.data:#沒問題
        output = feedback[userid]
        ret = tempview_confirm(output, db)#把它目前的回答推個confirm template給他看看
        line_bot_api.reply_message(event.reply_token, ret)

    elif 'revise=' in event.postback.data and 'NO' in event.postback.data:#待改進
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="請簡述災情"))
        revise_result = False

    ##################################
    ########## 重設帳號或不設 #########
    ##################################

    if event.postback.data == 'account_reset':
        delete_userid_db(userid, db)
        account[userid] = {'userid':userid, 'name':0, 'county':0, 'school':0, 'phone':0}
        ret = TextSendMessage(text="請問您尊姓大名？")
        line_bot_api.reply_message(event.reply_token, ret)
        account_q = 1
    elif event.postback.data == 'account_remain':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="好的，謝謝😁"))

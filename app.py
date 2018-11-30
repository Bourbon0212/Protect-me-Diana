##################################
#########   Just Import  #########
##################################

from __future__ import unicode_literals
import errno
import os
import sys
import tempfile
from argparse import ArgumentParser
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction, PostbackTemplateAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)

#from class_DB import DB              #DB抓問題(.filename)
from extract_function import *       #RE抓數字
from ct_push import *                #抓推播新的carousel template
from confirm import *                #抓confirm template 進來
from carousel import *               #抓caousel columns
from confirm_push import *
from next import *
from get_res_db import *
from tempview import *
from converter import *
from revise import *

app = Flask(__name__)

    ##################################
    #########儲存使用者填答紀錄#########
    ##################################

data = {}
result = True #True是預設為沒問題；False就改成待改進；詳情請看後續發展
revise_result = True #不要懷疑就是有
feedback = {} #使用者回饋
EPD = 0 #填問卷的時候的絕對題號
revise_EPD = 0

    ##################################
    ##########  Good Simu   ##########
    ##################################

line_bot_api = None
if os.environ.get("FLASK_ENV") == "development":
    line_bot_api = LineBotApi(os.environ.get("TOKEN"), "http://localhost:8080")
else:
    line_bot_api = LineBotApi(os.environ.get("TOKEN"))

handler = WebhookHandler(os.environ.get("SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

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

    if text == '請給我表單填寫':
        if userid not in feedback:
            feedback[userid] = []

        if userid not in data:#沒有USERID的話，add key(第一次填寫的時候) 然後推處死carousel
            data[userid] = {"Quick":0, "Normal":0, "Indoors":0, "Corridor":0, "Outdoors":0, "Answered":[]}
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
                    ret = tempview_confirm(output)

                else:
                    carousel_template = CarouselTemplate(columns=ct_container)
                    ret = [
                    TemplateSendMessage(
                        alt_text='問卷選單',
                        template=carousel_template,
                    )]

            else:
                data[userid][cat] += 1 #待改進沒填到最後一題+1
                ret = [confirm(cat, data[userid][cat])]

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
            ret = [revise_confirm(cat, i)]
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
            ret = tempview_confirm(output)
            line_bot_api.reply_message(
                event.reply_token, [TextSendMessage(text='『' + text + '』已收到回覆')] + ret)



    #################################
    ############## 貼圖 ##############
    ##################################

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    userid = event.source.user_id

    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )

    ##################################
    ##########Postback Event#########
    ##################################

@handler.add(PostbackEvent)
def handle_postback(event):
    userid = event.source.user_id#取得Userid
    parse_no = 0 #從填寫confirm template的時候，抓出相對題號

    global result
    global revise_result
    global EPD
    ##################################
    ########## 填問卷的過程 ##########
    ##################################

    #QC丟問題，相對題號
    if event.postback.data == 'Quick':
        line_bot_api.reply_message(
            event.reply_token, confirm_push(data, userid, event.postback.data))

    #四類丟問題，相對題號
    elif event.postback.data in ['Normal', 'Indoors', 'Corridor', 'Outdoors']:
        line_bot_api.reply_message(
            event.reply_token, confirm_push(data, userid, event.postback.data))

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
                ret = tempview_confirm(output)#把它目前的回答推個confirm templatea給他看看

            #有類別沒填完
            else:
                carousel_template = CarouselTemplate(columns=ct_container)
                ret = TemplateSendMessage(alt_text='問卷選單', template=carousel_template)

        #處理題目的confirm template
        #待改進的話，或是非該類別的最後一題
        else:
            ret, result = next(data, userid, cat, parse)
            EPD = parse[0] if result is False else EPD

        line_bot_api.reply_message(event.reply_token, ret)
    except:
        if event.postback.data == 'edit=NO':
            output = feedback.pop(userid) #填完了消滅它
            data.pop(userid)
            get_feedback(output, userid, parse_no == 77) #寫進資料庫

            ret = [
                TextSendMessage(text="已收到您的回覆～謝謝您的貢獻！"),
                StickerSendMessage(package_id=11537,sticker_id=52002739),
            ]

            line_bot_api.reply_message(event.reply_token, ret)

        if event.postback.data == 'edit=OK':
            ret = [
            TextSendMessage(text="請問您要修改哪一題呢?"),
            TextSendMessage(text="請按照下列格式填寫，例如：\nNormal Q7"),
            ]
            line_bot_api.reply_message(event.reply_token, ret)

    ##################################
    ########## 修改答案的過程 #########
    ##################################

    if 'revise=' in event.postback.data and 'OK' in event.postback.data:#要改
        output = feedback[userid]
        ret = tempview_confirm(output)#把它目前的回答推個confirm templatea給他看看
        line_bot_api.reply_message(event.reply_token, ret)

    elif 'revise=' in event.postback.data and 'NO' in event.postback.data:#不要改
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="請簡述災情"))
        revise_result = False

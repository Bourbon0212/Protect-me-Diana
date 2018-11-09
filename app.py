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

app = Flask(__name__)

    ##################################
    #########儲存使用者填答紀錄#########
    ##################################

data = {}
result = True #True是預設為沒問題；False就改成待改進；詳情請看後續發展
feedback = {} #使用者回饋
EPD = 0 #絕對題號

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

    feedback[userid] = []
    global data

    if text == 'carousel':
        if userid not in data:#沒有USERID的話，add key(第一次填寫的時候) 然後推處死carousel
            data[userid] = {"Quick":0, "Normal":0, "Indoors":0, "Corridor":0, "Outdoors":0, "Answered":[]}
            ct_container = ct_push(data, userid)  #把4類別加進來
            ct_container.insert(0, Quick)         #還沒填過，所以加進來qc
            carousel_template = CarouselTemplate(columns=ct_container)
            template_message = TemplateSendMessage(alt_text='災情回覆問卷', template=carousel_template)
            line_bot_api.reply_message(event.reply_token, template_message)

        elif data[userid]['Quick'] != 0:#QC填到一半智障又打一次carousel
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="您已選擇快速檢核！請填頁面上的最後一題"))

        else:
            print(data[userid]['Normal'])
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
                    ret = [
                        TextSendMessage(text="問卷已經填答完成咯～謝謝您的貢獻！"),
                        StickerSendMessage(package_id=2,sticker_id=150),
                    ]

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
    ##################################
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

    global result
    global EPD

    ##################################
    ########## 填問卷的過程 ##########
    ##################################

    #QC丟問題，相對題號
    if event.postback.data == 'Quick':
        line_bot_api.reply_message(
            event.reply_token, confirm("Quick",data[userid]['Quick']))

    #四類丟問題，相對題號
    elif event.postback.data in ['Normal', 'Indoors', 'Corridor', 'Outdoors']:
        line_bot_api.reply_message(
            event.reply_token, confirm_push(data, userid, event.postback.data))

    #戳confirm template的時候
    else:
        parse = extract(event.postback.data) #[0]是絕對題號；[1]是OK/NO
        ret = None
        cat = ''
        last = 0

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

        #填完該類別最後一題且最後一題是沒問題
        if parse[0] == last and parse[1] == 'OK':
            data[userid][cat] += 1
            ct_container = ct_push(data, userid)

            #QC填完 or 全部都填過了
            if parse[0] == 77 or ct_container == [Normal1, Indoors1, Corridor1, Outdoors1]:
                ret = [
                    TextSendMessage(text="問卷已經填答完成咯～謝謝您的貢獻！"),
                    StickerSendMessage(package_id=2,sticker_id=150),
                ]

            #有類別沒填完
            else:
                carousel_template = CarouselTemplate(columns=ct_container)
                ret = TemplateSendMessage(alt_text='問卷選單', template=carousel_template)

        #待改進的話，或是非該類別的最後一題
        else:
            ret, result = next(data, userid, cat, parse)
            EPD = parse[0] if result is False else EPD

        line_bot_api.reply_message(event.reply_token, ret)

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

from class_DB import DB              #DB抓問題(.filename)
from extract_function import *       #RE抓數字
from carousel import *               #CT抓欄位


app = Flask(__name__)

##################################
##########  Good Simu   ##########
##################################


line_bot_api = LineBotApi(os.environ.get("TOKEN"), "http://localhost:8080")
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


    if text == 'carousel':
        carousel_template = CarouselTemplate(columns=[Quick, Normal0, Indoors0, Corridor0, Outdoors0])
        template_message = TemplateSendMessage(alt_text='問卷選單', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    else:
        pass



@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


##################################
#########Confirm Template#########
##################################

data = {}
quick = {}

def confirm(cat, i):
    db = DB()
    questions = db.get_category(cat)
    return   TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text = questions[i][1],
                    actions=[
                        PostbackTemplateAction(
                            label='沒問題',
                            text='沒問題',
                            data='no=' + str(questions[i][0]) + '&answer=OK' #questions是整份問卷第幾題 相對題號
                        ),
                        PostbackTemplateAction(
                            label='待改進',
                            text='待改進',
                            data='no=' + str(questions[i][0]) + '&answer=NO'
                        )
                    ]
                ))

##################################
##########Postback Event##########
##################################

@handler.add(PostbackEvent)
def handle_postback(event):
    userid = event.source.user_id#取得Userid

    ##################################
    ##########  戳 CT 的時候 ##########
    ##################################

    if event.postback.data == 'Quick':
        if userid not in quick:#沒有USERID的話，add key(第一次填寫的時候)
            quick[userid] = {"Quick":0}
        else:
            pass
        line_bot_api.reply_message(
            event.reply_token, confirm("QuickCheck",quick[userid]['Quick']))


    #Normal丟問題，相對題號
    elif event.postback.data == 'Normal':
        if userid not in data:#沒有USERID的話，add key(第一次填寫的時候)
            data[userid] = {"Normal":0, "Indoors":0, "Corridor":0, "Outdoors":0}
        else:
            pass
        line_bot_api.reply_message(
            event.reply_token, confirm("Normal",data[userid]['Normal']))

    #Indoors丟問題，相對題號
    elif event.postback.data == 'Indoors':
        if userid not in data:#沒有USERID的話，add key(第一次填寫的時候)
            data[userid] = {"Normal":0, "Indoors":0, "Corridor":0, "Outdoors":0}
        else:
            pass
        line_bot_api.reply_message(
            event.reply_token, confirm("Indoors",data[userid]['Indoors']))

    #Corridor丟問題，相對題號
    elif event.postback.data == 'Corridor':
        if userid not in data:#沒有USERID的話，add key(第一次填寫的時候)
            data[userid] = {"Normal":0, "Indoors":0, "Corridor":0, "Outdoors":0}
        else:
            pass
        line_bot_api.reply_message(
            event.reply_token, confirm("Corridor",data[userid]['Corridor']))

    #Outdoors丟問題，相對題號
    elif event.postback.data == 'Outdoors':
        if userid not in data:#沒有USERID的話，add key(第一次填寫的時候)
            data[userid] = {"Normal":0, "Indoors":0, "Corridor":0, "Outdoors":0}
        else:
            pass
        line_bot_api.reply_message(
            event.reply_token, confirm("Outdoors",data[userid]['Outdoors']))


        ##################################
        ###########   計數器    ##########
        ##################################

    #從 Confirm 收到Quick Check 65-77題，自訂函數 extract
    elif extract(event.postback.data) in list(range(65,77)):
        quick[userid]['Quick'] += 1
        line_bot_api.reply_message(
            event.reply_token, confirm("QuickCheck",quick[userid]['Quick']))

    #從 Confirm 收到Normal 1-11題，自訂函數 extract
    elif extract(event.postback.data) in list(range(1,12)):
        data[userid]['Normal'] += 1
        line_bot_api.reply_message(
            event.reply_token, confirm("Normal",data[userid]['Normal']))

    #從 Confirm 收到Indoors 13-32題，自訂函數 extract
    elif extract(event.postback.data) in list(range(13,32)):
        data[userid]['Indoors'] += 1
        line_bot_api.reply_message(
            event.reply_token, confirm("Indoors",data[userid]['Indoors']))

    #從 Confirm 收到Corridor 33-45題，自訂函數 extract
    elif extract(event.postback.data) in list(range(33,45)):
        data[userid]['Corridor'] += 1
        line_bot_api.reply_message(
            event.reply_token, confirm("Corridor",data[userid]['Corridor']))

    #從 Confirm 收到Outdoors 46-64題，自訂函數 extract
    elif extract(event.postback.data) in list(range(46,64)):
        data[userid]['Outdoors'] += 1
        line_bot_api.reply_message(
            event.reply_token, confirm("Outdoors",data[userid]['Outdoors']))


        ##################################
        ##########重新調整CT，戳###########
        ##################################

    elif extract(event.postback.data) == 77:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="問卷已經填答完成咯～謝謝您的貢獻！"))

    #如果Confirm收到12(Normal的最後一題)的話要跳回去Ct
    elif extract(event.postback.data) == 12:#絕對題數
        ct_container = []
        ct_container.append(Normal1)

        if data[userid]['Indoors'] == 19:#該類題數
            ct_container.append(Indoors1)
        else:
            ct_container.append(Indoors0)

        if data[userid]['Corridor'] == 12:#該類題數
            ct_container.append(Corridor1)
        else:
            ct_container.append(Corridor0)

        if data[userid]['Outdoors'] == 18:#該類題數
            ct_container.append(Outdoors1)
        else:
            ct_container.append(Outdoors0)

        if ct_container == [Normal1, Indoors1, Corridor1, Outdoors1]: #所有類別均填答完成後
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="問卷已經填答完成咯～謝謝您的貢獻！"))
        else:
            carousel_template = CarouselTemplate(columns=ct_container)
            template_message = TemplateSendMessage(alt_text='問卷選單', template=carousel_template)
            #把CT推出去
            line_bot_api.reply_message(
                event.reply_token, template_message)


    #如果Confirm收到32(Indoors的最後一題)的話要跳回去Ct
    elif extract(event.postback.data) == 32:#絕對題數
        ct_container = []
        ct_container.append(Indoors1)

        if data[userid]['Normal'] == 11:#該類題數
            ct_container.insert(0, Normal1)
        else:
            ct_container.insert(0, Normal0)


        if data[userid]['Corridor'] == 12:#該類題數
            ct_container.insert(2, Corridor1)
        else:
            ct_container.insert(2, Corridor0)

        if data[userid]['Outdoors'] == 18:#該類題數
            ct_container.append(Outdoors1)
        else:
            ct_container.append(Outdoors0)

        if ct_container == [Normal1, Indoors1, Corridor1, Outdoors1]: #所有類別均填答完成後
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="問卷已經填答完成咯～謝謝您的貢獻！"))
        else:
            carousel_template = CarouselTemplate(columns=ct_container)
            template_message = TemplateSendMessage(alt_text='問卷選單', template=carousel_template)
            #把CT推出去
            line_bot_api.reply_message(
                event.reply_token, template_message)


    #如果Confirm收到45(Corridor的最後一題)的話要跳回去Ct
    elif extract(event.postback.data) == 45:#絕對題數
        ct_container = []
        ct_container.append(Corridor1)

        if data[userid]['Normal'] == 11:#該類題數
            ct_container.insert(0, Normal1)
        else:
            ct_container.insert(0, Normal0)

        if data[userid]['Indoors'] == 19:#該類題數
            ct_container.insert(1, Indoors1)
        else:
            ct_container.insert(1, Indoors0)

        if data[userid]['Outdoors'] == 18:#該類題數
            ct_container.append(Outdoors1)
        else:
            ct_container.append(Outdoors0)

        if ct_container == [Normal1, Indoors1, Corridor1, Outdoors1]: #所有類別均填答完成後
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="問卷已經填答完成咯～謝謝您的貢獻！"))
        else:
            carousel_template = CarouselTemplate(columns=ct_container)
            template_message = TemplateSendMessage(alt_text='問卷選單', template=carousel_template)
            #把CT推出去
            line_bot_api.reply_message(
                event.reply_token, template_message)


    #如果Confirm收到64(Outdoors的最後一題)的話要跳回去Ct
    elif extract(event.postback.data) == 64:#絕對題數
        ct_container = []
        ct_container.append(Outdoors1)

        if data[userid]['Normal'] == 11:#該類題數
            ct_container.insert(0, Normal1)
        else:
            ct_container.insert(0, Normal0)

        if data[userid]['Indoors'] == 19:#該類題數
            ct_container.insert(1, Indoors1)
        else:
            ct_container.insert(1, Indoors0)

        if data[userid]['Corridor'] == 12:#該類題數
            ct_container.insert(2, Corridor1)
        else:
            ct_container.insert(2, Corridor0)

        if ct_container == [Normal1, Indoors1, Corridor1, Outdoors1]: #所有類別均填答完成後
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="問卷已經填答完成咯～謝謝您的貢獻！"))
            line_bot_api.reply_message(
                event.reply_token,
                StickerSendMessage(
                    package_id=event.message.package_id,
                    sticker_id=event.message.sticker_id)
            )
        else:
            carousel_template = CarouselTemplate(columns=ct_container)
            template_message = TemplateSendMessage(alt_text='問卷選單', template=carousel_template)
            #把CT推出去
            line_bot_api.reply_message(
                event.reply_token, template_message)

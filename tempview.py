from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
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
from class_DB import DB              #DB抓問題

from class_DB import DB              #DB抓問題

def takeFirst(elem):
    return elem[0]

def tempview(output):
    db = DB()
    questions = db.get_all()
    render = []

    output.sort(key=takeFirst)

    for i, value in output:
        i -= 1 #題號校正
        display = """題目：{} Q{}({})
回覆：{}""".format(questions[i][2], str(questions[i][3]), questions[i][1], value)
        render.append(display)

    return """您好，您的回覆如下：

{}

未顯示之題目為『沒問題』

【注意】：當您填寫快速檢核時，不能修改其他四類問題；反之亦然。""".format('\n\n'.join(render))

    # 功能：給他暫時看看他剛剛到底說了什麼要待改進的東西
    # 輸入：output = feedback[userid]
    # 輸出：str (他所回覆要待改進的內容)

def tempview_confirm(output):
    ret = [
        StickerSendMessage(package_id=2,sticker_id=150),
        TextSendMessage(text=tempview(output)),
        TemplateSendMessage(
                    alt_text='Confirm template',
                    template=ConfirmTemplate(
                        text = '請問您要修改您的回答嗎？',
                        actions=[
                            PostbackTemplateAction(
                                label='要',
                                text='我要修改我的答案',  #給使用者看相對題號
                                data='edit=OK' #questions是整份問卷第幾題 絕對題號
                            ),
                            PostbackTemplateAction(
                                label='不要',
                                text='我已確認沒問題', #給使用者看相對題號
                                data='edit=NO'
                            )
                        ]
                    ))
    ]
    return ret

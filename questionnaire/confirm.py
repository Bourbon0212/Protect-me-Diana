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

from .class_DB import DB             #DB抓問題


def confirm(cat, i):
    db = DB()
    questions = db.get_category(cat)
    #這裡i 不用 -= 1 是因為data[userid][cat]是從 0開始計算
    return   TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text = str(questions[i][2]) + ' Q' + str(questions[i][3]) + ' : ' + questions[i][1],
                    actions=[
                        PostbackTemplateAction(
                            label='沒問題',
                            text=str(questions[i][2]) + ' 第' + str(questions[i][3]) + '題已回覆沒問題',  #給使用者看相對題號
                            data='no=' + str(questions[i][0]) + '&answer=OK' #questions是整份問卷第幾題 絕對題號
                        ),
                        PostbackTemplateAction(
                            label='待改進',
                            text=str(questions[i][2]) + ' 第' + str(questions[i][3]) + '題已回覆待改進', #給使用者看相對題號
                            data='no=' + str(questions[i][0]) + '&answer=NO'
                        )
                    ]
                ))

    # 功能：從DB抓問題，編織成confirm tempate
    # 輸入：1.cat ： 類別
    #      2. i  ： 絕對題號
    # 輸出：ConfirmTemplate with question

def account_confirm():
    return   TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text = "你已經設定過帳戶資訊囉，請問您要重新設定嗎？",
                    actions=[
                        PostbackTemplateAction(
                            label='是的',
                            # text="我要設定帳號",  #給使用者看相對題號
                            data='account_reset' #questions是整份問卷第幾題 絕對題號
                        ),
                        PostbackTemplateAction(
                            label='不用',
                            text="不用，謝謝", #給使用者看相對題號
                            data='account_remain'
                        )
                    ]
                ))

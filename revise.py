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

from class_DB import DB              #DB抓問題

def revise_idiot(text, cat, i):

    if cat == "Quick" and int(i) > 13:
        ret = str(cat)+"最多只有13題唷"
        return ret
    elif cat == "Normal" and int(i) > 12:
        ret = str(cat)+"最多只有12題唷"
        return ret
    elif cat == "Indoors" and int(i) > 20:
        ret = str(cat)+"最多只有20題唷"
        return ret
    elif cat == "Corridor" and int(i) > 13:
        ret = str(cat)+"最多只有13題唷"
        return ret
    elif cat == "Outdoors" and int(i) > 19:
        ret = str(cat)+"最多只有19題唷"
        return ret
    else:
        ret = '請輸入正確格式\n例如：Normal Q10'

def revise_confirm(cat, i):
    i -= 1 #相對題號從1開始算，所以要減1才能符合list的規定
    db = DB()
    questions = db.get_category(cat)
    return   TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text = str(questions[i][2]) + ' Q' + str(questions[i][3]) + ' : ' + questions[i][1],
                    actions=[
                        PostbackTemplateAction(
                            label='沒問題',
                            text=str(questions[i][2]) + ' 第' + str(questions[i][3]) + '題已回覆沒問題',  #給使用者看相對題號
                            data='revise=' + str(questions[i][0]) + '&answer=OK' #questions是整份問卷第幾題 絕對題號
                        ),
                        PostbackTemplateAction(
                            label='待改進',
                            text=str(questions[i][2]) + ' 第' + str(questions[i][3]) + '題已回覆待改進', #給使用者看相對題號
                            data='revise=' + str(questions[i][0]) + '&answer=NO'
                        )
                    ]
                ))

    # 功能： 為了避免與之前的confirm搞混，我們改變該confirm template回傳的data
    # 輸入： 1. cat = revise_extract(text)[0]
    #       2. i   = revise_extract(text)[1]
    # 輸出： ConfirmTemplate

def revise_able(cat, i):

    if cat == 'Quick' and i in range(14):
        return True

    elif cat == 'Normal' and i in range(13):
        return True

    elif cat == 'Indoors' and i in range(21):
        return True

    elif cat == 'Corridor' and i in range(14):
        return True

    elif cat == 'Outdoors' and i in range(20):
        return True

    else:
        return False

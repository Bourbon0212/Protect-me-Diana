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

from confirm import *                #抓confirm template 進來

def next(data, userid, cat, parse):

        if parse[0] in data[userid]["Answered"]:
            return TextSendMessage(text="您已經填寫過此題了！請填頁面上的最後一題"), True

        else:
            if parse[1] == 'OK':
                data[userid]["Answered"].append(parse[0])
                data[userid][cat] += 1
                return confirm(cat ,data[userid][cat]), True

            elif parse[1] == 'NO':
                return TextSendMessage(text="請簡述災情"), False

    # 功能：首先，不讓他重複填答。若使用者回覆沒問題，則在data[userid]['Answered']中
    #      加入該題絕對題號，然後計數器data[userid][cat] + 1，並且推下議題的confirm
    #      template；若該題之回覆為待改進，則叫他打字
    # 輸入：
    #      1. data
    #      2. userid
    #      3. cat
    #      4. parse:extarct(event.postback.data) [0]是絕對題號；[1]是OK/NO
    # 輸出：
    #      0. (str) 叫他不要重複填寫
    #      1. 沒問題：ConfirmTemplate & result = True
    #      2. 待改進：(str)叫他簡述災情 & result = False

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

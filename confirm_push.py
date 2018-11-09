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


def confirm_push(data, userid, cat):

        if data[userid]['Quick'] == 12:#QC填完了
            return TextSendMessage(text="問卷已經填答完成咯～謝謝您的貢獻！")

        elif data[userid]['Quick'] != 0:#QC填到一半 智障又打一次carousel
            return TextSendMessage(text="您已選擇快速檢核！請填頁面上的最後一題")

        else:
            return confirm(cat ,data[userid][cat])

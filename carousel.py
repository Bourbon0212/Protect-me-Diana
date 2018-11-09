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

from image import *     #IM抓照片

Quick = CarouselColumn(
                    thumbnail_image_url=image_url_QC,
                    title='Quick Check',
                    text='若事況緊急，請直接填寫快速檢核！',
                    actions=[
                        PostbackTemplateAction(
                            label='開始填寫',
                            text='Quick Check',
                            data='Quick'
                        )
                    ]
                )
Normal0 = CarouselColumn(
                    thumbnail_image_url=image_url_N0,
                    title='Normal',
                    text='這是一般性檢查',
                    actions=[
                        PostbackTemplateAction(
                            label='開始填寫',
                            text='Normal',
                            data='Normal'
                        )
                    ]
                )
Normal1 = CarouselColumn(
                    thumbnail_image_url=image_url_N1,
                    title='Normal',
                    text='這是一般性檢查',
                    actions=[
                        PostbackTemplateAction(
                            label='已經填寫了~',
                            #text='postback text1',
                            data='已經填寫了~'
                        )
                    ]
                )
Indoors0 = CarouselColumn(
                    thumbnail_image_url=image_url_I0,
                    title='Indoors',
                    text='這是門/窗/牆/天花板/柱/地板',
                    actions=[
                        PostbackTemplateAction(
                            label='開始填寫',
                            text='Indoors',
                            data='Indoors'
                        )
                    ]
                )
Indoors1 = CarouselColumn(
                    thumbnail_image_url=image_url_I1,
                    title='Indoors',
                    text='這是門/窗/牆/天花板/柱/地板',
                    actions=[
                        PostbackTemplateAction(
                            label='已經填寫了~',
                            #text='postback text1',
                            data='已經填寫了~'
                        )
                    ]
                )
Corridor0 = CarouselColumn(
                    thumbnail_image_url=image_url_C0,
                    title='Corridor',
                    text='這是欄杆/樓梯/走廊',
                    actions=[
                        PostbackTemplateAction(
                            label='開始填寫',
                            text='Corridor',
                            data='Corridor'
                        )
                    ]
                )
Corridor1 = CarouselColumn(
                    thumbnail_image_url=image_url_C1,
                    title='Corridor',
                    text='這是欄杆/樓梯/走廊',
                    actions=[
                        PostbackTemplateAction(
                            label='已經填寫了~',
                            #text='postback text1',
                            data='已經填寫了~'
                        )
                    ]
                )
Outdoors0 = CarouselColumn(
                    thumbnail_image_url=image_url_O0,
                    title='Outdoors',
                    text='這是地基/屋頂/管線/消防',
                    actions=[
                        PostbackTemplateAction(
                            label='開始填寫',
                            text='Outdoors',
                            data='Outdoors'
                        )
                    ]
                )
Outdoors1 = CarouselColumn(
                    thumbnail_image_url=image_url_O1,
                    title='Outdoors',
                    text='這是地基/屋頂/管線/消防',
                    actions=[
                        PostbackTemplateAction(
                            label='已經填寫了~',
                            #text='postback text1',
                            data='已經填寫了~'
                        )
                    ]
                )

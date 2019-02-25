from linebot.models import (
    TemplateSendMessage, ConfirmTemplate, PostbackTemplateAction,
)

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

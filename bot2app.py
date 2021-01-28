import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


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
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    text = event.message.text
    data = text.split()
    if "@query" in text:
        if len(data) == 3:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="https://www.google.com/search?q="+data[1]+data[2])
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="格式錯誤，請以空格隔開時間與@query，\n 查詢請輸入 @query + 時間 \n(ex: 1/31 12:00) ，\n 申報請輸入 @report + 時間 + 交流道 \n(ex: 1/31 12:00 新竹交流道)")
            )
    elif "@report" in text:
        if len(data) == 4:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="https://www.google.com/search?q="+data[1]+data[2]+data[3])
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="格式錯誤，請以空格隔開時間與@report，\n 查詢請輸入 @query + 時間 \n(ex: 1/31 12:00) ，\n 申報請輸入 @report + 時間 + 交流道 \n(ex: 1/31 12:00 新竹交流道)")
            )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="格式錯誤，\n 查詢請輸入 @query + 時間 \n(ex: 1/31 12:00) ，\n 申報請輸入 @report + 時間 + 交流道 \n(ex: 1/31 12:00 新竹交流道)")
        )




if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=True, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
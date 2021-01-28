from flask import (
    Flask,
    render_template,
    send_from_directory,
    request,
    abort
)

from argparse import ArgumentParser
from flask_bootstrap import Bootstrap
from decrypt import decrypt_token
from pyngrok import ngrok
import os

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
bootstrap = Bootstrap(app)

HOST = None
SYSTEM_HOST = 'http://localhost:8508'

if __name__ == '__main__':

    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=443, help='port')
    arg_parser.add_argument('-d', '--debug', default=True, help='debug')
    arg_parser.add_argument('-n', '--nobot', default=False, help='nobot')
    options = arg_parser.parse_args()

    port = int(os.environ.get("BOTPORT", options.port))

    if not options.nobot:
        # get channel_secret and channel_access_token from your environment variable
        channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
        channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
        if channel_secret is None:
            print('Specify LINE_CHANNEL_SECRET as environment variable.')
            exit(1)
        if channel_access_token is None:
            print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
            exit(1)

        line_bot_api = LineBotApi(channel_access_token)
        handler = WebhookHandler(channel_secret)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/query')
def query():
    return render_template("query.html")

@app.route('/psys')
def psys():
    return render_template("psys.html")

@app.route('/ssys', methods=['GET'])
def ssys():
    SYSTEM_HOST = request.values.get('host')
    print(f'SYSTEM_HOST = {SYSTEM_HOST}')
    return 'OK'

@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory(os.path.join('templates', 'dist'), path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(os.path.join('templates', 'css'), path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(os.path.join('templates', 'js'), path)

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

if not options.nobot:
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

if __name__ == '__main__':

    #print("============ Setup ngrok ======================")
    #ngrok.set_auth_token(decrypt_token(os.path.join('meta', 'encrypted.bot.ngrok.token')))
    #hook_url = ngrok.connect(port).replace("http", "https")
    #print("Hook url: " + hook_url)
    #HOST = hook_url

    print(f"\nopen http://localhost:{port}/psys to wait system server\n")

    if not HOST: HOST = f'http://localhost:{port}'

    sslcert, sslkey = os.getenv('SSL_CERT', None), os.getenv('SSL_KEY', None)

    print("============ App run ==========================")

    if sslcert and sslkey:
        app.run(host="0.0.0.0", debug=options.debug, port=port, ssl_context=(sslcert, sslkey))
    else:
        app.run(host="0.0.0.0", debug=options.debug, port=port)

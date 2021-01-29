#coding=utf-8
import datetime
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
        label = parse_str(event.message.text)
        if label["type"] == "query":
            if label["Error"] == []:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="https://www.google.com/search?q=")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="格式錯誤，\n 查詢請輸入 query + 地點 + 時間 \n(ex: query 新竹交流道 1/31 13:00) ，\n 申報請輸入 report + 交流道1 + 交流道2 + 時間 \n(ex: report 新竹交流道 到 台北交流道 1/31 13:00)")
                )
        elif label["type"] == "report":
            if label["Error"] == []:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="https://www.google.com/search?q=")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="格式錯誤，\n 查詢請輸入 query + 地點 + 時間 \n(ex: query 新竹交流道 1/31 13:00) ，\n 申報請輸入 report + 交流道1 + 交流道2 + 時間 \n(ex: report 新竹交流道 到 台北交流道 1/31 13:00)")
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="格式錯誤，\n 查詢請輸入 query + 地點 + 時間 \n(ex: query 新竹交流道 1/31 13:00) ，\n 申報請輸入 report + 交流道1 + 交流道2 + 時間 \n(ex: report 新竹交流道 到 台北交流道 1/31 13:00)")
            )
loc_table = ["基隆端", "基隆", "八堵", "大華系統", "五堵", "汐止", "汐止系統", "高架汐止端", "東湖", "內湖", "圓山", "台北", "三重", "五股轉接道", "五股", "高公局", "泰山轉接道", "林口", "桃園", "機場系統", "中壢服務區", "內壢", "中壢轉接一", "中壢轉接二", "中壢", "平鎮系統", "幼獅", "楊梅", "高架楊梅端", "湖口", "湖口服務區", "竹北", "新竹", "新竹系統", "頭份", "頭屋", "苗栗", "銅鑼", "三義", "泰安服務區", "后里", "台中系統", "豐原", "大雅", "台中", "南屯", "王田", "彰化系統", "彰化", "埔鹽系統", "員林", "北斗", "西螺服務區", "西螺", "虎尾", "斗南", "雲林系統", "大林", "民雄", "嘉義", "水上", "嘉義系統", "新營服務區", "新營", "下營系統", "麻豆", "安定", "台南系統", "永康", "大灣", "仁德", "仁德系統", "仁德服務區", "路竹", "高科", "岡山", "楠梓", "鼎金系統", "高雄", "瑞隆路", "五甲系統", "五甲", "中山四路", "漁港路", "高雄端"]
def parse_str(text):
    data = text.split()
    label = {"type":"","date":"","time":"","loc":"","loc_from":"","loc_to":"","Error":[]}
    if any([("申報" in d or "report" in d) for d in data]):
        label["type"] = "report"
        loc_list = []
        for i in range(len(data)):
            if ":" in data[i]: # time
                label = parse_time(data,i,label)
            elif "/" in data[i]: # date
                label = parse_date(data,i,label)
            elif any([(loc in data[i]) for loc in loc_table]): # loc
                index_list = []
                for loc in loc_table:
                    if loc in data[i]:
                        index_list.append((loc,data[i].index(loc)))
                for loc, _ in sorted(index_list, key=lambda x: x[1]):
                    loc_list.append(loc)
        if len(loc_list) == 2:
            label["loc_from"] = loc_list[0]
            label["loc_to"] = loc_list[1]
        else:
            label["Error"].append("loc_from") 
            label["Error"].append("loc_to") 
    elif any([("查詢" in d or "query" in d or "查" in d) for d in data]):
        label["type"]="query"
        for i in range(len(data)):
            if ":" in data[i]: # time
                label = parse_time(data,i,label)
            elif "/" in data[i]: # date
                label = parse_date(data,i,label)
            elif any([(loc in data[i]) for loc in loc_table]): # loc
                for loc in loc_table:
                    if loc in data[i]:
                        label["loc"] = loc
                if label["loc"] == "":
                    label["Error"].append("loc") 
                
    return label

def parse_date(data,i,label):
    if len(data[i])==1:
        if (i != 0 or i != len(data)-1) and data[i-1].isnumeric() and data[i+1].isnumeric():
            try:
                year = datetime.date.today().year
                datetime.date(year,data[i-1],data[i+1])
                label["time"] = data[i-1] + "/" + data[i+1]
            except:
                label["Error"].append("date") 
        else:
            label["Error"].append("date") 
    else:
        date_data = data[i].split("/")
        if len(date_data) == 2 and date_data[0].isnumeric() and date_data[1].isnumeric():
            try:
                year = datetime.date.today().year
                datetime.date(year,date_data[i-1],date_data[i+1])
                label["date"] = date_data[0] + "/" + date_data[1]
            except:
                label["Error"].append("date") 
        else:
            label["Error"].append("date") 
    return label

def parse_time(data,i,label):
    if len(data[i])==1:
        if (i != 0 or i != len(data)-1) and data[i-1].isnumeric() and data[i+1].isnumeric():
            if 0 <= int(data[i-1]) <= 24 and 0 <= int(data[i+1]) < 60:
                label["time"] = data[i-1] + ":" + data[i+1]
            else:
                label["Error"].append("time") 
        else:
            label["Error"].append("time") 
    else:
        time_data = data[i].split(":")
        if len(time_data) == 2 and time_data[0].isnumeric() and time_data[1].isnumeric():
            if 0 <= int(time_data[0]) <= 24 and 0 <= int(time_data[1]) < 60:
                label["time"] = time_data[0] + ":" + time_data[1]
            else:
                label["Error"].append("time") 
        else:
            label["Error"].append("time") 
    return label

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

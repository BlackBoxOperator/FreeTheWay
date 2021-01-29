#coding=utf-8
from datetime import datetime
import pandas as pd
from motc_data.motc_data import *
import pymongo
import random
#from ckiptagger import WS
from fuzzywuzzy import fuzz, process
from flask import (
    Flask,
    jsonify,
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

# from linebot import (
#     LineBotApi, WebhookHandler
# )
# from linebot.exceptions import (
#     InvalidSignatureError
# )
# from linebot.models import (
#     MessageEvent, TextMessage, TextSendMessage,
# )

app = Flask(__name__)
bootstrap = Bootstrap(app)

HOST = None
SYSTEM_HOST = 'http://localhost:8508'
#ws = WS("./data")

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
    # print(f'SYSTEM_HOST = {SYSTEM_HOST}')
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
        print(label)
        if label["type"] == "query":
            print(label["type"] == "query",label["type"])
            if len(label["Error"])==0:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="https://www.google.com/search?q="+label["date"]+label["time"]+label["loc"])
                )
            else:
                rtn = ""
                for er in label["Error"]:
                    if er == "date":
                        rtn += "日期錯誤，"
                    if er == "time":
                        rtn += "時間錯誤，"
                    if er == "loc":
                        rtn += "地點錯誤或交流道不存在，"
                rtn += "格式錯誤，\n 查詢請輸入 查詢(or query) + 地點 + 時間 \n(ex: query 新竹交流道 1/31 13:00) ，\n 申報請輸入 申報(or report) + 起點交流道 + 終點交流道 + 時間 \n(ex: report 新竹交流道 到 台北交流道 1/31 13:00)"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=rtn)
                )
        elif label["type"] == "report":
            print(label["type"] == "report",label["type"])
            if len(label["Error"])==0:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="https://www.google.com/search?q="+label["date"]+label["time"]+label["loc_from"]+label["loc_to"])
                )
            else:
                rtn = ""
                for er in label["Error"]:
                    if er == "date":
                        rtn += "日期錯誤，"
                    if er == "time":
                        rtn += "時間錯誤，"
                    if er == "loc_from":
                        rtn += "起點地點錯誤或交流道不存在，"
                    if er == "loc_to":
                        rtn += "終點地點錯誤或交流道不存在，"
                rtn += "格式錯誤，\n 查詢請輸入 查詢(or query) + 地點 + 時間 \n(ex: query 新竹交流道 1/31 13:00) ，\n 申報請輸入 申報(or report) + 起點交流道 + 終點交流道 + 時間 \n(ex: report 新竹交流道 到 台北交流道 1/31 13:00)"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=rtn)
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="格式錯誤，\n 查詢請輸入 查詢(or query) + 地點 + 時間 \n(ex: query 新竹交流道 1/31 13:00) ，\n 申報請輸入 申報(or report) + 起點交流道 + 終點交流道 + 時間 \n(ex: report 新竹交流道 到 台北交流道 1/31 13:00)")
            )
loc_table = ["基隆端", "基隆", "八堵", "大華系統", "五堵", "汐止", "汐止系統", "高架汐止端", "東湖", "內湖", "圓山", "台北", "三重", "五股轉接道", "五股", "高公局", "泰山轉接道", "林口", "桃園", "機場系統", "中壢服務區", "內壢", "中壢轉接一", "中壢轉接二", "中壢", "平鎮系統", "幼獅", "楊梅", "高架楊梅端", "湖口", "湖口服務區", "竹北", "新竹", "新竹系統", "頭份", "頭屋", "苗栗", "銅鑼", "三義", "泰安服務區", "后里", "台中系統", "豐原", "大雅", "台中", "南屯", "王田", "彰化系統", "彰化", "埔鹽系統", "員林", "北斗", "西螺服務區", "西螺", "虎尾", "斗南", "雲林系統", "大林", "民雄", "嘉義", "水上", "嘉義系統", "新營服務區", "新營", "下營系統", "麻豆", "安定", "台南系統", "永康", "大灣", "仁德", "仁德系統", "仁德服務區", "路竹", "高科", "岡山", "楠梓", "鼎金系統", "高雄", "瑞隆路", "五甲系統", "五甲", "中山四路", "漁港路", "高雄端"]
def parse_str(text):
    return None
#    data = ws([text])[0]
#
#    label = {"type":"","date":"","time":"","loc":"","loc_from":"","loc_to":"","Error":[]}
#    if any([("申報" in d or "report" in d) for d in data]):
#        label["type"] = "report"
#        loc_list = []
#        for i in range(len(data)):
#            if ":" in data[i]: # time
#                label = parse_time(data,i,label)
#            elif "/" in data[i]: # date
#                label = parse_date(data,i,label)
#            elif len(data[i]) >= 2: # loc
#                try:
#                    blur_pro = process.extractOne(data[i], loc_table)
#                    if blur_pro[1] > 40:
#                        loc_list.append(blur_pro[0])
#                except:
#                    print(data[i])
#        if len(loc_list) == 2:
#            label["loc_from"] = loc_list[0]
#            label["loc_to"] = loc_list[1]
#        else:
#            label["Error"].append("loc_from")
#            label["Error"].append("loc_to")
#    elif any([("看" in d or "搜尋" in d  or "查詢" in d or "query" in d or "查" in d) for d in data]):
#        label["type"]="query"
#        for i in range(len(data)):
#            if ":" in data[i]: # time
#                label = parse_time(data,i,label)
#            elif "/" in data[i]: # date
#                label = parse_date(data,i,label)
#            elif len(data[i]) >= 2: # loc
#                try:
#                    blur_pro = process.extractOne(data[i], loc_table)
#                    if blur_pro[1] > 40:
#                        label["loc"] = blur_pro[0]
#                except:
#                    label["Error"].append("loc")
#                    print(data[i])
#
#
#    return label

def parse_date(data,i,label):
    if len(data[i])==1:
        if (i != 0 or i != len(data)-1) and data[i-1].isnumeric() and data[i+1].isnumeric():
            try:
                year = datetime.date.today().year
                datetime.date(year,int(data[i-1]),int(data[i+1]))
                label["time"] = data[i-1] + "/" + data[i+1]
            except:
                label["Error"].append("date")
        else:
            label["Error"].append("date")
    else:
        data[i] = data[i].replace('月','')
        data[i] = data[i].replace('日','')
        data[i] = data[i].replace('號','')
        date_data = data[i].split("/")
        if len(date_data) == 2 and date_data[0].isnumeric() and date_data[1].isnumeric():
            try:
                year = datetime.date.today().year
                datetime.date(year,int(date_data[0]),int(date_data[1]))
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

@app.route('/pbot')
def pbot():
    return render_template("pbot.html")

@app.route('/sbot', methods=['GET'])
def sbot():
    BOT_HOST = request.values.get('host')
    # print(f'BOT_HOST = {BOT_HOST}')
    return 'OK'

@app.route('/traffic', methods=['POST'])
def traffic_at_time():
    global traffic_db
    global section_ids
    global travel_time_dict

    data = request.get_json()


    reportid = data['reportid'] if 'reportid' in data else None

    direction = data['direction'] if 'direction' in data else None


    dl = reportid.split('.') if 'reportid' in data else None
    time = data['time'] if 'time' in data else dl[1]+'/'+dl[2]+' '+'0:00'

    # print(time)




    strip = 20
    maxv = int(24 * 60 / strip)



                # if a.count() != 0:
                #     print(list(a))


    t = time.split(' ')[1].split(':')
    day = time.split(' ')[0].split('/')

    w = int(t[0])*60 + int(t[1])

    m = int(day[0]) * 100
    d = int(day[1])
    tag = str(m + d)

    if tag not in travel_time_dict:
        travel_time_dict[tag] = {}
        travel_time_dict[tag] = init_travel_time(travel_time_dict[tag])

    _travel_time_dict = travel_time_dict[tag]
    db = client['traffic_db_'+tag]


    Dict = {'N': {}, 'S': {}}

    if reportid:
        results = []
        user_dir = reportid[0]
        cols = [(db[key], key, value['Start'], value['End']) for key, value in section_ids[user_dir].items()]
        for tcol, key, start, end in cols:
            for i in range(0, maxv + 1):
                a = tcol[(str(i))].find_one({'reportid': reportid})
                if a:
                    results.append((str(i), key, start, end))
                    break
                # if a:
                #     print(a)
        for tt, key, start, end in results:
            time, level = _travel_time_dict[key][tt]
            rec = {'time': time,
                   'start': start,
                   'end': end,
                   'level': level }
            Dict[user_dir][start] = rec

        return Dict





    # Dict['N'] = {}
    # Dict['S'] = {}

    # for key, value in section_ids[direction].items():
    #     tt = str(int(w/strip))
    #     time, level = _travel_time_dict[key][tt]
    #     rec = {'time': time,
    #            'start': value['Start'],
    #            'end': value['End'],
    #            'level': level }

    #     Dict[value['Start']] = rec
    #     w += time / 60




    for sd, d in [(section_ids['N'], 'N'), (section_ids['S'], 'S')]:
        w = int(t[0])*60 + int(t[1])
        for key, value in sd.items():
            tt = str(int(w/strip))
            time, level = _travel_time_dict[key][tt]
            rec = {'time': time,
                   'start': value['Start'],
                   'end': value['End'],
                   'level': level }

            Dict[d][value['Start']] = rec
            w += time / 60


    # for tcol, key in cols:
    #     for i in range(0, maxv + 1):
    #         a = tcol[str(i)].find({'reportid': reportid} if reportid else {})
    #         if a.count() != 0:

    #             print(list(a))

    return jsonify(Dict[direction] if direction else Dict)



@app.route('/sysquery', methods=['POST'])
def sysquery():
    global section_ids
    global user_db
    rcol= user_db['Report']
    ucol = user_db['User']

    data = request.get_json()

    userid = data['userid']

    key = {"userid": userid}
    if ucol.find(key).count() == 0:
        return jsonify({'message':f'should register the account first'})
        # return jsonify({'message':f'should register the account first'})

    result = rcol.find(key)
    ret = []
    for obj in result:
        record = {'reportid': obj['reportid'],
                  'userid': obj['userid'],
                  'carid': obj['carid'],
                  'start': obj['start'],
                  'end': obj['end'],
                  'time': obj['time'] }
        ret.append(record)
        l = traffic_of_two_points(obj['start'], obj['end'], section_ids)
        print([key for key, _ in l])

    return jsonify(ret)



def fix_time(tcol, key, tt, num):
    global bound
    global bound2
    global travel_time_dict
    global speed_levels
    print('fix time: ', tcol, key, tt)

    level = 2

    # report_num = tcol[tt].find({}).count()
    current =  tcol[tt].find({})
    report_num = current.count()

    direction = 'S' if int(key) & 1 else 'N'
    length = section_ids[direction][key]['Length']
    # sec, value = section_ids[direction][key]

    travel_time_dict[key][tt] = (float(length) * 60 * 60 / speed_levels[level], level + 1)



    # for x in current:

    # for x in:
    #     print(x)

    # # if report_num + num > bound2:
    # #     num = int((report_num + num) / 2)
    # #     # affetch the next timeline
    # #     next_time = str(int(tt) + 1)
    # #     fix_time(tcol, key, next_time, num)



    # # tcol[time]

    # pass

@app.route('/report', methods=['POST'])
def report():
    global client
    global user_db
    global travel_time_db
    global traffic_db
    global section_ids
    global travel_time_dict
    global bound

    rcol= user_db['Report']
    _rcol= user_db['_Report']
    ucol = user_db['User']

    data = request.get_json()

    userid = data['userid']

    # serach its car id from ucol
    key = {"userid": userid}
    if ucol.find(key).count() == 0:
        return jsonify({'message':f'should register the account first'})

    obj = ucol.find_one(key)
    carid = obj['carid']

    # construct the data to insert from report
    start = data['start']
    end = data['end']
    time = data['time']

    t = time.split(' ')[1].split(':')
    day = time.split(' ')[0].split('/')
    # month / day
    m = int(day[0]) * 100
    d = int(day[1])
    tag = str(m + d)

    # create a new db with date
    db = client['traffic_db_'+tag]
    # client.drop_database('traffic_db_'+tag)

    l = traffic_of_two_points(start, end, section_ids)
    cols = [(db[key], key) for key, _ in l]
    direction = 'S' if int(cols[0][1]) & 1 else 'N'

    strip = 20
    w = int(t[0])*60 + int(t[1])

    now = datetime.now()
    sec = str(int(unix_time_secs(now)))
    r = str(int(random.uniform(100000, 999999)))
    reportid = direction+userid+r+sec+'.'+day[0]+'.'+day[1]
    maxv = int(24 * 60 / strip)

    if tag not in travel_time_dict:
        travel_time_dict[tag] = {}
        travel_time_dict[tag]  = init_travel_time(travel_time_dict[tag])

    _travel_time_dict = travel_time_dict[tag]

    # report rate = 10%
    # 4500 * 10% = 450
    for tcol, key in cols:
        tt = str(int(w/strip))
        rec = { 'reportid': reportid, "userid": userid, "time": time }
        tcol[tt].insert_one(rec)

        report_num = tcol[tt].find({}).count()
        # print(report_num)
        t_time, level = _travel_time_dict[key][tt]

        w += t_time / 60

        if report_num + 1 > bound and bound != -1:
            bound = -1
            num = int((report_num + 1) / 2)
            # affetch the next timeline
            next_time = str(int(tt) + 1)
            fix_time(tcol, key, next_time, num)


    # # all location
    # for tcol, key in cols:
    #     # all time
    #     for i in range(0, maxv + 1):

    #         a = tcol[str(i)].find({})
    #         if a.count() != 0:
    #             print('time:', i)
    #             print(list(a))
    #     print('-------------------------------')


        # print(a)
        # f = tcol.find_one(rec)
        # print(f)
    #     print(rec)
        # tcol[tt].update('{' + f'_id:{tt}' +  '}',
        #                 '{$push: {"reportid":"' + reportid  + '"}}')




    key = {'reportid': reportid}


    # for tcol in cols:
    #     # cursor = tcol.find({})
    #     print(list(tcol.find({})))

    # for tcol in cols:
    #     tcol.drop()
       # for x in tcol.find(key):
       #     print(x)

    #     loc_col[]


    # tcol = traffic_db[tag]

    # myquery = { "name": { "$regex": "^F" } }
    # newvalues = { "$set": { "alexa": "123" } }

    # tcol.update('{_id:1}','{$push: {score:{"physics":100}}}')


    # l.insert_one()
    # print([key for key, _ in l])

    # np.empty(())
    # 5 mins
    strip = 5
    dim1 = int(12 * (60 / strip))
    dim2 = len(section_ids['S'].items())

    # arr = np.empty((dim1, dim2), dtype=)
    # arr.fill({})
    # print(arr)
    # tl = traffic_of_two_points('基隆端', '高雄端', section_ids)
    # print([value['Start'] for key, value in tl])
    # print(len(tl))


     # # Make a query to the specific DB and Collection
    # cursor = db[collection].find(query)

    # # Expand the cursor and construct the DataFrame
    # df =  pd.DataFrame(list(cursor))





    # record = { 'reportid': userid+r+sec,
    #            'userid': userid,
    #            'carid': carid,
    #            'start': start,
    #            'end': end,
    #            'time': time }

    # rcol.insert_one(record)

    return jsonify({'message':f'successful create a report {reportid}', 'time': time, 'report_id': reportid})





@app.route('/deluser', methods=['POST'])
def del_user():
    global user_db
    col = user_db['User']
    # data = user_db['Report']

    data = request.get_json()

    if 'userid' not in data:
        return jsonify({'message':f'deluser argument not completed'})

    userid = data['userid']

    key = {"userid": userid}

    if col.find(key).count() == 0:
        return jsonify({'message':f'no user can be deleted'})

    col.delete_one(key)
    return jsonify({'message':f'delete user {userid}'})

@app.route('/register', methods=['POST'])
def add_user():
    # User column
    global user_db
    col = user_db['User']

    data = request.get_json()

    if 'userid' not in data or 'carid' not in data:
        return jsonify({'message':f'register argument not completed'})

    userid = data['userid']
    carid = data['carid']

    key = {"userid": userid }

    update = False
    new = False

    if col.find(key).count() == 0:
        new = True
        record = { 'userid': userid, 'carid': carid, 'reward:': 0 }
        col.insert_one(record)
    else:
        obj = col.find_one(key)
        origin_carid = obj['carid']
        if origin_carid != carid:
            update = True
        data = {"$set":{"carid":carid}}
        col.update_one(key, data, upsert=True)

    for x in col.find(key):
        print(x)

    if new:
        return jsonify({'message':f'add user with new car id: {carid}'})
    elif update:
        return jsonify({'message':f'update car id: {carid}'})
    else:
        return jsonify({'message':f'car id already existed, not changed'})


def check_for_db(test_client,db_name):
    dblist = test_client.list_database_names()
    if db_name in dblist:
        print(db_name + ' ? database exists')
    else:
        print(db_name + ' ? database does NOT exists')


def predict(db):
    pass



def init_travel_time(travel_time_dict):
    global speed_levels
    global section_ids

    speed_levels = [90, 60, 40]
    level = 0

    l1 = list(section_ids['S'].items())
    l2 = list(section_ids['N'].items())

    l = l1 + l2

    strip = 20
    maxv = int(30 * 60 / strip)
    maxv = 200
    for key, value in l:
        travel_time_dict[key] = {}
        length = value['Length']
        # print(float(length) * 60 * 60 / 90)
        for i in range(0, maxv + 1):
            travel_time_dict[key][str(i)] = (float(length) * 60 * 60 / speed_levels[level], level + 1)

    return travel_time_dict
    # 4.1km
    # for x in l:

    # for

    # # l = section_ids['N'].items()
    # cols = [db[key] for key, _ in l]
    # strip = 20
    # maxv = int(24 * 60 / strip)
    # for tcol in cols:
    #     rec = {'time': 100}               # TODO should upon on every section
    #     for i in range(0, maxv + 1):
    #         tcol[str(i)].insert_one(rec)

    # # report rate = 5%
    # # 4000 * 5% =  200
    # bound = 200
    # for tcol in cols:
    #     rec = { 'reportid': reportid }
    #     tcol[tt].insert_one(rec)

    #     report_num = tcol[tt].find({})
    #     if report_num + 1 > bound:
    #         pass
    #         # affetch the next timeline



    # # all location
    # for tcol in cols:
    #     # all time
    #     for i in range(0, maxv + 1):
    #         a = tcol[str(i)].find({})

    #         if a.count() != 0:
    #             print(list(a))
    #     print('-------------------------------')





    # l = traffic_of_two_points('台北交流道', '新竹交流道', section_ids)

    # print(db.list_collection_names())
    # for i in l1:
    #     ncol.

    # print(section_ids['S'][l1[0]])

epoch = datetime.utcfromtimestamp(0)
def unix_time_secs(dt):
    return (dt - epoch).total_seconds() * 1


if __name__ == '__main__':
    global travel_time_dict
    travel_time_dict = {}
    global client
    client = pymongo.MongoClient("localhost", 27017)
    global travel_time_db
    global user_db
    global traffic_db
    global bound
    global bound2
    bound = 8
    bound2 = 6
    user_db = client.user_info
    traffic_db = client.traffic_info
    travel_time_db = client.travel_time_info

    # col = user_db['User']
    # col.drop()
    # col = user_db['Report']
    # col.drop()



    global section_ids
    section_ids = extract_data('motc_data/Section.xml',
                               callback=partial(id_process,
                                                road='000010'))

    print(client.list_database_names())

    print(f"\nopen http://localhost:{port}/pbot to wait bot server\n")

    datelist = pd.date_range(start="2021-01-01",end="2022-01-01")
    print(datelist)

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

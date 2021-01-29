from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_bootstrap import Bootstrap
from decrypt import decrypt_token
from pyngrok import ngrok
from datetime import datetime
import os
import pymongo
import time
from motc_data.motc_data import *
import pandas as pd
import random
import numpy as np

app = Flask(__name__)
bootstrap = Bootstrap(app)

## API
# register
# curl -X POST -d '{"userid":"12345", "carid":"AAA-0002"}' 127.0.0.1:8508/register -H 'Content-Type:application/json'

# delete user
# curl -X POST -d '{"userid":"12345"}' 127.0.0.1:8508/deluser -H 'Content-Type:application/json'

# report
# curl -X POST -d '{"userid":"12345", "start":"新竹交流道", "end":"台北交流道", "time":"1/28 17:00" }' 127.0.0.1:8508/query -H 'Content-Type: application/json'

# query user data
# curl -X POST -d '{"userid":"12345"}' 127.0.0.1:8508/query -H 'Content-Type: application/json'


HOST = None
BOT_HOST = 'http://localhost:443'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/pbot')
def psys():
    return render_template("pbot.html")

@app.route('/sbot', methods=['GET'])
def ssys():
    BOT_HOST = request.values.get('host')
    print(f'BOT_HOST = {BOT_HOST}')
    return 'OK'

@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory(os.path.join('templates', 'dist'), path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(os.path.join('templates', 'css'), path)

@app.route('/traffic', methods=['POST'])
def traffic_at_time():
    global traffic_db
    global section_ids
    global travel_time_dict

    data = request.get_json()

    time = data['time']
    direction = data['direction']

    reportid = data['reportid'] if 'reportid' in data else None

    t = time.split(' ')[1].split(':')
    day = time.split(' ')[0].split('/')

    w = int(t[0])*60 + int(t[1])

    m = int(day[0]) * 100
    d = int(day[1])
    tag = str(m + d)

    db = client['traffic_db_'+tag]

    cols = [(db[key], key) for key, _ in section_ids[direction].items()]
    strip = 20
    # maxv = int(24 * 60 / strip)

    Dict = {}

    for key, value in section_ids[direction].items():
        tt = str(int(w/strip))
        time = travel_time_dict[key][tt]
        rec = {'time': time,
               'start': value['Start'],
               'end': value['End'] }

        Dict[value['Start']] = rec
        w += time / 60

    # for tcol, key in cols:
    #     for i in range(0, maxv + 1):
    #         a = tcol[str(i)].find({'reportid': reportid} if reportid else {})
    #         if a.count() != 0:

    #             print(list(a))

    return jsonify(Dict)



@app.route('/query', methods=['POST'])
def query():
    global section_ids
    global user_db
    rcol= user_db['Report']
    ucol = user_db['User']

    data = request.get_json()

    userid = data['userid']

    key = {"userid": userid}
    if ucol.find(key).count() == 0:
        return jsonify({'message':f'should register the account first'})

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


@app.route('/report', methods=['POST'])
def report():
    global client
    global user_db
    global travel_time_db
    global traffic_db
    global section_ids
    global travel_time_dict

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
    client.drop_database('traffic_db_'+tag)

    l = traffic_of_two_points(start, end, section_ids)
    cols = [(db[key], key) for key, _ in l]

    strip = 20
    w = int(t[0])*60 + int(t[1])

    now = datetime.now()
    sec = str(int(unix_time_secs(now)))
    r = str(int(random.uniform(100000, 999999)))
    reportid = userid+r+sec
    maxv = int(24 * 60 / strip)

    # report rate = 5%
    # 4500 * 10% = 450
    bound = 200
    for tcol, key in cols:
        tt = str(int(w/strip))
        rec = { 'reportid': reportid, "userid": userid }
        tcol[tt].insert_one(rec)

        report_num = tcol[tt].find({}).count()
        print(report_num)

        w +=  travel_time_dict[key][tt] / 60


        # if report_num + 1 > bound:
        #     # affetch the next timeline
        #     next_time = str(int(tt) + 1)





    # all location
    for tcol, key in cols:
        # all time
        for i in range(0, maxv + 1):

            a = tcol[str(i)].find({})
            if a.count() != 0:
                print('time:', i)
                print(list(a))
        print('-------------------------------')


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

    return jsonify({'message':f'successful create a report {reportid}'})





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



def init_travel_time_db(db):
    global travel_time_dict
    global speed_levels
    global section_ids
    global client

    travel_time_dict = {}
    trave_time_dict = {}
    speed_levels = [90, 40]

    l1 = list(section_ids['S'].items())
    l2 = list(section_ids['N'].items())

    l = l1 + l2

    strip = 20
    maxv = int(24 * 60 / strip)
    for key, value in l:
        travel_time_dict[key] = {}
        length = value['Length']
        # print(float(length) * 60 * 60 / 90)
        for i in range(0, maxv + 1):
            travel_time_dict[key][str(i)] = float(length) * 60 * 60 / speed_levels[0]

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
    port = int(os.environ.get("SYSPORT", 8508))
    global client
    client = pymongo.MongoClient("localhost", 27017)
    global travel_time_db
    global user_db
    global traffic_db
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

    if not HOST: HOST = f'http://localhost:{port}'

    datelist = pd.date_range(start="2021-01-01",end="2022-01-01")
    print(datelist)


    init_travel_time_db(travel_time_db)

    print("============ App run ==========================")
    app.run(debug=True, port=port)

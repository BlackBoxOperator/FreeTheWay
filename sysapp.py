from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_bootstrap import Bootstrap
from decrypt import decrypt_token
from pyngrok import ngrok
import os
import pymongo
import time
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


@app.route('/query', methods=['POST'])
def query():
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
        record = {'userid': obj['userid'],
                  'carid': obj['carid'],
                  'start': obj['start'],
                  'end': obj['end'],
                  'time': obj['time'] }
        ret.append(record)

    return jsonify(ret)


@app.route('/report', methods=['POST'])
def report():
    global user_db
    rcol= user_db['Report']
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

    record = { 'userid': userid,
               'carid': carid,
               'start': start,
               'end': end,
               'time': time }

    rcol.insert_one(record)

    return jsonify({'message':f'successful create a report'})



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


if __name__ == '__main__':
    port = int(os.environ.get("SYSPORT", 8508))

    client = pymongo.MongoClient("localhost", 27017)

    global user_db
    user_db = client.user_info

    print(client.list_database_names())

    print(f"\nopen http://localhost:{port}/pbot to wait bot server\n")

    if not HOST: HOST = f'http://localhost:{port}'

    print("============ App run ==========================")
    app.run(debug=True, port=port)

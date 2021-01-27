from flask import Flask, render_template, send_from_directory, request
from flask_bootstrap import Bootstrap
from decrypt import decrypt_token
from pyngrok import ngrok
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)

HOST = None
BOT_HOST = None

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

if __name__ == '__main__':
    port = int(os.environ.get("SYSPORT", 8508))

    #print("============ Setup ngrok ======================")
    #ngrok.set_auth_token(decrypt_token(os.path.join('meta', 'encrypted.ngrok.token')))
    #hook_url = ngrok.connect(port).replace("http", "https")
    #print("Hook url: " + hook_url)

    print(f"\nopen http://localhost:{port}/pbot to wait bot server\n")

    if not HOST: HOST = f'http://localhost:{port}'

    print("============ App run ==========================")
    app.run(debug=True, port=port)

from flask import Flask, render_template, send_from_directory, request
from flask_bootstrap import Bootstrap
from decrypt import decrypt_token
from pyngrok import ngrok
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)

HOST = None
SYSTEM_HOST = None

@app.route('/')
def index():
    return render_template("index.html")

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

if __name__ == '__main__':
    port = int(os.environ.get("BOTPORT", 8501))

    #print("============ Setup ngrok ======================")
    #ngrok.set_auth_token(decrypt_token(os.path.join('meta', 'encrypted.bot.ngrok.token')))
    #hook_url = ngrok.connect(port).replace("http", "https")
    #print("Hook url: " + hook_url)

    print(f"\nopen http://localhost:{port}/psys to wait system server\n")

    if not HOST: HOST = f'http://localhost:{port}'

    print("============ App run ==========================")
    app.run(debug=True, port=port)

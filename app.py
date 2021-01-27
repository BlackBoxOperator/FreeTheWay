from flask import Flask, render_template, send_from_directory
from flask_bootstrap import Bootstrap
import os
app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory(os.path.join('templates', 'dist'), path)

if __name__ == '__main__':
    app.debug = True
    app.run()
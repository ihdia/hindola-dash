from flask import Flask,render_template, redirect, request, url_for, flash,abort,jsonify,session
from flaskext.mysql import MySQL
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cvitdata'
app.config['MYSQL_DATABASE_DB'] = 'annotation_web'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@socketio.on('message')
def handleMessage(msg):
    print(msg)
    send(msg)

if __name__ == '__main__':
    socketio.run(app,debug=True,host='10.5.0.142',port=20000)

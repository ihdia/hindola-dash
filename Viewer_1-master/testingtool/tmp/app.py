from flask import Flask,render_template, redirect, request, url_for, flash,abort,jsonify,session
from flaskext.mysql import MySQL
from flask_socketio import SocketIO, send,emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pankaj'
app.config['MYSQL_DATABASE_DB'] = 'annotation_web'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
pathtojson='/home/dba/test/json/'


@socketio.on('myevent')
def custom(message):
    print(message)

user_data = []

@socketio.on('fetchimage')
def fetchimage(db):
    conn = mysql.connect()
    cursor = conn.cursor()
       
@socketio.on('remove')
def remove():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('delete from bookmarks where 1 = 1')
    conn.commit()

@socketio.on('remove_corrections')
def remove_corrections():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('delete from corrections where 1 = 1')
    conn.commit()
    # print("hohohoho")

@socketio.on('bookmark_image')
def bookmark_image(list):
    conn = mysql.connect()
    cursor = conn.cursor()
    # print(list)
    sql = 'insert into bookmarks (file) VALUES (%s)'
    data = (list[1])
    cursor.execute(sql,data)
    # sql = 'delete from info where localurl = %s'
    # data = (list[4])
    # cursor.execute(sql,data)
    conn.commit()

@socketio.on('correct_image')
def correct_image(list):
    conn = mysql.connect()
    cursor = conn.cursor()
    # print(list)
    sql = 'select file from info where localurl = %s'
    data = (list)
    cursor.execute(sql,data)
    file = cursor.fetchone()
    # print(file[0][0])
    sql = 'select pfilepath from puids where pfile = %s'
    data = (file[0])
    cursor.execute(sql,data)
    filepath = cursor.fetchone()
    # print(filepath[0])
    sql = 'insert into corrections (pfile,pfilepath) VALUES (%s,%s)'
    data = (file[0],filepath[0])
    cursor.execute(sql,data)
    conn.commit()

@socketio.on('filter_image')
def filter_image(db,variable):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql= 'select localurl from info where status = %s'
    data = ("skipped")
    cursor.execute(sql,data)
    rows = cursor.fetchall()
    tmp = []
    # print(rows)
    if db != 0:
        if db == "PIH":
            for row in rows:
                if 'penn' in row[0]:
                    tmp.append(row)
        elif db == "Bhoomi":
            for row in rows:
                if 'Bhoomi' in row[0]:
                    tmp.append(row)
        rows = tmp

    if variable != 0:
        count = 0   
        variable = variable*5
        for row in rows:
            count = count+1
            if count%variable == 0:
                tmp.append(row)
        rows = tmp
    emit('change_image',rows)

@socketio.on('fetchjsonfile')
def fetch(user,db,variable):
    print(user)
    conn = mysql.connect()
    cursor = conn.cursor()
    if user != 0:
        sql= 'select distinct(file) from info where username = %s and status = "annotated"'
        data = (user)
        cursor.execute(sql,data)
    else:
        sql= 'select distinct(file) from info where status = "annotated"'
        cursor.execute(sql)

    rows = cursor.fetchall()
    tmp = []
    if db != 0:
        if db == "PIH":
            for row in rows:
                if 'pih' in row[0]:
                    tmp.append(row)
        elif db == "Bhoomi":
            for row in rows:
                if 'bhoomi' in row[0]:
                    tmp.append(row)
        rows = tmp
    if(len(rows) == 0):
        emit('fetchJson',"none")
    else:
        # print(rows)
#Getting File path
        sql = "select pfilepath from puids where pfile = %s"
        filename = (rows[variable%len(rows)][0])
        cursor.execute(sql,filename)
        path = cursor.fetchone()
        filepath = path[0]
#Opening file
        file=open(filepath,'r')
        data=str(file.read())
        file.close()
        # print(str(data))
#Getting Image link
        # sql = "select links from imagelinks where file = %s"
        # cursor.execute(sql,filename)
        # imagelink = cursor.fetchone()[0]
        # print(imagelink)  
        emit('fetchJson',str(data))  

@app.route('/bookmark')
def bookmark():
    db = mysql.connect()    
    cur = db.cursor()
    cur.execute("select * from bookmarks")
    links = cur.fetchall()
    rows = []
    for link in links:
        sql = "select localurl from info where file = %s"
        data = (link[0])
        cur.execute(sql,data)
        tmp = cur.fetchone()
        rows.append(tmp)
    print(rows)
    return render_template('bookmark.html',rows = rows)

@app.route('/null')
def null():
    return render_template('null.html')

@app.route("/")
def viewer():
    return render_template("viewer.html")

@app.route('/unannotated')
def unann():
    db = mysql.connect()    
    cur = db.cursor()
    cur.execute("select * from info")
    rows = cur.fetchall()
    cur.execute("select username from users")
    users = cur.fetchall()
    no_users = len(users)
    return render_template('unann.html',users=users,no_users=no_users,rows = rows)

@app.route('/annotated')
def ann():
    db = mysql.connect()    
    cur = db.cursor()
    cur.execute("select * from info")
    rows = cur.fetchall()
    cur.execute("select username from users")
    users = cur.fetchall()
    no_users = len(users)
    return render_template('annotated.html',users=users,no_users=no_users,rows = rows)

if __name__ == '__main__':
    socketio.run(app,debug=True,host='localhost',port=20000)

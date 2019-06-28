from myproject import app,db,socketio
from flask import render_template, redirect, request, url_for, flash,abort,jsonify,session
from flask_login import login_user,login_required,logout_user,current_user
from myproject.models import User
from myproject.forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
import time
from flask_socketio import  send,emit
# from flask_pymongo import PyMongo,MongoClient
from flask import Response
# from bson.json_util import loads
import json
import os, os.path
####################################################
# MySQL configurations
import pymysql
from flaskext.mysql import MySQL
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cvitdata'
app.config['MYSQL_DATABASE_DB'] = 'annotation_web'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
####################################################
# pathtojson='/home/saurav/Music/json/'
# pathtomodifiedjson='/home/saurav/Music/modified_json/'
# pathtojson='/home/saurav/Music/json/'
# pathtomodifiedjson='/home/saurav/Music/modified_json/'

pathtojson='/home/dba/test/json/'
# pathtomodifiedjson='/home/dba/test/modified_json/'

stat_B = 0
stat_D = 0
@socketio.on('myconnection')
def test_connect(msg):
    # TODO: push all in_process uid to uid table
    print(msg)

# r = json.dumps(jsonfile)
# print(type(r)) #Output str
# loaded_r = json.loads(r)
# print(type(loaded_r)) #Output dict
# t=json.load(json.dumps(jsonfile))

@socketio.on('fetchUID')
def fetchUID(aid):
    #  added to request queue
    # caid=RequestUIDS(ruid=aid)
    # db.session.add(caid)
    # db.session.commit()
    print('AID: ',aid, 'Requesting: ')

    sql = "INSERT INTO ruids (ruid) VALUES(%s)"
    data = (aid)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()


    time.sleep(1)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ruids limit 1;")
    conn.commit()

    conn = mysql.connect()
    # cursor = conn.cursor()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    sql2 = "SELECT COUNT(*) FROM corrections;"
    cursor.execute(sql2)
    de = cursor.fetchone()
    de = de['COUNT(*)']
    print(de)
    global stat_D
    global stat_filepath
    if de <= 0:
        cursor.execute("SELECT * FROM puids ORDER BY RAND() LIMIT 1;")
        pfile = cursor.fetchone()
        conn.commit()
        stat_D = 0
    else:
        cursor.execute("SELECT * FROM corrections ORDER BY RAND() LIMIT 1;")
        pfile = cursor.fetchone()
        conn.commit()
        filename=pfile['pfile']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM corrections WHERE pfile=%s",filename)
        stat_D = 1
        stat_filepath = pfile['pfilepath']
        conn.commit()
    
    


    # GET THE FIRST FILE IN modified folder
    # TODO: FIND THE FILE Number
    if pfile:
        # TODO(1): choose randomly from puids table
        filename=pfile['pfile']
        filepath=pfile['pfilepath']
        ##############################################
        # data='bhoomi_ANINGYA%20VYAKHYA_PIVS_001_16_Sun Jan 13 16:00:33 2019.json'
        print(filepath)
        file=open(filepath,'r')
        data=str(file.read())
        file.close()
        ############### uncomment below #########
        # TODO: add a session variable here with a key as "uid_by_aid" and value ="uid-aid"
        # if not session['uid_by_aid']:
            # session['uid_by_aid'] = str(uids[0].uid) +'_'+ str(current_user.id)
        #############################################

        #  add the info into table
        #  get the image links also

        # imagelink=ImageLinksi.query.filter_by(file=filename).first()
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
	
	
        sql="SELECT * FROM imagelinks WHERE file=%s LIMIT 1;"
        d=(filename)
        cursor.execute(sql,d)
        imagelinks=cursor.fetchone()
        conn.commit()

        dateOfAnnotation=time.ctime()
        status="in_process"
        # Info database, mark status Column as "in_process"

            # info=Info(str(current_user.username),filename,status,dateOfAnnotation,str(imagelink.links))
            # info=Info(file=filename,username=current_user.username,status=status,dateOfAnnotation,str(imagelink.links))
            # db.session.add(info)
            # db.sess ion.commit()

        sql = "INSERT INTO info(username, file,status,date,localurl) VALUES(%s, %s, %s,%s,%s)"
        d = (current_user.username,filename,status,dateOfAnnotation,imagelinks['links'])
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,d)
        conn.commit()

        emit('fetchUIDAnswer',str(data))
        # emit('fetchUIDAnswer',"no json in folder")
    else:
        emit('fetchUIDAnswer',"na")



@socketio.on('mydata')
def mydata(data):

    # TODO(2): check whether the data is in puids if there update the path accordingly....
    print(type(data)) # <class 'str'>
    # print('received data: ' + (data))
    jsonfile=json.loads(data)
    # print(jsonfile)
    filename=str(jsonfile['file'])

    print('filename saved: '+ filename)
    ###################################
    # delete in the modified path
    # fullpath=pathtomodifiedjson+filename+'_'+str(curr_time)'.json'
    # fullpath=pathtomodifiedjson+filename+'.json'
    # print(fullpath)
    # try:
    #     os.remove(fullpath)
    # except OSError:
    #     print("file not exist in modified directory")
    ###################################

    curr_time=time.ctime()
    newfullpath=pathtojson+filename+'_'+curr_time+'.json'
    print(newfullpath)
    file=open(newfullpath,'w')
    file.write(data)
    file.close()

    #TODO: check if filename as pfile exist in puid table, update the table column  "pfilepath"
    sql = "SELECT * from puids where pfile = %s LIMIT 1"
    d = filename
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql,d)
    puidtemp=cursor.fetchone()
    conn.commit()


    # put the file in processed .
    # pfile=PUIDS(pfile=filename,pfilepath=fullpath)
    # db.session.add(pfile)
    # db.session.commit()
    save_date = time.ctime()
    if puidtemp:
        # saving annotated image
        # update the puid table
        print("saving existing annotated image.....")
        sql = "UPDATE puids SET pfilepath=%s, saved_date=%s WHERE pfile=%s"
        d = (newfullpath, save_date, filename)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, d)
    else:
        # saving new Image
        print("saving new annotated image.....")
        sql = "INSERT INTO puids(pfile, pfilepath, saved_date) VALUES(%s, %s,%s)"
        data = (filename, newfullpath, save_date)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
    
    conn.commit()


    in_process="in_process"
    status="annotated"
    # temp = Info.query.filter_by(file=filename,username=str(current_user.username)).first()
    # temp.status=status
    # temp.dateOfAnnotation=str(temp.dateOfAnnotation)+"---"+str(time.ctime());
    # db.session.commit()

    sql = "UPDATE info SET status=%s WHERE file=%s and username=%s"
    d = (status,filename,current_user.username)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, d)
    conn.commit()

    print("saved annotated file: "+filename+" by User  :"+ str(current_user.username) )
    emit('saveconfirmation',"saved")

@socketio.on('request_cancelled')
def request_cancelled(n):
    filename=str(n)
    # putting back to UIDS
    # uid=UIDS(ufile=filename)
    # db.session.add(uid)
    # db.session.commit()
    print("request cancelled")

    conn = mysql.connect()
    cursor = conn.cursor()
    sql="insert into uids(ufile) values(%s)"
    data=(filename)
    cursor.execute(sql,data)
    conn.commit()

    # temp = Info.query.filter_by(file=filename,username=str(current_user.username)).first()
    # if temp:
    #     db.session.delete(temp)
    #     db.session.commit()

    conn = mysql.connect()
    cursor = conn.cursor()
    sql="DELETE from info WHERE file=%s and username=%s"
    data=(filename,current_user.username)
    cursor.execute(sql,data)
    conn.commit()


@socketio.on('fetchNext')
def fetchNext(n):
    filename=str(n)
    print('Skipped file: '+ filename)
    #########################
    # push to uid current uid
    # uid=UIDS(ufile=filename)
    # db.session.add(uid)
    # db.session.commit()
    global stat_B
    global stat_D
    global stat_filepath
    conn = mysql.connect()
    cursor = conn.cursor()
    if stat_B == 1:
        sql = "INSERT INTO bookmarks(file) VALUES(%s)"
        stat_B = 0
        data=(filename)
        cursor.execute(sql,data)
        conn.commit()
    elif stat_D == 1:
        sql = "INSERT INTO corrections(pfile,pfilepath) VALUES(%s,%s)"
        stat_D = 0
        data=(filename,stat_filepath)
        cursor.execute(sql,data)
        conn.commit()
    else:
        sql="INSERT INTO uids(ufile) VALUES(%s)"
        stat_B = 0
        data=(filename)
        cursor.execute(sql,data)
        conn.commit()

    #########################
    # remove in-process of this n in Info table
    # temp = Info.query.filter_by(file=filename,username=str(current_user.username)).first()
    # if temp:
    #     temp.status="skipped"
    #     db.session.commit()

    status="skipped"
    sql = "UPDATE info SET status=%s WHERE file=%s and username=%s"
    data = (status,filename,current_user.username)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    #########################

    time.sleep(1)


    emit('fetchNextResponse',str("skipped"))
    # else:
    #     # TODO: handle this exception
    #     emit('fetchNextResponse',str("none"))

################## handling file not found ########################
# reportBack function
@socketio.on('reportBack')
def reportBack(n):
    # emit('fetchNextResponse',str("skipped"))
    filename=str(n)
    print('Reported file: '+ filename)

    # delete from Image LInks
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("DELETE FROM imagelinks WHERE file=%s;",filename)
    conn.commit()

    # delete from UID
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM uids WHERE ufile=%s",filename)
    conn.commit()


    pathtoreportfile='home/dba/test/report.text'
    # keep the corrupted file in a text file
    with open(pathtoreportfile,'a') as f:
        f.write(filename)
    
    emit('fetchNextResponse',str("Reported"))
###################################################################
# fetchURL and send it back
@socketio.on('fetchURL')
def fetchURL(aid):

    #  added to request queue
    # caid=RequestUIDS(ruid=aid)
    # db.session.add(caid)
    # db.session.commit()
    print('AID: ',aid, 'Requesting: ')

    sql = "INSERT INTO ruids (ruid) VALUES(%s)"
    data = (aid)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()

    time.sleep(1)
    # Puppy.query.all()
    # aid=RequestUIDS.query.all()
    # if aid[0].ruid:
    #     db.session.delete(aid[0])
    #     db.session.commit()

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ruids limit 1;")
    conn.commit()


    n=0
    # uids=UIDS.query.all()

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * from uids LIMIT 1;")
    rows = cursor.fetchone()
    conn.commit()

    # print("Allocated "+str(len(uids)))
    # print(random.randint(1,len(uids)))
    if rows:
        # n=randint(1,len(uids))
        # db.session.delete(uids[n])
        # db.session.commit()

        # SELECT * FROM uids ORDER BY RAND() LIMIT 1
        conn = mysql.connect()
        # cursor = conn.cursor()
       	cursor = conn.cursor(pymysql.cursors.DictCursor)
        sql2 = "SELECT COUNT(*) FROM bookmarks;"
        cursor.execute(sql2)
        de = cursor.fetchone()
        de = de['COUNT(*)']
        print(de)
        global stat_B
        if de <= 0:
                cursor.execute("SELECT * FROM uids ORDER BY RAND() LIMIT 1;")
                uid = cursor.fetchone()
                conn.commit()
                filename=uid['ufile']
                stat_B = 0
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM uids WHERE ufile=%s",filename)
                uid = cursor.fetchone()
                conn.commit()
        else:
                cursor.execute("SELECT * FROM bookmarks ORDER BY RAND() LIMIT 1;")
                uid = cursor.fetchone()
                conn.commit()
                filename=uid['file']
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bookmarks WHERE file=%s",filename)
                uid = cursor.fetchone()
                stat_B = 1
                conn.commit()

		

        # int(uids[0].uid)
        # filename=str(uids[n].ufile)
        print("Allocated filename "+filename)

        # imagelink=ImageLinks.query.filter_by(file=filename).first()
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM imagelinks WHERE file=%s LIMIT 1;",filename)
        imagelinks = cursor.fetchone()
        conn.commit()


        imagelink=str(imagelinks['links'])
        jsonfile={}
        # give file id ,not n
        jsonfile['file']=filename
        jsonfile['imagelinks']=str(imagelink)
        data=json.dumps(jsonfile)
        print(type(data))

        # update the info table
        ############# uncomment below ############
        status="in_process"
        dateOfAnnotation=time.ctime()
        # info=Info(str(current_user.username),filename,status,dateOfAnnotation,str(imagelink))
        # db.session.add(info)
        # db.session.commit()

        sql = "INSERT INTO info(username, file,status,date,localurl) VALUES(%s, %s, %s,%s,%s)"
        d = (str(current_user.username),filename,status,dateOfAnnotation,imagelink)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, d)
        conn.commit()


        emit('fetchURLResponse',str(data))
    else:
        # TODO: handle this exception
        emit('fetchURLResponse',str("none"))


@app.route('/')
def home():
    # TODO: show user their undone work and update info table(inprocess-undone)
    # temp=Info.query.filter_by(status="in_process")
    # undoneUID=[]
    # for i in temp:
    #     # print(i.uid)
    #     i.status="undone"
    #     uid=UIDS((i.file))
    #     db.session.add(uid)
    # else:
    #     db.session.commit()

    # sql = "UPDATE tbl_user SET user_name=%s, user_email=%s, user_password=%s WHERE user_id=%s"
    in_process="in_process"
    undone="undone"
    sql = "UPDATE info SET status=%s WHERE status=%s"
    data = (undone,in_process)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()

    return render_template('home.html')


@app.route('/annotation')
@login_required
def annotationtool():

    # temp=Info.query.filter_by(status="in_process")
    # undoneUID=[]
    # for i in temp:
    #     # print(i.uid)
    #     i.status="undone"
    #     uid=UIDS((i.file))
    #     db.session.add(uid)
    # else:
    #     db.session.commit()

    in_process="in_process"
    undone="undone"
    sql = "UPDATE info SET status=%s WHERE status=%s"
    d = (undone,in_process)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, d)
    conn.commit()

    # ndoc=Info.query.filter_by(username=current_user.username).count()

    conn = mysql.connect()
    cursor=conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT count(*) as n FROM info WHERE username=%s and status=%s",(current_user.username,"skipped"))
    n_skipped = (cursor.fetchone())['n']
    # print("Skipped "+str(n_skipped))

    cursor.execute("SELECT count(*) as n FROM info WHERE username=%s and status=%s",(current_user.username,"undone"))
    n_undone = (cursor.fetchone())['n']
    # print("Undone: "+ str(n_undone))

    cursor.execute("SELECT count(*) as n FROM info WHERE username=%s and status=%s",(current_user.username,"annotated"))
    n_annotated = (cursor.fetchone())['n']
    # print("Annotated: "+ str(n_annotated))

    cursor.execute("SELECT count(*) as n FROM info WHERE username=%s",(current_user.username))
    n_served = (cursor.fetchone())['n']
    # print("Doc Served: "+ str(n_served))

    # nundone=Info.query.filter_by(username=current_user.username,status="undone").count()
    # nskipped=Info.query.filter_by(username=current_user.username,status="skipped").count()
    # nannotated=Info.query.filter_by(username=current_user.username,status="annotated").count()
    # ,nskipped=nskipped,nannotated=nannotated,nundone=nundone,ndoc=ndoc

    pannotate=0
    pskipped=0
    pundone=0
    if n_served!=0:
        pannotate=n_annotated/n_served*100
        pannotate=round(pannotate,2)
        pskipped=n_skipped/n_served*100
        pundone=n_undone/n_served*100
        
    return render_template('annotationtool.html',aid=current_user.id,n_served=n_served,n_undone=n_undone,n_skipped=n_skipped,n_annotated=n_annotated,pundone=pundone,pannotate=pannotate,pskipped=pskipped)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    # unset the session
    # session.pop('uid_by_aid','not_set')
    flash('You logged out!')
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user is not None and user.check_password(form.password.data):
            #Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0]=='/':
                next = url_for('annotationtool')

            return redirect(next)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()

        email=str(form.email.data)
        username=str(form.username.data)
        password=str(form.password.data)
        password=generate_password_hash(password)
        sql = "INSERT INTO users(email,username,password_hash) values(%s,%s,%s)"
        data = (email,username,password)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()

        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    # for i in range(1,792):
    #     t=UIDS(i)
    #     db.session.add(t)
    # db.session.commit()
    # db.create_all()
    # app.run(debug=True,host='10.5.0.142',port=12345)
    socketio.run(app,debug=True,host='10.5.0.142',port=12345)
    # socketio.run(app)

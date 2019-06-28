from myproject import app,db,socketio
from flask import render_template, redirect, request, url_for, flash,abort,jsonify,session
from flask_login import login_user,login_required,logout_user,current_user
from myproject.models import User,UIDS,RequestUIDS,PUIDS,Info,ImageLinks
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
# app.config["MONGO_URI"] = "mongodb://localhost:27017/annotate"
# mongo = PyMongo(app)

######### uncomment below ##########
# SESSION_TYPE = 'redis'
# app.config.from_object(__name__)
# session(app)
####################################
# sftp://dba@10.5.0.142/home/dba/test/json
pathtojson='/home/dba/test/json/'
pathtomodifiedjson='/home/dba/test/modified_json/'

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
    caid=RequestUIDS(ruid=aid)
    db.session.add(caid)
    db.session.commit()
    print('AID: ',aid, 'Requesting: ')

    time.sleep(1)
    # Puppy.query.all()
    aid=RequestUIDS.query.all()
    if aid[0].ruid:
        db.session.delete(aid[0])
        db.session.commit()

    # GET THE FIRST FILE IN modified folder
    # TODO: FIND THE FILE Number
    DIR = pathtomodifiedjson
    files=[name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]
    print("modified json"+str(len(files)))
    if len(files)>0:
        filename=str(files[0])
        n=int(filename[:-5])

        filepath=pathtomodifiedjson+filename
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
        imagelink=ImageLinks.query.filter_by(id=n).first()
        dateOfAnnotation=time.ctime()
        # Info database, mark status Column as "in_process"
        status="in_process"
        info=Info(str(current_user.id),str(n),status,dateOfAnnotation,str(imagelink.links))
        db.session.add(info)
        db.session.commit()
        print(data)
        emit('fetchUIDAnswer',str(data))
    else:
        emit('fetchUIDAnswer',"na")



@socketio.on('mydata')
def mydata(data):

    print(type(data)) # <class 'str'>
    # print('received data: ' + (data))
    jsonfile=json.loads(data)
    # print(jsonfile)
    n=int(jsonfile['file'])
    ###################################
    # delete in the modified path
    fullpath=pathtomodifiedjson+str(n)+'.json'
    print(fullpath)
    try:
        os.remove(fullpath)
    except OSError:
        print("file not exist")
    ###################################
    # put the file in processed .
    puid=PUIDS(n)
    db.session.add(puid)
    db.session.commit()

    fullpath=pathtojson+str(n)+'.json'
    file=open(fullpath,'w')
    file.write(data)
    file.close()

    status="annotated"
    temp = Info.query.filter_by(uid=str(n),aid=str(current_user.id)).first()
    temp.status=status
    temp.dateOfAnnotation=str(temp.dateOfAnnotation)+"---"+str(time.ctime());
    db.session.commit()
    print("saved annotated file: "+str(n)+" by User AId :"+ str(current_user.id) )
    emit('saveconfirmation',"saved")

@socketio.on('fetchNext')
def fetchNext(n):
    print('Skipped uid'+str(n))
    #########################
    # push to uid current uid
    uid=UIDS(int(n))
    db.session.add(uid)
    db.session.commit()
    #########################
    # remove in-process of this n in Info table
    temp = Info.query.filter_by(uid=str(n),aid=str(current_user.id)).first()
    if temp:
        db.session.delete(temp)
        db.session.commit()
    #########################
    #  added to request queue
    aid=int(current_user.id)

    caid=RequestUIDS(ruid=aid)
    db.session.add(caid)
    db.session.commit()
    print('AID: ',aid, 'Requesting: ')

    time.sleep(1)
    # Puppy.query.all()
    aid=RequestUIDS.query.all()
    if aid[0].ruid:
        db.session.delete(aid[0])
        db.session.commit()
        # set the session variable here
        # time.sleep(1)
        # TODO: n = no of annotated file in the database
    n=0
    uids=UIDS.query.all()
    if uids:
        db.session.delete(uids[0])
        db.session.commit()
        # int(uids[0].uid)
        n=int(uids[0].uid)
        imagelink=ImageLinks.query.get(n)
        # tempLinks = the nth url from ImageLinks TABLE
        imagelink=str(imagelink.links)
        jsonfile={}
        jsonfile['file']=n
        jsonfile['imagelinks']=str(imagelink)
        data=json.dumps(jsonfile)
        print(type(data))

        emit('fetchNextResponse',str(data))
    else:
        # TODO: handle this exception
        emit('fetchNextResponse',str("none"))



@socketio.on('autoupdate')
def autoupdate(jsondata):
    print(type(jsondata)) # <class 'str'>
    print('updating.....')
    jsonfile=json.loads(jsondata)
    n=int(jsonfile['file'])
    #############################
    # write to modified image
    fullpath=pathtomodifiedjson+str(n)+'.json'
    file=open(fullpath,'w')
    file.write(jsondata)
    file.close()
    #############################

@socketio.on('update')
def update(json_data):
    #w=1, upsert=True
    # mongo.db.docs.update_one({"file":3},{"$set": {"file":10}}, upsert=True)
    # return "Update Successful!"
    # update nth file
    d = json.load(json_data)
    # mongo.db.docs.update_one({"file":n},{"$set": d}, upsert=True)
    # return redirect(url_for("annotationtool"))

# fetchURL and send it back
@socketio.on('fetchURL')
def fetchURL(aid):

    #  added to request queue
    caid=RequestUIDS(ruid=aid)
    db.session.add(caid)
    db.session.commit()
    print('AID: ',aid, 'Requesting: ')

    time.sleep(1)
    # Puppy.query.all()
    aid=RequestUIDS.query.all()
    if aid[0].ruid:
        db.session.delete(aid[0])
        db.session.commit()
    # set the session variable here
    # time.sleep(1)
    # TODO: n = no of annotated file in the database
    n=0
    uids=UIDS.query.all()
    # print("Allocated "+str(len(uids)))
    # print(random.randint(1,len(uids)))
    if uids:
        n=randint(1,len(uids))
        db.session.delete(uids[n])
        db.session.commit()
        # int(uids[0].uid)
        n=int(uids[n].uid)
        imagelink=ImageLinks.query.get(n)
        # tempLinks = the nth url from ImageLinks TABLE
        imagelink=str(imagelink.links)
        jsonfile={}
        jsonfile['file']=n
        jsonfile['imagelinks']=str(imagelink)
        data=json.dumps(jsonfile)
        print(type(data))

        # update the info table
        ############# uncomment below ############
        status="in_process"
        dateOfAnnotation=time.ctime()
        info=Info(str(current_user.id),n,status,dateOfAnnotation,str(imagelink))
        db.session.add(info)
        db.session.commit()
        emit('fetchURLResponse',str(data))
    else:
        # TODO: handle this exception
        emit('fetchURLResponse',str("none"))

@socketio.on('pushebackUID')
def pushebackUID(uid):
    # TODO: get the uid last added to info table by current_user
    # and push it back to uid and
    # delete the same from puid
    current_userAID=current_user.id
    # get last updated value of current user
    uid=Info.query.filter_by(aid=str(current_userAID)).order_by(Info.dateOfAnnotation.desc()).first()
    if uid is not None:
        # delete from info
        db.session.delete(uid)
        db.session.commit()

        # delete from puids
        puid=PUIDS.query.filter_by(puid=uid.uid).first()
        db.session.delete(puid)
        db.session.commit()

        # insert to info
        uid=UIDS(uid=uid.uid)
        db.session.add(uid)
        db.session.commit()

@app.route('/')
def home():
    # TODO: show user their undone work and update info table(inprocess-undone)
    temp=Info.query.filter_by(status="in_process")
    undoneUID=[]
    for i in temp:
        # print(i.uid)
        i.status="undone"
        uid=UIDS(int(i.uid))
        db.session.add(uid)
    else:
        db.session.commit()

    return render_template('home.html')


@app.route('/annotation')
@login_required
def annotationtool():
    random_number = randint(1, 1000)
    return render_template('annotationtool.html',aid=current_user.id)

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

        if user.check_password(form.password.data) and user is not None:
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

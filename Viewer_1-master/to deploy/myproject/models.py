from myproject import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
# By inheriting the UserMixin we get access to a lot of built-in attributes
# which we will be able to call in our views!
# is_authenticated()
# is_active()
# is_anonymous()
# get_id()


# The user_loader decorator allows flask-login to load the current user
# and grab their id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):

    # Create a table in the db
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        # https://stackoverflow.com/questions/23432478/flask-generate-password-hash-not-constant-output
        return check_password_hash(self.password_hash,password)


#CREATE TABLE uids(
   # id    INTEGER  NOT NULL PRIMARY KEY
  # ,links VARCHAR(114) NOT NULL
# )

class UIDS(db.Model):
    __tablename__='uids'
    id=db.Column(db.Integer,primary_key=True)
    uid=db.Column(db.Integer,unique=True, nullable=False)
    # links=db.Column(db.String(114),nullable=False)

    def __init__(self,uid):
        self.uid=uid

class PUIDS(db.Model):
    __tablename__='puids'
    id=db.Column(db.Integer,primary_key=True)
    puid=db.Column(db.Integer)

    def __init__(self,puid):
        self.puid=puid

class RequestUIDS(db.Model):
    __tablename__='ruids'
    id=db.Column(db.Integer,primary_key=True)
    ruid=db.Column(db.Integer)

    def __init__(self,ruid):
        self.ruid=ruid

class Info(db.Model):
    __tablename__='info'

    id=db.Column(db.Integer,primary_key=True)
    aid=db.Column(db.String(64))
    uid=db.Column(db.String(64))
    # TODO: add the status column
    status=db.Column(db.String(10))
    imagelinks=db.Column(db.String(120))# time.ctime()
    dateOfAnnotation=db.Column(db.String(100))# time.ctime()

    def __init__(self,aid,uid,status,dateOfAnnotation,imagelinks):
        self.aid=aid
        self.uid=uid
        self.status=status
        self.dateOfAnnotation=dateOfAnnotation
        self.imagelinks=imagelinks

# CREATE TABLE imagelinks(
   # id    INTEGER  NOT NULL PRIMARY KEY
  # ,links VARCHAR(114) NOT NULL
# );
class ImageLinks(db.Model):
    __tablename__='imagelinks'

    id=db.Column(db.Integer,primary_key=True)
    links=db.Column(db.String(120),nullable=False)

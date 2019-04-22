from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask_user import UserMixin
from settings import ConfigClass
from werkzeug.security import generate_password_hash, check_password_hash 
from killCodeGen import getCode
from datetime import datetime
import time

app = Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    ID = db.Column('id', db.Integer, primary_key=True)

    #user auth
    username = db.Column('username', db.String(50), nullable=False, unique=True)
    password = db.Column('password', db.String(255), nullable=False, server_default='')

    #email bits
    email = db.Column('email', db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column('time_confirmed', db.DateTime())

    #user info
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    name = db.Column('name', db.String(255), nullable=False)
    killCode = db.Column('kill_code', db.String(255), server_default="")

    # O = OZ, M = Mod, H = Human, Z = Zombie, C = Corpse
    status = db.Column('player_status', db.String(1), server_default="C")

    #player willing to be the OZ
    willingOZ = db.Column('willing_oz', db.Boolean(), server_default="False")

    #number of kills this game
    gameKills = db.Column('game_kills', db.Integer(), server_default="0")

    #total number of kills for this player
    totalKills = db.Column('total_kills', db.Integer(), server_default="0")

    #Column will bet set to number of seconds between start and death on death
    gameSecondsAlive = db.Column('game_seconds_alive', db.Integer(), server_default="0")

    #Total seconds alive over all games added to on death of game close
    totalSecondsAlive = db.Column('total_seconds_alive', db.Integer(), server_default = "0")

    #number of games played
    gamesPlayed = db.Column('games_played', db.Integer(), server_default = "0")

    #whether or not the player is in the current game
    inGame = db.Column('in_current_game', db.Boolean(), server_default="False")

    #user methods
    def __init__(self, username, email, name):
        self.username=username
        self.email=email
        self.name=name


    def setPassword(self, password):
        self.password = generate_password_hash(password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def getNewKillCode(self):
        newKC=getCode()
        unique=False
        x = User.query.filter_by(killCode=newKC).first()
        while x is not None:
            newKC=getCode()
            x = User.query.filter_by(killCode=newKC).first()
        self.killCode = newKC
        db.session.commit()

    def update_status(self, newStatus):
        self.status=newStatus
        if newStatus=="H":
            self.getNewKillCode()
        if newStatus=="C":
            self.inGame=False
        db.session.commit()

    def join_game(self, OZ):
        self.getNewKillCode()
        self.inGame=True
        self.gamesPlayed += 1
        if self.status != "M":
            self.update_status("H")
        self.willingOZ = OZ
        newHomeMsg("%s has joined the game!" % (self.name))
        db.session.commit()

    def killed(self, secondsAlive):
        self.status = "Z"
        self.gameSecondsAlive = secondsAlive
        self.totalSecondsAlive += secondsAlive
        db.session.commit()

    def addKill(self):
        self.gameKills += 1
        self.totalKills += 1
        db.session.commit()

    def endGame(self):
        self.status="C"
        self.killCode=""
        self.gameKills=0
        self.willingOZ=False
        self.inGame=False
        db.session.commit()

    def addToGame(self):
        self.status="H"
        self.getNewKillCode()
        self.inGame=True
        db.session.commit()

    def get_id(self):
        return self.ID




#who killed who. victim is unique because you can only be kileld once
class Kills(db.Model):
    __tablename__ = 'kills'
    ID = db.Column(db.Integer(), primary_key=True)
    killerID = db.Column('killer_id', db.Integer(), db.ForeignKey("users.id"))
    victimID = db.Column('victim_id', db.Integer(), db.ForeignKey("users.id"), unique=True)
    timeKilled = db.Column('time_killed', db.DateTime())

    def __init__(self, kID, vID):
        self.killerID = kID
        self.victimID = vID
        timeKilled = datetime.now().time()


#message on the homepage such as who killed who and when missions are posted, not mission text
class homePage(db.Model):
    __tablename__ = 'homepage'
    ID = db.Column(db.Integer(), primary_key=True)
    info = db.Column('message', db.String(512))
    time_str = db.Column('time_string', db.String(30))
    time = db.Column('time_posted', db.Integer())

    def __init__(self, msg):
        self.info = msg
        self.time_str = datetime.now().strftime("%a, %H:%M")
        self.time = int(time.time())


#messages posted on the chat page
class chat(db.Model):
    __tablename__ = 'chatmessages'
    ID = db.Column(db.Integer(), primary_key=True)
    poster = db.Column('poster', db.String(255), db.ForeignKey("users.email")) 
    message = db.Column('message', db.String(2048), nullable=False)
    timePosted = db.Column('time_posted', db.DateTime())


#when missions are posted files live in another folder  ##not used
class missions(db.Model):
    __tablename__ = 'mission details'
    ID = db.Column(db.Integer(), primary_key=True)
    missionName = db.Column('mission_name', db.String(128))
    filePath = db.Column('file_path', db.String(512))
    published = db.Column('published', db.Boolean(), server_default='0')


def newUsr(username, email, name, password):
    user = User(username, email, name)
    user.setPassword(password)
    db.session.add(user)
    db.session.commit()


def newKill(killer, victim):
    k = Kills(killer.ID, victim.ID)
    if killer.status=="O":
        name = "An OZ"
    else:
        name = killer.name
    newHomeMsg("%s killed %s" % (name, victim.name))
    db.session.add(k)
    db.session.commit()


def newHomeMsg(text):
    msg = homePage(text)
    db.session.add(msg)
    db.session.commit()


import time
from collections import OrderedDict
import os
DATABASE = {
    'drivername': 'postgres',
    'host': 'localhost',
    'port': '5432',
    'username': 'beebgar',
    'password': '72beebe72',
    'database': 'hvz'
}

#email account stuff
acct=''
pswd=''
with open("./gameInfo/email.cfg") as f:
    acct = f.readline().strip()
    pswd = f.readline().strip()

class ConfigClass(object):
    #Flask
    SECRET_KEY = b'\xaf\x0fe\xd9)^\xdd\xde\xb1\xde\xc0\xc0\x96\\0\xc3\xd23\x05\xd6\x17\x0b*\xd2'
    #SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://beebgar:72beebe72@localhost:5432/hvz'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_POOL_SIZE = 100
    #WtForms
    CSRF_ENABLED = True
    #Mail - account and password set lower down
    MAIL_DEFAULT_SENDER = 'hvz@bvu.edu'
    MAIL_USERNAME = acct
    MAIL_PASSWORD = pswd
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    #User
    USER_APP_NAME = 'Humans Vs Zombies Webserver'
    USER_ENABLE_EMAIL = True
    USER_ENABLE_FORGOT_PASSWORD = True
    USER_USER_SESSION_EXPIRATION = 86400
    USER_ENABLE_CHANGE_USERNAME = False
    #User-Email
    USER_CONFIRM_EMAIL_TEMPLATE = ""
    USER_PASSWORD_CHANGED_EMAIL_TEMPLATE=""
    USER_REGISTERED_EMAIL_TEMPLATE=""

def parseBool(s):
    if s=="True":
        return True
    return False


class GameInfo(object):
    #startTime
    time=0
    gameState=""
    missions=[]
    hMissions=OrderedDict()
    zMissions=OrderedDict()
    x=""
    def __init__(self):
        self.x="./gameInfo/"
        #set state
        with open(self.x+"state.cfg", "r") as f:
            self.gameState = f.read().rstrip()

        #set time
        with open(self.x+"time.cfg", "r") as f:
            self.time = int(f.read().rstrip())

        #do the missions bit
        with open(self.x+"missions.cfg", "r") as f:
            for line in f:
                temp=line.rstrip().split('=')
                mName=temp[0]
                h = parseBool(temp[1].split(';')[0])
                z = parseBool(temp[1].split(';')[1])
                self.hMissions[mName] = h
                self.zMissions[mName] = z
                self.missions.append(mName)




    def updateState(self, newState):
        with open(self.x+"state.cfg", "w") as f:
            f.write(newState+"\n")
        self.gameState=newState
        if newState=="STARTED":
            self.startGame()


    def updateMission(self, missionName, status):

        #set mission published forreal
        self.hMissions[missionName] = status[0]
        self.zMissions[missionName] = status[1]
        #write to file
        with open(self.x+'missions.cfg', 'r') as old:
            with open(self.x+'tempMissions.cfg', 'w') as new:
                for line in old:
                    if not line.startswith('#'):
                        if line.startswith(missionName):
                            new.write("%s=%s;%s\n"%(missionName,status[0],status[1]))
                        else:
                            new.write(line)
                    else:
                        new.write(line)
        os.system("mv " + self.x + "tempMissions.cfg " + self.x + "missions.cfg")


    def startGame(self):
        t=int(time.time())
        self.time=t
        with open(self.x+"time.cfg", "w") as f:
            f.write(str(t))

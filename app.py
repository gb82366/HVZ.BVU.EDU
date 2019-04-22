import os
from flask import Flask, render_template, abort, request, redirect, \
url_for,flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_mail import Mail, Message
from settings import ConfigClass, GameInfo
from flask_login import login_required, LoginManager, UserMixin,\
login_user, current_user, logout_user
from flask_wtf import FlaskForm
from forms import *
from models import User, Kills, homePage, chat, newUsr, newKill, newHomeMsg
import hashlib
import time
from collections import OrderedDict
from flask_socketio import SocketIO, send, emit
from datetime import datetime
from threading import Thread
from random import choice

def calcGameTime(start):
    currTime=int(time.time())
    return  currTime-start

def timeStr(t):
    hours=t//3600
    minutes=(t%3600)//60
    if t<86400:
        return ("%d hours, %d minutes" % (hours,minutes))
    else:
        hours=(t%86400)//3600
        days=t//86400
        return ("%d days, %d hours, %d minutes" % (days,hours,minutes))

def getNow():
    return datetime.now().strftime("%a, %H:%M")


def getDict(group, config):
    if group == "H":
        return config.hMissions
    return config.zMissions
#-----------------------------------SET UP-------------------------------#

#app & configure
app = Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')

#websocket stuff
socketio = SocketIO(app)
def socketMessage(event, data):
    socketio.emit(event, data)

#SQLAlchemy and Mail
db = SQLAlchemy(app)
mail = Mail(app)

#Flask Login Stuff
manager = LoginManager(app)
manager.login_view = 'login'

@manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#my Custom Config Object
config = GameInfo()



#-----------CONTEXT PROCESSING(STUFF EVERY ROUTE SHOULD HAVE)------------#
@app.context_processor
def get_game_state():
    return dict(game_state = config.gameState)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


#-----------------------------HELPER FUNCTIONS---------------------------#
def bulkMail(subject, body, recipients):
    with app.app_context():
        with mail.connect() as conn:
            for recipient in recipients:
                msg = Message(subject, recipients=[recipient])
                msg.html = body
                conn.send(msg)
    return

def htmlify(text):
    x=text.split('\n')
    for i in range(len(x)):
        if x[i].startswith("<") == False:
            x[i] = '<p>'+x[i]+'</p>'
    return "\n".join(x)

def send_email(group, subject, content):
    if group == "A":
        recip = User.query.filter_by(inGame=True).all()
    else:
        recip = User.query.filter_by(status=group).all()
    all_recip = []
    for player in recip:
        all_recip.append(player.email)

    html = htmlify(content)
    body = render_template('generic_email.html', subject=subject, content=html)
    mail_thread = Thread(target=bulkMail, args=(subject, body, all_recip), daemon=True)
    mail_thread.start()
    return

def mission_published_email(group):
    group_name = "All"
    all_recip=[]
    if group == "HZ":
        recip = User.query.filter_by(inGame=True).all()
    else:
        recip = User.query.filter_by(status=group).all()
        if group=="H":
            group_name="Humans"
        else:
            group_name="Zombies"

    for player in recip:
        all_recip.append(player.email)

    if group=="Z":
        recip = User.query.filter_by(status="O").all()
        for player in recip:
            all_recip.append(player.email)


    subject = "A new mission has been published"
    body = render_template("mission_email.html", group=group_name)

    mail_thread = Thread(target=bulkMail, args=(subject, body, all_recip), daemon=True)
    mail_thread.start()
    return


#-----------------------------------ROUTES-------------------------------#
#Home
@app.route("/", methods=['GET'])
@app.route("/index", methods=['GET'])
def home():
    x = homePage.query.order_by(desc(homePage.time)).limit(10).all()
    messages=[]
    for i in x:
        messages.append((i.time_str,i.info))
    return render_template("home.html", messages=messages)


#Login
@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login = LoginForm()
    if login.validate_on_submit():
        print("Attempting Login")
        user = User.query.filter_by(email=login.email.data.lower().strip()).first()
        if user is None or not user.check_password(login.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', form=login)


#Logout
@app.route("/logout")
@login_required
def logout():
    print("Logging out "+current_user.name)
    logout_user()
    return redirect(url_for('home'))


#Missions
@app.route("/missions", methods=['GET'])
@login_required
def missions():
    if current_user.status=="H":
        #see if any missions are published
        pub=False
        #build dict of published missions
        missions=getDict("H", config)
        for i in missions:
            pub = missions[i]
            if pub:
                break
        pub = not pub
        return render_template("Hmissions.html", nonePub=pub, missions=missions)

    elif current_user.status in ["Z", "O", "M"]:
        pub=False
        missions=getDict("Z", config)
        for i in missions:
            pub = missions[i]
            if pub:
                break
        pub = not pub
        return render_template("Zmissions.html", nonePub=pub, missions=missions)
    else:
        flash("You are not a part of this game. Please contact a moderator if you believe this to be a mistake")
        return redirect(url_for('home'))


#Player Stats
@app.route("/mystats", methods=['GET'])
@login_required
def myStats():
    #get info for this page
    x=calcGameTime(config.time)
    gt=timeStr(x)
    tot=timeStr(x+current_user.totalSecondsAlive)
    if config.gameState!="STARTED":
        gt = "No open game."
        tot = timeStr(current_user.totalSecondsAlive)
    if current_user.inGame == False:
        gt = "Not in current game"
        tot = timeStr(current_user.totalSecondsAlive)
    return render_template("stats.html", game_time=gt, total_time=tot)


#Player listing
@app.route("/playerlist", methods=['GET'])
@login_required
def playerList():
    if config.gameState == "STARTED":
        users = User.query.filter_by(inGame=True).all()
    else:
        users = User.query
    h_count  = User.query.filter_by(status="H").count()
    oz_count = User.query.filter_by(status="O").count()
    z_count  = User.query.filter_by(status="Z").count()
    z_count += oz_count
    return render_template("playerList.html", players=users, h_count=h_count, z_count=z_count)


#Killcode Submission
@app.route("/killcodes", methods=['GET','POST'])
@login_required
def killCodes():
    kill = KillCodeSubmissionForm()
    if kill.validate_on_submit():
        if config.gameState=="STARTED":
            if current_user.status in ["Z","O"]:
                #find victim
                vic = User.query.filter_by(killCode=kill.killcode.data.strip()).first()
                #kill them
                vic.killed(calcGameTime(config.time))
                #add a kill to current user
                current_user.addKill()
                #create the kill relation
                newKill(current_user, vic)
                flash("%s is now a zombie." % (vic.name))
                msg = {'time':getNow()}
                if current_user.status == "O":
                    msg['content'] = ("An OZ has killed %s."%(vic.name))
                    socketMessage("home", msg)
                else:
                    msg['content'] = ("%s has killed %s." % (current_user.name, vic.name))
                    socketMessage("home", msg)
                return redirect(url_for('myStats'))
        else:
            flash("There is no active game")

    else:
        for field in kill.errors:
            for error in kill.errors[field]:
                flash(error)
    return render_template("killCodes.html", form=kill)


#Rules
@app.route("/rules", methods=['GET'])
def rules():
    return render_template("rules.html")

#Chat client
@app.route("/chat", methods=['GET'])
@login_required
def chat():
    return render_template("chat.html")

#Mod admin area
@app.route("/modpanel", methods=['GET', 'POST'])
@login_required
def modPanel():
    return render_template("modPanel.html")


#user registration
@app.route("/registration", methods=['GET','POST'])
def registration():
    register=RegistrationForm()
    if register.validate_on_submit():
        print("Registering a user")
        a = register.username.data.strip().lower()
        b = register.email.data.strip().lower()
        c = register.name.data.rstrip()
        d = register.password.data
        newUsr(a,b,c,d)
        flash("You have been registered successfully!")
        return redirect(url_for('login'))
    else:
        print("Validation errors")
        for field in register.errors:
            for error in register.errors[field]:
                flash(error)
    return render_template("register.html", form=register)

#password reset
@app.route("/passwordReset", methods=['GET','POST'])
def pwreset():
    pwReset=resetForm()
    if pwReset.validate_on_submit():
        print("Resestting a password")
        user = User.query.filter_by(email = current_user.email).first()
        user.setPassword(pwReset.password.data)
        flash("Your password has been changed successfully!")
        return redirect(url_for('myStats'))
    else:
        for field in pwReset.errors:
            for error in pwReset.errors[field]:
                flash(error)
    return render_template("pwReset.html", form=pwReset)

#-----------------------------------UTILITY ROUTES------------------------#


#----GAME STATUS----#
#mod open game
@app.route("/modpanel/openGame", methods=['GET','POST'])
@login_required
def openGame():
    if current_user.status=="M":
        config.updateState('OPEN')
        socketMessage('home', {'time':getNow(),'content':'The game is now open for joining!'})
        newHomeMsg("The game is now open for joining!")
        return redirect(url_for('modPanel'))
    else:
        return redirect(url_for('nosey'))

#mod start game
@app.route("/modpanel/startGame", methods=['GET','POST'])
@login_required
def startGame():
    if current_user.status=="M":
        config.updateState("STARTED")
        socketMessage('home', {'time':getNow(),'content':'The game has begun. Watch yourself.'})
        newHomeMsg("The game has begun. Watch yourself.")
        return redirect(url_for('modPanel'))
    else:
        return redirect(url_for('nosey'))

#mod close game
@app.route("/modpanel/closeGame", methods=['GET','POST'])
@login_required
def closeGame():
    if current_user.status=="M":
        config.updateState("CLOSED")
        x = User.query.filter_by(inGame=True).all()
        for i in x:
            i.endGame()
        socketMessage('home', {'time':getNow(),'content':'That\'s all folks. Thanks for playing'})
        newHomeMsg("That\'s all folks. Thanks for Playing")
        return redirect(url_for('modPanel'))
    else:
        return redirect(url_for('nosey'))

#----MOD UTILITY ROUTES---#
#mod publish mission
@app.route('/modpanel/publishMissions', methods=['GET','POST'])
@login_required
def pubMission():
    if current_user.status=="M":
        return render_template('publishMissions.html', missions=config.missions)
    else:
        return redirect(url_for('nosey'))


@app.route('/modpanel/publishMissions/update', methods=['GET','POST'])
@login_required
def updateMission():
    if current_user.status=="M":
        print(request.form)
        mission = request.form['mission']
        status = request.form['status']
        group = status
        if status=='none':
            status=[False,False]
        elif status=='H':
            status=[True,False]
        elif status=='Z':
            status=[False,True]
        elif status=='HZ':
            status=[True,True]
        config.updateMission(mission, status)
        flash("Mission: %s successfully published" % mission)
        newHomeMsg("A new mission has been published")
        socketMessage('home', {'time':getNow(), 'content':'A new mission has been published.'})
        if group != 'none':
            mission_published_email(group)
        return "doesn't matter"

#mod check OZs
@app.route('/modpanel/OZList')
@login_required
def ozList():
    #gather list
    if current_user.status=="M":
        OZs = User.query.filter_by(willingOZ=True).all()
        ozl = []
        for i in OZs:
            ozl.append((i.name, i.email))
        return render_template('OZPage.html', lst=ozl)

    else:
        return redirect(url_for('nosey'))

#mod change player status
@app.route('/modpanel/statusUpdate', methods=['GET', 'POST'])
@login_required
def statusUpdate():
    if current_user.status=="M":
        form = modPlayerStatus()
        if form.validate_on_submit():
            em = form.player.data.strip().lower()
            user = User.query.filter_by(email=em).first()
            if form.newStatus.data!="Z":
                user.update_status(form.newStatus.data)
            else:
                user.killed(calcGameTime(config.time))
            flash("%s's status updated successfully." % (user.name))
            return redirect(url_for('modPanel'))
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    flash(error)
        return render_template('masterForm.html', form=form, tit="Player Status")
    else:
        return redirect(url_for('nosey'))


#mod update killcode
@app.route('/modpanel/updateKillCode', methods=['GET','POST'])
@login_required
def updateKC():
    if current_user.status=="M":
        form = modUpdateKillCode()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.player.data.strip().lower()).first()
            user.getNewKillCode()
            flash("%s's killcode updated successfully" % (user.name))
            return redirect(url_for('modPanel'))
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    flash(error)
        return render_template('masterForm.html', form=form, tit="Update Killcode")
    else:
        return redirect(url_for('nosey'))


#mod reveal OZ
@app.route('/modpanel/revealOZ', methods=['GET','POST'])
@login_required
def reveal():
    if current_user.status=="M":
        OZ = User.query.filter_by(status='O')
        for i in OZ:
            newHomeMsg("%s has been revealed as an OZ." % (i.name))
            socketMessage('home', {'time':getNow(),'content':"%s has been revealed as an OZ." % i.name})
            i.update_status("Z")
        return redirect(url_for('modPanel'))
    else:
        return redirect(url_for('nosey'))

#mod designate OZ
@app.route('/modpanel/designateOZ', methods=['GET','POST'])
@login_required
def designate():
    if current_user.status=="M":
        form=modDesignateOZ()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.player.data.strip().lower()).first()
            user.update_status("O")
            socketMessage('home', {'time':getNow(),'content':"The mods have designated an OZ. Trust no one."})
            newHomeMsg("The mods have designated an OZ. Trust no one.")
            return redirect(url_for('modPanel'))
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    flash(error)
        return render_template('masterForm.html', form=form, tit="Designate OZ")
    else:
        return redirect(url_for('nosey'))

#mod home page message
@app.route('/modpanel/message', methods=['GET','POST'])
@login_required
def message():
    if current_user.status=="M":
        form=modHomePageMessage()
        if form.validate_on_submit():
            msg = ' <i>The mods say </i> "'+form.message.data.strip()+'"'
            socketMessage('home', {'time':getNow(),'content':msg})
            newHomeMsg(msg)
            flash('Message has been posted to home page')
            return redirect(url_for('modPanel'))
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    flash(error)
        return render_template('masterForm.html', form=form, tit='Home page Message')
    else:
        return redirect(url_for('nosey'))

#mod player join game
@app.route('/modpanel/addPlayer', methods=['GET','POST'])
@login_required
def addPlayer():
    if current_user.status == "M":
        form = modUserPick()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.user.data.strip().lower()).first()
            if config.gameState == "CLOSED":
                flash("The game is currently closed. There is currently no game to add this user to")
                return redirect(url_for('modPanel'))
            user.join_game(False)
            msg = "The mods have added %s to the game." % (user.name)
            socketMessage('home', {'time':getNow(),'content':msg})
            newHomeMsg(msg)
            flash("\""+msg+"\' posted to homepage")
            return redirect(url_for('modPanel'))
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    flash(error)
            return render_template('masterForm.html', form=form, tit='Add Player')
    else:
        return redirect(url_for('nosey'))



#mod email list
@app.route('/modpanel/email', methods=['GET','POST'])
@login_required
def email():
    if current_user.status == "M":
        form = modEmail()
        if form.validate_on_submit():
            subject = form.subject.data.strip()
            body = form.body.data.strip()
            group = form.group.data
            if group == "H":
                flash("Sending email to Humans.")
            if group == "Z":
                flash("Sending email to Zombies.")
            if group == "A":
                flash("Sending email to all players in the game")
            send_email(group, subject, body)
            return redirect(url_for('modPanel'))
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    flash(error)
            return render_template('masterForm.html', form=form, tit='Email')
    else:
        return redirect(url_for('nosey'))

#mod reset player password
@app.route('/modpanel/resetPlayerPassword', methods=["GET", "POST"])
@login_required
def modResetPlayerPassword():
    if current_user.status == "M":
        form = modUserPick()
        if form.validate_on_submit():
            #get user
            user_email = form.user.data.strip().lower()
            user = User.query.filter_by(email=user_email).first()
            #generate random password
            chars = "0123456789POIUYTREWQLKJHGFDSAMNBVCXZpoiuytrewqlkjhgfdsamnbvcxz"
            password = "".join([choice(chars) for i in range(6)])
            #set user's password
            user.setPassword(password)
            #flash message
            flash("%s's password has been changed to %s. Have them change this asap" % (user_email, password))
            #redirect back to mod page
            return redirect(url_for('modPanel'))
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    flash(error)
            return render_template('masterForm.html', form=form, tit="Reset Password")
    else:
        return redirect(url_for('nosey'))


#---- PLAYER JOIN----#
#player join game
@app.route("/join", methods=['GET','POST'])
@login_required
def joinGame():
    form = playerJoinGame()
    if config.gameState != "OPEN":
        flash("The game is not currently open for joining.")
        return redirect(url_for('home'))
    if form.validate_on_submit():
        current_user.join_game(form.OZ.data)
        socketMessage('home', {'time':getNow(),'content':" %s has joined the game!" % (current_user.name)})
        return redirect(url_for('myStats'))
    else:
        for field in form.errors:
            for error in form.errors[field]:
                flash(error)
    return render_template("masterForm.html", form=form, tit="Join Game")


#nosey people
@app.route("/niceTry")
def nosey():
    return render_template("nosey.html")

if __name__ == "__main__":
    socketio.run(app, port=80, host='0.0.0.0', debug=True)

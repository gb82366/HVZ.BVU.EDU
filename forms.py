from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, SelectField, validators, TextAreaField
from models import User, Kills

def noBamboozles(FlaskForm, field):#no html/javascript
    f = field.data
    if "<" in f or ">" in f or ";" in f or "&" in f or "=" in f:
        raise validators.ValidationError(message = "Hey, no bamboozles")

class RegistrationForm(FlaskForm):

    def nameIsName(FlaskForm, field):#making sure name contains first and last
        f = field.data
        if len(f.split())<2:
            raise validators.ValidationError(message = "Please enter your first and last name")

    name = StringField("First and Last Name", [
            validators.Length(min=5, max=255),
            validators.Required(message="You must enter a name."),
            noBamboozles,
            nameIsName])

    def usernameDb(FlaskForm, field):#new username
        un = User.query.filter_by(username=field.data.strip().lower()).first()
        if un is not None:
            raise validators.ValidationError(message = "Username taken")

    username = StringField("Username", [
            validators.Required(message="You must enter a username."),
            validators.Length(min=5, max=255),
            usernameDb,
            noBamboozles])

    def emailDb(FlaskForm, field):#new email
        em = User.query.filter_by(email=field.data.strip().lower()).first()
        if em is not None:
            raise validators.ValidationError(message = "Email in use")

    email = StringField("Email", [
            validators.Required(message = "You must enter an email."),
            validators.Length(min=6, max=255, message = "outside of length bounds"),
            validators.Email(message = "No, an email"),
            emailDb,
            noBamboozles])

    password = PasswordField('Password', [
            validators.Required(message="Passwords are required on this site"),
            validators.Length(min=8, message="Password must be at least 8 characters"),
            validators.EqualTo('confirmPW', message="Passwords must match")])

    confirmPW = PasswordField('Confirm Password', [
            validators.Required()])

    register = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField("Email", [
        validators.Required(),
        validators.Length(min=6, max=255)])
    password = PasswordField('Password', [
        validators.Required()])
    login = SubmitField("Login")


class KillCodeSubmissionForm(FlaskForm):

    def isValidCode(FlaskForm,field):
        vic = User.query.filter_by(killCode=field.data, status='H').first()
        if vic is None:
            raise validators.ValidationError("This person is already a zombie or the killcode was not valid.")

    killcode = StringField("Kill Code", [
            validators.Required(),
            isValidCode])
    submit = SubmitField("Submit")


class chatInput(FlaskForm):
    message = StringField("Message", [
            validators.Required(message = "You can't send an empty message"),
            noBamboozles])
    submit = SubmitField("Submit")

class resetForm(FlaskForm):
    password = PasswordField("New Password", [
            validators.Required(),
            validators.Length(min=8, message="Password must be at least 8 characters long."),
            validators.EqualTo('confirm', message="Passwords must match")])
    confirm = PasswordField("Confirm New Password", [
            validators.Required()])
    submit = SubmitField("Submit")

def isPlayer(FlaskForm, field):
    x = User.query.filter_by(email=field.data).first()
    if x is None:
        raise validators.ValidationError("This person is not a player")

class modPlayerStatus(FlaskForm):
    player = StringField("Player to modify's email", [
            validators.Required(message="You need to pick a player to modify"),
            validators.Email(message="Input must be an email address"),
            isPlayer])

    newStatus = SelectField("New Status:", [
            validators.Required(message="You must select a new status for this player")],
            choices=[("C", "Corpse"), ("Z","Zombie"),("H","Human"),("M","Moderator")])

    submit = SubmitField("Update Status")

class modDesignateOZ(FlaskForm):
    player = StringField("OZ:", [
            validators.required(message="You must pick a player to designate"),
            validators.Email(message="Input must be an email address"),
            isPlayer])
    submit = SubmitField("Designate")

class modUpdateKillCode(FlaskForm):
    player = StringField("Player to update:", [
            validators.Required(message="You must enter a player to update"),
            validators.Email(message="Input must be an email address"),
            isPlayer])
    submit = SubmitField("Update Player")

class playerJoinGame(FlaskForm):
    OZ = BooleanField("(Optional) I would like to be entered into the pool to be an OZ")
    rules = BooleanField("I agree to play by the rules as written by the mods", [
            validators.Required(message="You have to agree to the rules to play")])
    submit = SubmitField("Submit")

class modHomePageMessage(FlaskForm):
    message = TextAreaField("Message", [
            validators.Required(message="You can't send an empty message"),
            noBamboozles])
    submit = SubmitField("Submit")

class modUserPick(FlaskForm):
    user = StringField("User", [
            validators.Required(message="You must pick a user"),
            isPlayer])
    submit = SubmitField("Submit")

class modEmail(FlaskForm):
    group = SelectField("Group to Email:", [
            validators.Required("You must choose a group to email")],
            choices=[("H", "Human"), ("Z", "Zombie")])
    subject = StringField("Subject", [
            validators.required(message="Message must have a subject"),
            validators.Length(min=3, max=255, message="Outisde of length bounds.")])
    body = TextAreaField("Body:", [
            validators.required(message="There's no use to sending an email with an empty body")])
    submit = SubmitField("Submit")


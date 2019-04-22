# HVZ.BVU.EDU

This is a python based webserver using flask to service the game Humans Vs Zombies. (see https://en.wikipedia.org/wiki/Humans_vs._Zombies)

Required libraries:
- flask (base webserver)
- flask-mail (sends emails)
- flask-user (simplifies user process)
- flask-socketio (adds support for websockets)
- wtforms (makes web forms and validating input much easier)
- flask-wtf (adds flask support for wtforms)
- flask-sqlalchemy (database rows can be treated like objects)
- other standard library stuff and prerequisites that are installed automatically by pipenv when getting the others)

It currently supports:
- Players (Humans, Zombies, Corpses)
- Moderators (special powers listed farther down)
- Missions
- Email notifications
- websocket updates on home page for game updates
- Original Zombies

Moderator powers:
- Modify player status
- change player kill code
- reset a player's password
- disgnate/reveal OZ
- edit publish status of missions
- email a group
- send messages to homepage

Planned features:
- channel based chat
- mission editor
- autologin on user creation

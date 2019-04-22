from models import User
import sys
from random import choice

if (len(sys.argv)!=2):
    print("Error usage: python3 remoteUpdatePassword.py name@email.com")
    exit(1)

usr = User.query.filter_by(email=sys.argv[1]).first()


chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
randomPass = "".join([choice(chars) for a in range(6)])

usr.setPassword(randomPass)
print("Password for "+sys.argv[1]+" has been set to `"+randomPass+"`. Have them change this immediately!")

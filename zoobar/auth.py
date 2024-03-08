from zoodb import *
from debug import *

import hashlib
import secrets
from pbkdf2 import PBKDF2
import os

def newtoken(db, cred):
    hashinput = "%s.%s" % (secrets.token_bytes(16), cred.password)
    cred.token = hashlib.sha256(hashinput.encode('utf-8')).hexdigest()
    db.commit()
    return cred.token

def login(username, password):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if not cred:
        return None

    log(f"cred.salt: {cred.salt} type: {type(cred.salt)}")
    alleged_key = PBKDF2(password, cred.salt).read(32)
    if cred.password == alleged_key:
        return newtoken(db, cred)
    else:
        return None

def register(username, password):
    cred_db = cred_setup()
    cred = cred_db.query(Cred).get(username)
    if cred:
        return None

    # Salt and hash password.
    salt = str(os.urandom(8))
    key = PBKDF2(password, salt).read(32)

    newcred = Cred()
    newcred.username = username
    newcred.password = key
    newcred.salt = salt
    cred_db.add(newcred)
    cred_db.commit()

    nc = cred_db.query(Cred).get(username)
    log(f"New username: {nc.username} New password: {nc.password}")

    return newtoken(cred_db, newcred)

def check_token(username, token):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if cred and cred.token == token:
        return True
    else:
        return False

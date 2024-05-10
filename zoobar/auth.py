from zoodb import *
from debug import *

import hashlib
import secrets
import webauthn

def newtoken(db, person):
    hashinput = "%s.%s" % (secrets.token_bytes(16), person.password)
    person.token = hashlib.sha256(hashinput.encode('utf-8')).hexdigest()
    db.commit()
    return person.token

def login(username, password):
    db = person_setup()
    person = db.query(Person).get(username)
    if not person:
        return None
    if person.password == password:
        return newtoken(db, person)
    else:
        return None

def register(username, password):
    db = person_setup()
    person = db.query(Person).get(username)
    if person:
        return None
    newperson = Person()
    newperson.username = username
    newperson.password = password
    db.add(newperson)
    db.commit()
    return newtoken(db, newperson)

def webauthn_register_challenge(username):
    registration_options = webauthn.generate_registration_options(
        rp_id="localhost",
        rp_name="Zoobar",
        user_name=username
    )

    db = person_setup()
    person = db.query(Person).get(username)
    if person:
        return None
    newperson = Person()
    newperson.username = username
    newperson.challenge = webauthn.helpers.bytes_to_base64url(registration_options.challenge)
    db.add(newperson)
    db.commit()
    
    return webauthn.options_to_json(registration_options)

def webauthn_register(username, credential):
    db = person_setup()
    person = db.query(Person).get(username)
    if not person:
        return None

    try:
        webauthn.verify_registration_response(
            credential = credential,
            expected_challenge = webauthn.base64url_to_bytes(person.challenge),
            expected_rp_id = "localhost",
            expected_origin = "http://localhost:8080",
        )
    except webauthn.helper.exceptions.InvalidRegistrationResponse:
        return 
    
    return newtoken(db, person)

def check_token(username, token):
    db = person_setup()
    person = db.query(Person).get(username)
    if person and person.token == token:
        return True
    else:
        return False

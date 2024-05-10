from zoodb import *
from debug import *

import hashlib
import secrets
import webauthn

ORIGIN = "https://zoobar-localhost.csail.mit.edu:8443"
RP = "zoobar-localhost.csail.mit.edu"

def get_challenge_list(person):
    challenge_str = person.challenge
    if challenge_str is None:
        return []
    return challenge_str.split(';')

def get_challenge_str(challenge_lst):
    return ';'.join(challenge_lst)

def newtoken(db, person):
    hashinput = "%s.%s" % (secrets.token_bytes(16), person.cred_id)
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
        rp_id=RP,
        rp_name="Zoobar",
        user_name=username
    )

    db = person_setup()
    person = db.query(Person).get(username)
    if person:
        return None
    newperson = Person()
    newperson.username = username
    challenge_list = get_challenge_list(newperson)
    challenge_list.append(webauthn.helpers.bytes_to_base64url(registration_options.challenge))
    newperson.challenge = get_challenge_str(challenge_list)
    log(f"New register challenge for {username}: {newperson.challenge}")
    db.add(newperson)
    db.commit()

    options = webauthn.options_to_json(registration_options)
    return  options

def webauthn_auth_challenge(username):
    db = person_setup()
    person = db.query(Person).get(username)
    if not person:
        return None

    cred_descriptor = webauthn.helpers.structs.PublicKeyCredentialDescriptor(
        id=webauthn.helpers.base64url_to_bytes(person.cred_id)
    )
    auth_options = webauthn.generate_authentication_options(
        rp_id=RP,
        allow_credentials=[cred_descriptor]
    )

    challenge_list = get_challenge_list(person)
    challenge_list.append(webauthn.helpers.bytes_to_base64url(auth_options.challenge))
    person.challenge = get_challenge_str(challenge_list)
    log(f"New auth challenge for {username}: {person.challenge}")
    db.commit()

    options = webauthn.options_to_json(auth_options)
    return options

def webauthn_register(username, credential):
    db = person_setup()
    person = db.query(Person).get(username)
    if not person:
        return None

    challenge_list = get_challenge_list(person)
    expected_challenge = challenge_list.pop()
    log(f"Registering {username} with challenge {expected_challenge}")
    try:
        verification = webauthn.verify_registration_response(
            credential = credential,
            expected_challenge = webauthn.base64url_to_bytes(expected_challenge),
            expected_rp_id = RP,
            expected_origin = ORIGIN
        )
    except webauthn.helpers.exceptions.InvalidRegistrationResponse as e:
        log("failed registration")
        log(e)
        return

    person.cred_id = webauthn.helpers.bytes_to_base64url(verification.credential_id)
    person.cred_pk = webauthn.helpers.bytes_to_base64url(verification.credential_public_key)
    person.challenge = get_challenge_str(challenge_list)
    person.sign_count = 0
    db.commit()
    return newtoken(db, person)

def webauthn_login(username, credential):
    db = person_setup()
    person = db.query(Person).get(username)
    if not person:
        return None

    challenge_list = get_challenge_list(person)
    expected_challenge = challenge_list.pop()
    log(f"Loging in {username} with challenge {expected_challenge}")
    try:
        verification = webauthn.verify_authentication_response(
            credential = credential,
            expected_challenge = webauthn.base64url_to_bytes(expected_challenge),
            expected_rp_id = RP,
            expected_origin = ORIGIN,
            credential_public_key = webauthn.base64url_to_bytes(person.cred_pk),
            credential_current_sign_count = person.sign_count,
        )
    except webauthn.helpers.exceptions.InvalidAuthenticationResponse as e:
        log("failed auth")
        log(e)
        return

    person.challenge = get_challenge_str(challenge_list)
    person.sign_count += 1
    db.commit()
    return newtoken(db, person)

def check_token(username, token):
    db = person_setup()
    person = db.query(Person).get(username)
    if person and person.token == token:
        return True
    else:
        return False

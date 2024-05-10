from flask import g, redirect, render_template, request, url_for, Markup, Response
from functools import wraps
from debug import *
from zoodb import *
from typing import Optional

import auth
import bank
import json

class User(object):
    def __init__(self):
        self.person = None

    def checkLogin(self, username: str, credential: str) -> Optional[str]:
        token = auth.webauthn_login(username, credential)
        if token is not None:
            return self.loginCookie(username, token)
        else:
            return None

    def loginCookie(self, username: str, token: str) -> str:
        self.setPerson(username, token)
        return "%s#%s" % (username, token)

    def logout(self) -> None:
        self.person = None

    def addRegistration(self, username: str, cred: str) -> Optional[str]:
        token = auth.webauthn_register(username, cred)
        if token is not None:
            return self.loginCookie(username, token)
        else:
            return None

    def checkCookie(self, cookie: str) -> None:
        if cookie is None or '#' not in cookie:
            return
        (username, token) = cookie.rsplit("#", 1)
        if auth.check_token(username, token):
            self.setPerson(username, token)

    def setPerson(self, username: str, token: str) -> None:
        persondb = person_setup()
        self.person = persondb.query(Person).get(username)
        self.token = token
        self.zoobars = bank.balance(username)

def logged_in() -> bool:
    g.user = User()
    g.user.checkCookie(request.cookies.get("PyZoobarLogin"))
    if g.user.person:
        return True
    else:
        return False

def requirelogin(page):
    @wraps(page)
    def loginhelper(*args, **kwargs):
        if not logged_in():
            return redirect(url_for('login') + "?nexturl=" + request.url)
        else:
            return page(*args, **kwargs)
    return loginhelper

@catch_err
def login() -> Response:
    cookie = None
    login_error = ""
    user = User()

    log(f"Login request: {request.get_data()}")

    if request.method == 'POST':
        username = request.form.get('login_username')
        cred = json.loads(request.form.get('login_cred'))

        if 'submit_registration' in request.form:
            if not username:
                login_error = "You must supply a username to register."
            elif not cred:
                login_error = "You must supply a credential to register."
            else:
                cookie = user.addRegistration(username, cred)
                if not cookie:
                    login_error = "Registration failed."
        elif 'submit_login' in request.form:
            if not username:
                login_error = "You must supply a username to log in."
            elif not cred:
                login_error = "You must supply a credential to log in."
            else:
                cookie = user.checkLogin(username, cred)
                if not cookie:
                    login_error = "Invalid credential."

    nexturl = request.values.get('nexturl', url_for('index'))
    if cookie:
        response = redirect(nexturl)
        ## Be careful not to include semicolons in cookie value; see
        ## https://github.com/mitsuhiko/werkzeug/issues/226 for more
        ## details.
        response.set_cookie('PyZoobarLogin', cookie)
        log(f"Login response with cookie: {response.get_data()}")
        return response

    return render_template('login.html',
                           nexturl=nexturl,
                           login_error=login_error,
                           login_username=Markup(request.form.get('login_username', '')))

@catch_err
def logout() -> Response:
    if logged_in():
        g.user.logout()
    response = redirect(url_for('login'))
    response.set_cookie('PyZoobarLogin', '')
    return response

@catch_err
def get_register_challenge() -> Response:
    log(f"get_register_challenge request: {request.json}")
    return auth.webauthn_register_challenge(request.json["login_username"])

@catch_err
def get_auth_challenge() -> Response:
    log(f"get_auth_challenge request: {request.json}")
    return auth.webauthn_auth_challenge(request.json["login_username"])

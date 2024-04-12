#!/usr/bin/python3

import flask
import os
import base64
import json
import requests
import util
import ca
import acme

## Check if the CA key already exists; if not, generate a fresh one.
try:
    with open("ca.key", "rb") as f:
        ca_key = util.key_from_bytes(f.read())
except FileNotFoundError:
    ca_key = util.gen_key()
    with open("ca.key", "wb") as f:
        f.write(util.key_to_bytes(ca_key))

ca = ca.CA(ca_key, u"6.566 Certificate Authority")
server = acme.ACME(ca)
app = flask.Flask(__name__)
server.flask_init(app)

if __name__ == "__main__":
    with open('/dev/null', 'r') as null:
        os.dup2(null.fileno(), 0)
    app.run(debug = True, host = '0.0.0.0')

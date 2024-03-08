from flask import g, render_template, request
from debug import *
import os
import rpclib
import sys

sys.path.append(os.getcwd())
import readconf

@catch_err
def echo():
    host = readconf.read_conf().lookup_host('echo')
    log(f"Trying to connect to echo host: {host}")
    with rpclib.client_connect(host) as c:
        log(f"Connected to echo host: {host}")
        ret = c.call('echo', s=request.args.get('s', ''))
        return render_template('echo.html', s=ret)

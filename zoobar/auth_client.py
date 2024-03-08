from debug import *
from zoodb import *
import rpclib

sys.path.append(os.getcwd())
import readconf

@catch_err
def login(username, password):
    log(f"Sending login RPC username: {username} password: {password}")

    host = readconf.read_conf().lookup_host('auth')
    log(f"Trying to connect to auth host {host}")
    with rpclib.client_connect(host) as c:
        log(f"Connected to auth host {host}")
        ret = c.call('login', username=username, password=password)
        return ret

@catch_err
def register(username, password):
    log(f"Sending register RPC username: {username} password: {password}")

    host = readconf.read_conf().lookup_host('auth')
    log(f"Trying to connect to auth host {host}")
    with rpclib.client_connect(host) as c:
        log(f"Connected to auth host {host}")
        log(f"username: {username}, password:{password}")
        ret = c.call('register', username=username, password=password)
        return ret

@catch_err
def check_token(username, token):
    log(f"Sending check_token RPC username: {username} token: {token}")

    host = readconf.read_conf().lookup_host('auth')
    log(f"Trying to connect to auth host {host}")
    with rpclib.client_connect(host) as c:
        log(f"Connected to auth host {host}")
        ret = c.call('check_token', username=username, token=token)
        return ret


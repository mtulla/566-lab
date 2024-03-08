from debug import *
from zoodb import *
import rpclib

sys.path.append(os.getcwd())
import readconf

@catch_err
def transfer(sender, recipient, zoobars, token):
    log(f"Sending transfer RPC sender: {sender} recipient: {recipient} zoobars: {zoobars} token: {token}")

    host = readconf.read_conf().lookup_host('bank')
    log(f"Trying to connect to bank host {host}")
    with rpclib.client_connect(host) as c:
        log(f"Connected to bank host {host}")
        ret = c.call('transfer', sender=sender, recipient=recipient, zoobars=zoobars, token=token)
        return ret

@catch_err
def balance(username):
    log(f"Sending balance RPC username: {username}")

    host = readconf.read_conf().lookup_host('bank')
    log(f"Trying to connect to bank host {host}")
    with rpclib.client_connect(host) as c:
        log(f"Connected to bank host {host}")
        log(f"username: {username}")
        ret = c.call('balance', username=username)
        return ret

@catch_err
def init_account(username):
    log(f"Sending init_account RPC username: {username}")

    host = readconf.read_conf().lookup_host('bank')
    log(f"Trying to connect to bank host {host}")
    with rpclib.client_connect(host) as c:
        log(f"Connected to bank host {host}")
        ret = c.call('init_account', username=username)
        return ret

@catch_err
def get_log(username):
    log(f"Sending get_log RPC username: {username}")

    host = readconf.read_conf().lookup_host('bank')
    log(f"Trying to connect to bank host {host}")
    with rpclib.client_connect(host) as c:
        log(f"Connected to bank host {host}")
        ret = c.call('get_log', username=username)
        return ret


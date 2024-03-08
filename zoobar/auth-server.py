#!/usr/bin/env python3

import rpcsrv
import sys
import auth
from debug import *

class AuthRpcServer(rpcsrv.RpcServer):
    def rpc_login(self, username, password):
        log(f"Got a login RPC username: {username} password: {password}")
        return auth.login(username, password)

    def rpc_register(self, username, password):
        log(f"Got a register RPC username: {username} password: {password}")
        return auth.register(username, password)

    def rpc_check_token(self, username, token):
        log(f"Got a check_token RPC username: {username} token: {token}")
        return auth.check_token(username, token)


if len(sys.argv) != 2:
    log(sys.argv[0], "too few args")

s = AuthRpcServer()
s.run_fork(sys.argv[1])

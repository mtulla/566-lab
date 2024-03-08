#!/usr/bin/env python3

import rpcsrv
import sys
import bank
from debug import *

class BankRpcServer(rpcsrv.RpcServer):
    def rpc_transfer(self, sender, recipient, zoobars, token):
        log(f"Got a transfer RPC sender: {sender} recipient: {recipient} zoobars: {zoobars}")
        return bank.transfer(sender, recipient, zoobars, token)

    def rpc_balance(self, username):
        log(f"Got a balance RPC username: {username}")
        return bank.balance(username)

    def rpc_init_account(self, username):
        log(f"Got a init_account RPC username: {username}")
        return bank.init_account(username)

    def rpc_get_log(self, username):
        log(f"Got a get_log RPC username: {username}")
        return bank.get_log(username)


if len(sys.argv) != 2:
    log(sys.argv[0], "too few args")

s = BankRpcServer()
s.run_fork(sys.argv[1])

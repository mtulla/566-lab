from zoodb import *
from debug import *

import auth_client
import time

@catch_err
def transfer(sender, recipient, zoobars, token):
    # Authenticate sender
    if not auth_client.check_token(sender, token):
        raise ValueError("Cannot authenticate sender.")

    bankdb = bank_setup()
    senderacc = bankdb.query(Bank).get(sender)
    recipientacc = bankdb.query(Bank).get(recipient)

    sender_balance = senderacc.zoobars - zoobars
    recipient_balance = recipientacc.zoobars + zoobars

    if sender_balance < 0 or recipient_balance < 0:
        raise ValueError()

    senderacc.zoobars = sender_balance
    recipientacc.zoobars = recipient_balance
    bankdb.commit()

    transfer = Transfer()
    transfer.sender = sender
    transfer.recipient = recipient
    transfer.amount = zoobars
    transfer.time = time.asctime()

    transferdb = transfer_setup()
    transferdb.add(transfer)
    transferdb.commit()

@catch_err
def balance(username):
    db = bank_setup()
    user_balance = db.query(Bank).get(username)
    return user_balance.zoobars

@catch_err
def init_account(username):
    db = bank_setup()
    user_balance = db.query(Bank).get(username)
    if user_balance:
        return None

    new_account = Bank()
    new_account.username = username
    db.add(new_account)
    db.commit()

    na = db.query(Bank).get(username)
    log(f"New username: {na.username} New Balance: {na.zoobars}")

    return (new_account.username, new_account.zoobars)

@catch_err
def get_log(username):
    db = transfer_setup()
    l = db.query(Transfer).filter(or_(Transfer.sender==username,
                                      Transfer.recipient==username))
    r = []
    for t in l:
       r.append({'time': t.time,
                 'sender': t.sender ,
                 'recipient': t.recipient,
                 'amount': t.amount })
    return r



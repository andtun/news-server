# This Python file uses the following encoding: utf-8

import os
import json
from bottle import *
from firebase import firebase

AUTH_TABLE_ADR = "/Auth"

def status_message(code, description=None):
    return json.dumps({'code': code, 'description': description})

class User:
    login = ""
    pwd = ""
    mail = ""
    telegram = ""

    def __init__(self, login, pwd, mail, telegram):
        self.login = login
        self.pwd = pwd
        self.mail = mail
        self.telegram = telegram

    @staticmethod
    def get_from_auth(login):
        return db.get(AUTH_TABLE_ADR, login)

    @staticmethod
    def login_exists(login):
        res = User.get_from_auth(login) is not None
        return res

    def exists(self):
        return User.login_exists(self.login)

    @staticmethod
    def get(login):
        d = User.get_from_auth(login)
        return User(d['login'],
                    d['pwd'],
                    d.get('mail', None),
                    d.get('telegram', None))


db = firebase.FirebaseApplication("https://jkdev-news.firebaseio.com/")


@get("/<login>/register")
def register(login):

    pwd = request.query['pwd']
    mail = request.query.get('mail', None)
    telegram = request.query.get('telegram', None)

    user = User(login, pwd, mail, telegram)
    if not user.exists():
        db.post(AUTH_TABLE_ADR + "/" + login, user.__dict__)
        return status_message(200, 'Registration success')

    return status_message(406, 'Username already taken')

# run the server
run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
